#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试递归导入的主脚本"""

import numpy as np
import pandas as pd
from helper import plot_data, analyze_data

def main():
    """主函数"""
    # 设置随机种子以便结果可复现
    np.random.seed(42)
    
    # 创建示例数据
    n_samples = 300
    
    # 创建三类数据
    categories = ['A', 'B', 'C']
    data = []
    
    # 为每个类别生成不同的数据分布
    for i, category in enumerate(categories):
        x = np.random.normal(i * 3, 1.0, n_samples // 3)
        y = np.random.normal(i * 2, 1.5, n_samples // 3)
        for j in range(len(x)):
            data.append({
                'x': x[j], 
                'y': y[j],
                'category': category
            })
    
    # 转换为DataFrame
    df = pd.DataFrame(data)
    
    # 使用helper模块的函数绘制数据
    plot_data(df, title="多类别数据的散点图")
    
    # 分析数据
    stats = analyze_data(df)
    
    # 打印分析结果
    print("\n数据分析结果:")
    print("-------------")
    
    print("\n样本数量:")
    for category, count in stats['count'].items():
        print(f"  类别 {category}: {count}个样本")
    
    print("\nX轴平均值:")
    for category, mean in stats['mean_x'].items():
        print(f"  类别 {category}: {mean:.4f}")
    
    print("\nY轴平均值:")
    for category, mean in stats['mean_y'].items():
        print(f"  类别 {category}: {mean:.4f}")
    
    print("\nX轴标准差:")
    for category, std in stats['std_x'].items():
        print(f"  类别 {category}: {std:.4f}")
    
    print("\nY轴标准差:")
    for category, std in stats['std_y'].items():
        print(f"  类别 {category}: {std:.4f}")

if __name__ == "__main__":
    main() 