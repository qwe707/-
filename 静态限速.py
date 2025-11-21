import sys
from sumolib import checkBinary
import traci


def run():
    step = 0
    edge_id = "E6"  # 指定要限速的道路
    speed_limit = 16.67# 限速值 (m/s，约60km/h)

    # 直接对道路设置限速
    traci.edge.setMaxSpeed(edge_id, speed_limit)
    print(f"\n已对道路 {edge_id} 设置限速为 {speed_limit:.2f} m/s ({speed_limit * 3.6:.2f} km/h)")
    
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step += 1

    traci.close()
    sys.stdout.flush()


if __name__ == "__main__":
    sumoBinary = checkBinary('sumo')
    traci.start([sumoBinary, "-c", "D:/SUMO/exaple2.sumocfg"])
    run()