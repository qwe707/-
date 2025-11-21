import xml.etree.ElementTree as ET

def calculate_ttt(tripinfo_file):
    tree = ET.parse(tripinfo_file)
    root = tree.getroot()
    total_travel_time = 0
    
    for trip in root.findall('tripinfo'):
        duration = float(trip.get('duration'))
        total_travel_time += duration
        
    return total_travel_time

# 使用绝对路径
tripinfo_file = r"D:\SUMO\tripinfo.xml"

try:
    # 计算静态策略的总行程时间
    total_time = calculate_ttt(tripinfo_file)
    print(f"\n静态策略的总行程时间: {total_time / 3600:.2f} 车·小时")
except FileNotFoundError:
    print(f"\n错误: 找不到文件 {tripinfo_file}")
except ET.ParseError:
    print(f"\n错误: 无法解析XML文件 {tripinfo_file}")
except Exception as e:
    print(f"\n发生错误: {str(e)}")