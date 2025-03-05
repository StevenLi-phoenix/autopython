#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导入本地模块的递归导入功能
"""

# 导入本地模块，utils.py中导入了pandas和matplotlib等库
import os
import sys

# 明确指定导入路径并使用绝对导入
examples_dir = os.path.abspath(os.path.dirname(__file__) if '__file__' in globals() else os.path.abspath('examples'))
sys.path.insert(0, examples_dir)  # 确保本地模块优先

# 使用相对导入路径
from examples.utils import data_utils, viz_utils

def main():
    """主函数"""
    print("测试本地模块的递归导入功能")
    
    # 通过utils中的函数创建数据
    print("生成数据...")
    data = data_utils.generate_sample_data(rows=100, cols=5)
    print(f"数据形状: {data.shape}")
    
    # 使用utils中的可视化函数
    print("绘制相关性矩阵...")
    correlation_file = viz_utils.plot_correlation(data, title="测试数据相关性")
    print(f"相关性矩阵已保存为: {correlation_file}")
    
    print("\n递归导入功能测试完成。")
    print("如果成功运行，说明autopython能够正确找到并安装utils模块中导入的所有依赖包。")

if __name__ == "__main__":
    main() 