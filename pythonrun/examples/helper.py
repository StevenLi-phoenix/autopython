#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""辅助模块，用于测试递归导入"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_data(data, title="数据可视化"):
    """绘制数据图表
    
    参数:
        data: pandas DataFrame，包含要绘制的数据
        title: 图表标题
    """
    # 创建图表
    plt.figure(figsize=(12, 8))
    
    # 使用seaborn绘制散点图
    sns.scatterplot(data=data, x='x', y='y', hue='category', palette='viridis', s=100)
    
    # 设置标题和标签
    plt.title(title, fontsize=16)
    plt.xlabel('X轴', fontsize=14)
    plt.ylabel('Y轴', fontsize=14)
    plt.grid(True, alpha=0.3)
    
    # 保存图表
    plt.savefig('scatterplot.png')
    plt.close()
    
    print("散点图已保存为scatterplot.png")
    
def analyze_data(data):
    """分析数据并返回统计结果
    
    参数:
        data: pandas DataFrame
    
    返回:
        统计结果的字典
    """
    # 分组计算统计量
    grouped = data.groupby('category')
    stats = {
        'count': grouped.count()['x'].to_dict(),
        'mean_x': grouped.mean()['x'].to_dict(),
        'mean_y': grouped.mean()['y'].to_dict(),
        'std_x': grouped.std()['x'].to_dict(),
        'std_y': grouped.std()['y'].to_dict(),
    }
    
    return stats 