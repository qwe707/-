import sys
from sumolib import checkBinary
import traci
import numpy as np
from bisect import bisect_left
from collections import defaultdict
import matplotlib.pyplot as plt



class EnhancedQLearningVSL:
    def __init__(self):
        # 状态空间定义
        self.upstream_states = self._create_upstream_states()  # 上游需求（veh/h）
        self.density_states = self._create_density_states()  # 瓶颈区密度（veh/km）
        self.speed_levels = [20, 30, 40, 45, 50, 55, 60, 65, 70, 75, 80]  # 动作空间

        # Q学习参数
        self.alpha = 0.2
        self.gamma = 0.9
        self.epsilon = 0.5

        # Q表初始化 (上游状态32 × 密度状态44 × 动作11)
        self.Q = np.zeros((len(self.upstream_states) * len(self.density_states),
                           len(self.speed_levels)))

        # 车辆追踪
        self.vehicle_counter = defaultdict(set)  # 记录各周期通过的车辆
        self.current_cycle = 0

    def _create_upstream_states(self):
        """上游需求状态（5分钟流量）"""
        return [(i * 50, (i + 1) * 50) for i in range(32)]  # 0-1600 veh/h

    def _create_density_states(self):
        """创建瓶颈区状态空间（保持原有44种）"""
        states = []
        states += [(i, i + 2) for i in range(0, 6, 2)]  # 0~6 (2veh/km)
        states += [(i, i + 1) for i in range(6, 12)]  # 6~12 (1veh/km)
        states += [(i / 2, (i + 1) / 2) for i in range(24, 36, 1)]  # 12~18 (0.5veh/km)
        states += [(i, i + 1) for i in range(18, 24)]  # 18~24 (1veh/km)
        states += [(i, i + 2) for i in range(24, 30, 2)]  # 24~30 (2veh/km)
        states += [(i, i + 10) for i in range(30, 70, 10)]  # 30~70 (10veh/km)
        states.append((70, 78))  # 终态
        return states

    def _get_state_index(self, upstream_density, current_density):
        """获取组合状态索引"""
        upstream_idx = bisect_left([s[0] for s in self.upstream_states], upstream_density) - 1
        upstream_idx = np.clip(upstream_idx, 0, 31)
        #密度状态索引
        density_idx = bisect_left([s[0] for s in self.density_states], current_density) - 1
        density_idx = np.clip(density_idx, 0, 43)
        return upstream_idx * 44 + density_idx

    def _get_state(self):
        """获取实时状态"""
        # 上游5分钟流量（veh/h）
        upstream_veh = traci.edge.getLastStepVehicleNumber("upstream_edge")
        upstream_flow = (upstream_veh / 5) * 60  # 转换为小时流量

        # 瓶颈区实时密度（veh/km）
        current_veh = traci.edge.getLastStepVehicleNumber("bottleneck")
        current_length = traci.lane.getLength("bottleneck_1")
        current_density = current_veh / (current_length / 1000) if current_length > 0 else 0

        return self._get_state_index(upstream_flow, current_density)

    def _reset_counter(self):
        """重置车辆计数器"""
        self.current_cycle += 1
        # 记录施工区下游已有车辆
        print(f"周期数{self.current_cycle}")
        self.vehicle_counter[self.current_cycle] =set()
        print(f"已有车辆{self.vehicle_counter}")

    def _get_passed_vehicles(self):
        """获取本周期通过车辆数"""
        current_vehicles = set(traci.edge.getLastStepVehicleIDs("downstream_edge"))

        passed = current_vehicles - self.vehicle_counter.get(self.current_cycle, set())

        self.vehicle_counter[self.current_cycle].update(passed)

        return len(passed)

    def _calculate_reward (self):
        """以通过施工区到达下游的车辆数 n 作为即时奖励"""
        n_passed=self._get_passed_vehicles()
        print(f"n_passed{n_passed}")
        return n_passed # 直接用通过施工区的车辆数作为奖励


    def choose_action(self, state_idx):
        """ε-greedy策略选择动作"""
        if np.random.rand() < self.epsilon:
            return np.random.choice(len(self.speed_levels))
        else:
            return np.argmax(self.Q[state_idx, :])

    def update_q(self, state_idx, action, reward, next_state_idx):
        """Q值更新（带边界检查）"""
        if state_idx >= self.Q.shape[0] or next_state_idx >= self.Q.shape[0]:
            return
        td_target = reward + self.gamma * np.max(self.Q[next_state_idx, :])
        self.Q[state_idx, action] += self.alpha * (td_target - self.Q[state_idx, action])

    def train(self, episodes=50):
        """增强训练流程"""
        for episode in range(episodes):
            traci.load(["-c", "D:/SUMO/exaple2.sumocfg"])
            # 初始化仿真
            self._reset_counter()
            while traci.simulation.getTime() < 3600:
                traci.simulationStep()
                print(f"Time: {traci.simulation.getTime()}, Upstream: {traci.edge.getLastStepVehicleNumber('upstream_edge')}, Bottleneck: {traci.edge.getLastStepVehicleNumber('bottleneck')}, Downstream: {traci.edge.getLastStepVehicleNumber('downstream_edge')}")


                state_idx = self._get_state()
                action = self.choose_action(state_idx)
                new_speed = self.speed_levels[action]
                traci.edge.setMaxSpeed("warning_zone", new_speed/3.6)  # 在警告区完成限速

                for _ in range(300):
                    traci.simulationStep()

                reward = self._calculate_reward()
                next_state_idx = self._get_state()
                self.update_q(state_idx, action, reward, next_state_idx)
                # 实时监控输出（每秒更新）
                print(f"[{traci.simulation.getTime():.1f}s] "
                      f"当前限速: {new_speed}km/h | "
                      f"通过车辆: {reward}辆 | "
                      f"警告区排队: {traci.edge.getLastStepHaltingNumber('warning_zone')}辆")
            print(f"Episode {episode + 1} completed. Avg Reward: {reward:.2f}")


def main():
    traci.start([checkBinary('sumo-gui'), "-c", "D:/SUMO/exaple2.sumocfg"])
    agent = EnhancedQLearningVSL()
    agent.train(episodes=50)
    traci.close()


if __name__ == "__main__":
    main()
    sys.stdout.flush()