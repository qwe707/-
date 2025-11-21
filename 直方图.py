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
from matplotlib.ticker import PercentFormatter # 导入百分比格式化工具

# --- 用户需要修改的配置 ---
# (您的配置部分保持不变)
# 1. SUMO 可执行文件路径
SUMO_PATH = shutil.which('sumo')
if SUMO_PATH is None:
    print("在系统路径中未找到SUMO可执行文件。请手动指定正确路径。")
    SUMO_PATH = "D:/SUMO/bin/sumo.exe"  # <--- 修改此行
    if not os.path.exists(SUMO_PATH):
        sys.exit(f"错误: 在指定路径未找到SUMO可执行文件: {SUMO_PATH}")

# 2. 基础目录
SCENARIO_DIR = "D:/SUMO"  # <--- 修改此行
if not os.path.isdir(SCENARIO_DIR):
    sys.exit(f"错误: 场景目录未找到: {SCENARIO_DIR}")

# 3. SUMO 配置文件名
SUMO_CFG_FILE_NAME = "exaple2.sumocfg"  # <--- 修改此行
sumo_cfg_full_path = os.path.join(SCENARIO_DIR, SUMO_CFG_FILE_NAME)
if not os.path.exists(sumo_cfg_full_path):
    sys.exit(f"错误: SUMO配置文件未找到: {sumo_cfg_full_path}")

# 3b. 路网文件名
NET_FILE_NAME = "lode2.net.xml"  # <--- 修改此行
net_file_full_path = os.path.join(SCENARIO_DIR, NET_FILE_NAME)
if not os.path.exists(net_file_full_path):
    sys.exit(f"错误: 路网文件未找到: {net_file_full_path}")

# 4. 主要路径文件名
MAIN_ROUTE_FILE_NAME = "1.rou.xml"  # <--- 修改此行
main_route_file_full_path = os.path.join(SCENARIO_DIR, MAIN_ROUTE_FILE_NAME)
if not os.path.exists(main_route_file_full_path):
    sys.exit(f"错误: 主要路径文件未找到: {main_route_file_full_path}")

# 5. 附加文件名模板
DETECTOR_TEMPLATE_FILE_NAME = "edgelanetrafficpara.add.xml"  # <--- 修改此行
detector_template_full_path = os.path.join(SCENARIO_DIR, DETECTOR_TEMPLATE_FILE_NAME)
if not os.path.exists(detector_template_full_path):
    sys.exit(f"错误: 检测器模板文件未找到: {detector_template_full_path}")

# 6. 检测器ID
detectorIds = ["e2_E1_main_0", "e2_E1_main_1"]  # <--- 修改此列表

# 7. 观测数据CSV文件路径
OBSERVED_DATA_CSV_FILE = "D:/SUMO/your_observed_data.csv"  # <--- 修改此行
if not os.path.exists(OBSERVED_DATA_CSV_FILE):
    sys.exit(f"错误: 观测数据CSV文件未找到: {OBSERVED_DATA_CSV_FILE}")

# 8. 仿真设置
warmUpDuration = 540
INTERVAL_DURATION_SEC = 60
NUM_OBSERVED_INTERVALS = 20
simDuration = warmUpDuration + (NUM_OBSERVED_INTERVALS * INTERVAL_DURATION_SEC) + 180
DETECTOR_OUTPUT_FILE_NAME = "detector_output.xml"
NUM_SIM_RUNS = 1 # 运行次数

# --- (数据读取和仿真的函数保持不变) ---
def read_observed_data(csv_file_path):
    """从CSV文件读取观测数据。"""
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
                except (ValueError, KeyError):
                    continue
        return observed_speeds_kmh_list, observed_flows_vehpermin_list
    except Exception:
        sys.exit(f"读取观测数据CSV文件时出错: {csv_file_path}")

def run_single_sumo_simulation_and_extract_data(sumo_path, scenario_dir, sumo_cfg_file,
                                                main_route_file, detector_template_file, net_file,
                                                detector_output_file, sim_duration, warmup_duration,
                                                interval_duration_sec, detector_ids, sim_seed):
    """
    Runs a single SUMO simulation with a given seed and extracts aggregated speed and flow for plotting.
    Returns: simulated_speeds_kmh (list), simulated_flows_vehpermin (list) or (None, None) on failure.
    """
    print(f"  Running SUMO simulation with seed {sim_seed}...")
    with tempfile.TemporaryDirectory(prefix=f"sumo_plot_seed{sim_seed}_") as tmpdir:
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
                # interval_end = float(interval_elem.get('end', '-1')) # Not strictly needed if interval_duration_sec is fixed
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

                        # print(f"  Interval {expected_start_time}-{expected_start_time+interval_duration_sec}s: Speed={current_avg_speed_kmh:.2f} km/h, Flow={current_total_flow_vehpermin:.2f} veh/min")
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



# --- 新增：用于绘制累积直方图的函数 ---

def plot_cumulative_histogram_speed(observed_speeds, simulated_speeds, title_suffix=""):
    """
    生成一个与目标样式完全一致的速度累积直方图 (柱子并排显示)。
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    all_data = np.concatenate([observed_speeds, simulated_speeds])
    # 保持bins数量为30，如果需要更细或更粗的柱子可以调整
    bins = np.linspace(all_data.min(), all_data.max(), 30)
    
    # --- 1. 计算，但不直接绘图 ---
    # 计算观测数据的直方图频数
    n_obs, _ = np.histogram(observed_speeds, bins=bins)
    # 计算仿真数据的直方图频数
    n_sim, _ = np.histogram(simulated_speeds, bins=bins)
    
    # --- 2. 计算累积概率 ---
    # 将频数转换为累积概率 (0到1之间)
    cum_prob_obs = np.cumsum(n_obs) / len(observed_speeds)
    cum_prob_sim = np.cumsum(n_sim) / len(simulated_speeds)

    # --- 3. 计算柱子的几何信息 (位置和宽度) ---
    bin_width = bins[1] - bins[0]
    bar_width = bin_width * 0.45  # 每个柱子的宽度，留出一点空隙
    bin_centers = (bins[:-1] + bins[1:]) / 2 # 每个区间的中心点
    
    # 计算蓝色柱子 (观测) 和红色柱子 (仿真) 的x轴位置
    x_obs = bin_centers - bar_width / 2
    x_sim = bin_centers + bar_width / 2

    # --- 4. 使用 ax.bar() 手动绘制并排的柱子 ---
    ax.bar(x_obs, cum_prob_obs, width=bar_width, color='blue', alpha=0.7, label='Observed Speed')
    ax.bar(x_sim, cum_prob_sim, width=bar_width, color='red', alpha=0.7, label='Simulated Speed')

    # --- 5. 绘制顶部的折线 ---
    # 蓝色阶梯线 (连接每个区间的左边界)
    ax.plot(np.insert(bins[:-1], 0, bins[0]), np.insert(cum_prob_obs, 0, 0), drawstyle='steps-post', color='blue', lw=2.5)
    # 红色平滑线 (连接每个红色柱子的中心点)
    ax.plot(np.insert(x_sim, 0, bins[0]), np.insert(cum_prob_sim, 0, 0), color='red', lw=2.5)

    # --- 格式化 ---
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_xlabel("Speed (km/h)")
    ax.set_ylabel("Cumulative Probability")
    ax.set_title(f"Cumulative Histogram: Simulated vs Observed Speed {title_suffix}")
    ax.grid(True, alpha=0.4)
    ax.legend()
    ax.set_ylim(0, 1.05)
    plt.show()



def plot_cumulative_histogram_flow(observed_flows, simulated_flows, title_suffix=""):
    """
    生成一个与目标样式完全一致的流量累积直方图 (柱子并排显示)。
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    all_data = np.concatenate([observed_flows, simulated_flows])
    bins = np.linspace(all_data.min(), all_data.max(), 30)

    n_obs, _ = np.histogram(observed_flows, bins=bins)
    n_sim, _ = np.histogram(simulated_flows, bins=bins)
    
    cum_prob_obs = np.cumsum(n_obs) / len(observed_flows)
    cum_prob_sim = np.cumsum(n_sim) / len(simulated_flows)

    bin_width = bins[1] - bins[0]
    bar_width = bin_width * 0.45
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    x_obs = bin_centers - bar_width / 2
    x_sim = bin_centers + bar_width / 2

    ax.bar(x_obs, cum_prob_obs, width=bar_width, color='blue', alpha=0.7, label='Observed Flow')
    ax.bar(x_sim, cum_prob_sim, width=bar_width, color='red', alpha=0.7, label='Simulated Flow')
    
    ax.plot(np.insert(bins[:-1], 0, bins[0]), np.insert(cum_prob_obs, 0, 0), drawstyle='steps-post', color='blue', lw=2.5)
    ax.plot(np.insert(x_sim, 0, bins[0]), np.insert(cum_prob_sim, 0, 0), color='red', lw=2.5)

    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_xlabel("Flow (veh/min)")
    ax.set_ylabel("Cumulative Probability")
    ax.set_title(f"Cumulative Histogram: Simulated vs Observed Flow {title_suffix}")
    ax.grid(True, alpha=0.4)
    ax.legend()
    ax.set_ylim(0, 1.05)
    plt.show()


# --- 主执行区 ---
if __name__ == "__main__":
    # 主执行区的逻辑基本保持不变
    observed_speeds_kmh, observed_flows_vehpermin = read_observed_data(OBSERVED_DATA_CSV_FILE)
    if not observed_speeds_kmh: # 简单检查数据是否加载失败
        sys.exit("未能加载观测数据。程序退出。")
     # --- 新增：输出观测到的速度 ---
    print("\n--- 观测速度 (Observed Speeds) ---")
    for i, speed in enumerate(observed_speeds_kmh):
        interval_start = warmUpDuration + (i * INTERVAL_DURATION_SEC)
        interval_end = interval_start + INTERVAL_DURATION_SEC
        # 假设观测数据都是有效的，直接打印
        print(f"  时间间隔 (Interval) {interval_start}s - {interval_end}s: {speed:.2f} km/h")
    print("------------------------------------\n")
    print("\n--- 观测流量 (Observed Flows) ---")
    for i, flow in enumerate(observed_flows_vehpermin):
        interval_start = warmUpDuration + (i * INTERVAL_DURATION_SEC)
        interval_end = interval_start + INTERVAL_DURATION_SEC
        # 假设观测数据都是有效的，直接打印
        print(f"  时间间隔 (Interval) {interval_start}s - {interval_end}s: {flow:} veh/min")
    print("------------------------------------\n")
        
    observed_speeds_kmh_np = np.array(observed_speeds_kmh)
    observed_flows_vehpermin_np = np.array(observed_flows_vehpermin)
    
    all_sim_speeds_runs, all_sim_flows_runs = [], []

    # (您的仿真循环保持不变)
    # ...
    
    # 在本示例中，我们只生成虚拟数据来展示绘图效果
    # 在您的真实脚本中，此循环将运行实际的SUMO仿真
    for run_idx in range(NUM_SIM_RUNS):
        current_seed = random.randint(1, 100000)  # Generate a new random seed for each run
        print(f"\n--- Running Simulation {run_idx + 1}/{NUM_SIM_RUNS} (Seed: {current_seed}) ---")

        sim_speeds_kmh_raw, sim_flows_vehpermin_raw = run_single_sumo_simulation_and_extract_data(
            SUMO_PATH, SCENARIO_DIR, sumo_cfg_full_path, main_route_file_full_path,
            detector_template_full_path, net_file_full_path, DETECTOR_OUTPUT_FILE_NAME,
            simDuration, warmUpDuration, INTERVAL_DURATION_SEC, detectorIds, current_seed
        )

        if sim_speeds_kmh_raw is None or sim_flows_vehpermin_raw is None:
            print(f"  Simulation {run_idx + 1} failed. Skipping this run for averaging.")
            continue

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
        sys.exit("严重错误：所有仿真运行均失败。")

    # --- 数据处理与求平均 (保持不变) ---
    avg_sim_speeds_kmh_np = np.nanmean(np.array(all_sim_speeds_runs), axis=0)
    avg_sim_flows_vehpermin_np = np.nanmean(np.array(all_sim_flows_runs), axis=0)
    # --- 新增：输出最终的平均仿真速度 ---
    print("\n--- 最终平均仿真速度 (Final Averaged Simulation Speeds) ---")
    for i, speed in enumerate(avg_sim_speeds_kmh_np):
        interval_start = warmUpDuration + (i * INTERVAL_DURATION_SEC)
        interval_end = interval_start + INTERVAL_DURATION_SEC
        if not np.isnan(speed):
            print(f"  时间间隔 (Interval) {interval_start}s - {interval_end}s: {speed:.2f} km/h")
        else:
            print(f"  时间间隔 (Interval) {interval_start}s - {interval_end}s: 无有效数据 (No valid data)")
    print("-----------------------------------------------------------\n")
    print("\n--- 最终平均仿真流量 (Final Averaged Simulation Flows) ---")
    for i, flow in enumerate(avg_sim_flows_vehpermin_np):
        interval_start = warmUpDuration + (i * INTERVAL_DURATION_SEC)
        interval_end = interval_start + INTERVAL_DURATION_SEC
        if not np.isnan(flow):
            print(f"  时间间隔 (Interval) {interval_start}s - {interval_end}s: {flow:} veh/min")
        else:
            print(f"  时间间隔 (Interval) {interval_start}s - {interval_end}s: 无有效数据 (No valid data)")
    print("-----------------------------------------------------------\n")
    

    valid_indices = ~np.isnan(avg_sim_speeds_kmh_np) & ~np.isnan(avg_sim_flows_vehpermin_np)
    plot_obs_speeds_kmh = observed_speeds_kmh_np[valid_indices]
    plot_sim_speeds_kmh = avg_sim_speeds_kmh_np[valid_indices]
    plot_obs_flows_vehpermin = observed_flows_vehpermin_np[valid_indices]
    plot_sim_flows_vehpermin = avg_sim_flows_vehpermin_np[valid_indices]
    # --- 新增：计算并输出流量的RMSE ---
    if len(plot_obs_flows_vehpermin) > 0:
        flow_rmse = np.sqrt(np.mean((plot_sim_flows_vehpermin - plot_obs_flows_vehpermin)**2))
        print(f"\n--- 流量均方根误差 (Flow RMSE) ---")
        print(f"  仿真流量与观测流量之间的RMSE为: {flow_rmse:.2f} veh/min")
        print(f"-------------------------------------\n")
    else:
        print("\n无法计算流量RMSE，因为没有有效的匹配数据点。")
        # --- 新增：计算并输出速度的RMSE ---
    if len(plot_obs_speeds_kmh) > 0:
        # 先以km/h为单位计算RMSE
        speed_rmse_kmh = np.sqrt(np.mean((plot_sim_speeds_kmh - plot_obs_speeds_kmh)**2))
        # 将其转换为m/s
        speed_rmse_ms = speed_rmse_kmh / 3.6
        print(f"\n--- 速度均方根误差 (Speed RMSE) ---")
        print(f"  仿真速度与观测速度之间的RMSE为: {speed_rmse_ms:.2f} m/s")
        print(f"-------------------------------------\n")
    else:
        print("\n无法计算速度RMSE，因为没有有效的匹配数据点。")


    if len(plot_obs_speeds_kmh) == 0:
        sys.exit("严重绘图错误：没有有效的数据点可用于绘图。")

    # --- 更新后的绘图区 ---
    print("\n正在生成累积直方图...")
    title_suffix = f"(Avg of {len(all_sim_speeds_runs)} Runs)"

    # 调用新的绘图函数
    plot_cumulative_histogram_speed(plot_obs_speeds_kmh, plot_sim_speeds_kmh, title_suffix)
    plot_cumulative_histogram_flow(plot_obs_flows_vehpermin, plot_sim_flows_vehpermin, title_suffix)

    print("\n脚本成功执行完毕。")