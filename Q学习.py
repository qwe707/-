import sys
import os
# 确保 sumo_tools 路径正确，如果环境变量未设置，可能需要手动指定
# sumo_tools = "C:/Program Files (x86)/Eclipse/Sumo/tools" # 示例路径, 根据你的安装修改
# sys.path.append(sumo_tools)
from sumolib import checkBinary
import traci
import numpy as np
from bisect import bisect_left
from collections import defaultdict
import matplotlib.pyplot as plt # 如果需要绘图，取消注释

# --- 常量定义 ---
UPSTREAM_EDGE_ID = "upstream_edge"
BOTTLENECK_EDGE_ID = "bottleneck"
BOTTLENECK_LANE_ID = "bottleneck_1"
WARNING_ZONE_EDGE_ID = "warning_zone"
DOWNSTREAM_EDGE_ID = "downstream_edge"
# --- 重要: 定义 SUMO 配置文件中添加的探测器 ID ---
DOWNSTREAM_ENTRY_DETECTOR_IDS = ["det_downstream_entry_0"] # 使用你在 .add.xml 中定义的 ID
# 如果下游入口有多条车道，且每条都放了探测器，像这样列出所有 ID:
# DOWNSTREAM_ENTRY_DETECTOR_IDS = ["det_downstream_entry_0", "det_downstream_entry_1"]

CYCLE_DURATION_SECONDS = 300 # Q-learning 决策周期时长（秒），必须与探测器 freq 匹配
SIMULATION_END_TIME = 3600 # 总仿真时长（秒）

class EnhancedQLearningVSL:
    def __init__(self, cycle_duration=CYCLE_DURATION_SECONDS, detector_ids=DOWNSTREAM_ENTRY_DETECTOR_IDS):
        self.upstream_states = self._create_upstream_states()
        self.density_states = self._create_density_states()
        self.speed_levels = [20, 30, 40, 45, 50, 55, 60, 65, 70, 75, 80] # km/h

        self.alpha = 0.2 # 学习率
        self.gamma = 0.9 # 折扣因子
        self.epsilon = 0.5 # 探索率 (可以考虑随回合数衰减)

        self.num_upstream_states = len(self.upstream_states)
        self.num_density_bins = len(self.density_states) # 根据实际生成的状态数确定
        self.Q = np.zeros((self.num_upstream_states * self.num_density_bins, len(self.speed_levels)))

        self.cycle_duration_steps = cycle_duration
        self.detector_ids = detector_ids
        self.episode_rewards = []


    def _create_upstream_states(self):
        # 0-50, 50-100, ..., 1550-1600 veh/h
        return [(i * 50, (i + 1) * 50) for i in range(32)]

    def _create_density_states(self):
        # 瓶颈区密度状态 (veh/km)
        states = []
        states += [(i, i + 2) for i in range(0, 6, 2)]      # 0-6 (步长 2)
        states += [(i, i + 1) for i in range(6, 12)]       # 6-12 (步长 1)
        states += [(i / 2.0, (i + 1) / 2.0) for i in range(24, 36)] # 12-18 (步长 0.5) - Python 2/3 兼容性注意浮点数
        states += [(i, i + 1) for i in range(18, 24)]      # 18-24 (步长 1)
        states += [(i, i + 2) for i in range(24, 30, 2)]   # 24-30 (步长 2)
        states += [(i, i + 10) for i in range(30, 70, 10)] # 30-70 (步长 10)
        states.append((70, 78))                            # 70-78 (示例终态)
        return states

    def _get_state_index(self, upstream_flow, current_density):
        up_idx = bisect_left([s[1] for s in self.upstream_states], upstream_flow)
        up_idx = np.clip(up_idx, 0, self.num_upstream_states - 1)

        dens_idx = bisect_left([s[1] for s in self.density_states], current_density)
        dens_idx = np.clip(dens_idx, 0, self.num_density_bins - 1)

        state_idx = up_idx * self.num_density_bins + dens_idx
        return state_idx

    def _get_current_state_values(self):
        # 注意: getLastStepVehicleNumber 仅给出最后一步的车辆数。
        # 用它估算 5 分钟流量可能不准确。更好的方法是也使用上游探测器。
        # 这里暂时保留基于瞬时计数的简单估算逻辑：
        upstream_veh_count_last_step = traci.edge.getLastStepVehicleNumber(UPSTREAM_EDGE_ID)
        # 简单估算：假设瞬时计数代表通过率 veh/sec，转换为 veh/h
        upstream_flow_estimate = upstream_veh_count_last_step * 3600

        current_veh_count = traci.edge.getLastStepVehicleNumber(BOTTLENECK_EDGE_ID)
        try:
            bottleneck_lane_length = traci.lane.getLength(BOTTLENECK_LANE_ID)
            num_lanes = traci.edge.getLaneNumber(BOTTLENECK_EDGE_ID)
            total_bottleneck_length_km = (bottleneck_lane_length * num_lanes) / 1000.0
        except traci.TraCIException:
             print(f"警告: 无法获取瓶颈区 {BOTTLENECK_EDGE_ID}/{BOTTLENECK_LANE_ID} 的长度/车道数。使用默认长度 1km。")
             total_bottleneck_length_km = 1.0 # 备用长度

        current_density = current_veh_count / total_bottleneck_length_km if total_bottleneck_length_km > 0 else 0

        return upstream_flow_estimate, current_density

    def get_state(self):
        upstream_flow, current_density = self._get_current_state_values()
        return self._get_state_index(upstream_flow, current_density)


    def _calculate_reward_from_detectors(self):
        total_passed_count = 0
        for detector_id in self.detector_ids:
            try:
                # getLastStepVehicleNumber 返回上一个聚合周期 ('freq'定义) 内通过的车辆数
                passed_count = traci.inductionloop.getLastStepVehicleNumber(detector_id)
                total_passed_count += passed_count
            except traci.TraCIException as e:
                print(f"警告: 无法读取探测器 {detector_id}: {e}。假设此探测器计数为 0。")
        return total_passed_count


    def choose_action(self, state_idx):
        if np.random.rand() < self.epsilon:
            action_idx = np.random.choice(len(self.speed_levels))
        else:
            if state_idx < self.Q.shape[0]:
                 action_idx = np.argmax(self.Q[state_idx, :])
            else:
                 print(f"警告: 状态索引 {state_idx} 超出 Q 表范围 (大小 {self.Q.shape[0]})。随机选择动作。")
                 action_idx = np.random.choice(len(self.speed_levels)) # 备用策略
        return action_idx

    def update_q(self, state_idx, action_idx, reward, next_state_idx):
        if state_idx >= self.Q.shape[0] or next_state_idx >= self.Q.shape[0] or action_idx >= self.Q.shape[1]:
            print(f"警告: 更新 Q 值时索引越界。"
                  f"状态: {state_idx}, 下一状态: {next_state_idx}, 动作: {action_idx}。"
                  f"Q 表形状: {self.Q.shape}。跳过更新。")
            return

        current_q = self.Q[state_idx, action_idx]
        max_next_q = np.max(self.Q[next_state_idx, :])
        td_target = reward + self.gamma * max_next_q
        td_error = td_target - current_q

        self.Q[state_idx, action_idx] += self.alpha * td_error


    def train(self, episodes=50, sumo_config_file="D:/SUMO/exaple2.sumocfg"):
        total_rewards_per_episode = []

        for episode in range(episodes):
            print(f"\n--- 开始回合 {episode + 1}/{episodes} ---")
            # sumo 或 sumo-gui
            sumo_binary = checkBinary('sumo')
            traci.start([sumo_binary, "-c", sumo_config_file])

            current_sim_time = 0
            total_episode_reward = 0

            while current_sim_time < SIMULATION_END_TIME:
                if current_sim_time == 0:
                     traci.simulationStep()
                     current_sim_time = traci.simulation.getTime()

                state_idx = self.get_state()

                action_idx = self.choose_action(state_idx)
                chosen_speed = self.speed_levels[action_idx]

                try:
                    traci.edge.setMaxSpeed(WARNING_ZONE_EDGE_ID, chosen_speed / 3.6) # km/h 转 m/s
                except traci.TraCIException as e:
                    print(f"错误: 无法在 {WARNING_ZONE_EDGE_ID} 设置最高速度: {e}")
                    break # 如果路段不存在，停止该回合

                start_time_this_cycle = current_sim_time
                target_end_time_this_cycle = start_time_this_cycle + self.cycle_duration_steps

                steps_ran_in_cycle = 0
                while current_sim_time < target_end_time_this_cycle:
                    if traci.simulation.getMinExpectedNumber() <= 0:
                        print("仿真提前结束。")
                        break
                    traci.simulationStep()
                    current_sim_time = traci.simulation.getTime()
                    steps_ran_in_cycle += 1
                    if current_sim_time >= SIMULATION_END_TIME:
                         break

                # 处理周期结束或仿真提前结束的情况
                if traci.simulation.getMinExpectedNumber() <= 0 or current_sim_time >= SIMULATION_END_TIME:
                     if steps_ran_in_cycle > 0: # 确保至少跑了一步才计算奖励和更新
                         reward = self._calculate_reward_from_detectors()
                         next_state_idx = self.get_state()
                         self.update_q(state_idx, action_idx, reward, next_state_idx)
                         total_episode_reward += reward
                     break # 结束当前回合的 while 循环

                reward = self._calculate_reward_from_detectors()
                total_episode_reward += reward

                next_state_idx = self.get_state()

                self.update_q(state_idx, action_idx, reward, next_state_idx)

                upstream_val, density_val = self._get_current_state_values()
                print(f"[{current_sim_time:.1f}s | 回合 {episode+1}] 周期结束: "
                      f"状态 (上游:{upstream_val:.0f}, 密度:{density_val:.1f} -> S:{state_idx}), "
                      f"动作: 速度={chosen_speed}km/h (A:{action_idx}), "
                      f"奖励: {reward} 辆, "
                      f"下一状态 (S':{next_state_idx}), "
                      f"排队(警告区): {traci.edge.getLastStepHaltingNumber(WARNING_ZONE_EDGE_ID)} 辆")

            print(f"--- 回合 {episode + 1} 结束。总奖励: {total_episode_reward} ---")
            total_rewards_per_episode.append(total_episode_reward)
            traci.close()

            # 可选: 逐步减小探索率
            # self.epsilon = max(0.05, self.epsilon * 0.99)

        print("\n--- 训练结束 ---")
        self.episode_rewards = total_rewards_per_episode
        # 可选: 保存 Q 表
        # np.save("q_table_final.npy", self.Q)
        # 可选: 绘制奖励图
        # self.plot_rewards()

    def plot_rewards(self):
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, len(self.episode_rewards) + 1), self.episode_rewards, marker='o')
        plt.title('每回合总奖励')
        plt.xlabel('回合 (Episode)')
        plt.ylabel('总奖励 (探测器计数之和)')
        plt.grid(True)
        plt.rcParams['font.sans-serif'] = ['SimHei'] # 指定默认字体为黑体
        plt.rcParams['axes.unicode_minus'] = False # 解决保存图像时负号'-'显示为方块的问题
        plt.show()


def main():
    sumo_cfg = "D:/SUMO/exaple2.sumocfg"

    # --- 重要 ---
    # 确保下面的探测器 ID 与你在 SUMO .add.xml 文件中定义的完全一致
    # 并且 XML 文件中探测器的 'freq' 属性值 (秒) 与下面的 CYCLE_DURATION_SECONDS 相同
    detector_ids = ["det_downstream_entry_0"] # 如果你用了不同 ID 或多个探测器，请修改
    cycle_seconds = 300 # 每个决策周期持续多少秒 (应与探测器 freq 一致)
    # --- /重要 ---

    agent = EnhancedQLearningVSL(cycle_duration=cycle_seconds, detector_ids=detector_ids)

    num_episodes = 50 # 设置训练的总回合数
    agent.train(episodes=num_episodes, sumo_config_file=sumo_cfg)

    agent.plot_rewards() # 训练结束后绘制奖励变化图


if __name__ == "__main__":
    # 检查 SUMO_HOME 环境变量
    if 'SUMO_HOME' not in os.environ:
         print("错误: 未设置 SUMO_HOME 环境变量。")
         # 尝试设置一个默认路径 (根据你的实际安装情况修改)
         os.environ['SUMO_HOME'] = 'C:/Program Files (x86)/Eclipse/Sumo'
         print("尝试使用默认 SUMO_HOME: ", os.environ['SUMO_HOME'])
         # 将 tools 目录添加到系统路径 (如果需要)
         sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))

    main()