import sys
import os
from sumolib import checkBinary
import traci
import numpy as np
from bisect import bisect_left
from collections import defaultdict
import matplotlib.pyplot as plt

# 常量定义
UPSTREAM_EDGE_ID = "upstream_edge"
BOTTLENECK_EDGE_ID = "bottleneck"
WARNING_ZONE_EDGE_ID = "warning_zone.785"  # 限速控制区
DOWNSTREAM_EDGE_ID = "downstream_edge"
SIMULATION_END_TIME = 3600  # 1小时仿真

class EnhancedQLearningVSL:
    def __init__(self, upstream_detector_ids=["upstream_detector_0", "upstream_detector_1", "upstream_detector_2"]):
        # 检测器配置 - 支持多个检测器
        self.upstream_detector_ids = upstream_detector_ids  # 上游检测器ID列表
        self.detector_freq = 300  # 检测器输出频率（5分钟=300秒）
        
        # 状态空间定义
        self.upstream_states = self._create_upstream_states()  # 上游交通需求（0-1600 veh/h）
        self.density_states = self._create_density_states()    # 限速区密度（veh/km）
        self.speed_history_states = self._create_speed_history_states()  # 历史限速状态
        
        # 动作空间：限速变化值（km/h）
        self.speed_changes = [-10, -5, 0, 5, 10]  # 每次可以增减的速度值
        self.min_speed = 40  # 最低限速（km/h）
        self.max_speed = 80  # 最高限速（km/h）
        self.current_speed_limit = 60  # 初始限速值
        
        # Q学习参数
        self.alpha = 0.2  # 学习率
        self.gamma = 0.9  # 折扣因子
        self.epsilon = 0.5  # 初始探索率
        self.epsilon_decay = 0.995  # 探索率衰减
        self.min_epsilon = 0.01  # 最小探索率
        
        # 状态空间大小计算
        self.num_upstream_states = len(self.upstream_states)
        self.num_density_states = len(self.density_states)
        self.num_speed_history_states = len(self.speed_history_states)
        
        # Q表初始化 (上游状态 × 密度状态 × 历史限速状态 × 动作)
        self.Q = np.zeros((
            self.num_upstream_states * 
            self.num_density_states * 
            self.num_speed_history_states,
            len(self.speed_changes)
        ))
        
        # 性能监控
        self.episode_rewards = []  # 每回合总奖励
        self.step_rewards = []     # 每步奖励
        self.speed_history = []    # 速度历史
        self.reward_per_episode = []  # 每回合的奖励列表（用于计算统计信息）
        
    def _create_upstream_states(self):
        """上游交通需求状态空间（veh/h）"""
        return [(i *300, (i + 1) * 300) for i in range(7)]  # 0-2100，步长300
        
    def _create_density_states(self):
        """限速区密度状态空间（veh/km）"""
        states = []
        states += [(i, i + 2) for i in range(0, 6, 2)]      # 0-6 (步长 2)
        states += [(i, i + 2) for i in range(6, 12,2)]        # 6-12 (步长 2)
        states += [(12 + i*0.5, 12 + (i+1)*0.5) for i in range(12)]  # 12-18 (步长 0.5)
        states += [(i, i + 1) for i in range(18, 24)]       # 18-24 (步长 1)
        states += [(i, i + 2) for i in range(24, 30, 2)]    # 24-30 (步长 2)
        states += [(i, i + 10) for i in range(30, 70, 10)]  # 30-70 (步长 10)
        states.append((70, 78))                             # 70-78
        return states
        
    def _create_speed_history_states(self):
        """历史限速状态空间（km/h）"""
        return [(i, i + 10) for i in range(40, 81, 10)]  # 40-80，步长10
        
    def _get_state_index(self, upstream_flow, density, current_speed):
        """获取组合状态索引"""
        up_idx = bisect_left([s[1] for s in self.upstream_states], upstream_flow)
        up_idx = np.clip(up_idx, 0, self.num_upstream_states - 1)
        
        den_idx = bisect_left([s[1] for s in self.density_states], density)
        den_idx = np.clip(den_idx, 0, self.num_density_states - 1)
        
        spd_idx = bisect_left([s[1] for s in self.speed_history_states], current_speed)
        spd_idx = np.clip(spd_idx, 0, self.num_speed_history_states - 1)
        
        return (up_idx * self.num_density_states * self.num_speed_history_states + 
                den_idx * self.num_speed_history_states + 
                spd_idx)
    
    def _get_upstream_flow_from_detector(self):
        """使用多个检测器获取上游统计周期流量（方案2：使用getLastIntervalVehicleNumber）"""
        total_interval_vehicles = 0
        successful_detectors = 0
        
        # 遍历所有上游检测器
        for detector_id in self.upstream_detector_ids:
            try:
                # 获取该检测器在最近统计周期内的车辆数（依赖于检测器配置的freq）
                interval_vehicles = traci.inductionloop.getLastIntervalVehicleNumber(detector_id)
                total_interval_vehicles += interval_vehicles
                successful_detectors += 1
                print(f"检测器 {detector_id}: {interval_vehicles}辆 (统计周期内)")
                
            except traci.TraCIException as e:
                print(f"警告：无法从检测器 {detector_id} 获取统计周期数据: {e}")
                # 尝试备用的单步数据作为fallback
                try:
                    step_vehicles = traci.inductionloop.getLastStepVehicleNumber(detector_id)
                    # 简单估算：假设单步数据代表当前流量强度
                    estimated_interval = step_vehicles * (self.detector_freq / 1)  # 粗略估算
                    total_interval_vehicles += estimated_interval
                    successful_detectors += 1
                    print(f"检测器 {detector_id}: {step_vehicles}辆/步 (估算为{estimated_interval:.0f}辆/周期)")
                except Exception as e2:
                    print(f"检测器 {detector_id} 完全无法访问: {e2}")
                    continue
        
        if successful_detectors > 0:
            # 将统计周期数据转换为每小时流量
            # 假设统计周期就是detector_freq（5分钟=300秒）
            intervals_per_hour = 3600 / self.detector_freq  # 每小时有多少个统计周期
            hourly_flow = total_interval_vehicles * intervals_per_hour
            
            print(f"统计周期总计: {total_interval_vehicles}辆/{self.detector_freq}秒")
            print(f"每小时流量: {total_interval_vehicles} × {intervals_per_hour:.1f} = {hourly_flow:.0f}辆/小时")
            print(f"数据来源: {successful_detectors}个检测器")
            
            return hourly_flow
        else:
            # 所有检测器都失败，使用边缘数据备用方案
            return self._get_backup_flow()
    
    def _get_backup_flow(self):
        """备用流量估算方法"""
        try:
            print("警告：所有检测器都无法获取数据，使用边缘数据备用方案")
            upstream_veh = traci.edge.getLastStepVehicleNumber(UPSTREAM_EDGE_ID)
            # 基于当前边缘车辆数的简单流量估算
            backup_flow = upstream_veh * 720  # 经验系数
            print(f"边缘当前车辆: {upstream_veh}辆，估算流量: {backup_flow:.0f}辆/小时")
            return backup_flow
        except Exception as e:
            print(f"备用流量估算失败: {e}")
            print("使用默认流量值: 800辆/小时")
            return 800
    
    def _get_current_state(self):
        """获取当前状态值"""
        # 使用检测器获取上游5分钟流量
        upstream_flow = self._get_upstream_flow_from_detector()
        
        # 获取限速区密度
        warning_veh = traci.edge.getLastStepVehicleNumber(WARNING_ZONE_EDGE_ID)
        WARNING_ZONE_LENGTH_KM = 0.8
        LANE_COUNT = 3
        density = warning_veh / (WARNING_ZONE_LENGTH_KM * LANE_COUNT) if WARNING_ZONE_LENGTH_KM > 0 else 0
        print(f"车数:{warning_veh}, 长度:{WARNING_ZONE_LENGTH_KM}km, 车道:{LANE_COUNT}, 密度:{density:.2f}")
        return upstream_flow, density, self.current_speed_limit
    
    def _calculate_reward(self):
        """计算奖励：下游断面通过的车辆数"""
        total_throughput = 0#开始的奖励为0
        # 这里填入你在 XML 中定义的检测器 id
        downstream_detectors = ["downstream_edge_0", "downstream_edge_1", "downstream_edge_2"]
        for det_id in downstream_detectors:
            try:
                # 使用 getLastIntervalVehicleNumber 获取上一统计周期（300秒）内的车辆数
                # 这代表了这5分钟内的吞吐量，而不是最后一秒的瞬时值
                count = traci.inductionloop.getLastIntervalVehicleNumber(det_id)
                if count>0:
                    total_throughput+=count 
            except traci.TraCIException as e:
                print(f"警告：无法获取检测器 {det_id} 的数据: {e}")
        return total_throughput
    
    def choose_action(self, state_idx):
        """选择动作（限速变化值）"""
        if np.random.rand() < self.epsilon:
            action_idx = np.random.choice(len(self.speed_changes))
        else:
            action_idx = np.argmax(self.Q[state_idx])
        
        # 计算新的限速值
        speed_change = self.speed_changes[action_idx]
        new_speed = np.clip(self.current_speed_limit + speed_change, 
                           self.min_speed, 
                           self.max_speed)
        
        return action_idx, new_speed
    
    def update_q(self, state_idx, action_idx, reward, next_state_idx):
        """更新Q值"""
        if state_idx >= self.Q.shape[0] or next_state_idx >= self.Q.shape[0]:
            print(f"警告：状态索引超出范围。跳过更新。")
            return
            
        current_q = self.Q[state_idx, action_idx]
        next_max_q = np.max(self.Q[next_state_idx])
        self.Q[state_idx, action_idx] += self.alpha * (
            reward + self.gamma * next_max_q - current_q
        )
    
    def train(self, episodes, sumo_cfg="D:/SUMO/exaple2.sumocfg"):
        """训练过程"""
        for episode in range(episodes):
            print(f"\n--- 开始回合 {episode + 1}/{episodes} ---")
            
            # 启动仿真时指定检测器配置文件
            detector_config_file = r"D:\SUMO\edgelanetrafficpara.add.xml"
            print(f"使用检测器配置文件: {detector_config_file}")
            
            # 使用SUMO无GUI版本
            sumo_binary = checkBinary('sumo')
            print(f"使用 sumo (无GUI): {sumo_binary}")
            
            traci.start([sumo_binary, "-c", sumo_cfg, 
                        "--additional-files", detector_config_file])
            
            total_reward = 0
            step = 0
            
            while traci.simulation.getTime() < SIMULATION_END_TIME:
                # 获取当前状态
                upstream_flow, density, current_speed = self._get_current_state()
                state_idx = self._get_state_index(upstream_flow, density, current_speed)
                
                # 选择动作
                action_idx, new_speed = self.choose_action(state_idx)
                
                # 应用新的限速值
                try:
                    traci.edge.setMaxSpeed(WARNING_ZONE_EDGE_ID, new_speed/3.6)  # 转换为m/s
                    self.current_speed_limit = new_speed
                    self.speed_history.append(new_speed)
                except traci.TraCIException as e:
                    print(f"错误：设置限速失败：{e}")
                    break
                
                # 仿真300步
                for _ in range(300):
                    if traci.simulation.getMinExpectedNumber() <= 0:
                        break
                    traci.simulationStep()
                
                # 计算奖励
                reward = self._calculate_reward()
                total_reward += reward
                self.step_rewards.append(reward)  # 记录每步奖励
                
                # 获取下一状态
                next_upstream, next_density, _ = self._get_current_state()
                next_state_idx = self._get_state_index(
                    next_upstream, next_density, new_speed
                )
                
                # 更新Q值
                self.update_q(state_idx, action_idx, reward, next_state_idx)
                
                # 输出状态信息
                print(f"[{traci.simulation.getTime():.1f}s] "
                      f"限速: {new_speed}km/h, "
                      f"奖励: {reward}辆, "
                      f"上游流量: {upstream_flow:.0f}veh/h, "
                      f"密度: {density:.1f}veh/km")
                
                step += 1
            
            # 回合结束
            avg_reward = total_reward / max(1, step)  # 平均每步奖励
            print(f"回合 {episode + 1} 结束，总奖励: {total_reward}, 平均奖励: {avg_reward:.2f}")
            self.episode_rewards.append(total_reward)
            self.reward_per_episode.append(avg_reward)
            traci.close()
            
            # 更新探索率
            self.epsilon = max(self.min_epsilon, 
                             self.epsilon * self.epsilon_decay)
        
        # 训练结束，绘制结果
        self.plot_training_results()
    
    def plot_training_results(self):
        """绘制详细的训练结果和奖励曲线"""
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        
        # 创建2x2的子图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. 每回合总奖励曲线
        ax1.plot(self.episode_rewards, 'b-', marker='o', linewidth=2, markersize=4)
        ax1.set_title('每回合总奖励变化', fontsize=14, fontweight='bold')
        ax1.set_xlabel('回合')
        ax1.set_ylabel('总奖励（通过车辆数）')
        ax1.grid(True, alpha=0.3)
        
        # 添加趋势线
        if len(self.episode_rewards) > 1:
            z = np.polyfit(range(len(self.episode_rewards)), self.episode_rewards, 1)
            p = np.poly1d(z)
            ax1.plot(range(len(self.episode_rewards)), p(range(len(self.episode_rewards))), 
                    'r--', alpha=0.8, label='趋势线')
            ax1.legend()
        
        # 2. 平均奖励曲线
        if len(self.reward_per_episode) > 0:
            ax2.plot(self.reward_per_episode, 'g-', marker='s', linewidth=2, markersize=4)
            ax2.set_title('每回合平均奖励变化', fontsize=14, fontweight='bold')
            ax2.set_xlabel('回合')
            ax2.set_ylabel('平均奖励')
            ax2.grid(True, alpha=0.3)
        
        # 3. 最近N步的奖励分布（如果有足够数据）
        if len(self.step_rewards) > 50:
            recent_rewards = self.step_rewards[-100:]  # 最近100步
            ax3.hist(recent_rewards, bins=20, alpha=0.7, color='orange', edgecolor='black')
            ax3.set_title('最近100步奖励分布', fontsize=14, fontweight='bold')
            ax3.set_xlabel('奖励值')
            ax3.set_ylabel('频次')
            ax3.grid(True, alpha=0.3)
        else:
            ax3.text(0.5, 0.5, '数据不足\n(需要>50步)', ha='center', va='center', 
                    transform=ax3.transAxes, fontsize=12)
            ax3.set_title('奖励分布', fontsize=14, fontweight='bold')
        
        # 4. 最后一回合的速度变化
        if len(self.speed_history) > 0:
            last_episode_speeds = self.speed_history[-int(SIMULATION_END_TIME/300):]
            ax4.plot(last_episode_speeds, 'm-', marker='.', linewidth=2, markersize=6)
            ax4.set_title('最后一回合限速值变化', fontsize=14, fontweight='bold')
            ax4.set_xlabel('决策步骤')
            ax4.set_ylabel('限速值 (km/h)')
            ax4.grid(True, alpha=0.3)
            
            # 添加限速范围线
            ax4.axhline(y=self.min_speed, color='r', linestyle='--', alpha=0.5, label='最低限速')
            ax4.axhline(y=self.max_speed, color='r', linestyle='--', alpha=0.5, label='最高限速')
            ax4.legend()
        else:
            ax4.text(0.5, 0.5, '无速度数据', ha='center', va='center', 
                    transform=ax4.transAxes, fontsize=12)
            ax4.set_title('限速值变化', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
        
        # 输出训练总结
        self._print_training_summary()
    
    def _print_training_summary(self):
        """输出训练总结统计"""
        if len(self.episode_rewards) > 0:
            print("\n" + "="*50)
            print("训练总结")
            print("="*50)
            print(f"总回合数: {len(self.episode_rewards)}")
            print(f"平均总奖励: {np.mean(self.episode_rewards):.2f}")
            print(f"最高总奖励: {np.max(self.episode_rewards):.2f}")
            print(f"最低总奖励: {np.min(self.episode_rewards):.2f}")
            print(f"奖励标准差: {np.std(self.episode_rewards):.2f}")
            
            if len(self.step_rewards) > 0:
                print(f"\n总决策步数: {len(self.step_rewards)}")
                print(f"平均每步奖励: {np.mean(self.step_rewards):.2f}")
                print(f"最高单步奖励: {np.max(self.step_rewards):.2f}")
            
            if len(self.speed_history) > 0:
                print(f"\n平均限速值: {np.mean(self.speed_history):.2f} km/h")
                print(f"限速变化范围: {np.min(self.speed_history):.1f} - {np.max(self.speed_history):.1f} km/h")
            
            print("="*50)

def main():
    # 检查环境变量
    if 'SUMO_HOME' not in os.environ:
        os.environ['SUMO_HOME'] = r'D:\SUMO'
        print(f"设置 SUMO_HOME: {os.environ['SUMO_HOME']}")
    
    # 创建并训练代理（使用默认检测器ID）
    agent = EnhancedQLearningVSL()
    agent.train(episodes=3000)

if __name__ == "__main__":
    main()