#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辅助模块，用于测试递归导入功能
"""

# 导入需要自动安装的库
import matplotlib.pyplot as plt
import seaborn as sns

def plot_data(df):
    """绘制数据图表
    
    参数:
        df: 包含x和y列的DataFrame
    """
    print("正在绘制数据...")
    
    # 设置样式
    sns.set_style('whitegrid')
    
    # 绘制散点图
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='x', y='y', data=df)
    
    # 添加标题和标签
    plt.title('测试数据可视化')
    plt.xlabel('X 轴')
    plt.ylabel('Y 轴')
    
    # 保存图表
    plt.savefig('example_plot.png')
    
    print("图表已保存为 example_plot.png") 