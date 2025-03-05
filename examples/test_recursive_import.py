#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试递归导入功能的示例文件
"""

# 导入需要自动安装的库
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_data(df):
    """绘制数据图表"""
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

def main():
    """主函数"""
    print("测试递归导入功能")
    
    # 创建一些测试数据
    data = np.random.randn(100, 2)
    df = pd.DataFrame(data, columns=['x', 'y'])
    print(f"创建了数据: {df.shape}")
    
    # 使用导入的函数
    plot_data(df)

if __name__ == "__main__":
    main() 