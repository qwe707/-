# sumo_spsa_calibration.py

import os
import sys
import subprocess
import xml.etree.ElementTree as ET
import numpy as np
import tempfile
import shutil
import matplotlib.pyplot as plt
import csv
import traceback
import random
import math
import re

# --- 用户需要修改的配置 ---
# 请根据你的实际环境和文件路径修改以下变量

# 1. SUMO executable path
SUMO_PATH = shutil.which('sumo')
if SUMO_PATH is None:
    print("SUMO executable not found in PATH. Please specify the correct path manually.")
    SUMO_PATH = "D:/SUMO/bin/sumo.exe"  # <--- 修改此行：你的SUMO可执行文件路径
    if not os.path.exists(SUMO_PATH):
        sys.exit(f"Error: SUMO executable not found at the specified path: {SUMO_PATH}")

# 2. Base directory (where your sumo.cfg, .net.xml, .rou.xml, .add.xml templates are)
SCENARIO_DIR = "D:/SUMO"  # <--- 修改此行：你的SUMO场景文件所在目录
if not os.path.isdir(SCENARIO_DIR):
    sys.exit(f"Error: Scenario directory not found at: {SCENARIO_DIR}")

# 3. SUMO configuration file name (main template)
SUMO_CFG_FILE_NAME = "exaple2.sumocfg"  # <--- 修改此行：你的SUMO配置文件名
sumo_cfg_full_path = os.path.join(SCENARIO_DIR, SUMO_CFG_FILE_NAME)
if not os.path.exists(sumo_cfg_full_path):
    sys.exit(f"Error: SUMO config file not found at: {sumo_cfg_full_path}")

# 3b. Network file name - REQUIRED
NET_FILE_NAME = "lode2.net.xml"  # <--- 修改此行：你的路网文件名
net_file_full_path = os.path.join(SCENARIO_DIR, NET_FILE_NAME)
if not os.path.exists(net_file_full_path):
    sys.exit(f"Error: Network file not found at: {net_file_full_path}")

# 4. Main route file name (template for vType definitions and flow)
MAIN_ROUTE_FILE_NAME = "1.rou.xml"  # <--- 修改此行：你的路由文件名，包含vType定义
main_route_file_full_path = os.path.join(SCENARIO_DIR, MAIN_ROUTE_FILE_NAME)
if not os.path.exists(main_route_file_full_path):
    sys.exit(f"Error: Main route file not found at: {main_route_file_full_path}")

# 5. Template additional file name (for detectors)
DETECTOR_TEMPLATE_FILE_NAME = "edgelanetrafficpara.add.xml"  # <--- 修改此行：你的检测器定义文件
detector_template_full_path = os.path.join(SCENARIO_DIR, DETECTOR_TEMPLATE_FILE_NAME)
if not os.path.exists(detector_template_full_path):
    sys.exit(f"Error: Detector template file not found at: {detector_template_full_path}")


# 6. Detector IDs configured in your .add.xml file.
# These should include ALL detectors you will use for calibration, across all locations.
# Make sure these detectors output meanSpeed and nVehEntered in your .add.xml with freq=60
detectorIds = ["e2_E1_main_0", "e2_E1_main_1"]  # <--- 修改此列表：所有用于校准的检测器ID

# 7. Observed data CSV file path
OBSERVED_DATA_CSV_FILE = "D:\\研究生\\小论文\\DJI_001\\your_observed_data.csv"  # <--- 修改此行：你的观测数据CSV文件路径
if not os.path.exists(OBSERVED_DATA_CSV_FILE):
    sys.exit(f"Error: Observed data CSV file not found at: {OBSERVED_DATA_CSV_FILE}")

# 8. Simulation time settings
warmUpDuration = 540  # Warm-up period in seconds (数据在此期间被忽略)
INTERVAL_DURATION_SEC = 60  # SUMO检测器输出频率和观测数据间隔，必须匹配
NUM_OBSERVED_INTERVALS = 20  # 观测到的1分钟间隔总数

# 根据观测数据总时长计算总模拟时长 + 暖场期 + 结束缓冲
# 注意：如果你的观测数据不是连续的，需要调整此处的simDuration或observed_data_points的结构
total_obs_duration = NUM_OBSERVED_INTERVALS * INTERVAL_DURATION_SEC
simDuration = warmUpDuration + total_obs_duration + 180  # 180秒是结束缓冲，确保所有数据都被收集

# 9. Detector output file name (必须与你的.add.xml中检测器'file'属性一致)
DETECTOR_OUTPUT_FILE_NAME = "e2_detector_output.xml"

# 10. Parameters to calibrate and their bounds
# 确保这些名称与你的1.rou.xml中目标vType元素的属性名称匹配
# 速度参数的单位是m/s，流量参数是veh/min。校准单位要与仿真内部单位一致
parameters_to_calibrate = {
    'accel': (1.0, 4.0),       # 最大加速度 [m/s²]
    'decel': (1.5, 4.5),       # 期望减速度 [m/s²]
    'tau': (0.5, 2.0),         # 期望车头时距 [s]
    # maxSpeed是vType的期望最高速度，其单位是m/s，范围应该反映车辆在非限速下的潜在速度
    'maxSpeed': (30.0, 35.0),  # vType的最高速度 [m/s] (例如 108-126 km/h)
    # speedFactor是乘数，normc(mean, std_dev, lower_bound, upper_bound)
    'speedFactor_mean': (1.0, 1.5),     # speedFactor正态分布的平均值
    'speedFactor_std_dev': (0.05, 0.3), # speedFactor正态分布的标准差 (必须 > 0)
    # 换道参数
    'lcSpeedGain': (0.0, 5.0),
    'lcStrategic': (0.0, 5.0),
    'lcCooperative': (0.0, 1.0),
    'lcKeepRight': (0.0, 5.0),
    'lcAssertive': (0.0, 5.0),
}
param_names = list(parameters_to_calibrate.keys())
param_bounds = np.array([parameters_to_calibrate[name] for name in param_names])
num_params = len(param_names)

# 固定speedFactor normc的lower_bound和upper_bound（从你原始XML中读取）
# 脚本会尝试从XML读取这些值，如果不存在则使用默认值
SPEEDFACTOR_DEFAULT_LOWER_BOUND = 0.8
SPEEDFACTOR_DEFAULT_UPPER_BOUND = 1.6
SPEEDFACTOR_REGEX = re.compile(r'normc\(([\d.]+),([\d.]+),([\d.]+),([\d.]+)\)') # 用于解析XML中的speedFactor

# 11. ID of the vType to calibrate in 1.rou.xml
target_vType_id = "passenger"  # <--- 修改此行：你要校准的vType ID

# --- SPSA Hyperparameters ---
# 根据经验或文献调整这些SPSA超参数
spsa_a = 0.05
spsa_c = 0.01
spsa_A = 50
spsa_alpha = 0.602
spsa_gamma = 0.101

# SPSA每轮运行的最大迭代次数 (在重启之间)
iterations_per_restart = 80  # <--- 修改此行

# SPSA的总运行次数 (包括初始运行)
num_restarts = 3  # <--- 修改此行

# Number of SUMO simulation runs to average per evaluation
NUM_SIM_RUNS = 3

# --- Step 1: Read Observed Data from CSV (Units: km/h for speed, veh/min for flow) ---
def read_observed_data(csv_file_path):
    """
    从CSV文件读取观测到的速度和流量数据。
    假设CSV文件包含列头'Observed_Speed_kmh'和'Observed_Flow_vehpermin'。
    返回两个列表：observed_speeds_kmh (km/h), observed_flows_vehpermin (veh/min)。
    """
    observed_speeds_kmh_list = []
    observed_flows_vehpermin_list = []
    try:
        with open(csv_file_path, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile, delimiter=',')
            for row in reader:
                try:
                    speed_kmh = float(row['Observed_Speed_kmh'])
                    flow_vehpermin = float(row['Observed_Flow_vehpermin'])

                    observed_speeds_kmh_list.append(speed_kmh)
                    observed_flows_vehpermin_list.append(flow_vehpermin)
                except ValueError:
                    print(f"Skipping row with invalid numerical data: {row}")
                    continue
                except KeyError as e:
                    print(
                        f"Missing expected column in CSV: {e}. Ensure headers are 'Observed_Speed_kmh' and 'Observed_Flow_vehpermin'.")
                    sys.exit(1)
        if len(observed_speeds_kmh_list) != NUM_OBSERVED_INTERVALS:
            print(
                f"Warning: Expected {NUM_OBSERVED_INTERVALS} observed intervals, but found {len(observed_speeds_kmh_list)}.")
        return observed_speeds_kmh_list, observed_flows_vehpermin_list
    except FileNotFoundError:
        print(f"Error: Observed data CSV file not found at {csv_file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading observed data CSV: {e}")
        traceback.print_exc()
        sys.exit(1)


# --- Read observed data (early definition for use in main block) ---
# 这在脚本的全局作用域被调用，所以observed_speeds_kmh_np等在main函数中是可用的
observed_speeds_kmh, observed_flows_vehpermin = read_observed_data(OBSERVED_DATA_CSV_FILE)
observed_speeds_kmh_np = np.array(observed_speeds_kmh)
observed_flows_vehpermin_np = np.array(observed_flows_vehpermin)
print(f"Successfully read {len(observed_speeds_kmh_np)} observed data intervals.")


# --- Step 2: Run a single SUMO Simulation and extract data ---
def run_single_sumo_simulation_and_extract_data(sumo_path, scenario_dir, sumo_cfg_file,
                                                main_route_file, detector_template_file, net_file,
                                                detector_output_file, sim_duration, warmup_duration,
                                                interval_duration_sec, detector_ids, sim_seed,
                                                calibrated_params_dict=None): # <--- ADDED: calibrated_params_dict
    """
    Runs a single SUMO simulation with a given seed and extracts aggregated speed and flow.
    If calibrated_params_dict is provided, it modifies the vType parameters before running.
    Returns: simulated_speeds_kmh (list), simulated_flows_vehpermin (list) or (None, None) on failure.
    """
    print(f"  Running SUMO simulation with seed {sim_seed}...")
    with tempfile.TemporaryDirectory(prefix=f"sumo_run_seed{sim_seed}_") as tmpdir: # Changed prefix to run
        # Define temporary file paths
        temp_route_file_path = os.path.join(tmpdir, os.path.basename(main_route_file))
        temp_detector_file_path = os.path.join(tmpdir, os.path.basename(detector_template_file))
        temp_net_file_path = os.path.join(tmpdir, os.path.basename(net_file))
        temp_detector_output_file_path = os.path.join(tmpdir, os.path.basename(detector_output_file))

        # Copy original route file, detector file, network file to temporary directory
        try:
            shutil.copy(net_file, temp_net_file_path) # Net file
            shutil.copy(detector_template_file, temp_detector_file_path) # Detector file
        except Exception as e:
            print(f"  Error copying input files for seed {sim_seed}: {e}")
            return None, None

        # --- NEW: Modify route file if calibrated_params_dict is provided ---
        try:
            tree = ET.parse(main_route_file) # Read original template
            root = tree.getroot()
            vtype_elem = root.find(f'.//vType[@id="{target_vType_id}"]')
            if vtype_elem is None:
                vtype_elem = root.find(f'.//vTypeDistribution/vType[@id="{target_vType_id}"]')

            if vtype_elem is None:
                print(f"  Error: vType with id '{target_vType_id}' not found in route file template '{os.path.basename(main_route_file)}'.")
                return None, None
            
            # --- Apply parameters if provided ---
            if calibrated_params_dict:
                # Read original speedFactor bounds from template if they exist
                original_speedfactor = vtype_elem.get('speedFactor', None)
                sf_lower_bound = SPEEDFACTOR_DEFAULT_LOWER_BOUND
                sf_upper_bound = SPEEDFACTOR_DEFAULT_UPPER_BOUND
                if original_speedfactor:
                    match = SPEEDFACTOR_REGEX.match(original_speedfactor)
                    if match:
                        sf_lower_bound = float(match.group(3))
                        sf_upper_bound = float(match.group(4))

                for param_name, param_value in calibrated_params_dict.items():
                    if param_name in ['speedFactor_mean', 'speedFactor_std_dev']:
                        new_mean = calibrated_params_dict.get('speedFactor_mean', 1.0)
                        new_std_dev = calibrated_params_dict.get('speedFactor_std_dev', 0.1)
                        new_speedfactor_string = f"normc({new_mean:.6f},{new_std_dev:.6f},{sf_lower_bound:.6f},{sf_upper_bound:.6f})"
                        vtype_elem.set('speedFactor', new_speedfactor_string)
                    else:
                        vtype_elem.set(param_name, str(param_value))
            
            tree.write(temp_route_file_path) # Write to temporary file
        except Exception as e:
            print(f"  Error modifying/saving route file for seed {sim_seed}: {e}")
            traceback.print_exc()
            return None, None


        # Build SUMO command
        sumo_command = [
            sumo_path, "-c", sumo_cfg_file,
            "--route-files", os.path.basename(temp_route_file_path),
            "--additional-files", os.path.basename(temp_detector_file_path),
            "--end", str(sim_duration),
            "--seed", str(sim_seed),  # Use the passed seed
            "--time-to-teleport", "300",
            "--step-length", "1",
            "--no-warnings", "true",
            "--verbose", "false",
        ]

        try:
            subprocess.run(sumo_command, cwd=tmpdir, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"  SUMO simulation with seed {sim_seed} failed with exit code {e.returncode}.")
            print("  SUMO stdout:", e.stdout)
            print("  SUMO stderr:", e.stderr)
            return None, None
        except Exception as e:
            print(f"  An unexpected error occurred during SUMO execution for seed {sim_seed}: {e}")
            traceback.print_exc()
            return None, None

        # --- Read SUMO Detector Output ---
        sim_speeds_kmh_current_run = []
        sim_flows_vehpermin_current_run = []

        try:
            if not os.path.exists(temp_detector_output_file_path):
                print(
                    f"  Error: SUMO detector output file not found for seed {sim_seed}: {temp_detector_output_file_path}")
                return None, None

            tree = ET.parse(temp_detector_output_file_path)
            root = tree.getroot()

            interval_data_by_detector = {}

            for interval_elem in root.findall('interval'):
                det_id_in_output = interval_elem.get('id')
                interval_begin = float(interval_elem.get('begin', '-1'))
                mean_speed_str = interval_elem.get('meanSpeed')
                n_veh_entered_str = interval_elem.get('nVehEntered')

                if det_id_in_output in detector_ids:
                    if interval_begin < warmup_duration:
                        continue

                    if interval_begin not in interval_data_by_detector:
                        interval_data_by_detector[interval_begin] = {}

                    if mean_speed_str is not None and mean_speed_str != '-1.0' and \
                            n_veh_entered_str is not None:
                        speed_ms = float(mean_speed_str)
                        flow_veh_per_min_calculated = float(n_veh_entered_str)

                        interval_data_by_detector[interval_begin][det_id_in_output] = {
                            'meanSpeed': speed_ms,
                            'flow': flow_veh_per_min_calculated
                        }

            for i in range(NUM_OBSERVED_INTERVALS):
                expected_start_time = warmup_duration + (i * interval_duration_sec)

                current_avg_speed_kmh = np.nan
                current_total_flow_vehpermin = np.nan

                if expected_start_time in interval_data_by_detector:
                    current_interval_data = interval_data_by_detector[expected_start_time]

                    if all(det_id in current_interval_data for det_id in detector_ids):
                        speeds_ms_for_this_interval = [current_interval_data[det_id]['meanSpeed'] for det_id in
                                                       detector_ids]
                        flows_per_min_for_this_detector = [current_interval_data[det_id]['flow'] for det_id in
                                                           detector_ids]

                        avg_speed_this_interval_ms = np.mean(speeds_ms_for_this_interval)
                        total_flow_this_interval_per_min = np.sum(flows_per_min_for_this_detector)

                        current_avg_speed_kmh = avg_speed_this_interval_ms * 3.6
                        current_total_flow_vehpermin = total_flow_this_interval_per_min

                    else:
                        print(
                            f"  Warning (Seed {sim_seed}): Interval {expected_start_time}s: Missing data for some detectors {current_interval_data.keys()} (Expected {detector_ids}). Appending NaN.")
                else:
                    print(f"  Warning (Seed {sim_seed}): Interval {expected_start_time}s not found in SUMO output. Appending NaN.")

                sim_speeds_kmh_current_run.append(current_avg_speed_kmh)
                sim_flows_vehpermin_current_run.append(current_total_flow_vehpermin)

        except Exception as e:
            print(f"  Error processing SUMO output XML for seed {sim_seed}: {e}")
            traceback.print_exc()
            return None, None

    print(f"  Successfully extracted {len(sim_speeds_kmh_current_run)} data intervals for seed {sim_seed}.")
    return sim_speeds_kmh_current_run, sim_flows_vehpermin_current_run


# --- Main Execution ---
if __name__ == "__main__":
    # --- Data preparation for plotting ---
    # `observed_speeds_kmh_np` and `observed_flows_vehpermin_np` are already defined and numpy arrays.
    
    # Lists to store results from multiple runs
    all_sim_speeds_runs = []  # List of numpy arrays, each array is one run's speeds
    all_sim_flows_runs = []  # List of numpy arrays, each array is one run's flows

    print(f"Starting {NUM_SIM_RUNS} SUMO simulation runs for averaging...")
    for run_idx in range(NUM_SIM_RUNS):
        current_seed = random.randint(1, 100000)  # Generate a new random seed for each run
        print(f"\n--- Running Simulation {run_idx + 1}/{NUM_SIM_RUNS} (Seed: {current_seed}) ---")

        # Pass None for calibrated_params_dict if running uncalibrated simulation
        sim_speeds_kmh_raw, sim_flows_vehpermin_raw = run_single_sumo_simulation_and_extract_data(
            SUMO_PATH, SCENARIO_DIR, sumo_cfg_full_path, main_route_file_full_path,
            detector_template_full_path, net_file_full_path, DETECTOR_OUTPUT_FILE_NAME,
            simDuration, warmUpDuration, INTERVAL_DURATION_SEC, detectorIds, current_seed,
            calibrated_params_dict=None # <--- Running uncalibrated simulation for plotting
        )

        if sim_speeds_kmh_raw is None or sim_flows_vehpermin_raw is None:
            print(f"  Simulation {run_idx + 1} failed. Skipping this run for averaging.")
            continue

        sim_speeds_kmh_np_this_run = np.array(sim_speeds_kmh_raw)
        sim_flows_vehpermin_np_this_run = np.array(sim_flows_vehpermin_raw)

        if len(sim_speeds_kmh_np_this_run) != NUM_OBSERVED_INTERVALS or \
                len(sim_flows_vehpermin_np_this_run) != NUM_OBSERVED_INTERVALS:
            print(f"  Warning: Simulation {run_idx + 1} did not return {NUM_OBSERVED_INTERVALS} intervals. Skipping.")
            continue

        all_sim_speeds_runs.append(sim_speeds_kmh_np_this_run)
        all_sim_flows_runs.append(sim_flows_vehpermin_np_this_run)

    if not all_sim_speeds_runs:
        print("CRITICAL ERROR: All simulation runs failed or returned no valid data. Exiting.")
        sys.exit(1)

    # Convert list of 1D numpy arrays to a single 2D numpy array for averaging
    all_sim_speeds_runs_np_final = np.array(all_sim_speeds_runs)
    all_sim_flows_runs_np_final = np.array(all_sim_flows_runs)

    # Calculate the average across the runs, ignoring NaNs
    avg_sim_speeds_kmh_np = np.nanmean(all_sim_speeds_runs_np_final, axis=0)
    avg_sim_flows_vehpermin_np = np.nanmean(all_sim_flows_runs_np_final, axis=0)

    print("\n--- Averaged Simulated Data ---")
    print(f"Averaged over {len(all_sim_speeds_runs)} successful runs.")
    print(f"Average Simulated Speeds (km/h): {avg_sim_speeds_kmh_np}")
    print(f"Average Simulated Flows (veh/min): {avg_sim_flows_vehpermin_np}")

    print("\n--- Final Data Check Before Plotting ---")
    print(f"Length of observed_speeds_kmh_np: {len(observed_speeds_kmh_np)}")
    print(f"Length of avg_sim_speeds_kmh_np: {len(avg_sim_speeds_kmh_np)}")
    print(f"Type of observed_speeds_kmh_np: {type(observed_speeds_kmh_np)}")
    print(f"Type of avg_sim_speeds_kmh_np: {type(avg_sim_speeds_kmh_np)}")

    if np.any(np.isnan(avg_sim_speeds_kmh_np)):
        print(f"Warning: Averaged simulated speeds contain NaN values: {avg_sim_speeds_kmh_np}")
    if np.any(np.isnan(avg_sim_flows_vehpermin_np)):
        print(f"Warning: Averaged simulated flows contain NaN values: {avg_sim_flows_vehpermin_np}")

    # Prepare data for plotting (filter out NaNs from averaged results)
    valid_indices = ~np.isnan(avg_sim_speeds_kmh_np) & ~np.isnan(avg_sim_flows_vehpermin_np) 
    
    plot_sim_speeds_kmh = avg_sim_speeds_kmh_np[valid_indices]
    plot_obs_speeds_kmh = observed_speeds_kmh_np[valid_indices]

    plot_sim_flows_vehpermin = avg_sim_flows_vehpermin_np[valid_indices]
    plot_obs_flows_vehpermin = observed_flows_vehpermin_np[valid_indices]

    if len(plot_sim_speeds_kmh) == 0:
        print("CRITICAL PLOTTING ERROR: After averaging and filtering, no valid simulated speed data points remain for plotting.")
        sys.exit(1)

    print(f"Number of VALID speed/flow data points for plotting: {len(plot_sim_speeds_kmh)}")
    print("----------------------------------------")


    # --- Plotting Scatter ---
    # Plot Speed Scatter
    plt.figure(figsize=(10, 10))
    plt.scatter(plot_obs_speeds_kmh, plot_sim_speeds_kmh, s=50, alpha=1.0, color='blue', marker='o',
                label="Simulated (Averaged) Data")
    
    min_val_speed = min(np.min(plot_obs_speeds_kmh), np.min(plot_sim_speeds_kmh)) * 0.9
    max_val_speed = max(np.max(plot_obs_speeds_kmh), np.max(plot_sim_speeds_kmh)) * 1.1
    plt.plot([min_val_speed, max_val_speed], [min_val_speed, max_val_speed], 'r--', label='Perfect Fit')
    
    plt.xlabel("Observed Speed (km/h)")
    plt.ylabel("Simulated Speed (km/h)")
    plt.title(f"Speed Comparison ({INTERVAL_DURATION_SEC}-sec Intervals)")
    plt.grid(True)
    plt.axis('equal')
    plt.xlim(min_val_speed, max_val_speed)
    plt.ylim(min_val_speed, max_val_speed)
    plt.legend()
    plt.show()

    # Plot Flow Scatter
    plt.figure(figsize=(10, 10))
    plt.scatter(plot_obs_flows_vehpermin, plot_sim_flows_vehpermin, s=50, alpha=1.0, color='green', marker='x',
                label="Simulated (Averaged) Data")
    
    min_val_flow = min(np.min(plot_obs_flows_vehpermin), np.min(plot_sim_flows_vehpermin)) * 0.9
    max_val_flow = max(np.max(plot_obs_flows_vehpermin), np.max(plot_sim_flows_vehpermin)) * 1.1
    plt.plot([min_val_flow, max_val_flow], [min_val_flow, max_val_flow], 'r--', label='Perfect Fit')
    
    plt.xlabel("Observed Flow (veh/min)")
    plt.ylabel("Simulated Flow (veh/min)")
    plt.title(f"Flow Comparison ({INTERVAL_DURATION_SEC}-sec Intervals)")
    plt.grid(True)
    plt.axis('equal')
    plt.xlim(min_val_flow, max_val_flow)
    plt.ylim(min_val_flow, max_val_flow)
    plt.legend()
    plt.show()

    print("\nScript finished successfully.")