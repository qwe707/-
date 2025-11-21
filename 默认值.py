import os
import sys
import subprocess
import xml.etree.ElementTree as ET
import numpy as np
import tempfile
import shutil
import time
import random
import matplotlib.pyplot as plt
import traceback
import re
import math

# --- 用户需要修改的配置 ---
# 请根据你的实际环境和文件路径修改以下变量

# 1. SUMO executable path
SUMO_PATH = shutil.which('sumo')
if SUMO_PATH is None:
    print("SUMO executable not found in PATH. Please specify the correct path manually.")
    # Fallback path - MAKE SURE THIS IS CORRECT FOR YOUR SYSTEM
    SUMO_PATH = "D:/SUMO/bin/sumo.exe" # <--- 修改此行
    if not os.path.exists(SUMO_PATH):
        sys.exit(f"Error: SUMO executable not found at the specified path: {SUMO_PATH}")

# 2. Base directory (where your sumo.cfg, .net.xml, .rou.xml, .add.xml templates are)
SCENARIO_DIR = "D:/SUMO" # <--- 修改此行
if not os.path.isdir(SCENARIO_DIR):
     sys.exit(f"Error: Scenario directory not found at: {SCENARIO_DIR}")

# 3. SUMO configuration file name (main template)
SUMO_CFG_FILE_NAME = "exaple2.sumocfg" # <--- 修改此行
sumo_cfg_full_path = os.path.join(SCENARIO_DIR, SUMO_CFG_FILE_NAME)
if not os.path.exists(sumo_cfg_full_path):
     sys.exit(f"Error: SUMO config file not found at: {sumo_cfg_full_path}")

# 3b. Network file name - ADDED (Required if your sumocfg net-file is just a name and you run in tempdir)
NET_FILE_NAME = "lode2.net.xml" # <--- 修改此行：你的网络文件名
net_file_full_path = os.path.join(SCENARIO_DIR, NET_FILE_NAME)
if not os.path.exists(net_file_full_path):
    sys.exit(f"Error: Network file not found at: {net_file_full_path}")


# 4. Main route file name (template for vType)
MAIN_ROUTE_FILE_NAME = "1.rou.xml" # <--- 修改此行
main_route_file_full_path = os.path.join(SCENARIO_DIR, MAIN_ROUTE_FILE_NAME)
if not os.path.exists(main_route_file_full_path):
    sys.exit(f"Error: Main route file not found at: {main_route_file_full_path}")

# 5. Template additional file name (for detectors)
DETECTOR_TEMPLATE_FILE_NAME = "edgelanetrafficpara.add.xml" # <--- 修改此行
detector_template_full_path = os.path.join(SCENARIO_DIR, DETECTOR_TEMPLATE_FILE_NAME)
if not os.path.exists(detector_template_full_path):
    sys.exit(f"Error: Detector template file not found at: {detector_template_full_path}")

# 6. Detector IDs configured in your .add.xml file.
all_detector_ids_in_add_file = [ "e2_E1_main_0", "e2_E1_main_1"] # <--- 修改此列表

# 7. Observed data points - DIRECTLY DEFINED HERE
observed_data_points = [
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 80.31},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 75.84},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 72.21},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 80.56},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 80.42},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 80.15},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 74.33},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 70.56},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 65.26},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 67.55},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 80.60},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 72.84},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 75.27},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 80.77},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 82.23},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 80.93},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 77.54},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 77.35},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 79.00},
    {'location_detector_ids': ["e2_E1_main_0", "e2_E1_main_1"], 'duration_s': 60, 'observed_speed_kmh': 73.16},
]
for point in observed_data_points:
    point['observed_speed_ms'] = point['observed_speed_kmh'] / 3.6

# 8. Simulation time settings
warmUpDuration = 540
DETECTOR_FINE_FREQ = 60
CALIBRATION_START_TIME_SIM = warmUpDuration
total_obs_duration = sum(point['duration_s'] for point in observed_data_points) if observed_data_points else 0
simDuration = CALIBRATION_START_TIME_SIM + total_obs_duration + 180

# 9. Parameters to calibrate and their bounds
parameters_to_calibrate = {
    'accel': (1.0, 4.0),
    'decel': (1.0, 3.0),
    'tau': (0.5, 2.0),
    'maxSpeed': (30.0, 35.0),
    'minGap':(1.0,3.0),
    'lcSpeedGain': (0.0, 5.0),
    'lcStrategic': (0.0, 5.0),
    'lcCooperative': (0.0, 1.0),
    'lcKeepRight': (0.0, 5.0),
    'lcAssertive': (0.0, 5.0),
}
param_names = list(parameters_to_calibrate.keys())
param_bounds = np.array([parameters_to_calibrate[name] for name in param_names])
num_params = len(param_names)

# 10. ID of the vType to calibrate
target_vType_id = "passenger" # <--- 修改此行

# 11. Detector output file name
DETECTOR_OUTPUT_FILE_NAME = "detector_output.xml"

# Regex for speedFactor
SPEEDFACTOR_REGEX = re.compile(r'normc\(([\d.]+),([\d.]+),([\d.]+),([\d.]+)\)')

# --- 目标函数: 运行SUMO模拟并计算RMSE ---
def evaluate_simulation(parameters, run_id_suffix="eval"):
    """
    (函数内容与您提供的代码完全相同，此处省略以保持简洁)
    """
    if isinstance(parameters, dict):
         param_values_dict = parameters
    else:
        param_values_dict = dict(zip(param_names, parameters))

    with tempfile.TemporaryDirectory(prefix=f"sumo_calib_{run_id_suffix}_") as tmpdir:
        temp_route_file_basename = os.path.basename(MAIN_ROUTE_FILE_NAME)
        temp_detector_file_basename = os.path.basename(DETECTOR_TEMPLATE_FILE_NAME)
        temp_net_file_basename = os.path.basename(NET_FILE_NAME)
        temp_route_file_path = os.path.join(tmpdir, temp_route_file_basename)
        temp_detector_file_path = os.path.join(tmpdir, temp_detector_file_basename)
        temp_detector_output_file_path = os.path.join(tmpdir, DETECTOR_OUTPUT_FILE_NAME)
        temp_net_file_path = os.path.join(tmpdir, temp_net_file_basename)

        try:
            tree = ET.parse(main_route_file_full_path)
            root = tree.getroot()
            vtype_elem = root.find(f'.//vType[@id="{target_vType_id}"]')
            if vtype_elem is None:
                 vtype_elem = root.find(f'.//vTypeDistribution/vType[@id="{target_vType_id}"]')
            if vtype_elem is None:
                print(f"ERROR [{run_id_suffix}]: vType '{target_vType_id}' not found.")
                return 1e9

            original_speedfactor = vtype_elem.get('speedFactor', None)
            sf_lower_bound = 0.8
            sf_upper_bound = 1.6
            if original_speedfactor:
                 match = SPEEDFACTOR_REGEX.match(original_speedfactor)
                 if match:
                     sf_lower_bound = float(match.group(3))
                     sf_upper_bound = float(match.group(4))

            for param_name, param_value in param_values_dict.items():
                 if param_name in ['speedFactor_mean', 'speedFactor_std_dev']:
                     new_mean = param_values_dict.get('speedFactor_mean', 1.0)
                     new_std_dev = param_values_dict.get('speedFactor_std_dev', 0.1)
                     new_speedfactor_string = f"normc({new_mean:.6f},{new_std_dev:.6f},{sf_lower_bound:.6f},{sf_upper_bound:.6f})"
                     vtype_elem.set('speedFactor', new_speedfactor_string)
                 else:
                    vtype_elem.set(param_name, str(param_value))
            tree.write(temp_route_file_path)
        except Exception as e:
            print(f"ERROR [{run_id_suffix}]: Failed to modify vType: {e}")
            traceback.print_exc()
            return 1e9

        try:
            shutil.copy(detector_template_full_path, temp_detector_file_path)
            shutil.copy(net_file_full_path, temp_net_file_path)
        except Exception as e:
            print(f"ERROR [{run_id_suffix}]: Failed to copy input files: {e}")
            return 1e9

        sumo_working_dir = tmpdir
        sumo_command = [
            SUMO_PATH, "-c", sumo_cfg_full_path,
            "--route-files", temp_route_file_basename,
            "--additional-files", temp_detector_file_basename,
            "--end", str(simDuration),
            "--seed", str(random.randint(1, 100000)),
            "--time-to-teleport", "300",
            "--step-length", "1",
            "--no-warnings", "true",
            "--verbose", "false",
        ]
        try:
            process = subprocess.run(sumo_command, cwd=sumo_working_dir, check=True, capture_output=True, text=True)
        except Exception as e:
            print(f"ERROR [{run_id_suffix}]: SUMO simulation failed: {e}")
            if hasattr(e, 'stdout'): print("SUMO stdout:\n", process.stdout)
            if hasattr(e, 'stderr'): print("SUMO stderr:\n", process.stderr)
            return 1e9

        try:
            if not os.path.exists(temp_detector_output_file_path):
                print(f"ERROR [{run_id_suffix}]: SUMO output file not found: {temp_detector_output_file_path}")
                return 1e9
            tree = ET.parse(temp_detector_output_file_path)
            root = tree.getroot()
            fine_grained_speeds_by_detector = {det_id: {} for det_id in all_detector_ids_in_add_file}
            found_all_required_detector_ids_in_output = set()
            for interval_elem in root.findall('interval'):
                 det_id_in_output = interval_elem.get('id')
                 interval_begin = float(interval_elem.get('begin', '-1'))
                 mean_speed_str = interval_elem.get('meanSpeed')
                 if det_id_in_output in all_detector_ids_in_add_file:
                     found_all_required_detector_ids_in_output.add(det_id_in_output)
                     if mean_speed_str is not None and mean_speed_str != '-1.0':
                          fine_grained_speeds_by_detector[det_id_in_output][interval_begin] = float(mean_speed_str)
            if len(found_all_required_detector_ids_in_output) != len(all_detector_ids_in_add_file):
                 print(f"WARNING [{run_id_suffix}]: Some detectors {all_detector_ids_in_add_file} had no valid data intervals in the entire simulation output.")
                 return 1e9
        except Exception as e:
            print(f"ERROR [{run_id_suffix}]: Failed to process fine-grained output XML: {e}")
            traceback.print_exc()
            return 1e9

        squared_errors = []
        num_points_with_data = 0
        current_sim_window_start = CALIBRATION_START_TIME_SIM
        for i, obs_point in enumerate(observed_data_points):
            obs_location_detector_ids = obs_point['location_detector_ids']
            obs_duration = obs_point['duration_s']
            obs_speed_ms = obs_point['observed_speed_ms']
            sim_start_time = current_sim_window_start
            sim_end_time = sim_start_time + obs_duration
            current_sim_window_start = sim_end_time
            aggregated_sim_speeds_for_point = []
            for det_id in obs_location_detector_ids:
                if det_id not in fine_grained_speeds_by_detector:
                    print(f"WARNING [{run_id_suffix}]: Data for detector '{det_id}' not found in parsed output (for obs point {i} at sim time [{sim_start_time}, {sim_end_time}]s).")
                    continue
                detector_fine_speeds = fine_grained_speeds_by_detector[det_id]
                detector_times = sorted(detector_fine_speeds.keys())
                speeds_in_window = []
                for interval_begin_time in detector_times:
                    if interval_begin_time >= sim_start_time and interval_begin_time < sim_end_time:
                        speeds_in_window.append(detector_fine_speeds[interval_begin_time])
                    if interval_begin_time >= sim_end_time:
                        break
                if speeds_in_window:
                    aggregated_sim_speeds_for_point.extend(speeds_in_window)
                else:
                    print(f"WARNING [{run_id_suffix}]: No fine-grained speed data found for detector '{det_id}' for obs point {i} in simulation window [{sim_start_time}, {sim_end_time}]s.")
                    pass
            if not aggregated_sim_speeds_for_point:
                print(f"WARNING [{run_id_suffix}]: No valid simulated speed data found for observed point {i} (Detectors: {obs_location_detector_ids}, Duration: {obs_duration}s) in simulation window [{sim_start_time}, {sim_end_time}]s. Penalizing this point.")
                large_error_sq = (obs_speed_ms * 5) ** 2
                squared_errors.append(large_error_sq)
                continue
            average_simulated_speed_for_point_ms = np.mean(aggregated_sim_speeds_for_point)
            num_points_with_data += 1
            squared_error = (average_simulated_speed_for_point_ms - obs_speed_ms) ** 2
            squared_errors.append(squared_error)

        if not squared_errors:
            print(f"ERROR [{run_id_suffix}]: No valid data found in simulation for ANY of the observed data points to calculate RMSE.")
            return 1e9
        mean_squared_error = np.mean(squared_errors)
        rmse = np.sqrt(mean_squared_error)
        print(f"  Calculated RMSE for {run_id_suffix} (over {len(observed_data_points)} points, {num_points_with_data} with sim data): {rmse:.4f} m/s")
        return rmse


# --- SPSA Hyperparameters ---
spsa_a = 0.1
spsa_c = 0.1
spsa_A = 100
spsa_alpha = 0.602
spsa_gamma = 0.101
iterations_per_restart = 150
num_restarts = 3

# Parameters initial guess (SUMO defaults)
default_params = np.array([
    2.6, 4.5, 1.0, 32.0, 2.5, 1.0, 1.0, 1.0, 1.0, 1.0,
])
# Ensure initial guess is within defined bounds
default_params = np.clip(default_params, param_bounds[:, 0], param_bounds[:, 1])

# --- SPSA Algorithm Implementation ---
def run_spsa_calibration(objective_func, initial_params, bounds, max_iterations,
                         a, c, A, alpha, gamma, run_seed=None, run_name="Run"):
    """
    (函数内容与您提供的代码完全相同，此处省略以保持简洁)
    """
    if run_seed is not None:
        np.random.seed(run_seed)
        random.seed(run_seed)
    theta = np.copy(initial_params)
    n_params = len(theta)
    error_history_this_run = []
    best_error = float('inf')
    best_params = np.copy(theta)
    print(f"\n--- Starting SPSA Run: {run_name} ---")
    print(f"Initial Params: {dict(zip(param_names, initial_params))}")
    for k in range(max_iterations):
        a_k = a / (k + 1 + A)**alpha
        c_k = c / (k + 1)**gamma
        delta_k = (np.random.randint(0, 2, size=n_params) * 2 - 1.0)
        theta_plus = theta + c_k * delta_k
        theta_minus = theta - c_k * delta_k
        theta_plus = np.clip(theta_plus, bounds[:, 0], bounds[:, 1])
        theta_minus = np.clip(theta_minus, bounds[:, 0], bounds[:, 1])
        run_id_plus = f"{run_name}_iter{k+1}_p"
        run_id_minus = f"{run_name}_iter{k+1}_m"
        y_plus = objective_func(theta_plus, run_id_suffix=run_id_plus)
        y_minus = objective_func(theta_minus, run_id_suffix=run_id_minus)
        if y_plus >= 1e9 or y_minus >= 1e9:
            print(f"  {run_name} Iteration {k+1}/{max_iterations}: Evaluation failed. Skipping update.")
            error_history_this_run.append(best_error)
            continue
        denominator = 2.0 * c_k * delta_k
        denominator[np.abs(denominator) < 1e-9] = np.copysign(1e-9, denominator[np.abs(denominator) < 1e-9])
        grad_approx = (y_plus - y_minus) / denominator
        theta = theta - a_k * grad_approx
        theta = np.clip(theta, bounds[:, 0], bounds[:, 1])
        current_iteration_best_eval_error = min(y_plus, y_minus)
        if current_iteration_best_eval_error < best_error:
           best_error = current_iteration_best_eval_error
           if y_plus < y_minus:
               best_params = np.copy(theta_plus)
           else:
               best_params = np.copy(theta_minus)
        error_history_this_run.append(best_error)
        if (k + 1) % 10 == 0 or k == max_iterations - 1 or k == 0:
             print(f"  {run_name} Iteration {k+1}/{max_iterations}: Best Eval Error={current_iteration_best_eval_error:.4f} m/s, Best Error Found So Far in {run_name}={best_error:.4f} m/s")
    print(f"--- SPSA Run {run_name} Finished ---")
    return theta, best_params, best_error, error_history_this_run

# --- 主程序 ---
if __name__ == "__main__":
    print("--- Step 1: Evaluating Error with SUMO Default Parameters ---")
    try:
        # 将默认参数数组转换为字典，以便 evaluate_simulation 函数使用
        default_params_dict = dict(zip(param_names, default_params))
        
        # 调用评估函数，计算基准误差
        initial_rmse = evaluate_simulation(
            default_params_dict, 
            run_id_suffix="default_params_evaluation"
        )
        
        if initial_rmse < 1e9:
            print("\n" + "="*50)
            print(f"Initial RMSE with SUMO default parameters: {initial_rmse:.4f} m/s")
            print("This value represents the baseline error before calibration.")
            print("="*50 + "\n")
        else:
            print("\n" + "="*50)
            print("Evaluation with SUMO default parameters failed. Please check your setup.")
            print("="*50 + "\n")

    except Exception as e:
        print(f"\nAn error occurred during the initial evaluation: {e}")
        traceback.print_exc()

    # --- Step 2: Proceed with SPSA Optimization ---
    print("\n--- Step 2: Starting SPSA Calibration with Algorithm Restarts ---")
    print(f"Targeting RMSE over {len(observed_data_points)} observed data points.")
    print(f"Parameters to calibrate ({len(param_names)}): {param_names}")

    start_time = time.time()
    total_error_history = []
    cumulative_iterations = []
    current_initial_guess = np.copy(default_params)
    best_params_overall = np.copy(current_initial_guess)
    best_error_overall = float('inf')
    per_run_convergence_history = []

    # --- SPSA 优化循环 ---
    # (此部分循环与您提供的代码完全相同，此处省略)
    for restart_idx in range(num_restarts):
        run_name = f"Run {restart_idx + 1}" if restart_idx == 0 else f"Restart {restart_idx}"
        run_seed = 12345 + restart_idx
        try:
            final_theta_this_run, best_in_run_params, best_in_run_error, history_this_run = run_spsa_calibration(
                objective_func=evaluate_simulation,
                initial_params=np.copy(current_initial_guess),
                bounds=param_bounds,
                max_iterations=iterations_per_restart,
                a=spsa_a, c=spsa_c, A=spsa_A, alpha=spsa_alpha, gamma=spsa_gamma,
                run_seed=run_seed,
                run_name=run_name
            )
            if best_in_run_error < best_error_overall:
                 best_error_overall = best_in_run_error
                 best_params_overall = np.copy(best_in_run_params)
            current_initial_guess = np.copy(final_theta_this_run)
            per_run_iterations = np.arange(1, len(history_this_run) + 1)
            per_run_convergence_history.append((run_name, per_run_iterations, history_this_run))
            current_cumulative_base = 0 if not cumulative_iterations else cumulative_iterations[-1]
            for i, error_in_run_so_far in enumerate(history_this_run):
                 cumulative_iterations.append(current_cumulative_base + i + 1)
                 if not total_error_history:
                      total_error_history.append(error_in_run_so_far)
                 else:
                      total_error_history.append(min(total_error_history[-1], error_in_run_so_far))
        except Exception as e:
            print(f"\nERROR: SPSA Run {run_name} failed: {e}")
            traceback.print_exc()
            pass

    # --- 结果输出和绘图 ---
    # (此部分与您提供的代码完全相同，此处省略)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("\n--- Overall SPSA Calibration Results ---")
    if best_params_overall is not None and best_error_overall != float('inf'):
        print("SPSA Optimization with restarts finished.")
        print(f"Total cumulative iterations: {len(cumulative_iterations)}")
        print(f"Best RMSE found across all runs: {best_error_overall:.4f} m/s")
        print("Best Parameters found overall:")
        best_params_dict = dict(zip(param_names, best_params_overall))
        for name, value in best_params_dict.items():
            print(f"  {name}: {value:.4f}")
        try:
            best_params_file = os.path.join(SCENARIO_DIR, "best_calibrated_parameters_spsa.txt")
            with open(best_params_file, "w") as f:
                for name, value in best_params_dict.items():
                    f.write(f"{name}: {value}\n")
            print(f"Best parameters saved to {best_params_file}")
        except Exception as e:
             print(f"ERROR: Failed to save best parameters file: {e}")
    else:
        print("SPSA Optimization did not complete successfully or found no valid parameters.")
    print(f"\nCalibration took {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes).")
    print("\nGenerating convergence plots...")
    try:
        if per_run_convergence_history:
            plt.figure(figsize=(10, 6))
            for run_name, iterations, history_values in per_run_convergence_history:
                if history_values:
                    plt.plot(iterations, history_values, label=run_name)
            plt.xlabel(f"Iteration (per run, max {iterations_per_restart})")
            plt.ylabel("Best Error Found So Far (RMSE m/s)")
            plt.title("SPSA Calibration Convergence (Per Run)")
            plt.grid(True)
            plt.ylim(bottom=0)
            plt.legend()
            plot_file_per_run = os.path.join(SCENARIO_DIR, "spsa_per_run_convergence.png")
            plt.savefig(plot_file_per_run)
            print(f"Per-run convergence plot saved to {plot_file_per_run}")
        else:
            print("No run histories available to plot per-run convergence.")
        if total_error_history and cumulative_iterations:
            plt.figure(figsize=(10, 6))
            plt.plot(cumulative_iterations, total_error_history)
            plt.xlabel(f"Cumulative Iteration (Total {len(cumulative_iterations)})")
            plt.ylabel("Overall Best Error Found So Far (RMSE m/s)")
            plt.title("SPSA Calibration Cumulative Convergence with Restarts")
            plt.grid(True)
            plt.ylim(bottom=0)
            plot_file_cumulative = os.path.join(SCENARIO_DIR, "spsa_cumulative_convergence.png")
            plt.savefig(plot_file_cumulative)
            print(f"Cumulative convergence plot saved to {plot_file_cumulative}")
        else:
             print("No cumulative error history available to plot.")
    except ImportError:
        print("Matplotlib not found. Skipping convergence plot generation.")
    except Exception as e:
        print(f"ERROR generating plots: {e}")
        traceback.print_exc()
    if best_params_overall is not None and best_error_overall != float('inf'):
        print("\nRunning final verification simulation with best SPSA parameters...")
        final_rmse_verify = evaluate_simulation(best_params_overall, run_id_suffix="final_verification")
        print(f"RMSE from final verification run: {final_rmse_verify:.4f} m/s")