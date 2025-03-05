#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据可视化工具模块
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_distribution(data, column, title=None):
    """绘制单变量分布图"""
    plt.figure(figsize=(10, 6))
    
    if isinstance(data, pd.DataFrame) and column in data.columns:
        sns.histplot(data[column], kde=True)
        plt.title(title or f'{column}的分布')
    else:
        sns.histplot(data, kde=True)
        plt.title(title or '数据分布')
    
    plt.savefig('distribution.png')
    plt.close()
    
    return 'distribution.png'

def plot_correlation(df, title=None):
    """绘制相关性热图"""
    plt.figure(figsize=(12, 10))
    
    # 计算相关系数
    corr = df.corr()
    
    # 绘制热图
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
    plt.title(title or '相关性热图')
    
    plt.savefig('correlation.png')
    plt.close()
    
    return 'correlation.png'

def plot_scatter(df, x, y, hue=None, title=None):
    """绘制散点图"""
    plt.figure(figsize=(10, 8))
    
    # 绘制散点图
    sns.scatterplot(data=df, x=x, y=y, hue=hue)
    plt.title(title or f'{x} vs {y}')
    
    plt.savefig('scatter.png')
    plt.close()
    
    return 'scatter.png' 