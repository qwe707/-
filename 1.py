import matplotlib.pyplot as plt
import numpy as np
import re
import math # Import math for inf

# --- 用户需要提供的数据 ---
# 将你的输出日志内容复制到这个多行字符串中
# 请确保日志内容中 Windows 路径的反斜杠 '\' 都替换为正斜杠 '/' 或双反斜杠 '\\'
log_data = """
D:/acondda/python.exe C:/Users/18039/AppData/Roaming/JetBrains/PyCharmCE2024.3/scratches/scratch.py 
Starting SPSA calibration with algorithm restarts...
Targeting RMSE over 20 observed data points.
Parameters to calibrate (10): ['accel', 'decel', 'tau', 'maxSpeed', 'minGap', 'lcSpeedGain', 'lcStrategic', 'lcCooperative', 'lcKeepRight', 'lcAssertive']

--- Starting SPSA Run: Run 1 ---
Initial Params: {'accel': 2.6, 'decel': 3.0, 'tau': 1.0, 'maxSpeed': 32.0, 'minGap': 2.5, 'lcSpeedGain': 1.0, 'lcStrategic': 1.0, 'lcCooperative': 1.0, 'lcKeepRight': 1.0, 'lcAssertive': 1.0}
  Calculated RMSE for Run 1_iter1_p (over 20 points, 20 with sim data): 1.4306 m/s
  Calculated RMSE for Run 1_iter1_m (over 20 points, 20 with sim data): 1.5264 m/s
  Run 1 Iteration 1/150: Best Eval Error=1.4306 m/s, Best Error Found So Far in Run 1=1.4306 m/s
  Calculated RMSE for Run 1_iter2_p (over 20 points, 20 with sim data): 1.6893 m/s
  Calculated RMSE for Run 1_iter2_m (over 20 points, 20 with sim data): 1.5457 m/s
  Calculated RMSE for Run 1_iter3_p (over 20 points, 20 with sim data): 1.3465 m/s
  Calculated RMSE for Run 1_iter3_m (over 20 points, 20 with sim data): 1.5593 m/s
  Calculated RMSE for Run 1_iter4_p (over 20 points, 20 with sim data): 1.7783 m/s
  Calculated RMSE for Run 1_iter4_m (over 20 points, 20 with sim data): 1.8312 m/s
  Calculated RMSE for Run 1_iter5_p (over 20 points, 20 with sim data): 1.7019 m/s
  Calculated RMSE for Run 1_iter5_m (over 20 points, 20 with sim data): 1.8370 m/s
  Calculated RMSE for Run 1_iter6_p (over 20 points, 20 with sim data): 1.6691 m/s
  Calculated RMSE for Run 1_iter6_m (over 20 points, 20 with sim data): 1.5947 m/s
  Calculated RMSE for Run 1_iter7_p (over 20 points, 20 with sim data): 1.8871 m/s
  Calculated RMSE for Run 1_iter7_m (over 20 points, 20 with sim data): 1.8508 m/s
  Calculated RMSE for Run 1_iter8_p (over 20 points, 20 with sim data): 1.9081 m/s
  Calculated RMSE for Run 1_iter8_m (over 20 points, 20 with sim data): 1.6354 m/s
  Calculated RMSE for Run 1_iter9_p (over 20 points, 20 with sim data): 1.7270 m/s
  Calculated RMSE for Run 1_iter9_m (over 20 points, 20 with sim data): 1.7103 m/s
  Calculated RMSE for Run 1_iter10_p (over 20 points, 20 with sim data): 1.6014 m/s
  Calculated RMSE for Run 1_iter10_m (over 20 points, 20 with sim data): 1.6819 m/s
  Run 1 Iteration 10/150: Best Eval Error=1.6014 m/s, Best Error Found So Far in Run 1=1.3465 m/s
  Calculated RMSE for Run 1_iter11_p (over 20 points, 20 with sim data): 1.4927 m/s
  Calculated RMSE for Run 1_iter11_m (over 20 points, 20 with sim data): 1.7889 m/s
  Calculated RMSE for Run 1_iter12_p (over 20 points, 20 with sim data): 1.8295 m/s
  Calculated RMSE for Run 1_iter12_m (over 20 points, 20 with sim data): 1.4877 m/s
  Calculated RMSE for Run 1_iter13_p (over 20 points, 20 with sim data): 1.3532 m/s
  Calculated RMSE for Run 1_iter13_m (over 20 points, 20 with sim data): 1.2328 m/s
  Calculated RMSE for Run 1_iter14_p (over 20 points, 20 with sim data): 1.5243 m/s
  Calculated RMSE for Run 1_iter14_m (over 20 points, 20 with sim data): 1.4936 m/s
  Calculated RMSE for Run 1_iter15_p (over 20 points, 20 with sim data): 1.6370 m/s
  Calculated RMSE for Run 1_iter15_m (over 20 points, 20 with sim data): 1.5898 m/s
  Calculated RMSE for Run 1_iter16_p (over 20 points, 20 with sim data): 1.6302 m/s
  Calculated RMSE for Run 1_iter16_m (over 20 points, 20 with sim data): 1.7872 m/s
  Calculated RMSE for Run 1_iter17_p (over 20 points, 20 with sim data): 1.5621 m/s
  Calculated RMSE for Run 1_iter17_m (over 20 points, 20 with sim data): 1.7939 m/s
  Calculated RMSE for Run 1_iter18_p (over 20 points, 20 with sim data): 1.5778 m/s
  Calculated RMSE for Run 1_iter18_m (over 20 points, 20 with sim data): 1.6959 m/s
  Calculated RMSE for Run 1_iter19_p (over 20 points, 20 with sim data): 1.7977 m/s
  Calculated RMSE for Run 1_iter19_m (over 20 points, 20 with sim data): 1.6189 m/s
  Calculated RMSE for Run 1_iter20_p (over 20 points, 20 with sim data): 1.6703 m/s
  Calculated RMSE for Run 1_iter20_m (over 20 points, 20 with sim data): 1.3614 m/s
  Run 1 Iteration 20/150: Best Eval Error=1.3614 m/s, Best Error Found So Far in Run 1=1.2328 m/s
  Calculated RMSE for Run 1_iter21_p (over 20 points, 20 with sim data): 1.4062 m/s
  Calculated RMSE for Run 1_iter21_m (over 20 points, 20 with sim data): 1.5510 m/s
  Calculated RMSE for Run 1_iter22_p (over 20 points, 20 with sim data): 1.6901 m/s
  Calculated RMSE for Run 1_iter22_m (over 20 points, 20 with sim data): 1.7731 m/s
  Calculated RMSE for Run 1_iter23_p (over 20 points, 20 with sim data): 1.6586 m/s
  Calculated RMSE for Run 1_iter23_m (over 20 points, 20 with sim data): 1.5204 m/s
  Calculated RMSE for Run 1_iter24_p (over 20 points, 20 with sim data): 1.7088 m/s
  Calculated RMSE for Run 1_iter24_m (over 20 points, 20 with sim data): 1.8337 m/s
  Calculated RMSE for Run 1_iter25_p (over 20 points, 20 with sim data): 1.6411 m/s
  Calculated RMSE for Run 1_iter25_m (over 20 points, 20 with sim data): 1.7855 m/s
  Calculated RMSE for Run 1_iter26_p (over 20 points, 20 with sim data): 1.7665 m/s
  Calculated RMSE for Run 1_iter26_m (over 20 points, 20 with sim data): 2.0750 m/s
  Calculated RMSE for Run 1_iter27_p (over 20 points, 20 with sim data): 1.6100 m/s
  Calculated RMSE for Run 1_iter27_m (over 20 points, 20 with sim data): 1.7996 m/s
  Calculated RMSE for Run 1_iter28_p (over 20 points, 20 with sim data): 1.2590 m/s
  Calculated RMSE for Run 1_iter28_m (over 20 points, 20 with sim data): 1.5969 m/s
  Calculated RMSE for Run 1_iter29_p (over 20 points, 20 with sim data): 1.5719 m/s
  Calculated RMSE for Run 1_iter29_m (over 20 points, 20 with sim data): 1.8979 m/s
  Calculated RMSE for Run 1_iter30_p (over 20 points, 20 with sim data): 1.4121 m/s
  Calculated RMSE for Run 1_iter30_m (over 20 points, 20 with sim data): 1.4892 m/s
  Run 1 Iteration 30/150: Best Eval Error=1.4121 m/s, Best Error Found So Far in Run 1=1.2328 m/s
  Calculated RMSE for Run 1_iter31_p (over 20 points, 20 with sim data): 1.5828 m/s
  Calculated RMSE for Run 1_iter31_m (over 20 points, 20 with sim data): 1.7157 m/s
  Calculated RMSE for Run 1_iter32_p (over 20 points, 20 with sim data): 1.7113 m/s
  Calculated RMSE for Run 1_iter32_m (over 20 points, 20 with sim data): 1.8751 m/s
  Calculated RMSE for Run 1_iter33_p (over 20 points, 20 with sim data): 1.8580 m/s
  Calculated RMSE for Run 1_iter33_m (over 20 points, 20 with sim data): 1.6769 m/s
  Calculated RMSE for Run 1_iter34_p (over 20 points, 20 with sim data): 1.6839 m/s
  Calculated RMSE for Run 1_iter34_m (over 20 points, 20 with sim data): 1.5776 m/s
  Calculated RMSE for Run 1_iter35_p (over 20 points, 20 with sim data): 1.5802 m/s
  Calculated RMSE for Run 1_iter35_m (over 20 points, 20 with sim data): 1.6345 m/s
  Calculated RMSE for Run 1_iter36_p (over 20 points, 20 with sim data): 1.5930 m/s
  Calculated RMSE for Run 1_iter36_m (over 20 points, 20 with sim data): 1.5614 m/s
  Calculated RMSE for Run 1_iter37_p (over 20 points, 20 with sim data): 1.5076 m/s
  Calculated RMSE for Run 1_iter37_m (over 20 points, 20 with sim data): 1.4849 m/s
  Calculated RMSE for Run 1_iter38_p (over 20 points, 20 with sim data): 1.1534 m/s
  Calculated RMSE for Run 1_iter38_m (over 20 points, 20 with sim data): 1.4468 m/s
  Calculated RMSE for Run 1_iter39_p (over 20 points, 20 with sim data): 1.5896 m/s
  Calculated RMSE for Run 1_iter39_m (over 20 points, 20 with sim data): 1.4378 m/s
  Calculated RMSE for Run 1_iter40_p (over 20 points, 20 with sim data): 1.7495 m/s
  Calculated RMSE for Run 1_iter40_m (over 20 points, 20 with sim data): 1.6547 m/s
  Run 1 Iteration 40/150: Best Eval Error=1.6547 m/s, Best Error Found So Far in Run 1=1.1534 m/s
  Calculated RMSE for Run 1_iter41_p (over 20 points, 20 with sim data): 1.6928 m/s
  Calculated RMSE for Run 1_iter41_m (over 20 points, 20 with sim data): 1.3121 m/s
  Calculated RMSE for Run 1_iter42_p (over 20 points, 20 with sim data): 1.8008 m/s
  Calculated RMSE for Run 1_iter42_m (over 20 points, 20 with sim data): 1.8330 m/s
  Calculated RMSE for Run 1_iter43_p (over 20 points, 20 with sim data): 1.6386 m/s
  Calculated RMSE for Run 1_iter43_m (over 20 points, 20 with sim data): 1.6923 m/s
  Calculated RMSE for Run 1_iter44_p (over 20 points, 20 with sim data): 1.3652 m/s
  Calculated RMSE for Run 1_iter44_m (over 20 points, 20 with sim data): 1.3195 m/s
  Calculated RMSE for Run 1_iter45_p (over 20 points, 20 with sim data): 1.8341 m/s
  Calculated RMSE for Run 1_iter45_m (over 20 points, 20 with sim data): 1.8259 m/s
  Calculated RMSE for Run 1_iter46_p (over 20 points, 20 with sim data): 1.6628 m/s
  Calculated RMSE for Run 1_iter46_m (over 20 points, 20 with sim data): 1.6280 m/s
  Calculated RMSE for Run 1_iter47_p (over 20 points, 20 with sim data): 1.8002 m/s
  Calculated RMSE for Run 1_iter47_m (over 20 points, 20 with sim data): 1.3352 m/s
  Calculated RMSE for Run 1_iter48_p (over 20 points, 20 with sim data): 1.6309 m/s
  Calculated RMSE for Run 1_iter48_m (over 20 points, 20 with sim data): 1.6489 m/s
  Calculated RMSE for Run 1_iter49_p (over 20 points, 20 with sim data): 1.8159 m/s
  Calculated RMSE for Run 1_iter49_m (over 20 points, 20 with sim data): 1.3803 m/s
  Calculated RMSE for Run 1_iter50_p (over 20 points, 20 with sim data): 1.7126 m/s
  Calculated RMSE for Run 1_iter50_m (over 20 points, 20 with sim data): 1.2356 m/s
  Run 1 Iteration 50/150: Best Eval Error=1.2356 m/s, Best Error Found So Far in Run 1=1.1534 m/s
  Calculated RMSE for Run 1_iter51_p (over 20 points, 20 with sim data): 1.4911 m/s
  Calculated RMSE for Run 1_iter51_m (over 20 points, 20 with sim data): 1.7160 m/s
  Calculated RMSE for Run 1_iter52_p (over 20 points, 20 with sim data): 1.5009 m/s
  Calculated RMSE for Run 1_iter52_m (over 20 points, 20 with sim data): 1.2067 m/s
  Calculated RMSE for Run 1_iter53_p (over 20 points, 20 with sim data): 1.6207 m/s
  Calculated RMSE for Run 1_iter53_m (over 20 points, 20 with sim data): 1.6862 m/s
  Calculated RMSE for Run 1_iter54_p (over 20 points, 20 with sim data): 1.8133 m/s
  Calculated RMSE for Run 1_iter54_m (over 20 points, 20 with sim data): 1.2444 m/s
  Calculated RMSE for Run 1_iter55_p (over 20 points, 20 with sim data): 1.3231 m/s
  Calculated RMSE for Run 1_iter55_m (over 20 points, 20 with sim data): 1.7420 m/s
  Calculated RMSE for Run 1_iter56_p (over 20 points, 20 with sim data): 1.9698 m/s
  Calculated RMSE for Run 1_iter56_m (over 20 points, 20 with sim data): 1.8422 m/s
  Calculated RMSE for Run 1_iter57_p (over 20 points, 20 with sim data): 1.6160 m/s
  Calculated RMSE for Run 1_iter57_m (over 20 points, 20 with sim data): 1.5964 m/s
  Calculated RMSE for Run 1_iter58_p (over 20 points, 20 with sim data): 1.3424 m/s
  Calculated RMSE for Run 1_iter58_m (over 20 points, 20 with sim data): 1.7384 m/s
  Calculated RMSE for Run 1_iter59_p (over 20 points, 20 with sim data): 1.5045 m/s
  Calculated RMSE for Run 1_iter59_m (over 20 points, 20 with sim data): 1.7033 m/s
  Calculated RMSE for Run 1_iter60_p (over 20 points, 20 with sim data): 1.8724 m/s
  Calculated RMSE for Run 1_iter60_m (over 20 points, 20 with sim data): 1.6003 m/s
  Run 1 Iteration 60/150: Best Eval Error=1.6003 m/s, Best Error Found So Far in Run 1=1.1534 m/s
  Calculated RMSE for Run 1_iter61_p (over 20 points, 20 with sim data): 1.6558 m/s
  Calculated RMSE for Run 1_iter61_m (over 20 points, 20 with sim data): 1.2678 m/s
  Calculated RMSE for Run 1_iter62_p (over 20 points, 20 with sim data): 1.5979 m/s
  Calculated RMSE for Run 1_iter62_m (over 20 points, 20 with sim data): 1.4618 m/s
  Calculated RMSE for Run 1_iter63_p (over 20 points, 20 with sim data): 1.5836 m/s
  Calculated RMSE for Run 1_iter63_m (over 20 points, 20 with sim data): 1.5106 m/s
  Calculated RMSE for Run 1_iter64_p (over 20 points, 20 with sim data): 2.0497 m/s
  Calculated RMSE for Run 1_iter64_m (over 20 points, 20 with sim data): 1.5760 m/s
  Calculated RMSE for Run 1_iter65_p (over 20 points, 20 with sim data): 1.8247 m/s
  Calculated RMSE for Run 1_iter65_m (over 20 points, 20 with sim data): 1.4018 m/s
  Calculated RMSE for Run 1_iter66_p (over 20 points, 20 with sim data): 2.2829 m/s
  Calculated RMSE for Run 1_iter66_m (over 20 points, 20 with sim data): 1.5329 m/s
  Calculated RMSE for Run 1_iter67_p (over 20 points, 20 with sim data): 1.8626 m/s
  Calculated RMSE for Run 1_iter67_m (over 20 points, 20 with sim data): 1.2772 m/s
  Calculated RMSE for Run 1_iter68_p (over 20 points, 20 with sim data): 1.3319 m/s
  Calculated RMSE for Run 1_iter68_m (over 20 points, 20 with sim data): 1.5074 m/s
  Calculated RMSE for Run 1_iter69_p (over 20 points, 20 with sim data): 1.4793 m/s
  Calculated RMSE for Run 1_iter69_m (over 20 points, 20 with sim data): 1.7247 m/s
  Calculated RMSE for Run 1_iter70_p (over 20 points, 20 with sim data): 1.6956 m/s
  Calculated RMSE for Run 1_iter70_m (over 20 points, 20 with sim data): 1.2417 m/s
  Run 1 Iteration 70/150: Best Eval Error=1.2417 m/s, Best Error Found So Far in Run 1=1.1534 m/s
  Calculated RMSE for Run 1_iter71_p (over 20 points, 20 with sim data): 1.5742 m/s
  Calculated RMSE for Run 1_iter71_m (over 20 points, 20 with sim data): 1.6214 m/s
  Calculated RMSE for Run 1_iter72_p (over 20 points, 20 with sim data): 1.5208 m/s
  Calculated RMSE for Run 1_iter72_m (over 20 points, 20 with sim data): 1.2517 m/s
  Calculated RMSE for Run 1_iter73_p (over 20 points, 20 with sim data): 1.6561 m/s
  Calculated RMSE for Run 1_iter73_m (over 20 points, 20 with sim data): 5.5173 m/s
  Calculated RMSE for Run 1_iter74_p (over 20 points, 20 with sim data): 1.7014 m/s
  Calculated RMSE for Run 1_iter74_m (over 20 points, 20 with sim data): 1.7945 m/s
  Calculated RMSE for Run 1_iter75_p (over 20 points, 20 with sim data): 1.2475 m/s
  Calculated RMSE for Run 1_iter75_m (over 20 points, 20 with sim data): 1.5949 m/s
  Calculated RMSE for Run 1_iter76_p (over 20 points, 20 with sim data): 1.7831 m/s
  Calculated RMSE for Run 1_iter76_m (over 20 points, 20 with sim data): 1.7682 m/s
  Calculated RMSE for Run 1_iter77_p (over 20 points, 20 with sim data): 1.5509 m/s
  Calculated RMSE for Run 1_iter77_m (over 20 points, 20 with sim data): 1.4042 m/s
  Calculated RMSE for Run 1_iter78_p (over 20 points, 20 with sim data): 1.7024 m/s
  Calculated RMSE for Run 1_iter78_m (over 20 points, 20 with sim data): 1.7348 m/s
  Calculated RMSE for Run 1_iter79_p (over 20 points, 20 with sim data): 1.6319 m/s
  Calculated RMSE for Run 1_iter79_m (over 20 points, 20 with sim data): 1.5745 m/s
  Calculated RMSE for Run 1_iter80_p (over 20 points, 20 with sim data): 1.3106 m/s
  Calculated RMSE for Run 1_iter80_m (over 20 points, 20 with sim data): 1.7977 m/s
  Run 1 Iteration 80/150: Best Eval Error=1.3106 m/s, Best Error Found So Far in Run 1=1.1534 m/s
  Calculated RMSE for Run 1_iter81_p (over 20 points, 20 with sim data): 1.6914 m/s
  Calculated RMSE for Run 1_iter81_m (over 20 points, 20 with sim data): 1.5613 m/s
  Calculated RMSE for Run 1_iter82_p (over 20 points, 20 with sim data): 1.7524 m/s
  Calculated RMSE for Run 1_iter82_m (over 20 points, 20 with sim data): 1.5684 m/s
  Calculated RMSE for Run 1_iter83_p (over 20 points, 20 with sim data): 1.7200 m/s
  Calculated RMSE for Run 1_iter83_m (over 20 points, 20 with sim data): 1.6558 m/s
  Calculated RMSE for Run 1_iter84_p (over 20 points, 20 with sim data): 1.6874 m/s
  Calculated RMSE for Run 1_iter84_m (over 20 points, 20 with sim data): 1.4707 m/s
  Calculated RMSE for Run 1_iter85_p (over 20 points, 20 with sim data): 1.7812 m/s
  Calculated RMSE for Run 1_iter85_m (over 20 points, 20 with sim data): 1.4876 m/s
  Calculated RMSE for Run 1_iter86_p (over 20 points, 20 with sim data): 1.6410 m/s
  Calculated RMSE for Run 1_iter86_m (over 20 points, 20 with sim data): 1.6092 m/s
  Calculated RMSE for Run 1_iter87_p (over 20 points, 20 with sim data): 1.5241 m/s
  Calculated RMSE for Run 1_iter87_m (over 20 points, 20 with sim data): 1.4189 m/s
  Calculated RMSE for Run 1_iter88_p (over 20 points, 20 with sim data): 1.3987 m/s
  Calculated RMSE for Run 1_iter88_m (over 20 points, 20 with sim data): 1.5312 m/s
  Calculated RMSE for Run 1_iter89_p (over 20 points, 20 with sim data): 1.6869 m/s
  Calculated RMSE for Run 1_iter89_m (over 20 points, 20 with sim data): 1.7503 m/s
  Calculated RMSE for Run 1_iter90_p (over 20 points, 20 with sim data): 1.3762 m/s
  Calculated RMSE for Run 1_iter90_m (over 20 points, 20 with sim data): 1.9169 m/s
  Run 1 Iteration 90/150: Best Eval Error=1.3762 m/s, Best Error Found So Far in Run 1=1.1534 m/s
  Calculated RMSE for Run 1_iter91_p (over 20 points, 20 with sim data): 1.7259 m/s
  Calculated RMSE for Run 1_iter91_m (over 20 points, 20 with sim data): 1.5983 m/s
  Calculated RMSE for Run 1_iter92_p (over 20 points, 20 with sim data): 1.7917 m/s
  Calculated RMSE for Run 1_iter92_m (over 20 points, 20 with sim data): 1.5891 m/s
  Calculated RMSE for Run 1_iter93_p (over 20 points, 20 with sim data): 1.8005 m/s
  Calculated RMSE for Run 1_iter93_m (over 20 points, 20 with sim data): 1.5741 m/s
  Calculated RMSE for Run 1_iter94_p (over 20 points, 20 with sim data): 1.6276 m/s
  Calculated RMSE for Run 1_iter94_m (over 20 points, 20 with sim data): 1.7873 m/s
  Calculated RMSE for Run 1_iter95_p (over 20 points, 20 with sim data): 1.8386 m/s
  Calculated RMSE for Run 1_iter95_m (over 20 points, 20 with sim data): 1.5304 m/s
  Calculated RMSE for Run 1_iter96_p (over 20 points, 20 with sim data): 1.1665 m/s
  Calculated RMSE for Run 1_iter96_m (over 20 points, 20 with sim data): 1.7540 m/s
  Calculated RMSE for Run 1_iter97_p (over 20 points, 20 with sim data): 1.5046 m/s
  Calculated RMSE for Run 1_iter97_m (over 20 points, 20 with sim data): 1.5286 m/s
  Calculated RMSE for Run 1_iter98_p (over 20 points, 20 with sim data): 1.6429 m/s
  Calculated RMSE for Run 1_iter98_m (over 20 points, 20 with sim data): 1.7205 m/s
  Calculated RMSE for Run 1_iter99_p (over 20 points, 20 with sim data): 1.8555 m/s
  Calculated RMSE for Run 1_iter99_m (over 20 points, 20 with sim data): 1.5406 m/s
  Calculated RMSE for Run 1_iter100_p (over 20 points, 20 with sim data): 1.5762 m/s
  Calculated RMSE for Run 1_iter100_m (over 20 points, 20 with sim data): 1.5008 m/s
  Run 1 Iteration 100/150: Best Eval Error=1.5008 m/s, Best Error Found So Far in Run 1=1.1534 m/s
  Calculated RMSE for Run 1_iter101_p (over 20 points, 20 with sim data): 1.4778 m/s
  Calculated RMSE for Run 1_iter101_m (over 20 points, 20 with sim data): 1.4456 m/s
  Calculated RMSE for Run 1_iter102_p (over 20 points, 20 with sim data): 1.4292 m/s
  Calculated RMSE for Run 1_iter102_m (over 20 points, 20 with sim data): 1.3880 m/s
  Calculated RMSE for Run 1_iter103_p (over 20 points, 20 with sim data): 1.8387 m/s
  Calculated RMSE for Run 1_iter103_m (over 20 points, 20 with sim data): 1.5443 m/s
  Calculated RMSE for Run 1_iter104_p (over 20 points, 20 with sim data): 1.2447 m/s
  Calculated RMSE for Run 1_iter104_m (over 20 points, 20 with sim data): 1.7166 m/s
  Calculated RMSE for Run 1_iter105_p (over 20 points, 20 with sim data): 1.5204 m/s
  Calculated RMSE for Run 1_iter105_m (over 20 points, 20 with sim data): 1.7103 m/s
  Calculated RMSE for Run 1_iter106_p (over 20 points, 20 with sim data): 1.3878 m/s
  Calculated RMSE for Run 1_iter106_m (over 20 points, 20 with sim data): 1.6491 m/s
  Calculated RMSE for Run 1_iter107_p (over 20 points, 20 with sim data): 1.5259 m/s
  Calculated RMSE for Run 1_iter107_m (over 20 points, 20 with sim data): 1.6005 m/s
  Calculated RMSE for Run 1_iter108_p (over 20 points, 20 with sim data): 1.3971 m/s
  Calculated RMSE for Run 1_iter108_m (over 20 points, 20 with sim data): 1.7942 m/s
  Calculated RMSE for Run 1_iter109_p (over 20 points, 20 with sim data): 1.5603 m/s
  Calculated RMSE for Run 1_iter109_m (over 20 points, 20 with sim data): 1.7607 m/s
  Calculated RMSE for Run 1_iter110_p (over 20 points, 20 with sim data): 1.5662 m/s
  Calculated RMSE for Run 1_iter110_m (over 20 points, 20 with sim data): 1.7240 m/s
  Run 1 Iteration 110/150: Best Eval Error=1.5662 m/s, Best Error Found So Far in Run 1=1.1534 m/s
  Calculated RMSE for Run 1_iter111_p (over 20 points, 20 with sim data): 1.4826 m/s
  Calculated RMSE for Run 1_iter111_m (over 20 points, 20 with sim data): 1.9516 m/s
  Calculated RMSE for Run 1_iter112_p (over 20 points, 20 with sim data): 1.5525 m/s
  Calculated RMSE for Run 1_iter112_m (over 20 points, 20 with sim data): 1.6650 m/s
  Calculated RMSE for Run 1_iter113_p (over 20 points, 20 with sim data): 1.3484 m/s
  Calculated RMSE for Run 1_iter113_m (over 20 points, 20 with sim data): 1.5025 m/s
  Calculated RMSE for Run 1_iter114_p (over 20 points, 20 with sim data): 1.2938 m/s
  Calculated RMSE for Run 1_iter114_m (over 20 points, 20 with sim data): 1.9416 m/s
  Calculated RMSE for Run 1_iter115_p (over 20 points, 20 with sim data): 1.5948 m/s
  Calculated RMSE for Run 1_iter115_m (over 20 points, 20 with sim data): 1.1985 m/s
  Calculated RMSE for Run 1_iter116_p (over 20 points, 20 with sim data): 1.9329 m/s
  Calculated RMSE for Run 1_iter116_m (over 20 points, 20 with sim data): 1.4848 m/s
  Calculated RMSE for Run 1_iter117_p (over 20 points, 20 with sim data): 1.4329 m/s
  Calculated RMSE for Run 1_iter117_m (over 20 points, 20 with sim data): 1.7035 m/s
  Calculated RMSE for Run 1_iter118_p (over 20 points, 20 with sim data): 1.5847 m/s
  Calculated RMSE for Run 1_iter118_m (over 20 points, 20 with sim data): 1.6641 m/s
  Calculated RMSE for Run 1_iter119_p (over 20 points, 20 with sim data): 1.4449 m/s
  Calculated RMSE for Run 1_iter119_m (over 20 points, 20 with sim data): 1.8097 m/s
  Calculated RMSE for Run 1_iter120_p (over 20 points, 20 with sim data): 1.7889 m/s
  Calculated RMSE for Run 1_iter120_m (over 20 points, 20 with sim data): 1.4707 m/s
  Run 1 Iteration 120/150: Best Eval Error=1.4707 m/s, Best Error Found So Far in Run 1=1.1534 m/s
  Calculated RMSE for Run 1_iter121_p (over 20 points, 20 with sim data): 1.1408 m/s
  Calculated RMSE for Run 1_iter121_m (over 20 points, 20 with sim data): 1.6529 m/s
  Calculated RMSE for Run 1_iter122_p (over 20 points, 20 with sim data): 1.2741 m/s
  Calculated RMSE for Run 1_iter122_m (over 20 points, 20 with sim data): 1.6874 m/s
  Calculated RMSE for Run 1_iter123_p (over 20 points, 20 with sim data): 1.6332 m/s
  Calculated RMSE for Run 1_iter123_m (over 20 points, 20 with sim data): 1.8357 m/s
  Calculated RMSE for Run 1_iter124_p (over 20 points, 20 with sim data): 1.3801 m/s
  Calculated RMSE for Run 1_iter124_m (over 20 points, 20 with sim data): 1.7641 m/s
  Calculated RMSE for Run 1_iter125_p (over 20 points, 20 with sim data): 1.2508 m/s
  Calculated RMSE for Run 1_iter125_m (over 20 points, 20 with sim data): 1.5072 m/s
  Calculated RMSE for Run 1_iter126_p (over 20 points, 20 with sim data): 1.3880 m/s
  Calculated RMSE for Run 1_iter126_m (over 20 points, 20 with sim data): 1.8707 m/s
  Calculated RMSE for Run 1_iter127_p (over 20 points, 20 with sim data): 1.7418 m/s
  Calculated RMSE for Run 1_iter127_m (over 20 points, 20 with sim data): 1.6482 m/s
  Calculated RMSE for Run 1_iter128_p (over 20 points, 20 with sim data): 1.5277 m/s
  Calculated RMSE for Run 1_iter128_m (over 20 points, 20 with sim data): 1.5120 m/s
  Calculated RMSE for Run 1_iter129_p (over 20 points, 20 with sim data): 1.8026 m/s
  Calculated RMSE for Run 1_iter129_m (over 20 points, 20 with sim data): 1.6967 m/s
  Calculated RMSE for Run 1_iter130_p (over 20 points, 20 with sim data): 1.4028 m/s
  Calculated RMSE for Run 1_iter130_m (over 20 points, 20 with sim data): 1.4536 m/s
  Run 1 Iteration 130/150: Best Eval Error=1.4028 m/s, Best Error Found So Far in Run 1=1.1408 m/s
  Calculated RMSE for Run 1_iter131_p (over 20 points, 20 with sim data): 1.7317 m/s
  Calculated RMSE for Run 1_iter131_m (over 20 points, 20 with sim data): 1.5084 m/s
  Calculated RMSE for Run 1_iter132_p (over 20 points, 20 with sim data): 1.4876 m/s
  Calculated RMSE for Run 1_iter132_m (over 20 points, 20 with sim data): 1.5243 m/s
  Calculated RMSE for Run 1_iter133_p (over 20 points, 20 with sim data): 1.7863 m/s
  Calculated RMSE for Run 1_iter133_m (over 20 points, 20 with sim data): 1.4023 m/s
  Calculated RMSE for Run 1_iter134_p (over 20 points, 20 with sim data): 1.5845 m/s
  Calculated RMSE for Run 1_iter134_m (over 20 points, 20 with sim data): 1.4928 m/s
  Calculated RMSE for Run 1_iter135_p (over 20 points, 20 with sim data): 1.7705 m/s
  Calculated RMSE for Run 1_iter135_m (over 20 points, 20 with sim data): 1.4887 m/s
  Calculated RMSE for Run 1_iter136_p (over 20 points, 20 with sim data): 1.4103 m/s
  Calculated RMSE for Run 1_iter136_m (over 20 points, 20 with sim data): 1.3491 m/s
  Calculated RMSE for Run 1_iter137_p (over 20 points, 20 with sim data): 1.6761 m/s
  Calculated RMSE for Run 1_iter137_m (over 20 points, 20 with sim data): 1.4097 m/s
  Calculated RMSE for Run 1_iter138_p (over 20 points, 20 with sim data): 1.4782 m/s
  Calculated RMSE for Run 1_iter138_m (over 20 points, 20 with sim data): 1.7046 m/s
  Calculated RMSE for Run 1_iter139_p (over 20 points, 20 with sim data): 1.5929 m/s
  Calculated RMSE for Run 1_iter139_m (over 20 points, 20 with sim data): 1.4756 m/s
  Calculated RMSE for Run 1_iter140_p (over 20 points, 20 with sim data): 1.4422 m/s
  Calculated RMSE for Run 1_iter140_m (over 20 points, 20 with sim data): 1.6051 m/s
  Run 1 Iteration 140/150: Best Eval Error=1.4422 m/s, Best Error Found So Far in Run 1=1.1408 m/s
  Calculated RMSE for Run 1_iter141_p (over 20 points, 20 with sim data): 1.3873 m/s
  Calculated RMSE for Run 1_iter141_m (over 20 points, 20 with sim data): 1.5021 m/s
  Calculated RMSE for Run 1_iter142_p (over 20 points, 20 with sim data): 1.6790 m/s
  Calculated RMSE for Run 1_iter142_m (over 20 points, 20 with sim data): 1.2275 m/s
  Calculated RMSE for Run 1_iter143_p (over 20 points, 20 with sim data): 1.3153 m/s
  Calculated RMSE for Run 1_iter143_m (over 20 points, 20 with sim data): 1.6199 m/s
  Calculated RMSE for Run 1_iter144_p (over 20 points, 20 with sim data): 2.1039 m/s
  Calculated RMSE for Run 1_iter144_m (over 20 points, 20 with sim data): 1.3767 m/s
  Calculated RMSE for Run 1_iter145_p (over 20 points, 20 with sim data): 1.8205 m/s
  Calculated RMSE for Run 1_iter145_m (over 20 points, 20 with sim data): 1.2009 m/s
  Calculated RMSE for Run 1_iter146_p (over 20 points, 20 with sim data): 1.4108 m/s
  Calculated RMSE for Run 1_iter146_m (over 20 points, 20 with sim data): 1.6015 m/s
  Calculated RMSE for Run 1_iter147_p (over 20 points, 20 with sim data): 1.5190 m/s
  Calculated RMSE for Run 1_iter147_m (over 20 points, 20 with sim data): 1.4970 m/s
  Calculated RMSE for Run 1_iter148_p (over 20 points, 20 with sim data): 1.6065 m/s
  Calculated RMSE for Run 1_iter148_m (over 20 points, 20 with sim data): 1.7711 m/s
  Calculated RMSE for Run 1_iter149_p (over 20 points, 20 with sim data): 1.7535 m/s
  Calculated RMSE for Run 1_iter149_m (over 20 points, 20 with sim data): 1.6998 m/s
  Calculated RMSE for Run 1_iter150_p (over 20 points, 20 with sim data): 1.5500 m/s
  Calculated RMSE for Run 1_iter150_m (over 20 points, 20 with sim data): 1.5749 m/s
  Run 1 Iteration 150/150: Best Eval Error=1.5500 m/s, Best Error Found So Far in Run 1=1.1408 m/s
--- SPSA Run Run 1 Finished ---

--- Starting SPSA Run: Restart 1 ---
Initial Params: {'accel': 2.2764448083111066, 'decel': 2.80859223382969, 'tau': 1.1137930575657233, 'maxSpeed': 31.814478751453223, 'minGap': 2.3776716388610843, 'lcSpeedGain': 0.9824593716310143, 'lcStrategic': 0.8972443653209069, 'lcCooperative': 0.92446114427447, 'lcKeepRight': 0.8920703755339289, 'lcAssertive': 1.166724347874321}
  Calculated RMSE for Restart 1_iter1_p (over 20 points, 20 with sim data): 1.3657 m/s
  Calculated RMSE for Restart 1_iter1_m (over 20 points, 20 with sim data): 1.9338 m/s
  Restart 1 Iteration 1/150: Best Eval Error=1.3657 m/s, Best Error Found So Far in Restart 1=1.3657 m/s
  Calculated RMSE for Restart 1_iter2_p (over 20 points, 20 with sim data): 1.4400 m/s
  Calculated RMSE for Restart 1_iter2_m (over 20 points, 20 with sim data): 1.4516 m/s
  Calculated RMSE for Restart 1_iter3_p (over 20 points, 20 with sim data): 1.4807 m/s
  Calculated RMSE for Restart 1_iter3_m (over 20 points, 20 with sim data): 1.6163 m/s
  Calculated RMSE for Restart 1_iter4_p (over 20 points, 20 with sim data): 1.6352 m/s
  Calculated RMSE for Restart 1_iter4_m (over 20 points, 20 with sim data): 1.3596 m/s
  Calculated RMSE for Restart 1_iter5_p (over 20 points, 20 with sim data): 1.5972 m/s
  Calculated RMSE for Restart 1_iter5_m (over 20 points, 20 with sim data): 1.7281 m/s
  Calculated RMSE for Restart 1_iter6_p (over 20 points, 20 with sim data): 1.8990 m/s
  Calculated RMSE for Restart 1_iter6_m (over 20 points, 20 with sim data): 1.5824 m/s
  Calculated RMSE for Restart 1_iter7_p (over 20 points, 20 with sim data): 1.8598 m/s
  Calculated RMSE for Restart 1_iter7_m (over 20 points, 20 with sim data): 1.6038 m/s
  Calculated RMSE for Restart 1_iter8_p (over 20 points, 20 with sim data): 1.5779 m/s
  Calculated RMSE for Restart 1_iter8_m (over 20 points, 20 with sim data): 1.4944 m/s
  Calculated RMSE for Restart 1_iter9_p (over 20 points, 20 with sim data): 1.3836 m/s
  Calculated RMSE for Restart 1_iter9_m (over 20 points, 20 with sim data): 1.4232 m/s
  Calculated RMSE for Restart 1_iter10_p (over 20 points, 20 with sim data): 1.9047 m/s
  Calculated RMSE for Restart 1_iter10_m (over 20 points, 20 with sim data): 1.4623 m/s
  Restart 1 Iteration 10/150: Best Eval Error=1.4623 m/s, Best Error Found So Far in Restart 1=1.3596 m/s
  Calculated RMSE for Restart 1_iter11_p (over 20 points, 20 with sim data): 1.5204 m/s
  Calculated RMSE for Restart 1_iter11_m (over 20 points, 20 with sim data): 1.4957 m/s
  Calculated RMSE for Restart 1_iter12_p (over 20 points, 20 with sim data): 1.5630 m/s
  Calculated RMSE for Restart 1_iter12_m (over 20 points, 20 with sim data): 1.4625 m/s
  Calculated RMSE for Restart 1_iter13_p (over 20 points, 20 with sim data): 1.4883 m/s
  Calculated RMSE for Restart 1_iter13_m (over 20 points, 20 with sim data): 1.7109 m/s
  Calculated RMSE for Restart 1_iter14_p (over 20 points, 20 with sim data): 1.4938 m/s
  Calculated RMSE for Restart 1_iter14_m (over 20 points, 20 with sim data): 1.7793 m/s
  Calculated RMSE for Restart 1_iter15_p (over 20 points, 20 with sim data): 1.6274 m/s
  Calculated RMSE for Restart 1_iter15_m (over 20 points, 20 with sim data): 1.4967 m/s
  Calculated RMSE for Restart 1_iter16_p (over 20 points, 20 with sim data): 1.3067 m/s
  Calculated RMSE for Restart 1_iter16_m (over 20 points, 20 with sim data): 1.5520 m/s
  Calculated RMSE for Restart 1_iter17_p (over 20 points, 20 with sim data): 1.4302 m/s
  Calculated RMSE for Restart 1_iter17_m (over 20 points, 20 with sim data): 1.4612 m/s
  Calculated RMSE for Restart 1_iter18_p (over 20 points, 20 with sim data): 1.7448 m/s
  Calculated RMSE for Restart 1_iter18_m (over 20 points, 20 with sim data): 1.5802 m/s
  Calculated RMSE for Restart 1_iter19_p (over 20 points, 20 with sim data): 1.5204 m/s
  Calculated RMSE for Restart 1_iter19_m (over 20 points, 20 with sim data): 1.5778 m/s
  Calculated RMSE for Restart 1_iter20_p (over 20 points, 20 with sim data): 1.7574 m/s
  Calculated RMSE for Restart 1_iter20_m (over 20 points, 20 with sim data): 1.5452 m/s
  Restart 1 Iteration 20/150: Best Eval Error=1.5452 m/s, Best Error Found So Far in Restart 1=1.3067 m/s
  Calculated RMSE for Restart 1_iter21_p (over 20 points, 20 with sim data): 1.6878 m/s
  Calculated RMSE for Restart 1_iter21_m (over 20 points, 20 with sim data): 1.4443 m/s
  Calculated RMSE for Restart 1_iter22_p (over 20 points, 20 with sim data): 1.6339 m/s
  Calculated RMSE for Restart 1_iter22_m (over 20 points, 20 with sim data): 1.4376 m/s
  Calculated RMSE for Restart 1_iter23_p (over 20 points, 20 with sim data): 1.7170 m/s
  Calculated RMSE for Restart 1_iter23_m (over 20 points, 20 with sim data): 1.8596 m/s
  Calculated RMSE for Restart 1_iter24_p (over 20 points, 20 with sim data): 1.3167 m/s
  Calculated RMSE for Restart 1_iter24_m (over 20 points, 20 with sim data): 1.4409 m/s
  Calculated RMSE for Restart 1_iter25_p (over 20 points, 20 with sim data): 1.7031 m/s
  Calculated RMSE for Restart 1_iter25_m (over 20 points, 20 with sim data): 1.7162 m/s
  Calculated RMSE for Restart 1_iter26_p (over 20 points, 20 with sim data): 1.4254 m/s
  Calculated RMSE for Restart 1_iter26_m (over 20 points, 20 with sim data): 1.6403 m/s
  Calculated RMSE for Restart 1_iter27_p (over 20 points, 20 with sim data): 1.2468 m/s
  Calculated RMSE for Restart 1_iter27_m (over 20 points, 20 with sim data): 1.2824 m/s
  Calculated RMSE for Restart 1_iter28_p (over 20 points, 20 with sim data): 1.7457 m/s
  Calculated RMSE for Restart 1_iter28_m (over 20 points, 20 with sim data): 1.8220 m/s
  Calculated RMSE for Restart 1_iter29_p (over 20 points, 20 with sim data): 1.7641 m/s
  Calculated RMSE for Restart 1_iter29_m (over 20 points, 20 with sim data): 1.7372 m/s
  Calculated RMSE for Restart 1_iter30_p (over 20 points, 20 with sim data): 1.6644 m/s
  Calculated RMSE for Restart 1_iter30_m (over 20 points, 20 with sim data): 1.5987 m/s
  Restart 1 Iteration 30/150: Best Eval Error=1.5987 m/s, Best Error Found So Far in Restart 1=1.2468 m/s
  Calculated RMSE for Restart 1_iter31_p (over 20 points, 20 with sim data): 1.8829 m/s
  Calculated RMSE for Restart 1_iter31_m (over 20 points, 20 with sim data): 1.6756 m/s
  Calculated RMSE for Restart 1_iter32_p (over 20 points, 20 with sim data): 1.2725 m/s
  Calculated RMSE for Restart 1_iter32_m (over 20 points, 20 with sim data): 1.2382 m/s
  Calculated RMSE for Restart 1_iter33_p (over 20 points, 20 with sim data): 1.7919 m/s
  Calculated RMSE for Restart 1_iter33_m (over 20 points, 20 with sim data): 1.5261 m/s
  Calculated RMSE for Restart 1_iter34_p (over 20 points, 20 with sim data): 1.5059 m/s
  Calculated RMSE for Restart 1_iter34_m (over 20 points, 20 with sim data): 1.6934 m/s
  Calculated RMSE for Restart 1_iter35_p (over 20 points, 20 with sim data): 1.4105 m/s
  Calculated RMSE for Restart 1_iter35_m (over 20 points, 20 with sim data): 1.2721 m/s
  Calculated RMSE for Restart 1_iter36_p (over 20 points, 20 with sim data): 1.7720 m/s
  Calculated RMSE for Restart 1_iter36_m (over 20 points, 20 with sim data): 1.4972 m/s
  Calculated RMSE for Restart 1_iter37_p (over 20 points, 20 with sim data): 1.7577 m/s
  Calculated RMSE for Restart 1_iter37_m (over 20 points, 20 with sim data): 1.5349 m/s
  Calculated RMSE for Restart 1_iter38_p (over 20 points, 20 with sim data): 1.5696 m/s
  Calculated RMSE for Restart 1_iter38_m (over 20 points, 20 with sim data): 1.2705 m/s
  Calculated RMSE for Restart 1_iter39_p (over 20 points, 20 with sim data): 1.6619 m/s
  Calculated RMSE for Restart 1_iter39_m (over 20 points, 20 with sim data): 1.5279 m/s
  Calculated RMSE for Restart 1_iter40_p (over 20 points, 20 with sim data): 1.7771 m/s
  Calculated RMSE for Restart 1_iter40_m (over 20 points, 20 with sim data): 1.3612 m/s
  Restart 1 Iteration 40/150: Best Eval Error=1.3612 m/s, Best Error Found So Far in Restart 1=1.2382 m/s
  Calculated RMSE for Restart 1_iter41_p (over 20 points, 20 with sim data): 1.5740 m/s
  Calculated RMSE for Restart 1_iter41_m (over 20 points, 20 with sim data): 1.6517 m/s
  Calculated RMSE for Restart 1_iter42_p (over 20 points, 20 with sim data): 1.4029 m/s
  Calculated RMSE for Restart 1_iter42_m (over 20 points, 20 with sim data): 1.4682 m/s
  Calculated RMSE for Restart 1_iter43_p (over 20 points, 20 with sim data): 1.3839 m/s
  Calculated RMSE for Restart 1_iter43_m (over 20 points, 20 with sim data): 1.5859 m/s
  Calculated RMSE for Restart 1_iter44_p (over 20 points, 20 with sim data): 1.8877 m/s
  Calculated RMSE for Restart 1_iter44_m (over 20 points, 20 with sim data): 1.5011 m/s
  Calculated RMSE for Restart 1_iter45_p (over 20 points, 20 with sim data): 1.5571 m/s
  Calculated RMSE for Restart 1_iter45_m (over 20 points, 20 with sim data): 1.4539 m/s
  Calculated RMSE for Restart 1_iter46_p (over 20 points, 20 with sim data): 1.6401 m/s
  Calculated RMSE for Restart 1_iter46_m (over 20 points, 20 with sim data): 1.5377 m/s
  Calculated RMSE for Restart 1_iter47_p (over 20 points, 20 with sim data): 1.3507 m/s
  Calculated RMSE for Restart 1_iter47_m (over 20 points, 20 with sim data): 1.2541 m/s
  Calculated RMSE for Restart 1_iter48_p (over 20 points, 20 with sim data): 1.6697 m/s
  Calculated RMSE for Restart 1_iter48_m (over 20 points, 20 with sim data): 1.5052 m/s
  Calculated RMSE for Restart 1_iter49_p (over 20 points, 20 with sim data): 2.0225 m/s
  Calculated RMSE for Restart 1_iter49_m (over 20 points, 20 with sim data): 1.9275 m/s
  Calculated RMSE for Restart 1_iter50_p (over 20 points, 20 with sim data): 1.5369 m/s
  Calculated RMSE for Restart 1_iter50_m (over 20 points, 20 with sim data): 1.7313 m/s
  Restart 1 Iteration 50/150: Best Eval Error=1.5369 m/s, Best Error Found So Far in Restart 1=1.2382 m/s
  Calculated RMSE for Restart 1_iter51_p (over 20 points, 20 with sim data): 1.6665 m/s
  Calculated RMSE for Restart 1_iter51_m (over 20 points, 20 with sim data): 1.4584 m/s
  Calculated RMSE for Restart 1_iter52_p (over 20 points, 20 with sim data): 1.3402 m/s
  Calculated RMSE for Restart 1_iter52_m (over 20 points, 20 with sim data): 1.6127 m/s
  Calculated RMSE for Restart 1_iter53_p (over 20 points, 20 with sim data): 1.7718 m/s
  Calculated RMSE for Restart 1_iter53_m (over 20 points, 20 with sim data): 1.4412 m/s
  Calculated RMSE for Restart 1_iter54_p (over 20 points, 20 with sim data): 1.6786 m/s
  Calculated RMSE for Restart 1_iter54_m (over 20 points, 20 with sim data): 1.4176 m/s
  Calculated RMSE for Restart 1_iter55_p (over 20 points, 20 with sim data): 1.8056 m/s
  Calculated RMSE for Restart 1_iter55_m (over 20 points, 20 with sim data): 1.6772 m/s
  Calculated RMSE for Restart 1_iter56_p (over 20 points, 20 with sim data): 1.4902 m/s
  Calculated RMSE for Restart 1_iter56_m (over 20 points, 20 with sim data): 1.3622 m/s
  Calculated RMSE for Restart 1_iter57_p (over 20 points, 20 with sim data): 1.8118 m/s
  Calculated RMSE for Restart 1_iter57_m (over 20 points, 20 with sim data): 1.6457 m/s
  Calculated RMSE for Restart 1_iter58_p (over 20 points, 20 with sim data): 1.4959 m/s
  Calculated RMSE for Restart 1_iter58_m (over 20 points, 20 with sim data): 1.6568 m/s
  Calculated RMSE for Restart 1_iter59_p (over 20 points, 20 with sim data): 1.4170 m/s
  Calculated RMSE for Restart 1_iter59_m (over 20 points, 20 with sim data): 1.6062 m/s
  Calculated RMSE for Restart 1_iter60_p (over 20 points, 20 with sim data): 1.2531 m/s
  Calculated RMSE for Restart 1_iter60_m (over 20 points, 20 with sim data): 1.9124 m/s
  Restart 1 Iteration 60/150: Best Eval Error=1.2531 m/s, Best Error Found So Far in Restart 1=1.2382 m/s
  Calculated RMSE for Restart 1_iter61_p (over 20 points, 20 with sim data): 1.4684 m/s
  Calculated RMSE for Restart 1_iter61_m (over 20 points, 20 with sim data): 1.5090 m/s
  Calculated RMSE for Restart 1_iter62_p (over 20 points, 20 with sim data): 1.3313 m/s
  Calculated RMSE for Restart 1_iter62_m (over 20 points, 20 with sim data): 1.5323 m/s
  Calculated RMSE for Restart 1_iter63_p (over 20 points, 20 with sim data): 1.5421 m/s
  Calculated RMSE for Restart 1_iter63_m (over 20 points, 20 with sim data): 1.9674 m/s
  Calculated RMSE for Restart 1_iter64_p (over 20 points, 20 with sim data): 1.7569 m/s
  Calculated RMSE for Restart 1_iter64_m (over 20 points, 20 with sim data): 1.6237 m/s
  Calculated RMSE for Restart 1_iter65_p (over 20 points, 20 with sim data): 1.7638 m/s
  Calculated RMSE for Restart 1_iter65_m (over 20 points, 20 with sim data): 1.4993 m/s
  Calculated RMSE for Restart 1_iter66_p (over 20 points, 20 with sim data): 1.6030 m/s
  Calculated RMSE for Restart 1_iter66_m (over 20 points, 20 with sim data): 1.5950 m/s
  Calculated RMSE for Restart 1_iter67_p (over 20 points, 20 with sim data): 1.8842 m/s
  Calculated RMSE for Restart 1_iter67_m (over 20 points, 20 with sim data): 1.6398 m/s
  Calculated RMSE for Restart 1_iter68_p (over 20 points, 20 with sim data): 1.7279 m/s
  Calculated RMSE for Restart 1_iter68_m (over 20 points, 20 with sim data): 1.4181 m/s
  Calculated RMSE for Restart 1_iter69_p (over 20 points, 20 with sim data): 1.7333 m/s
  Calculated RMSE for Restart 1_iter69_m (over 20 points, 20 with sim data): 1.3617 m/s
  Calculated RMSE for Restart 1_iter70_p (over 20 points, 20 with sim data): 1.8391 m/s
  Calculated RMSE for Restart 1_iter70_m (over 20 points, 20 with sim data): 1.7092 m/s
  Restart 1 Iteration 70/150: Best Eval Error=1.7092 m/s, Best Error Found So Far in Restart 1=1.2382 m/s
  Calculated RMSE for Restart 1_iter71_p (over 20 points, 20 with sim data): 1.7257 m/s
  Calculated RMSE for Restart 1_iter71_m (over 20 points, 20 with sim data): 1.9589 m/s
  Calculated RMSE for Restart 1_iter72_p (over 20 points, 20 with sim data): 1.4832 m/s
  Calculated RMSE for Restart 1_iter72_m (over 20 points, 20 with sim data): 1.3530 m/s
  Calculated RMSE for Restart 1_iter73_p (over 20 points, 20 with sim data): 1.2516 m/s
  Calculated RMSE for Restart 1_iter73_m (over 20 points, 20 with sim data): 1.7083 m/s
  Calculated RMSE for Restart 1_iter74_p (over 20 points, 20 with sim data): 1.6370 m/s
  Calculated RMSE for Restart 1_iter74_m (over 20 points, 20 with sim data): 1.6085 m/s
  Calculated RMSE for Restart 1_iter75_p (over 20 points, 20 with sim data): 1.6770 m/s
  Calculated RMSE for Restart 1_iter75_m (over 20 points, 20 with sim data): 1.4907 m/s
  Calculated RMSE for Restart 1_iter76_p (over 20 points, 20 with sim data): 1.3895 m/s
  Calculated RMSE for Restart 1_iter76_m (over 20 points, 20 with sim data): 1.6283 m/s
  Calculated RMSE for Restart 1_iter77_p (over 20 points, 20 with sim data): 1.5133 m/s
  Calculated RMSE for Restart 1_iter77_m (over 20 points, 20 with sim data): 1.3806 m/s
  Calculated RMSE for Restart 1_iter78_p (over 20 points, 20 with sim data): 1.5116 m/s
  Calculated RMSE for Restart 1_iter78_m (over 20 points, 20 with sim data): 1.5679 m/s
  Calculated RMSE for Restart 1_iter79_p (over 20 points, 20 with sim data): 1.4570 m/s
  Calculated RMSE for Restart 1_iter79_m (over 20 points, 20 with sim data): 1.3616 m/s
  Calculated RMSE for Restart 1_iter80_p (over 20 points, 20 with sim data): 1.7657 m/s
  Calculated RMSE for Restart 1_iter80_m (over 20 points, 20 with sim data): 1.3829 m/s
  Restart 1 Iteration 80/150: Best Eval Error=1.3829 m/s, Best Error Found So Far in Restart 1=1.2382 m/s
  Calculated RMSE for Restart 1_iter81_p (over 20 points, 20 with sim data): 1.7836 m/s
  Calculated RMSE for Restart 1_iter81_m (over 20 points, 20 with sim data): 1.6494 m/s
  Calculated RMSE for Restart 1_iter82_p (over 20 points, 20 with sim data): 1.5727 m/s
  Calculated RMSE for Restart 1_iter82_m (over 20 points, 20 with sim data): 1.4253 m/s
  Calculated RMSE for Restart 1_iter83_p (over 20 points, 20 with sim data): 1.6594 m/s
  Calculated RMSE for Restart 1_iter83_m (over 20 points, 20 with sim data): 1.6346 m/s
  Calculated RMSE for Restart 1_iter84_p (over 20 points, 20 with sim data): 1.5170 m/s
  Calculated RMSE for Restart 1_iter84_m (over 20 points, 20 with sim data): 1.6414 m/s
  Calculated RMSE for Restart 1_iter85_p (over 20 points, 20 with sim data): 1.4857 m/s
  Calculated RMSE for Restart 1_iter85_m (over 20 points, 20 with sim data): 1.4870 m/s
  Calculated RMSE for Restart 1_iter86_p (over 20 points, 20 with sim data): 1.7289 m/s
  Calculated RMSE for Restart 1_iter86_m (over 20 points, 20 with sim data): 1.2114 m/s
  Calculated RMSE for Restart 1_iter87_p (over 20 points, 20 with sim data): 1.5039 m/s
  Calculated RMSE for Restart 1_iter87_m (over 20 points, 20 with sim data): 1.6298 m/s
  Calculated RMSE for Restart 1_iter88_p (over 20 points, 20 with sim data): 1.6878 m/s
  Calculated RMSE for Restart 1_iter88_m (over 20 points, 20 with sim data): 1.6696 m/s
  Calculated RMSE for Restart 1_iter89_p (over 20 points, 20 with sim data): 1.3891 m/s
  Calculated RMSE for Restart 1_iter89_m (over 20 points, 20 with sim data): 1.6538 m/s
  Calculated RMSE for Restart 1_iter90_p (over 20 points, 20 with sim data): 1.4337 m/s
  Calculated RMSE for Restart 1_iter90_m (over 20 points, 20 with sim data): 1.7653 m/s
  Restart 1 Iteration 90/150: Best Eval Error=1.4337 m/s, Best Error Found So Far in Restart 1=1.2114 m/s
  Calculated RMSE for Restart 1_iter91_p (over 20 points, 20 with sim data): 1.5831 m/s
  Calculated RMSE for Restart 1_iter91_m (over 20 points, 20 with sim data): 1.4673 m/s
  Calculated RMSE for Restart 1_iter92_p (over 20 points, 20 with sim data): 1.3844 m/s
  Calculated RMSE for Restart 1_iter92_m (over 20 points, 20 with sim data): 1.4587 m/s
  Calculated RMSE for Restart 1_iter93_p (over 20 points, 20 with sim data): 1.9666 m/s
  Calculated RMSE for Restart 1_iter93_m (over 20 points, 20 with sim data): 1.7351 m/s
  Calculated RMSE for Restart 1_iter94_p (over 20 points, 20 with sim data): 1.4810 m/s
  Calculated RMSE for Restart 1_iter94_m (over 20 points, 20 with sim data): 1.5364 m/s
  Calculated RMSE for Restart 1_iter95_p (over 20 points, 20 with sim data): 1.5195 m/s
  Calculated RMSE for Restart 1_iter95_m (over 20 points, 20 with sim data): 1.5398 m/s
  Calculated RMSE for Restart 1_iter96_p (over 20 points, 20 with sim data): 1.7996 m/s
  Calculated RMSE for Restart 1_iter96_m (over 20 points, 20 with sim data): 1.4044 m/s
  Calculated RMSE for Restart 1_iter97_p (over 20 points, 20 with sim data): 1.7191 m/s
  Calculated RMSE for Restart 1_iter97_m (over 20 points, 20 with sim data): 1.6645 m/s
  Calculated RMSE for Restart 1_iter98_p (over 20 points, 20 with sim data): 1.2985 m/s
  Calculated RMSE for Restart 1_iter98_m (over 20 points, 20 with sim data): 1.7117 m/s
  Calculated RMSE for Restart 1_iter99_p (over 20 points, 20 with sim data): 1.6973 m/s
  Calculated RMSE for Restart 1_iter99_m (over 20 points, 20 with sim data): 1.2398 m/s
  Calculated RMSE for Restart 1_iter100_p (over 20 points, 20 with sim data): 1.6001 m/s
  Calculated RMSE for Restart 1_iter100_m (over 20 points, 20 with sim data): 2.0207 m/s
  Restart 1 Iteration 100/150: Best Eval Error=1.6001 m/s, Best Error Found So Far in Restart 1=1.2114 m/s
  Calculated RMSE for Restart 1_iter101_p (over 20 points, 20 with sim data): 1.5027 m/s
  Calculated RMSE for Restart 1_iter101_m (over 20 points, 20 with sim data): 1.4022 m/s
  Calculated RMSE for Restart 1_iter102_p (over 20 points, 20 with sim data): 1.4653 m/s
  Calculated RMSE for Restart 1_iter102_m (over 20 points, 20 with sim data): 1.7270 m/s
  Calculated RMSE for Restart 1_iter103_p (over 20 points, 20 with sim data): 1.6547 m/s
  Calculated RMSE for Restart 1_iter103_m (over 20 points, 20 with sim data): 2.0285 m/s
  Calculated RMSE for Restart 1_iter104_p (over 20 points, 20 with sim data): 1.6658 m/s
  Calculated RMSE for Restart 1_iter104_m (over 20 points, 20 with sim data): 1.9490 m/s
  Calculated RMSE for Restart 1_iter105_p (over 20 points, 20 with sim data): 1.7863 m/s
  Calculated RMSE for Restart 1_iter105_m (over 20 points, 20 with sim data): 1.6366 m/s
  Calculated RMSE for Restart 1_iter106_p (over 20 points, 20 with sim data): 1.6547 m/s
  Calculated RMSE for Restart 1_iter106_m (over 20 points, 20 with sim data): 1.5930 m/s
  Calculated RMSE for Restart 1_iter107_p (over 20 points, 20 with sim data): 1.6860 m/s
  Calculated RMSE for Restart 1_iter107_m (over 20 points, 20 with sim data): 1.8408 m/s
  Calculated RMSE for Restart 1_iter108_p (over 20 points, 20 with sim data): 1.3880 m/s
  Calculated RMSE for Restart 1_iter108_m (over 20 points, 20 with sim data): 1.5933 m/s
  Calculated RMSE for Restart 1_iter109_p (over 20 points, 20 with sim data): 1.3029 m/s
  Calculated RMSE for Restart 1_iter109_m (over 20 points, 20 with sim data): 1.6953 m/s
  Calculated RMSE for Restart 1_iter110_p (over 20 points, 20 with sim data): 1.4323 m/s
  Calculated RMSE for Restart 1_iter110_m (over 20 points, 20 with sim data): 1.7813 m/s
  Restart 1 Iteration 110/150: Best Eval Error=1.4323 m/s, Best Error Found So Far in Restart 1=1.2114 m/s
  Calculated RMSE for Restart 1_iter111_p (over 20 points, 20 with sim data): 1.4777 m/s
  Calculated RMSE for Restart 1_iter111_m (over 20 points, 20 with sim data): 1.5996 m/s
  Calculated RMSE for Restart 1_iter112_p (over 20 points, 20 with sim data): 1.5637 m/s
  Calculated RMSE for Restart 1_iter112_m (over 20 points, 20 with sim data): 1.3471 m/s
  Calculated RMSE for Restart 1_iter113_p (over 20 points, 20 with sim data): 1.5987 m/s
  Calculated RMSE for Restart 1_iter113_m (over 20 points, 20 with sim data): 1.5411 m/s
  Calculated RMSE for Restart 1_iter114_p (over 20 points, 20 with sim data): 1.5176 m/s
  Calculated RMSE for Restart 1_iter114_m (over 20 points, 20 with sim data): 1.8764 m/s
  Calculated RMSE for Restart 1_iter115_p (over 20 points, 20 with sim data): 1.2731 m/s
  Calculated RMSE for Restart 1_iter115_m (over 20 points, 20 with sim data): 1.6044 m/s
  Calculated RMSE for Restart 1_iter116_p (over 20 points, 20 with sim data): 1.4644 m/s
  Calculated RMSE for Restart 1_iter116_m (over 20 points, 20 with sim data): 1.5470 m/s
  Calculated RMSE for Restart 1_iter117_p (over 20 points, 20 with sim data): 1.7836 m/s
  Calculated RMSE for Restart 1_iter117_m (over 20 points, 20 with sim data): 1.7779 m/s
  Calculated RMSE for Restart 1_iter118_p (over 20 points, 20 with sim data): 1.2364 m/s
  Calculated RMSE for Restart 1_iter118_m (over 20 points, 20 with sim data): 1.7155 m/s
  Calculated RMSE for Restart 1_iter119_p (over 20 points, 20 with sim data): 1.6045 m/s
  Calculated RMSE for Restart 1_iter119_m (over 20 points, 20 with sim data): 1.6907 m/s
  Calculated RMSE for Restart 1_iter120_p (over 20 points, 20 with sim data): 1.6731 m/s
  Calculated RMSE for Restart 1_iter120_m (over 20 points, 20 with sim data): 1.2969 m/s
  Restart 1 Iteration 120/150: Best Eval Error=1.2969 m/s, Best Error Found So Far in Restart 1=1.2114 m/s
  Calculated RMSE for Restart 1_iter121_p (over 20 points, 20 with sim data): 1.8001 m/s
  Calculated RMSE for Restart 1_iter121_m (over 20 points, 20 with sim data): 1.4228 m/s
  Calculated RMSE for Restart 1_iter122_p (over 20 points, 20 with sim data): 1.6452 m/s
  Calculated RMSE for Restart 1_iter122_m (over 20 points, 20 with sim data): 1.5536 m/s
  Calculated RMSE for Restart 1_iter123_p (over 20 points, 20 with sim data): 1.3954 m/s
  Calculated RMSE for Restart 1_iter123_m (over 20 points, 20 with sim data): 1.2881 m/s
  Calculated RMSE for Restart 1_iter124_p (over 20 points, 20 with sim data): 1.5827 m/s
  Calculated RMSE for Restart 1_iter124_m (over 20 points, 20 with sim data): 1.4320 m/s
  Calculated RMSE for Restart 1_iter125_p (over 20 points, 20 with sim data): 1.5474 m/s
  Calculated RMSE for Restart 1_iter125_m (over 20 points, 20 with sim data): 1.5827 m/s
  Calculated RMSE for Restart 1_iter126_p (over 20 points, 20 with sim data): 1.4088 m/s
  Calculated RMSE for Restart 1_iter126_m (over 20 points, 20 with sim data): 1.4382 m/s
  Calculated RMSE for Restart 1_iter127_p (over 20 points, 20 with sim data): 1.6528 m/s
  Calculated RMSE for Restart 1_iter127_m (over 20 points, 20 with sim data): 1.2474 m/s
  Calculated RMSE for Restart 1_iter128_p (over 20 points, 20 with sim data): 1.5314 m/s
  Calculated RMSE for Restart 1_iter128_m (over 20 points, 20 with sim data): 1.5013 m/s
  Calculated RMSE for Restart 1_iter129_p (over 20 points, 20 with sim data): 1.5398 m/s
  Calculated RMSE for Restart 1_iter129_m (over 20 points, 20 with sim data): 1.9603 m/s
  Calculated RMSE for Restart 1_iter130_p (over 20 points, 20 with sim data): 1.6528 m/s
  Calculated RMSE for Restart 1_iter130_m (over 20 points, 20 with sim data): 1.4563 m/s
  Restart 1 Iteration 130/150: Best Eval Error=1.4563 m/s, Best Error Found So Far in Restart 1=1.2114 m/s
  Calculated RMSE for Restart 1_iter131_p (over 20 points, 20 with sim data): 1.4389 m/s
  Calculated RMSE for Restart 1_iter131_m (over 20 points, 20 with sim data): 1.2447 m/s
  Calculated RMSE for Restart 1_iter132_p (over 20 points, 20 with sim data): 1.4627 m/s
  Calculated RMSE for Restart 1_iter132_m (over 20 points, 20 with sim data): 1.7845 m/s
  Calculated RMSE for Restart 1_iter133_p (over 20 points, 20 with sim data): 1.2496 m/s
  Calculated RMSE for Restart 1_iter133_m (over 20 points, 20 with sim data): 1.7164 m/s
  Calculated RMSE for Restart 1_iter134_p (over 20 points, 20 with sim data): 1.5238 m/s
  Calculated RMSE for Restart 1_iter134_m (over 20 points, 20 with sim data): 1.4991 m/s
  Calculated RMSE for Restart 1_iter135_p (over 20 points, 20 with sim data): 1.8106 m/s
  Calculated RMSE for Restart 1_iter135_m (over 20 points, 20 with sim data): 1.6663 m/s
  Calculated RMSE for Restart 1_iter136_p (over 20 points, 20 with sim data): 1.5677 m/s
  Calculated RMSE for Restart 1_iter136_m (over 20 points, 20 with sim data): 1.4940 m/s
  Calculated RMSE for Restart 1_iter137_p (over 20 points, 20 with sim data): 1.5110 m/s
  Calculated RMSE for Restart 1_iter137_m (over 20 points, 20 with sim data): 1.5838 m/s
  Calculated RMSE for Restart 1_iter138_p (over 20 points, 20 with sim data): 1.4587 m/s
  Calculated RMSE for Restart 1_iter138_m (over 20 points, 20 with sim data): 1.8164 m/s
  Calculated RMSE for Restart 1_iter139_p (over 20 points, 20 with sim data): 1.4851 m/s
  Calculated RMSE for Restart 1_iter139_m (over 20 points, 20 with sim data): 1.6248 m/s
  Calculated RMSE for Restart 1_iter140_p (over 20 points, 20 with sim data): 1.4998 m/s
  Calculated RMSE for Restart 1_iter140_m (over 20 points, 20 with sim data): 1.7001 m/s
  Restart 1 Iteration 140/150: Best Eval Error=1.4998 m/s, Best Error Found So Far in Restart 1=1.2114 m/s
  Calculated RMSE for Restart 1_iter141_p (over 20 points, 20 with sim data): 1.8253 m/s
  Calculated RMSE for Restart 1_iter141_m (over 20 points, 20 with sim data): 1.5783 m/s
  Calculated RMSE for Restart 1_iter142_p (over 20 points, 20 with sim data): 1.5554 m/s
  Calculated RMSE for Restart 1_iter142_m (over 20 points, 20 with sim data): 1.2719 m/s
  Calculated RMSE for Restart 1_iter143_p (over 20 points, 20 with sim data): 1.6943 m/s
  Calculated RMSE for Restart 1_iter143_m (over 20 points, 20 with sim data): 1.6499 m/s
  Calculated RMSE for Restart 1_iter144_p (over 20 points, 20 with sim data): 1.6809 m/s
  Calculated RMSE for Restart 1_iter144_m (over 20 points, 20 with sim data): 1.6782 m/s
  Calculated RMSE for Restart 1_iter145_p (over 20 points, 20 with sim data): 1.3250 m/s
  Calculated RMSE for Restart 1_iter145_m (over 20 points, 20 with sim data): 1.4938 m/s
  Calculated RMSE for Restart 1_iter146_p (over 20 points, 20 with sim data): 2.0122 m/s
  Calculated RMSE for Restart 1_iter146_m (over 20 points, 20 with sim data): 1.5234 m/s
  Calculated RMSE for Restart 1_iter147_p (over 20 points, 20 with sim data): 1.4335 m/s
  Calculated RMSE for Restart 1_iter147_m (over 20 points, 20 with sim data): 1.6134 m/s
  Calculated RMSE for Restart 1_iter148_p (over 20 points, 20 with sim data): 1.5172 m/s
  Calculated RMSE for Restart 1_iter148_m (over 20 points, 20 with sim data): 1.5726 m/s
  Calculated RMSE for Restart 1_iter149_p (over 20 points, 20 with sim data): 1.6279 m/s
  Calculated RMSE for Restart 1_iter149_m (over 20 points, 20 with sim data): 1.5948 m/s
  Calculated RMSE for Restart 1_iter150_p (over 20 points, 20 with sim data): 1.2027 m/s
  Calculated RMSE for Restart 1_iter150_m (over 20 points, 20 with sim data): 1.4198 m/s
  Restart 1 Iteration 150/150: Best Eval Error=1.2027 m/s, Best Error Found So Far in Restart 1=1.2027 m/s
--- SPSA Run Restart 1 Finished ---

--- Starting SPSA Run: Restart 2 ---
Initial Params: {'accel': 2.266641608557204, 'decel': 2.7927687016422866, 'tau': 1.2106287460685579, 'maxSpeed': 31.734156978733832, 'minGap': 2.3443482695160482, 'lcSpeedGain': 0.8488024188961258, 'lcStrategic': 0.9091386138248183, 'lcCooperative': 0.9848876295000928, 'lcKeepRight': 0.7476850075103127, 'lcAssertive': 1.2229005967036266}
  Calculated RMSE for Restart 2_iter1_p (over 20 points, 20 with sim data): 1.3727 m/s
  Calculated RMSE for Restart 2_iter1_m (over 20 points, 20 with sim data): 1.6460 m/s
  Restart 2 Iteration 1/150: Best Eval Error=1.3727 m/s, Best Error Found So Far in Restart 2=1.3727 m/s
  Calculated RMSE for Restart 2_iter2_p (over 20 points, 20 with sim data): 1.4204 m/s
  Calculated RMSE for Restart 2_iter2_m (over 20 points, 20 with sim data): 1.5827 m/s
  Calculated RMSE for Restart 2_iter3_p (over 20 points, 20 with sim data): 1.5100 m/s
  Calculated RMSE for Restart 2_iter3_m (over 20 points, 20 with sim data): 1.6287 m/s
  Calculated RMSE for Restart 2_iter4_p (over 20 points, 20 with sim data): 1.5616 m/s
  Calculated RMSE for Restart 2_iter4_m (over 20 points, 20 with sim data): 1.6111 m/s
  Calculated RMSE for Restart 2_iter5_p (over 20 points, 20 with sim data): 1.9159 m/s
  Calculated RMSE for Restart 2_iter5_m (over 20 points, 20 with sim data): 1.6920 m/s
  Calculated RMSE for Restart 2_iter6_p (over 20 points, 20 with sim data): 1.5429 m/s
  Calculated RMSE for Restart 2_iter6_m (over 20 points, 20 with sim data): 1.6402 m/s
  Calculated RMSE for Restart 2_iter7_p (over 20 points, 20 with sim data): 2.0314 m/s
  Calculated RMSE for Restart 2_iter7_m (over 20 points, 20 with sim data): 1.6639 m/s
  Calculated RMSE for Restart 2_iter8_p (over 20 points, 20 with sim data): 1.4874 m/s
  Calculated RMSE for Restart 2_iter8_m (over 20 points, 20 with sim data): 1.4406 m/s
  Calculated RMSE for Restart 2_iter9_p (over 20 points, 20 with sim data): 1.6302 m/s
  Calculated RMSE for Restart 2_iter9_m (over 20 points, 20 with sim data): 1.5969 m/s
  Calculated RMSE for Restart 2_iter10_p (over 20 points, 20 with sim data): 1.2102 m/s
  Calculated RMSE for Restart 2_iter10_m (over 20 points, 20 with sim data): 1.6415 m/s
  Restart 2 Iteration 10/150: Best Eval Error=1.2102 m/s, Best Error Found So Far in Restart 2=1.2102 m/s
  Calculated RMSE for Restart 2_iter11_p (over 20 points, 20 with sim data): 1.4029 m/s
  Calculated RMSE for Restart 2_iter11_m (over 20 points, 20 with sim data): 1.5925 m/s
  Calculated RMSE for Restart 2_iter12_p (over 20 points, 20 with sim data): 1.7583 m/s
  Calculated RMSE for Restart 2_iter12_m (over 20 points, 20 with sim data): 1.5068 m/s
  Calculated RMSE for Restart 2_iter13_p (over 20 points, 20 with sim data): 1.5217 m/s
  Calculated RMSE for Restart 2_iter13_m (over 20 points, 20 with sim data): 1.5460 m/s
  Calculated RMSE for Restart 2_iter14_p (over 20 points, 20 with sim data): 1.5247 m/s
  Calculated RMSE for Restart 2_iter14_m (over 20 points, 20 with sim data): 1.6196 m/s
  Calculated RMSE for Restart 2_iter15_p (over 20 points, 20 with sim data): 1.5643 m/s
  Calculated RMSE for Restart 2_iter15_m (over 20 points, 20 with sim data): 1.8136 m/s
  Calculated RMSE for Restart 2_iter16_p (over 20 points, 20 with sim data): 1.8142 m/s
  Calculated RMSE for Restart 2_iter16_m (over 20 points, 20 with sim data): 1.6292 m/s
  Calculated RMSE for Restart 2_iter17_p (over 20 points, 20 with sim data): 1.7513 m/s
  Calculated RMSE for Restart 2_iter17_m (over 20 points, 20 with sim data): 1.3797 m/s
  Calculated RMSE for Restart 2_iter18_p (over 20 points, 20 with sim data): 1.4938 m/s
  Calculated RMSE for Restart 2_iter18_m (over 20 points, 20 with sim data): 1.8681 m/s
  Calculated RMSE for Restart 2_iter19_p (over 20 points, 20 with sim data): 1.9392 m/s
  Calculated RMSE for Restart 2_iter19_m (over 20 points, 20 with sim data): 1.4230 m/s
  Calculated RMSE for Restart 2_iter20_p (over 20 points, 20 with sim data): 1.6073 m/s
  Calculated RMSE for Restart 2_iter20_m (over 20 points, 20 with sim data): 1.7563 m/s
  Restart 2 Iteration 20/150: Best Eval Error=1.6073 m/s, Best Error Found So Far in Restart 2=1.2102 m/s
  Calculated RMSE for Restart 2_iter21_p (over 20 points, 20 with sim data): 1.2943 m/s
  Calculated RMSE for Restart 2_iter21_m (over 20 points, 20 with sim data): 1.5465 m/s
  Calculated RMSE for Restart 2_iter22_p (over 20 points, 20 with sim data): 1.5718 m/s
  Calculated RMSE for Restart 2_iter22_m (over 20 points, 20 with sim data): 1.4506 m/s
  Calculated RMSE for Restart 2_iter23_p (over 20 points, 20 with sim data): 1.7849 m/s
  Calculated RMSE for Restart 2_iter23_m (over 20 points, 20 with sim data): 1.6137 m/s
  Calculated RMSE for Restart 2_iter24_p (over 20 points, 20 with sim data): 1.3494 m/s
  Calculated RMSE for Restart 2_iter24_m (over 20 points, 20 with sim data): 1.6433 m/s
  Calculated RMSE for Restart 2_iter25_p (over 20 points, 20 with sim data): 1.4788 m/s
  Calculated RMSE for Restart 2_iter25_m (over 20 points, 20 with sim data): 1.3730 m/s
  Calculated RMSE for Restart 2_iter26_p (over 20 points, 20 with sim data): 1.5819 m/s
  Calculated RMSE for Restart 2_iter26_m (over 20 points, 20 with sim data): 1.5344 m/s
  Calculated RMSE for Restart 2_iter27_p (over 20 points, 20 with sim data): 1.7232 m/s
  Calculated RMSE for Restart 2_iter27_m (over 20 points, 20 with sim data): 1.3258 m/s
  Calculated RMSE for Restart 2_iter28_p (over 20 points, 20 with sim data): 1.6473 m/s
  Calculated RMSE for Restart 2_iter28_m (over 20 points, 20 with sim data): 1.5509 m/s
  Calculated RMSE for Restart 2_iter29_p (over 20 points, 20 with sim data): 1.6217 m/s
  Calculated RMSE for Restart 2_iter29_m (over 20 points, 20 with sim data): 1.6673 m/s
  Calculated RMSE for Restart 2_iter30_p (over 20 points, 20 with sim data): 1.7067 m/s
  Calculated RMSE for Restart 2_iter30_m (over 20 points, 20 with sim data): 1.7119 m/s
  Restart 2 Iteration 30/150: Best Eval Error=1.7067 m/s, Best Error Found So Far in Restart 2=1.2102 m/s
  Calculated RMSE for Restart 2_iter31_p (over 20 points, 20 with sim data): 1.6101 m/s
  Calculated RMSE for Restart 2_iter31_m (over 20 points, 20 with sim data): 2.0691 m/s
  Calculated RMSE for Restart 2_iter32_p (over 20 points, 20 with sim data): 1.0488 m/s
  Calculated RMSE for Restart 2_iter32_m (over 20 points, 20 with sim data): 1.5041 m/s
  Calculated RMSE for Restart 2_iter33_p (over 20 points, 20 with sim data): 1.8775 m/s
  Calculated RMSE for Restart 2_iter33_m (over 20 points, 20 with sim data): 1.7822 m/s
  Calculated RMSE for Restart 2_iter34_p (over 20 points, 20 with sim data): 1.5599 m/s
  Calculated RMSE for Restart 2_iter34_m (over 20 points, 20 with sim data): 1.6131 m/s
  Calculated RMSE for Restart 2_iter35_p (over 20 points, 20 with sim data): 1.4572 m/s
  Calculated RMSE for Restart 2_iter35_m (over 20 points, 20 with sim data): 1.6087 m/s
  Calculated RMSE for Restart 2_iter36_p (over 20 points, 20 with sim data): 1.5819 m/s
  Calculated RMSE for Restart 2_iter36_m (over 20 points, 20 with sim data): 1.6061 m/s
  Calculated RMSE for Restart 2_iter37_p (over 20 points, 20 with sim data): 1.3744 m/s
  Calculated RMSE for Restart 2_iter37_m (over 20 points, 20 with sim data): 1.7155 m/s
  Calculated RMSE for Restart 2_iter38_p (over 20 points, 20 with sim data): 1.4189 m/s
  Calculated RMSE for Restart 2_iter38_m (over 20 points, 20 with sim data): 1.8027 m/s
  Calculated RMSE for Restart 2_iter39_p (over 20 points, 20 with sim data): 1.5388 m/s
  Calculated RMSE for Restart 2_iter39_m (over 20 points, 20 with sim data): 1.7843 m/s
  Calculated RMSE for Restart 2_iter40_p (over 20 points, 20 with sim data): 1.5401 m/s
  Calculated RMSE for Restart 2_iter40_m (over 20 points, 20 with sim data): 1.5746 m/s
  Restart 2 Iteration 40/150: Best Eval Error=1.5401 m/s, Best Error Found So Far in Restart 2=1.0488 m/s
  Calculated RMSE for Restart 2_iter41_p (over 20 points, 20 with sim data): 1.5584 m/s
  Calculated RMSE for Restart 2_iter41_m (over 20 points, 20 with sim data): 1.7491 m/s
  Calculated RMSE for Restart 2_iter42_p (over 20 points, 20 with sim data): 1.3994 m/s
  Calculated RMSE for Restart 2_iter42_m (over 20 points, 20 with sim data): 1.5245 m/s
  Calculated RMSE for Restart 2_iter43_p (over 20 points, 20 with sim data): 1.7210 m/s
  Calculated RMSE for Restart 2_iter43_m (over 20 points, 20 with sim data): 1.8704 m/s
  Calculated RMSE for Restart 2_iter44_p (over 20 points, 20 with sim data): 1.5489 m/s
  Calculated RMSE for Restart 2_iter44_m (over 20 points, 20 with sim data): 1.6349 m/s
  Calculated RMSE for Restart 2_iter45_p (over 20 points, 20 with sim data): 2.0160 m/s
  Calculated RMSE for Restart 2_iter45_m (over 20 points, 20 with sim data): 1.5761 m/s
  Calculated RMSE for Restart 2_iter46_p (over 20 points, 20 with sim data): 1.7054 m/s
  Calculated RMSE for Restart 2_iter46_m (over 20 points, 20 with sim data): 1.6039 m/s
  Calculated RMSE for Restart 2_iter47_p (over 20 points, 20 with sim data): 1.8321 m/s
  Calculated RMSE for Restart 2_iter47_m (over 20 points, 20 with sim data): 1.4749 m/s
  Calculated RMSE for Restart 2_iter48_p (over 20 points, 20 with sim data): 1.6907 m/s
  Calculated RMSE for Restart 2_iter48_m (over 20 points, 20 with sim data): 1.6663 m/s
  Calculated RMSE for Restart 2_iter49_p (over 20 points, 20 with sim data): 1.8364 m/s
  Calculated RMSE for Restart 2_iter49_m (over 20 points, 20 with sim data): 1.7159 m/s
  Calculated RMSE for Restart 2_iter50_p (over 20 points, 20 with sim data): 1.6580 m/s
  Calculated RMSE for Restart 2_iter50_m (over 20 points, 20 with sim data): 1.3539 m/s
  Restart 2 Iteration 50/150: Best Eval Error=1.3539 m/s, Best Error Found So Far in Restart 2=1.0488 m/s
  Calculated RMSE for Restart 2_iter51_p (over 20 points, 20 with sim data): 1.6760 m/s
  Calculated RMSE for Restart 2_iter51_m (over 20 points, 20 with sim data): 1.4724 m/s
  Calculated RMSE for Restart 2_iter52_p (over 20 points, 20 with sim data): 1.5430 m/s
  Calculated RMSE for Restart 2_iter52_m (over 20 points, 20 with sim data): 1.8127 m/s
  Calculated RMSE for Restart 2_iter53_p (over 20 points, 20 with sim data): 1.7954 m/s
  Calculated RMSE for Restart 2_iter53_m (over 20 points, 20 with sim data): 1.6625 m/s
  Calculated RMSE for Restart 2_iter54_p (over 20 points, 20 with sim data): 1.6783 m/s
  Calculated RMSE for Restart 2_iter54_m (over 20 points, 20 with sim data): 1.5232 m/s
  Calculated RMSE for Restart 2_iter55_p (over 20 points, 20 with sim data): 1.5196 m/s
  Calculated RMSE for Restart 2_iter55_m (over 20 points, 20 with sim data): 1.6146 m/s
  Calculated RMSE for Restart 2_iter56_p (over 20 points, 20 with sim data): 2.0788 m/s
  Calculated RMSE for Restart 2_iter56_m (over 20 points, 20 with sim data): 1.7312 m/s
  Calculated RMSE for Restart 2_iter57_p (over 20 points, 20 with sim data): 1.7115 m/s
  Calculated RMSE for Restart 2_iter57_m (over 20 points, 20 with sim data): 1.5592 m/s
  Calculated RMSE for Restart 2_iter58_p (over 20 points, 20 with sim data): 1.4397 m/s
  Calculated RMSE for Restart 2_iter58_m (over 20 points, 20 with sim data): 1.4818 m/s
  Calculated RMSE for Restart 2_iter59_p (over 20 points, 20 with sim data): 1.9490 m/s
  Calculated RMSE for Restart 2_iter59_m (over 20 points, 20 with sim data): 1.7424 m/s
  Calculated RMSE for Restart 2_iter60_p (over 20 points, 20 with sim data): 1.9426 m/s
  Calculated RMSE for Restart 2_iter60_m (over 20 points, 20 with sim data): 1.6442 m/s
  Restart 2 Iteration 60/150: Best Eval Error=1.6442 m/s, Best Error Found So Far in Restart 2=1.0488 m/s
  Calculated RMSE for Restart 2_iter61_p (over 20 points, 20 with sim data): 1.8353 m/s
  Calculated RMSE for Restart 2_iter61_m (over 20 points, 20 with sim data): 1.7357 m/s
  Calculated RMSE for Restart 2_iter62_p (over 20 points, 20 with sim data): 1.3938 m/s
  Calculated RMSE for Restart 2_iter62_m (over 20 points, 20 with sim data): 1.3347 m/s
  Calculated RMSE for Restart 2_iter63_p (over 20 points, 20 with sim data): 1.2963 m/s
  Calculated RMSE for Restart 2_iter63_m (over 20 points, 20 with sim data): 1.5158 m/s
  Calculated RMSE for Restart 2_iter64_p (over 20 points, 20 with sim data): 1.7646 m/s
  Calculated RMSE for Restart 2_iter64_m (over 20 points, 20 with sim data): 1.2837 m/s
  Calculated RMSE for Restart 2_iter65_p (over 20 points, 20 with sim data): 1.8548 m/s
  Calculated RMSE for Restart 2_iter65_m (over 20 points, 20 with sim data): 1.6276 m/s
  Calculated RMSE for Restart 2_iter66_p (over 20 points, 20 with sim data): 1.4223 m/s
  Calculated RMSE for Restart 2_iter66_m (over 20 points, 20 with sim data): 1.6665 m/s
  Calculated RMSE for Restart 2_iter67_p (over 20 points, 20 with sim data): 1.6139 m/s
  Calculated RMSE for Restart 2_iter67_m (over 20 points, 20 with sim data): 1.4559 m/s
  Calculated RMSE for Restart 2_iter68_p (over 20 points, 20 with sim data): 1.3404 m/s
  Calculated RMSE for Restart 2_iter68_m (over 20 points, 20 with sim data): 1.8147 m/s
  Calculated RMSE for Restart 2_iter69_p (over 20 points, 20 with sim data): 1.4002 m/s
  Calculated RMSE for Restart 2_iter69_m (over 20 points, 20 with sim data): 1.2705 m/s
  Calculated RMSE for Restart 2_iter70_p (over 20 points, 20 with sim data): 1.7693 m/s
  Calculated RMSE for Restart 2_iter70_m (over 20 points, 20 with sim data): 1.5001 m/s
  Restart 2 Iteration 70/150: Best Eval Error=1.5001 m/s, Best Error Found So Far in Restart 2=1.0488 m/s
  Calculated RMSE for Restart 2_iter71_p (over 20 points, 20 with sim data): 1.4928 m/s
  Calculated RMSE for Restart 2_iter71_m (over 20 points, 20 with sim data): 1.4949 m/s
  Calculated RMSE for Restart 2_iter72_p (over 20 points, 20 with sim data): 1.3200 m/s
  Calculated RMSE for Restart 2_iter72_m (over 20 points, 20 with sim data): 1.4098 m/s
  Calculated RMSE for Restart 2_iter73_p (over 20 points, 20 with sim data): 1.6484 m/s
  Calculated RMSE for Restart 2_iter73_m (over 20 points, 20 with sim data): 1.5937 m/s
  Calculated RMSE for Restart 2_iter74_p (over 20 points, 20 with sim data): 1.3706 m/s
  Calculated RMSE for Restart 2_iter74_m (over 20 points, 20 with sim data): 1.6535 m/s
  Calculated RMSE for Restart 2_iter75_p (over 20 points, 20 with sim data): 1.4830 m/s
  Calculated RMSE for Restart 2_iter75_m (over 20 points, 20 with sim data): 1.4442 m/s
  Calculated RMSE for Restart 2_iter76_p (over 20 points, 20 with sim data): 1.6061 m/s
  Calculated RMSE for Restart 2_iter76_m (over 20 points, 20 with sim data): 1.7686 m/s
  Calculated RMSE for Restart 2_iter77_p (over 20 points, 20 with sim data): 1.7161 m/s
  Calculated RMSE for Restart 2_iter77_m (over 20 points, 20 with sim data): 1.5882 m/s
  Calculated RMSE for Restart 2_iter78_p (over 20 points, 20 with sim data): 1.7736 m/s
  Calculated RMSE for Restart 2_iter78_m (over 20 points, 20 with sim data): 1.5518 m/s
  Calculated RMSE for Restart 2_iter79_p (over 20 points, 20 with sim data): 1.7312 m/s
  Calculated RMSE for Restart 2_iter79_m (over 20 points, 20 with sim data): 1.8265 m/s
  Calculated RMSE for Restart 2_iter80_p (over 20 points, 20 with sim data): 1.5927 m/s
  Calculated RMSE for Restart 2_iter80_m (over 20 points, 20 with sim data): 1.5616 m/s
  Restart 2 Iteration 80/150: Best Eval Error=1.5616 m/s, Best Error Found So Far in Restart 2=1.0488 m/s
  Calculated RMSE for Restart 2_iter81_p (over 20 points, 20 with sim data): 1.3343 m/s
  Calculated RMSE for Restart 2_iter81_m (over 20 points, 20 with sim data): 1.6747 m/s
  Calculated RMSE for Restart 2_iter82_p (over 20 points, 20 with sim data): 1.8841 m/s
  Calculated RMSE for Restart 2_iter82_m (over 20 points, 20 with sim data): 1.9309 m/s
  Calculated RMSE for Restart 2_iter83_p (over 20 points, 20 with sim data): 1.7311 m/s
  Calculated RMSE for Restart 2_iter83_m (over 20 points, 20 with sim data): 1.5609 m/s
  Calculated RMSE for Restart 2_iter84_p (over 20 points, 20 with sim data): 1.7709 m/s
  Calculated RMSE for Restart 2_iter84_m (over 20 points, 20 with sim data): 1.6404 m/s
  Calculated RMSE for Restart 2_iter85_p (over 20 points, 20 with sim data): 1.7697 m/s
  Calculated RMSE for Restart 2_iter85_m (over 20 points, 20 with sim data): 1.2249 m/s
  Calculated RMSE for Restart 2_iter86_p (over 20 points, 20 with sim data): 1.4806 m/s
  Calculated RMSE for Restart 2_iter86_m (over 20 points, 20 with sim data): 1.4894 m/s
  Calculated RMSE for Restart 2_iter87_p (over 20 points, 20 with sim data): 1.4093 m/s
  Calculated RMSE for Restart 2_iter87_m (over 20 points, 20 with sim data): 1.3281 m/s
  Calculated RMSE for Restart 2_iter88_p (over 20 points, 20 with sim data): 1.7693 m/s
  Calculated RMSE for Restart 2_iter88_m (over 20 points, 20 with sim data): 1.4562 m/s
  Calculated RMSE for Restart 2_iter89_p (over 20 points, 20 with sim data): 1.6298 m/s
  Calculated RMSE for Restart 2_iter89_m (over 20 points, 20 with sim data): 1.5529 m/s
  Calculated RMSE for Restart 2_iter90_p (over 20 points, 20 with sim data): 1.5832 m/s
  Calculated RMSE for Restart 2_iter90_m (over 20 points, 20 with sim data): 1.9844 m/s
  Restart 2 Iteration 90/150: Best Eval Error=1.5832 m/s, Best Error Found So Far in Restart 2=1.0488 m/s
  Calculated RMSE for Restart 2_iter91_p (over 20 points, 20 with sim data): 1.5584 m/s
  Calculated RMSE for Restart 2_iter91_m (over 20 points, 20 with sim data): 1.3449 m/s
  Calculated RMSE for Restart 2_iter92_p (over 20 points, 20 with sim data): 1.2641 m/s
  Calculated RMSE for Restart 2_iter92_m (over 20 points, 20 with sim data): 1.8181 m/s
  Calculated RMSE for Restart 2_iter93_p (over 20 points, 20 with sim data): 1.6843 m/s
  Calculated RMSE for Restart 2_iter93_m (over 20 points, 20 with sim data): 1.6155 m/s
  Calculated RMSE for Restart 2_iter94_p (over 20 points, 20 with sim data): 1.9414 m/s
  Calculated RMSE for Restart 2_iter94_m (over 20 points, 20 with sim data): 1.6180 m/s
  Calculated RMSE for Restart 2_iter95_p (over 20 points, 20 with sim data): 1.2862 m/s
  Calculated RMSE for Restart 2_iter95_m (over 20 points, 20 with sim data): 1.5153 m/s
  Calculated RMSE for Restart 2_iter96_p (over 20 points, 20 with sim data): 1.7247 m/s
  Calculated RMSE for Restart 2_iter96_m (over 20 points, 20 with sim data): 1.9566 m/s
  Calculated RMSE for Restart 2_iter97_p (over 20 points, 20 with sim data): 1.5825 m/s
  Calculated RMSE for Restart 2_iter97_m (over 20 points, 20 with sim data): 1.4645 m/s
  Calculated RMSE for Restart 2_iter98_p (over 20 points, 20 with sim data): 1.7566 m/s
  Calculated RMSE for Restart 2_iter98_m (over 20 points, 20 with sim data): 1.4460 m/s
  Calculated RMSE for Restart 2_iter99_p (over 20 points, 20 with sim data): 1.2553 m/s
  Calculated RMSE for Restart 2_iter99_m (over 20 points, 20 with sim data): 1.5772 m/s
  Calculated RMSE for Restart 2_iter100_p (over 20 points, 20 with sim data): 1.6767 m/s
  Calculated RMSE for Restart 2_iter100_m (over 20 points, 20 with sim data): 1.2274 m/s
  Restart 2 Iteration 100/150: Best Eval Error=1.2274 m/s, Best Error Found So Far in Restart 2=1.0488 m/s
  Calculated RMSE for Restart 2_iter101_p (over 20 points, 20 with sim data): 1.6051 m/s
  Calculated RMSE for Restart 2_iter101_m (over 20 points, 20 with sim data): 1.6972 m/s
  Calculated RMSE for Restart 2_iter102_p (over 20 points, 20 with sim data): 1.4683 m/s
  Calculated RMSE for Restart 2_iter102_m (over 20 points, 20 with sim data): 1.6480 m/s
  Calculated RMSE for Restart 2_iter103_p (over 20 points, 20 with sim data): 1.7096 m/s
  Calculated RMSE for Restart 2_iter103_m (over 20 points, 20 with sim data): 1.3130 m/s
  Calculated RMSE for Restart 2_iter104_p (over 20 points, 20 with sim data): 1.6893 m/s
  Calculated RMSE for Restart 2_iter104_m (over 20 points, 20 with sim data): 1.6525 m/s
  Calculated RMSE for Restart 2_iter105_p (over 20 points, 20 with sim data): 1.8487 m/s
  Calculated RMSE for Restart 2_iter105_m (over 20 points, 20 with sim data): 1.7342 m/s
  Calculated RMSE for Restart 2_iter106_p (over 20 points, 20 with sim data): 1.2856 m/s
  Calculated RMSE for Restart 2_iter106_m (over 20 points, 20 with sim data): 1.6960 m/s
  Calculated RMSE for Restart 2_iter107_p (over 20 points, 20 with sim data): 1.7261 m/s
  Calculated RMSE for Restart 2_iter107_m (over 20 points, 20 with sim data): 1.6492 m/s
  Calculated RMSE for Restart 2_iter108_p (over 20 points, 20 with sim data): 1.7537 m/s
  Calculated RMSE for Restart 2_iter108_m (over 20 points, 20 with sim data): 1.4648 m/s
  Calculated RMSE for Restart 2_iter109_p (over 20 points, 20 with sim data): 1.3919 m/s
  Calculated RMSE for Restart 2_iter109_m (over 20 points, 20 with sim data): 1.6741 m/s
  Calculated RMSE for Restart 2_iter110_p (over 20 points, 20 with sim data): 1.7223 m/s
  Calculated RMSE for Restart 2_iter110_m (over 20 points, 20 with sim data): 1.5692 m/s
  Restart 2 Iteration 110/150: Best Eval Error=1.5692 m/s, Best Error Found So Far in Restart 2=1.0488 m/s
  Calculated RMSE for Restart 2_iter111_p (over 20 points, 20 with sim data): 1.5832 m/s
  Calculated RMSE for Restart 2_iter111_m (over 20 points, 20 with sim data): 1.3141 m/s
  Calculated RMSE for Restart 2_iter112_p (over 20 points, 20 with sim data): 1.7451 m/s
  Calculated RMSE for Restart 2_iter111_m (over 20 points, 20 with sim data): 1.3141 m/s
  Calculated RMSE for Restart 2_iter111_m (over 20 points, 20 with sim data): 1.3141 m/s
  Calculated RMSE for Restart 2_iter112_p (over 20 points, 20 with sim data): 1.7451 m/s
  Calculated RMSE for Restart 2_iter112_m (over 20 points, 20 with sim data): 1.9467 m/s
  Calculated RMSE for Restart 2_iter113_p (over 20 points, 20 with sim data): 1.6978 m/s
  Calculated RMSE for Restart 2_iter113_m (over 20 points, 20 with sim data): 1.4766 m/s
  Calculated RMSE for Restart 2_iter114_p (over 20 points, 20 with sim data): 1.6555 m/s
  Calculated RMSE for Restart 2_iter114_m (over 20 points, 20 with sim data): 1.6451 m/s
  Calculated RMSE for Restart 2_iter115_p (over 20 points, 20 with sim data): 1.3606 m/s
  Calculated RMSE for Restart 2_iter115_m (over 20 points, 20 with sim data): 1.5676 m/s
  Calculated RMSE for Restart 2_iter116_p (over 20 points, 20 with sim data): 1.4764 m/s
  Calculated RMSE for Restart 2_iter116_m (over 20 points, 20 with sim data): 1.4747 m/s
  Calculated RMSE for Restart 2_iter117_p (over 20 points, 20 with sim data): 1.5456 m/s
  Calculated RMSE for Restart 2_iter117_m (over 20 points, 20 with sim data): 1.3050 m/s
  Calculated RMSE for Restart 2_iter118_p (over 20 points, 20 with sim data): 1.7126 m/s
  Calculated RMSE for Restart 2_iter118_m (over 20 points, 20 with sim data): 1.5732 m/s
  Calculated RMSE for Restart 2_iter119_p (over 20 points, 20 with sim data): 1.5587 m/s
  Calculated RMSE for Restart 2_iter119_m (over 20 points, 20 with sim data): 1.6689 m/s
  Calculated RMSE for Restart 2_iter120_p (over 20 points, 20 with sim data): 1.9084 m/s
  Calculated RMSE for Restart 2_iter120_m (over 20 points, 20 with sim data): 1.7582 m/s
  Restart 2 Iteration 120/150: Best Eval Error=1.7582 m/s, Best Error Found So Far in Restart 2=1.0488 m/s
  Calculated RMSE for Restart 2_iter121_p (over 20 points, 20 with sim data): 1.6849 m/s
  Calculated RMSE for Restart 2_iter121_m (over 20 points, 20 with sim data): 1.6942 m/s
  Calculated RMSE for Restart 2_iter122_p (over 20 points, 20 with sim data): 1.5645 m/s
  Calculated RMSE for Restart 2_iter122_m (over 20 points, 20 with sim data): 1.5210 m/s
  Calculated RMSE for Restart 2_iter123_p (over 20 points, 20 with sim data): 1.4633 m/s
  Calculated RMSE for Restart 2_iter123_m (over 20 points, 20 with sim data): 1.7051 m/s
  Calculated RMSE for Restart 2_iter124_p (over 20 points, 20 with sim data): 1.3578 m/s
  Calculated RMSE for Restart 2_iter124_m (over 20 points, 20 with sim data): 1.3974 m/s
  Calculated RMSE for Restart 2_iter125_p (over 20 points, 20 with sim data): 1.3535 m/s
  Calculated RMSE for Restart 2_iter125_m (over 20 points, 20 with sim data): 1.5664 m/s
  Calculated RMSE for Restart 2_iter126_p (over 20 points, 20 with sim data): 1.7396 m/s
  Calculated RMSE for Restart 2_iter126_m (over 20 points, 20 with sim data): 1.3819 m/s
  Calculated RMSE for Restart 2_iter127_p (over 20 points, 20 with sim data): 1.6533 m/s
  Calculated RMSE for Restart 2_iter127_m (over 20 points, 20 with sim data): 1.5893 m/s
  Calculated RMSE for Restart 2_iter128_p (over 20 points, 20 with sim data): 1.8410 m/s
  Calculated RMSE for Restart 2_iter128_m (over 20 points, 20 with sim data): 1.2635 m/s
  Calculated RMSE for Restart 2_iter129_p (over 20 points, 20 with sim data): 1.6773 m/s
  Calculated RMSE for Restart 2_iter129_m (over 20 points, 20 with sim data): 1.7708 m/s
  Calculated RMSE for Restart 2_iter130_p (over 20 points, 20 with sim data): 1.5791 m/s
  Calculated RMSE for Restart 2_iter130_m (over 20 points, 20 with sim data): 1.5217 m/s
  Restart 2 Iteration 130/150: Best Eval Error=1.5217 m/s, Best Error Found So Far in Restart 2=1.0488 m/s
  Calculated RMSE for Restart 2_iter131_p (over 20 points, 20 with sim data): 1.4104 m/s
  Calculated RMSE for Restart 2_iter131_m (over 20 points, 20 with sim data): 1.8223 m/s
  Calculated RMSE for Restart 2_iter132_p (over 20 points, 20 with sim data): 1.5927 m/s
  Calculated RMSE for Restart 2_iter132_m (over 20 points, 20 with sim data): 1.1761 m/s
  Calculated RMSE for Restart 2_iter133_p (over 20 points, 20 with sim data): 1.4578 m/s
  Calculated RMSE for Restart 2_iter133_m (over 20 points, 20 with sim data): 1.8159 m/s
  Calculated RMSE for Restart 2_iter134_p (over 20 points, 20 with sim data): 1.8228 m/s
  Calculated RMSE for Restart 2_iter134_m (over 20 points, 20 with sim data): 1.3613 m/s
  Calculated RMSE for Restart 2_iter135_p (over 20 points, 20 with sim data): 1.5931 m/s
  Calculated RMSE for Restart 2_iter135_m (over 20 points, 20 with sim data): 1.4462 m/s
  Calculated RMSE for Restart 2_iter136_p (over 20 points, 20 with sim data): 1.7040 m/s
  Calculated RMSE for Restart 2_iter136_m (over 20 points, 20 with sim data): 1.3329 m/s
  Calculated RMSE for Restart 2_iter137_p (over 20 points, 20 with sim data): 1.6250 m/s
  Calculated RMSE for Restart 2_iter137_m (over 20 points, 20 with sim data): 1.4990 m/s
  Calculated RMSE for Restart 2_iter138_p (over 20 points, 20 with sim data): 1.9089 m/s
  Calculated RMSE for Restart 2_iter138_m (over 20 points, 20 with sim data): 1.3184 m/s
  Calculated RMSE for Restart 2_iter139_p (over 20 points, 20 with sim data): 1.4375 m/s
  Calculated RMSE for Restart 2_iter139_m (over 20 points, 20 with sim data): 1.6292 m/s
  Calculated RMSE for Restart 2_iter140_p (over 20 points, 20 with sim data): 1.6802 m/s
  Calculated RMSE for Restart 2_iter140_m (over 20 points, 20 with sim data): 1.8633 m/s
  Restart 2 Iteration 140/150: Best Eval Error=1.6802 m/s, Best Error Found So Far in Restart 2=1.0488 m/s
  Calculated RMSE for Restart 2_iter141_p (over 20 points, 20 with sim data): 1.2783 m/s
  Calculated RMSE for Restart 2_iter141_m (over 20 points, 20 with sim data): 1.5299 m/s
  Calculated RMSE for Restart 2_iter142_p (over 20 points, 20 with sim data): 1.7239 m/s
  Calculated RMSE for Restart 2_iter142_m (over 20 points, 20 with sim data): 1.5567 m/s
  Calculated RMSE for Restart 2_iter143_p (over 20 points, 20 with sim data): 1.4733 m/s
  Calculated RMSE for Restart 2_iter143_m (over 20 points, 20 with sim data): 1.5682 m/s
  Calculated RMSE for Restart 2_iter144_p (over 20 points, 20 with sim data): 1.5144 m/s
  Calculated RMSE for Restart 2_iter144_m (over 20 points, 20 with sim data): 1.8887 m/s
  Calculated RMSE for Restart 2_iter145_p (over 20 points, 20 with sim data): 1.4970 m/s
  Calculated RMSE for Restart 2_iter145_m (over 20 points, 20 with sim data): 1.8218 m/s
  Calculated RMSE for Restart 2_iter146_p (over 20 points, 20 with sim data): 1.7839 m/s
  Calculated RMSE for Restart 2_iter146_m (over 20 points, 20 with sim data): 1.4438 m/s
  Calculated RMSE for Restart 2_iter147_p (over 20 points, 20 with sim data): 1.6204 m/s
  Calculated RMSE for Restart 2_iter147_m (over 20 points, 20 with sim data): 1.6390 m/s
  Calculated RMSE for Restart 2_iter148_p (over 20 points, 20 with sim data): 1.4565 m/s
  Calculated RMSE for Restart 2_iter148_m (over 20 points, 20 with sim data): 1.5814 m/s
  Calculated RMSE for Restart 2_iter149_p (over 20 points, 20 with sim data): 1.4826 m/s
  Calculated RMSE for Restart 2_iter149_m (over 20 points, 20 with sim data): 1.9980 m/s
  Calculated RMSE for Restart 2_iter150_p (over 20 points, 20 with sim data): 1.7202 m/s
  Calculated RMSE for Restart 2_iter150_m (over 20 points, 20 with sim data): 1.4253 m/s
  Restart 2 Iteration 150/150: Best Eval Error=1.4253 m/s, Best Error Found So Far in Restart 2=1.0488 m/s
--- SPSA Run Restart 2 Finished ---

--- Overall SPSA Calibration Results ---
SPSA Optimization with restarts finished.
Total cumulative iterations: 450
Best RMSE found across all runs: 1.0488 m/s
Best Parameters found overall:
  accel: 2.1421
  decel: 2.8374
  tau: 1.2557
  maxSpeed: 31.6797
  minGap: 2.2181
  lcSpeedGain: 0.9349
  lcStrategic: 0.8621
  lcCooperative: 1.0000
  lcKeepRight: 0.8432
  lcAssertive: 1.1962
Best parameters saved to D:/SUMO\best_calibrated_parameters_spsa.txt

Calibration took 1962.07 seconds (32.70 minutes).

Generating convergence plots...
Per-run convergence plot saved to D:/SUMO\spsa_per_run_convergence.png
Cumulative convergence plot saved to D:/SUMO\spsa_cumulative_convergence.png

Running final verification simulation with best SPSA parameters...
  Calculated RMSE for final_verification (over 20 points, 20 with sim data): 1.8332 m/s
RMSE from final verification run: 1.8332 m/s
进程已结束，退出代码为 0

"""
# --- 解析日志数据 ---
# We want to extract y_p and y_m for each iteration
run_iteration_eval_pairs = {}
current_run_name = None
current_iteration_evals = {} # {iteration: {'p': error_p, 'm': error_m}}

# Regex to match 'Calculated RMSE' lines
# Captures Run/Restart name, iter, perturbation type (p/m), and error value
eval_log_pattern = re.compile(r"^\s*Calculated RMSE for (Run \d+|Restart \d+)_iter(\d+)_(p|m) \(.*?\):\s*([\d.]+?)\s*([%m/s]*)$")
run_start_pattern = re.compile(r"^--- Starting SPSA Run: (Run \d+|Restart \d+) ---$")

# Iterate through the log data line by line
for line in log_data.strip().split('\n'):
    # Check for the start of a new run
    start_match = run_start_pattern.match(line)
    if start_match:
        if current_run_name is not None: # If we were already processing a run
             # Store the collected iteration evaluation pairs for the previous run
             run_iteration_eval_pairs[current_run_name] = current_iteration_evals
        current_run_name = start_match.group(1)
        current_iteration_evals = {} # Reset for the new run
        # print(f"--- Found run: {current_run_name} ---") # Debug print
        continue

    # Check for 'Calculated RMSE' line
    eval_match = eval_log_pattern.match(line)
    if eval_match and current_run_name is not None:
        # Extract data
        run_name_in_log_line = eval_match.group(1)
        iteration = int(eval_match.group(2))
        perturbation_type = eval_match.group(3) # 'p' or 'm'
        error_str = eval_match.group(4)
        # unit_str = eval_match.group(5).strip() # Unit string

        # Convert error to float
        try:
            error_value = float(error_str)
        except ValueError:
            print(f"Warning: Could not convert error value to float: '{error_str}' in line '{line}'. Skipping.")
            continue

        # Make sure the log line belongs to the current run
        if run_name_in_log_line == current_run_name:
            # Store the evaluation result for this iteration and perturbation type
            if iteration not in current_iteration_evals:
                current_iteration_evals[iteration] = {}
            current_iteration_evals[iteration][perturbation_type] = error_value
            # print(f"  Logged eval for {current_run_name} iter {iteration} ({perturbation_type}): {error_value}") # Debug print

# Store the evaluations for the very last run after the loop finishes
if current_run_name is not None and current_iteration_evals:
    run_iteration_eval_pairs[current_run_name] = current_iteration_evals


# Debug print: Check parsed data structure
print("\nParsed Log Data Structure (Iteration Evaluations):")
for run_name, iterations_data in run_iteration_eval_pairs.items():
    print(f"  Run: {run_name}, Number of iterations with eval pairs: {len(iterations_data)}")
    if iterations_data:
        # Print first few and last few iterations
        iter_keys = sorted(iterations_data.keys())
        print(f"    Iterations logged: {iter_keys[:5]} ... {iter_keys[-5:] if len(iter_keys)>5 else iter_keys}")
        # Example of data for an iteration
        first_iter_key = iter_keys[0]
        if first_iter_key in iterations_data:
            print(f"    Example data for iter {first_iter_key}: {iterations_data[first_iter_key]}")
print("-" * 30)


# --- Determine Error Unit for Plotting ---
# Check the unit string captured by the regex
error_unit = "%" # Default
# Iterate through evaluation points to find a unit
eval_log_pattern_unit_check = re.compile(r"^\s*Calculated RMSE for .*?:\s*[\d.]+?\s*([%m/s]*)$")
unit_found = False
for line in log_data.strip().split('\n'):
     unit_match = eval_log_pattern_unit_check.match(line)
     if unit_match:
          unit_str = unit_match.group(1).strip()
          if "%" in unit_str: error_unit = "%"
          elif "m/s" in unit_str.lower(): error_unit = "m/s" # Case insensitive for m/s
          unit_found = True
          break # Found a unit

if not unit_found:
    print("Warning: Could not definitively determine error unit from log lines. Assuming %.")

error_ylabel = f"min(y_p, y_m) ({error_unit})"


# --- 绘制每次迭代的 min(y_p, y_m) 图 (带点标记) ---
plt.figure(figsize=(10, 6))

# Sort run names for consistent plotting order
def sort_key(run_name):
    if run_name == "Run 1":
        return 0
    else:
        parts = run_name.split(" ")
        if len(parts) > 1 and parts[0] == "Restart":
             try:
                 return int(parts[1])
             except ValueError:
                 return len(run_iteration_eval_pairs)
        return len(run_iteration_eval_pairs)

sorted_run_names = sorted(run_iteration_eval_pairs.keys(), key=sort_key)

# Define a list of markers to cycle through for different runs
markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*'] # Circle, Square, Triangle_up, Diamond, etc.


MARKER_SIZE = 2 # <-- 定义你想要的标记大小，可以调整这个值

for i, run_name in enumerate(sorted_run_names):
    iterations_data = run_iteration_eval_pairs[run_name]
    if not iterations_data: continue

    iterations = sorted(iterations_data.keys())
    min_errors = []
    valid_iterations = []
    for iter_num in iterations:
        evals_this_iter = iterations_data[iter_num]
        if 'p' in evals_this_iter and 'm' in evals_this_iter:
            min_errors.append(min(evals_this_iter['p'], evals_this_iter['m']))
            valid_iterations.append(iter_num)
        elif 'p' in evals_this_iter:
             min_errors.append(evals_this_iter['p'])
             valid_iterations.append(iter_num)
        elif 'm' in evals_this_iter:
             min_errors.append(evals_this_iter['m'])
             valid_iterations.append(iter_num)


    # Plot the line with markers
    marker_style = markers[i % len(markers)]
    plt.plot(valid_iterations, min_errors,
             marker=marker_style,
             markersize=MARKER_SIZE, # <-- 在这里添加 markersize 参数
             linestyle='-',
             label=run_name)


plt.xlabel("Iteration (per run)")
plt.ylabel(error_ylabel)
plt.title("SPSA Calibration min(y_p, y_m) per Iteration (with markers)")
plt.grid(True)
plt.ylim(0.8, 2.2)
plt.legend()
plt.show()