#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pythonrun示例：主文件导入辅助模块
"""

import os
import sys

# 导入pandas进行数据处理
import pandas as pd

# 导入本地模块
from helper_module import process_data, visualize_data

def main():
    """主函数"""
    print("创建示例数据...")
    
    # 创建示例数据
    data = {
        'x': [1, 2, 3, 4, 5],
        'y': [2, 4, 6, 8, 10]
    }
    df = pd.DataFrame(data)
    print("数据预览:")
    print(df)
    
    # 使用辅助模块处理数据
    processed_df = process_data(df)
    print("\n处理后的数据:")
    print(processed_df)
    
    # 可视化数据
    plot_file = visualize_data(processed_df, 'correlation.png')
    print(f"\n数据可视化已保存到: {plot_file}")
    
    print("\n示例运行完成!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 