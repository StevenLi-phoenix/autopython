#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试pythonrun自动安装功能的示例脚本"""

import numpy as np
import matplotlib.pyplot as plt

def main():
    # 创建一些随机数据
    data = np.random.randn(1000)
    
    # 绘制直方图
    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    plt.title('正态分布直方图', fontsize=15)
    plt.xlabel('值', fontsize=12)
    plt.ylabel('频率', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # 保存图像
    plt.savefig('histogram.png')
    plt.close()
    
    print("已生成直方图并保存为histogram.png")
    
    # 计算一些统计量
    mean = np.mean(data)
    median = np.median(data)
    std = np.std(data)
    
    print(f"均值: {mean:.4f}")
    print(f"中位数: {median:.4f}")
    print(f"标准差: {std:.4f}")

if __name__ == "__main__":
    main() 