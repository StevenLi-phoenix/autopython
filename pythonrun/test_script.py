#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pythonrun测试脚本，用于测试自动安装功能
此脚本尝试导入一些常见的第三方库
"""

import sys
import os

print("Python版本:", sys.version)
print("运行环境:", os.environ.get('VIRTUAL_ENV', '系统Python'))

try:
    import numpy as np
    print("成功导入 numpy:", np.__version__)
    
    # 创建一个随机数组
    arr = np.random.rand(5, 5)
    print("随机数组示例:\n", arr)
except ImportError as e:
    print("无法导入 numpy:", e)

try:
    import matplotlib.pyplot as plt
    print("成功导入 matplotlib:", plt.matplotlib.__version__)
    
    # 创建一个简单的图表
    plt.figure(figsize=(8, 6))
    plt.plot(np.random.rand(10))
    plt.title('随机数据测试图')
    plt.savefig('test_plot.png')
    print("图表已保存为 test_plot.png")
    plt.close()
except ImportError as e:
    print("无法导入 matplotlib:", e)

print("\n测试完成!") 