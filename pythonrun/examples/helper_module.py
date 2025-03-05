#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pythonrun示例：辅助模块，提供数据处理和可视化功能
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def process_data(df):
    """处理数据，计算相关性并添加随机噪声"""
    # 添加相关性噪声
    df['z'] = df['x'] * 0.5 + df['y'] * 0.3 + np.random.normal(0, 1, len(df))
    
    # 计算相关系数
    df['correlation'] = df['x'].corr(df['y'])
    
    return df

def visualize_data(df, output_file='plot.png'):
    """可视化数据"""
    # 设置样式
    sns.set_theme(style="whitegrid")
    
    # 创建图表
    plt.figure(figsize=(10, 8))
    
    # 绘制散点图和回归线
    sns.regplot(x='x', y='y', data=df, scatter_kws={'s': 80})
    
    # 添加标题和标签
    plt.title('数据相关性分析', fontsize=15)
    plt.xlabel('X变量', fontsize=12)
    plt.ylabel('Y变量', fontsize=12)
    
    # 保存图表
    output_path = os.path.join(os.getcwd(), output_file)
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    return output_path 