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
# These should include ALL detectors you will use for calibration, across all locations.
# The 'id' attributes must match the 'location_detector_ids' in the observed_data_points below.
all_detector_ids_in_add_file = [ "guodu_0", "guodu_1"] # <--- 修改此列表，列出所有检测器ID

# 7. Observed data points - DIRECTLY DEFINED HERE
# Each item is a dictionary representing one video observation.
# 'location_detector_ids': LIST of detector IDs in SUMO corresponding to this video's location.
# 'duration_s': Duration of the video in seconds.
# 'observed_speed_kmh': Observed average speed from the video in km/h.
# You have 10 videos, so this list should have 10 dictionaries.
observed_data_points = [
    # Example structure - MODIFY THIS LIST WITH YOUR 10 DATA POINTS
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 83.14},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 78.16},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 74.12},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 79.91},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 78.86},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 80.7},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 77.35},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 73.1},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 69.76},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 70.43},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 83.66},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 73.18},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 78.65},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 83.93},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 83.37},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 82.32},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 85.56},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 85.14},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 85.18},
    {'location_detector_ids': ["guodu_0", "guodu_1"], 'duration_s': 60, 'observed_speed_kmh': 78.2},
    # Make sure you have exactly 10 dictionaries here, reflecting your 10 videos.
]
# Convert observed speeds to m/s
for point in observed_data_points:
    point['observed_speed_ms'] = point['observed_speed_kmh'] / 3.6


# 8. Simulation time settings (Unified for the single long simulation)
warmUpDuration = 540 # Warm-up period in seconds (data during this time is ignored)
DETECTOR_FINE_FREQ = 60 # Fine-grained detector output frequency in seconds (e.g., 60s)
# Calibration time window starts after warm-up
CALIBRATION_START_TIME_SIM = warmUpDuration
# Determine total simulation duration needed based on the longest observation
total_obs_duration = sum(point['duration_s'] for point in observed_data_points) if observed_data_points else 0
simDuration = CALIBRATION_START_TIME_SIM + total_obs_duration + 180 # Add warm-up buffer + end buffer





# 9. Parameters to calibrate and their bounds (as before, including speedFactor)
parameters_to_calibrate = {
    'accel': (1.0, 4.0),
    'decel': (1.0, 3.0),
    'tau': (0.5, 2.0),
    'maxSpeed': (30.0, 35.0), # Base speed in m/s
    'minGap':(1.0,3.0),
    'lcSpeedGain': (0.0, 5.0),
    'lcStrategic': (0.0, 5.0),
    'lcCooperative': (0.0, 1.0),
    'lcKeepRight': (0.0, 5.0),
    'lcAssertive': (0.0, 5.0),
    'speedFactor_mean': (0.2, 2.0),      # Mean of speedFactor normc
    'speedFactor_std_dev': (0, 0.5),  #
}
param_names = list(parameters_to_calibrate.keys())
param_bounds = np.array([parameters_to_calibrate[name] for name in param_names])
num_params = len(param_names)

# Fixed bounds for speedFactor normc (from your original XML - ensure your template has these)
# These will be read from the template to maintain consistency
# SPEEDFACTOR_LOWER_BOUND = 0.8
# SPEEDFACTOR_UPPER_BOUND = 1.6

# 10. ID of the vType to calibrate in 1.rou.xml
target_vType_id = "passenger" # <--- 修改此行

# 11. Detector output file name (must match the 'file' attribute in your .add.xml for the detectors used)
DETECTOR_OUTPUT_FILE_NAME = "detector_output.xml" # <--- 确保与模板文件一致

# Regex to parse the speedFactor string (normc function)
SPEEDFACTOR_REGEX = re.compile(r'normc\(([\d.]+),([\d.]+),([\d.]+),([\d.]+)\)')


# --- 目标函数: 运行SUMO模拟并计算RMSE ---
def evaluate_simulation(parameters, run_id_suffix="eval"):
    """
    Objective function for the optimizer.
    Takes parameter values, modifies vType, runs ONE long simulation,
    reads fine-grained detector output, aggregates based on observed data points,
    and returns the RMSE.
    """
    if isinstance(parameters, dict):
         param_values_dict = parameters
    else:
        param_values_dict = dict(zip(param_names, parameters))

    # --- Use tempfile.TemporaryDirectory ---
    with tempfile.TemporaryDirectory(prefix=f"sumo_calib_{run_id_suffix}_") as tmpdir:
        # Define base names for temporary files (use original names)
        temp_route_file_basename = os.path.basename(MAIN_ROUTE_FILE_NAME)
        temp_detector_file_basename = os.path.basename(DETECTOR_TEMPLATE_FILE_NAME)
        temp_net_file_basename = os.path.basename(NET_FILE_NAME)

        # Define full paths for temporary files inside the temporary directory
        temp_route_file_path = os.path.join(tmpdir, temp_route_file_basename)
        temp_detector_file_path = os.path.join(tmpdir, temp_detector_file_basename)
        temp_detector_output_file_path = os.path.join(tmpdir, DETECTOR_OUTPUT_FILE_NAME)
        temp_net_file_path = os.path.join(tmpdir, temp_net_file_basename)


        # --- Step 1: Read original route file, modify vType parameters, save to a temporary file ---
        try:
            tree = ET.parse(main_route_file_full_path)
            root = tree.getroot()
            # Use XPath to find the vType element anywhere in the tree
            vtype_elem = root.find(f'.//vType[@id="{target_vType_id}"]')
            if vtype_elem is None:
                 vtype_elem = root.find(f'.//vTypeDistribution/vType[@id="{target_vType_id}"]')
            if vtype_elem is None:
                print(f"ERROR [{run_id_suffix}]: vType '{target_vType_id}' not found.")
                return 1e9

            # Read original speedFactor bounds from template if they exist
            original_speedfactor = vtype_elem.get('speedFactor', None)
            sf_lower_bound = 0.8 # Default bounds if not in template
            sf_upper_bound = 1.6
            if original_speedfactor:
                 match = SPEEDFACTOR_REGEX.match(original_speedfactor)
                 if match:
                     sf_lower_bound = float(match.group(3))
                     sf_upper_bound = float(match.group(4))
                 # else: print(f"Warning: speedFactor for '{target_vType_id}' not in normc format. Using default bounds.")


            for param_name, param_value in param_values_dict.items():
                 if param_name in ['speedFactor_mean', 'speedFactor_std_dev']:
                     # Construct the speedFactor string using calibrated mean/std_dev and original bounds
                     new_mean = param_values_dict.get('speedFactor_mean', 1.0) # Use calibrated, default 1.0
                     new_std_dev = param_values_dict.get('speedFactor_std_dev', 0.1) # Use calibrated, default 0.1
                     new_speedfactor_string = f"normc({new_mean:.6f},{new_std_dev:.6f},{sf_lower_bound:.6f},{sf_upper_bound:.6f})"
                     vtype_elem.set('speedFactor', new_speedfactor_string)
                     # print(f"  [{run_id_suffix}] Updated speedFactor to: {new_speedfactor_string}") # Optional print
                 else:
                    # Set other parameters directly as attributes
                    vtype_elem.set(param_name, str(param_value))

            tree.write(temp_route_file_path)

        except Exception as e:
            print(f"ERROR [{run_id_suffix}]: Failed to modify vType: {e}")
            traceback.print_exc()
            return 1e9

        # --- Step 2: Prepare other input files (copy templates) ---
        try:
            shutil.copy(detector_template_full_path, temp_detector_file_path)
            shutil.copy(net_file_full_path, temp_net_file_path)
        except Exception as e:
            print(f"ERROR [{run_id_suffix}]: Failed to copy input files: {e}")
            return 1e9

        # --- Step 3: Build and run SUMO command ---
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
        # print(f"  Running SUMO simulation {run_id_suffix}...")
        try:
            process = subprocess.run(sumo_command, cwd=sumo_working_dir, check=True, capture_output=True, text=True)
        except Exception as e:
            print(f"ERROR [{run_id_suffix}]: SUMO simulation failed: {e}")
            if hasattr(e, 'stdout'): print("SUMO stdout:\n", process.stdout)
            if hasattr(e, 'stderr'): print("SUMO stderr:\n", process.stderr)
            return 1e9

        # --- Step 4: Read and process fine-grained detector output ---
        try:
            if not os.path.exists(temp_detector_output_file_path):
                print(f"ERROR [{run_id_suffix}]: SUMO output file not found: {temp_detector_output_file_path}")
                return 1e9

            tree = ET.parse(temp_detector_output_file_path)
            root = tree.getroot()

            # Store fine-grained speeds by detector ID and time
            # Structure: {detector_id: {begin_time: mean_speed_ms, ...}, ...}
            fine_grained_speeds_by_detector = {det_id: {} for det_id in all_detector_ids_in_add_file}
            found_all_required_detector_ids_in_output = set()

            # Iterate through all interval elements in the output file
            # Your output format is <interval begin="..." end="..." id="..." meanSpeed="..." .../>
            # Ensure the detector in your .add.xml outputs 'meanSpeed' and 'id'
            for interval_elem in root.findall('interval'):
                 det_id_in_output = interval_elem.get('id') # Assuming interval id IS the detector id
                 interval_begin = float(interval_elem.get('begin', '-1'))
                 mean_speed_str = interval_elem.get('speed')

                 # Store data only for detectors we care about
                 if det_id_in_output in all_detector_ids_in_add_file:
                     found_all_required_detector_ids_in_output.add(det_id_in_output)
                     if mean_speed_str is not None and mean_speed_str != '-1.0':
                          fine_grained_speeds_by_detector[det_id_in_output][interval_begin] = float(mean_speed_str)
                     # else: Store invalid/missing as None or similar if needed for aggregation logic


            # Check if we found *any* data for each required detector ID
            # This is a basic check, doesn't guarantee enough data for specific windows
            if len(found_all_required_detector_ids_in_output) != len(all_detector_ids_in_add_file):
                 print(f"WARNING [{run_id_suffix}]: Some detectors {all_detector_ids_in_add_file} had no valid data intervals in the entire simulation output.")
                 return 1e9 # Penalize simulations with no data from detectors


        except Exception as e:
            print(f"ERROR [{run_id_suffix}]: Failed to process fine-grained output XML: {e}")
            traceback.print_exc()
            return 1e9


        # --- Step 5: Aggregate simulation speeds based on observed data points ---
        squared_errors = []
        num_points_with_data = 0  # Track how many observation points actually had data in sim

        # Initialize the starting time for the *first* observation window
        current_sim_window_start = CALIBRATION_START_TIME_SIM

        for i, obs_point in enumerate(observed_data_points):  # Added 'i' for reference
            obs_location_detector_ids = obs_point['location_detector_ids']  # List of detector IDs for this observation
            obs_duration = obs_point['duration_s']
            obs_speed_ms = obs_point['observed_speed_ms']

            # Determine the simulation time window for THIS observation
            # This observation starts where the previous one ended (or after warm-up for the first one)
            sim_start_time = current_sim_window_start
            sim_end_time = sim_start_time + obs_duration

            # Update current_sim_window_start for the *next* observation
            current_sim_window_start = sim_end_time  # The next observation will start immediately after this one

            # Aggregate speeds for THIS observation point across its detectors and duration
            aggregated_sim_speeds_for_point = []  # Speeds aggregated from all relevant detectors for this specific point

            for det_id in obs_location_detector_ids:
                if det_id not in fine_grained_speeds_by_detector:
                    print(
                        f"WARNING [{run_id_suffix}]: Data for detector '{det_id}' not found in parsed output (for obs point {i} at sim time [{sim_start_time}, {sim_end_time}]s).")
                    continue

                detector_fine_speeds = fine_grained_speeds_by_detector[det_id]
                detector_times = sorted(detector_fine_speeds.keys())

                speeds_in_window = []
                for interval_begin_time in detector_times:
                    # Check if the *start* of the fine-grained interval is within the observation window
                    if interval_begin_time >= sim_start_time and interval_begin_time < sim_end_time:
                        speeds_in_window.append(detector_fine_speeds[interval_begin_time])
                    # Optimization: If we passed the end time, stop for this detector
                    if interval_begin_time >= sim_end_time:
                        break

                # If we got any data from this specific detector in this window, add it to the aggregated list
                if speeds_in_window:
                    aggregated_sim_speeds_for_point.extend(speeds_in_window)
                else:
                    # This warning is now more precise, indicating no data for THIS detector in THIS time window
                    print(
                        f"WARNING [{run_id_suffix}]: No fine-grained speed data found for detector '{det_id}' for obs point {i} in simulation window [{sim_start_time}, {sim_end_time}]s.")
                # If no data for *any* detector in this observation, penalize this observation point
                # Need to check aggregated_sim_speeds_for_point after the inner loop over detectors
                pass  # This check is done below

            # Check if we got data from *any* of the detectors for this observation point
            if not aggregated_sim_speeds_for_point:
                print(
                    f"WARNING [{run_id_suffix}]: No valid simulated speed data found for observed point {i} (Detectors: {obs_location_detector_ids}, Duration: {obs_duration}s) in simulation window [{sim_start_time}, {sim_end_time}]s. Penalizing this point.")
                # Penalize observations with no data by assigning a large error
                large_error_sq = (obs_speed_ms * 5) ** 2
                squared_errors.append(large_error_sq)
                continue  # Move to the next observation point

            # Calculate the average simulated speed across all *valid* data points for THIS observation point
            average_simulated_speed_for_point_ms = np.mean(aggregated_sim_speeds_for_point)
            num_points_with_data += 1  # Count this observation point as having valid data

            # Calculate squared error for this point
            squared_error = (average_simulated_speed_for_point_ms - obs_speed_ms) ** 2
            squared_errors.append(squared_error)

            # --- Rest of Step 5 (checking for data, calculating RMSE) remains the same ---
        if not squared_errors:
            print(
                f"ERROR [{run_id_suffix}]: No valid data found in simulation for ANY of the observed data points to calculate RMSE.")
            return 1e9

        mean_squared_error = np.mean(squared_errors)
        rmse = np.sqrt(mean_squared_error)

        print(
            f"  Calculated RMSE for {run_id_suffix} (over {len(observed_data_points)} points, {num_points_with_data} with sim data): {rmse:.4f} m/s")

        return rmse

    # Temporary directory and its contents are automatically removed here


# --- SPSA Hyperparameters ---
# Adjust these based on experience or literature for SPSA
spsa_a = 0.1
spsa_c = 0.1
spsa_A = 100
spsa_alpha = 0.602
spsa_gamma = 0.101

# SPSA Maximum iterations for a single run (between restarts)
iterations_per_restart = 150 # <--- Adjust iterations per run

# Total number of SPSA runs (including the first run)
num_restarts = 3 # <--- Adjust number of runs/restarts

# Parameters initial guess for the first run (midpoint of bounds)
default_params = np.array([
    2.6,    # accel (SUMO默认值)
    4.5,    # decel (SUMO默认值)
    1.0,    # tau (SUMO默认值)
    32, # maxSpeed (SUMO默认值，注意：若超出你的bounds需调整)
    2.5,    # minGap (SUMO默认值)
    1.0,    # lcSpeedGain (SUMO默认值)
    1.0,    # lcStrategic (SUMO默认值)
    1.0,    # lcCooperative (SUMO默认值)
    1.0,    # lcKeepRight (SUMO默认值)
    1.0,    # lcAssertive (SUMO默认值)
    1.0,    # speedFactor_mean (initial guess)
    0.1,    # speedFactor_std_dev (initial guess)
 
 
 
])
default_params=np.clip(default_params, param_bounds[:, 0], param_bounds[:, 1])
# --- SPSA Algorithm Implementation ---
def run_spsa_calibration(objective_func, initial_params, bounds, max_iterations,
                         a, c, A, alpha, gamma, run_seed=None, run_name="Run"):
    """
    Executes SPSA calibration for a single run.

    Args:
        objective_func: The function to minimize. Takes parameter numpy array, returns scalar error (RMSE).
        initial_params (np.array): Initial guess for parameters.
        bounds (np.array): Bounds for parameters [(min1, max1), ...].
        max_iterations (int): Maximum number of SPSA iterations.
        a, c, A, alpha, gamma: SPSA hyperparameters.
        run_seed (int, optional): Random seed for reproducibility.
        run_name (str): Name for this calibration run (e.g., "Run 1", "Restart 1").

    Returns:
        tuple: (final_params_of_this_run, best_params_in_this_run, best_error_in_this_run, error_history_this_run)
        error_history_this_run records the best error found *so far* within THIS run at each iteration.
    """
    if run_seed is not None:
        np.random.seed(run_seed)
        random.seed(run_seed)

    theta = np.copy(initial_params)
    n_params = len(theta)
    error_history_this_run = []
    best_error = float('inf') # Initialize best error to infinity
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
            error_history_this_run.append(best_error) # Append previous best error
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
           # print(f"  {run_name} Iteration {k+1}/{max_iterations}: NEW BEST found in run: {best_error:.4f} m/s")

        error_history_this_run.append(best_error)

        if (k + 1) % 10 == 0 or k == max_iterations - 1 or k == 0:
             print(f"  {run_name} Iteration {k+1}/{max_iterations}: Best Eval Error={current_iteration_best_eval_error:.4f} m/s, Best Error Found So Far in {run_name}={best_error:.4f} m/s")


    print(f"--- SPSA Run {run_name} Finished ---")
    return theta, best_params, best_error, error_history_this_run


# --- 7. Run SPSA Optimization with Algorithm Restarts ---

print("Starting SPSA calibration with algorithm restarts...")
print(f"Targeting RMSE over {len(observed_data_points)} observed data points.")
print(f"Parameters to calibrate ({len(param_names)}): {param_names}")

start_time = time.time()

total_error_history = []
cumulative_iterations = []


current_initial_guess = np.copy(default_params)
best_params_overall = np.copy(current_initial_guess)
best_error_overall = float('inf') # RMSE is in m/s

per_run_convergence_history = []


# --- Outer loop: Execute multiple SPSA runs (Algorithm Restarts) ---
for restart_idx in range(num_restarts):
    run_name = f"Run {restart_idx + 1}" if restart_idx == 0 else f"Restart {restart_idx}"
    run_seed = None

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


# Optimization finished after all restarts

end_time = time.time()
elapsed_time = end_time - start_time

# --- 8. Output Results ---
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


# --- 9. 绘制误差历史 ---
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


# Optional: Run final verification
if best_params_overall is not None and best_error_overall != float('inf'):
    print("\nRunning final verification simulation with best SPSA parameters...")
    final_rmse_verify = evaluate_simulation(best_params_overall, run_id_suffix="final_verification")
    print(f"RMSE from final verification run: {final_rmse_verify:.4f} m/s")