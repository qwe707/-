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

# --- 用户需要修改的配置 ---
# 请根据你的实际环境和文件路径修改以下变量

# 1. SUMO executable path
SUMO_PATH = shutil.which('sumo')
if SUMO_PATH is None:
    print("SUMO executable not found in PATH. Please specify the correct path manually.")
    SUMO_PATH = "D:/SUMO/bin/sumo.exe"  # <--- 修改此行
    if not os.path.exists(SUMO_PATH):
        sys.exit(f"Error: SUMO executable not found at the specified path: {SUMO_PATH}")

# 2. Base directory (where your sumo.cfg, .net.xml, .rou.xml, .add.xml templates are)
SCENARIO_DIR = "D:/SUMO"  # <--- 修改此行
if not os.path.isdir(SCENARIO_DIR):
    sys.exit(f"Error: Scenario directory not found at: {SCENARIO_DIR}")

# 3. SUMO configuration file name (main template)
SUMO_CFG_FILE_NAME = "exaple2.sumocfg"  # <--- 修改此行
sumo_cfg_full_path = os.path.join(SCENARIO_DIR, SUMO_CFG_FILE_NAME)
if not os.path.exists(sumo_cfg_full_path):
    sys.exit(f"Error: SUMO config file not found at: {sumo_cfg_full_path}")

# 3b. Network file name - REQUIRED
NET_FILE_NAME = "lode2.net.xml"  # <--- 修改此行：你的网络文件名
net_file_full_path = os.path.join(SCENARIO_DIR, NET_FILE_NAME)
if not os.path.exists(net_file_full_path):
    sys.exit(f"Error: Network file not found at: {net_file_full_path}")

# 4. Main route file name (for vType definitions and flow)
MAIN_ROUTE_FILE_NAME = "1.rou.xml"  # <--- 修改此行
main_route_file_full_path = os.path.join(SCENARIO_DIR, MAIN_ROUTE_FILE_NAME)
if not os.path.exists(main_route_file_full_path):
    sys.exit(f"Error: Main route file not found at: {main_route_file_full_path}")

# 5. Template additional file name (for detectors)
DETECTOR_TEMPLATE_FILE_NAME = "edgelanetrafficpara.add.xml"  # <--- 修改此行
detector_template_full_path = os.path.join(SCENARIO_DIR, DETECTOR_TEMPLATE_FILE_NAME)
if not os.path.exists(detector_template_full_path):
    sys.exit(f"Error: Detector template file not found at: {detector_template_full_path}")

# 6. Detector IDs configured in your .add.xml file.
detectorIds = ["guodu_0", "guodu_1"]  # <--- 修改此列表

# 7. Observed data CSV file path
OBSERVED_DATA_CSV_FILE = "D:/SUMO/your_observed_data.csv"  # <--- 修改此行
if not os.path.exists(OBSERVED_DATA_CSV_FILE):
    sys.exit(f"Error: Observed data CSV file not found at: {OBSERVED_DATA_CSV_FILE}")

# 8. Simulation time settings
warmUpDuration = 540  # Warm-up period in seconds
INTERVAL_DURATION_SEC = 60  # MUST MATCH your SUMO detector freq and observed data interval
NUM_OBSERVED_INTERVALS = 20  # Total number of observed 1-minute intervals

# Calculated total simulation duration based on observed data + warm-up + buffer
simDuration = warmUpDuration + (NUM_OBSERVED_INTERVALS * INTERVAL_DURATION_SEC) + 180  # Add 3 min buffer at end

# 9. Detector output file name
DETECTOR_OUTPUT_FILE_NAME = "detector_output.xml"

# --- NEW: Number of simulation runs for averaging ---
NUM_SIM_RUNS = 3  # <--- 设置模拟运行的次数


# --- Step 1: Read Observed Data from CSV (Units: km/h for speed, veh/min for flow) ---
def read_observed_data(csv_file_path):
    """
    Reads observed speed and flow data from a CSV file.
    Assumes CSV has headers 'Observed_Speed_kmh' and 'Observed_Flow_vehpermin'.
    Returns two lists: observed_speeds_kmh, observed_flows_vehpermin.
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


# Read observed data
observed_speeds_kmh, observed_flows_vehpermin = read_observed_data(OBSERVED_DATA_CSV_FILE)
# Convert to numpy arrays immediately after reading for consistency
observed_speeds_kmh_np = np.array(observed_speeds_kmh)
observed_flows_vehpermin_np = np.array(observed_flows_vehpermin)
print(f"Successfully read {len(observed_speeds_kmh_np)} observed data intervals.")


# --- Step 2: Run a single SUMO Simulation and extract data ---
def run_single_sumo_simulation_and_extract_data(sumo_path, scenario_dir, sumo_cfg_file,
                                                main_route_file, detector_template_file, net_file,
                                                detector_output_file, sim_duration, warmup_duration,
                                                interval_duration_sec, detector_ids,
                                                sim_seed):  # Added sim_seed parameter
    """
    Runs a single SUMO simulation with a given seed and extracts aggregated speed and flow for plotting.
    Returns: simulated_speeds_kmh (list), simulated_flows_vehpermin (list) or (None, None) on failure.
    """
    print(f"  Running SUMO simulation with seed {sim_seed}...")
    with tempfile.TemporaryDirectory(prefix=f"sumo_plot_seed{sim_seed}_") as tmpdir:  # Uses seed in tempdir prefix
        # Define temporary file paths
        temp_route_file_path = os.path.join(tmpdir, os.path.basename(main_route_file))
        temp_detector_file_path = os.path.join(tmpdir, os.path.basename(detector_template_file))
        temp_net_file_path = os.path.join(tmpdir, os.path.basename(net_file))
        temp_detector_output_file_path = os.path.join(tmpdir, os.path.basename(detector_output_file))

        # Copy original route file, detector file, network file to temporary directory
        try:
            shutil.copy(main_route_file, temp_route_file_path)
            shutil.copy(detector_template_file, temp_detector_file_path)
            shutil.copy(net_file, temp_net_file_path)
        except Exception as e:
            print(f"  Error copying input files for seed {sim_seed}: {e}")
            return None, None

        # Build SUMO command
        sumo_command = [
            sumo_path, "-c", sumo_cfg_file,
            "--route-files", os.path.basename(temp_route_file_path),
            "--additional-files", os.path.basename(temp_detector_file_path),
            "--end", str(sim_duration),
            "--seed", str(sim_seed),  # Use the passed seed for SUMO
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
                # interval_end = float(interval_elem.get('end', '-1')) # Not strictly needed if nVehEntered is already for 60s
                mean_speed_str = interval_elem.get('speed')
                n_veh_entered_str = interval_elem.get('nVehEntered')

                if det_id_in_output in detector_ids:
                    if interval_begin < warmup_duration:
                        continue

                    if interval_begin not in interval_data_by_detector:
                        interval_data_by_detector[interval_begin] = {}

                    if mean_speed_str is not None and mean_speed_str != '-1.0' and \
                            n_veh_entered_str is not None:
                        speed_ms = float(mean_speed_str)
                        # flow_veh_per_min_calculated is already the count per INTERVAL_DURATION_SEC (e.g., 60s)
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

                        avg_speed_this_interval_ms = np.mean(
                            speeds_ms_for_this_interval)  # Speed is still average across detectors
                        total_flow_this_interval_per_min = np.sum(
                            flows_per_min_for_this_detector)  # Flow is sum across detectors

                        current_avg_speed_kmh = avg_speed_this_interval_ms * 3.6  # Convert to km/h for final list
                        current_total_flow_vehpermin = total_flow_this_interval_per_min

                        # print(f"  Interval {expected_start_time}-{expected_start_time+interval_duration_sec}s: Speed={current_avg_speed_kmh:.2f} km/h, Flow={current_total_flow_vehpermin:.2f} veh/min")
                    else:
                        print(
                            f"  Warning (Seed {sim_seed}): Interval {expected_start_time}s: Missing data for some detectors {current_interval_data.keys()} (Expected {detector_ids}). Appending NaN.")
                else:
                    print(
                        f"  Warning (Seed {sim_seed}): Interval {expected_start_time}s not found in SUMO output. Appending NaN.")

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
    # Lists to store results from multiple runs
    all_sim_speeds_runs = []  # List of numpy arrays, each array is one run's speeds
    all_sim_flows_runs = []  # List of numpy arrays, each array is one run's flows

    print(f"Starting {NUM_SIM_RUNS} SUMO simulation runs for averaging...")
    for run_idx in range(NUM_SIM_RUNS):
        current_seed = random.randint(1, 100000)  # Generate a new random seed for each run
        print(f"\n--- Running Simulation {run_idx + 1}/{NUM_SIM_RUNS} (Seed: {current_seed}) ---")

        sim_speeds_kmh_raw, sim_flows_vehpermin_raw = run_single_sumo_simulation_and_extract_data(
            SUMO_PATH, SCENARIO_DIR, sumo_cfg_full_path, main_route_file_full_path,
            detector_template_full_path, net_file_full_path, DETECTOR_OUTPUT_FILE_NAME,
            simDuration, warmUpDuration, INTERVAL_DURATION_SEC, detectorIds, current_seed  # Pass seed
        )

        if sim_speeds_kmh_raw is None or sim_flows_vehpermin_raw is None:
            print(f"  Simulation {run_idx + 1} failed. Skipping this run for averaging.")
            continue  # Skip this run if it failed

        # Convert to numpy arrays immediately after getting from function, and ensure length
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

    # Convert list of 1D numpy arrays to a single 2D numpy array for easier averaging
    all_sim_speeds_runs_np_final = np.array(all_sim_speeds_runs)  # Shape: (num_successful_runs, NUM_OBSERVED_INTERVALS)
    all_sim_flows_runs_np_final = np.array(all_sim_flows_runs)

    # Calculate the average across the runs, ignoring NaNs
    avg_sim_speeds_kmh_np = np.nanmean(all_sim_speeds_runs_np_final, axis=0)
    avg_sim_flows_vehpermin_np = np.nanmean(all_sim_flows_runs_np_final, axis=0)

    print("\n--- Averaged Simulated Data ---")
    print(f"Averaged over {len(all_sim_speeds_runs)} successful runs.")
    print(f"Average Simulated Speeds (km/h): {avg_sim_speeds_kmh_np}")
    print(f"Average Simulated Flows (veh/min): {avg_sim_flows_vehpermin_np}")

    print("\n--- Final Data Check Before Plotting ---")
    # Corrected variables for print statements: use _np version for consistency
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
        print(
            "CRITICAL PLOTTING ERROR: After averaging and filtering, no valid simulated speed data points remain for plotting.")
        sys.exit(1)

    print(f"Number of VALID speed/flow data points for plotting: {len(plot_sim_speeds_kmh)}")
    print("----------------------------------------")

    # --- Plotting Scatter ---
    # Plot Speed Scatter
    plt.figure(figsize=(10, 10))
    plt.scatter(plot_obs_speeds_kmh, plot_sim_speeds_kmh, s=50, alpha=1.0, color='blue', marker='o',
                label="Simulated (Averaged) Data")  # Updated label

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
                label="Simulated (Averaged) Data")  # Updated label

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