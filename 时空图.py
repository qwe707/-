import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def parse_fcd_xml(xml_file):
    """解析FCD XML文件，并返回一个Pandas DataFrame"""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    data = []
    for timestep in root.findall('timestep'):
        time = float(timestep.get('time'))
        for vehicle in timestep.findall('vehicle'):
            data.append({
                'time': time,
                'id': vehicle.get('id'),
                'x': float(vehicle.get('x')),
                'y': float(vehicle.get('y')),
                'speed': float(vehicle.get('speed')),
                'pos': float(vehicle.get('pos')), # 车辆在车道上的位置
                'lane': vehicle.get('lane')
            })
    return pd.DataFrame(data)

def create_spatiotemporal_diagram(df, road_prefix, time_bin_size=10, space_bin_size=50):
    """根据DataFrame创建时空图"""
    
    # 1. 筛选特定道路的数据
    # 假设我们只关心一条主干道，它的edge ID都以'E'开头
    # 请根据您的路网修改这个前缀！
    road_df = df[df['lane'].str.startswith(road_prefix, na=False)].copy()
    
    if road_df.empty:
        print(f"错误：找不到以 '{road_prefix}' 开头的道路。请检查您的路网edge ID。")
        return

    # 2. 将车道位置(pos)转换为整个道路的绝对位置
    # 这是一个简化的处理，假设所有edge是连续的。
    # 对于复杂路网，您可能需要更精确的距离计算。
    # 这里我们直接使用x坐标作为位置，假设道路是水平的。
    road_df['position'] = road_df['x'] 

    # 3. 创建时空网格 (Binning)
    max_time = road_df['time'].max()
    max_pos = road_df['position'].max()
    
    time_bins = np.arange(0, max_time + time_bin_size, time_bin_size)
    space_bins = np.arange(0, max_pos + space_bin_size, space_bin_size)
    
    # 4. 将每个数据点分配到网格中
    road_df['time_bin'] = pd.cut(road_df['time'], bins=time_bins, labels=False, right=False)
    road_df['space_bin'] = pd.cut(road_df['position'], bins=space_bins, labels=False, right=False)
    
    # 5. 计算每个网格单元的平均速度
    # 使用pivot_table进行聚合，更高效
    grid_speed = road_df.pivot_table(index='space_bin', columns='time_bin', values='speed', aggfunc='mean')

    # 6. 绘图
    plt.figure(figsize=(12, 8))
    
    # 使用pcolormesh来绘制，它能更好地处理网格数据
    # 注意：X是时间，Y是位置
    plt.pcolormesh(grid_speed.columns * time_bin_size, 
                   grid_speed.index * space_bin_size, 
                   grid_speed.values, 
                   cmap='viridis_r', # 使用反转的viridis颜色图，红色代表低速
                   shading='auto')

    plt.title(f'Spatiotemporal Diagram (Average Speed) for Road: {road_prefix}*')
    plt.xlabel('Time (s)')
    plt.ylabel('Position (m)')
    
    # 添加颜色条
    cbar = plt.colorbar()
    cbar.set_label('Average Speed (m/s)')
    
    plt.ylim(0, max_pos) # 设置Y轴范围
    plt.xlim(0, max_time) # 设置X轴范围
    
    plt.show()

# --- 主程序 ---
if __name__ == "__main__":
    # 1. 解析XML文件
    print("正在解析 trajectory.xml 文件...")
    fcd_df = parse_fcd_xml('trajectory.xml')
    print("解析完成！")

    # 2. 创建时空图
    # !!! 重要：请将 "E" 替换为您路网中主要道路的edge ID前缀 !!!
    # 例如，如果您的主路edge是 "main_0", "main_1"，就用 "main"
    road_prefix_to_plot = "E" 
    create_spatiotemporal_diagram(fcd_df, road_prefix_to_plot)