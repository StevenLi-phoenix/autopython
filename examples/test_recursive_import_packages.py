#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导入Python包的递归导入功能
"""

# 导入本地包
import os
import sys

# 明确指定导入路径
examples_dir = os.path.abspath(os.path.dirname(__file__) if '__file__' in globals() else os.path.abspath('examples'))
sys.path.insert(0, examples_dir)  # 确保本地模块优先

# 导入包（包含了对其他库的导入，如sklearn）
import package1
from package1.subpackage import train_model

def main():
    """主函数"""
    print("测试Python包的递归导入功能")
    
    # 创建样本数据
    import numpy as np
    X = np.random.randn(100, 4)  # 特征
    y = np.random.randint(0, 2, 100)  # 二分类标签
    
    # 使用package1中的函数
    print("标准化数据...")
    X_normalized = package1.normalize_data(X)
    print(f"标准化数据形状: {X_normalized.shape}")
    
    # 使用subpackage中的函数
    print("训练模型...")
    model, accuracy, report = train_model(X_normalized, y)
    print(f"模型准确率: {accuracy:.4f}")
    print("分类报告:")
    print(report)
    
    print("\nPython包递归导入功能测试完成。")
    print("如果成功运行，说明autopython能够正确找到并安装Python包中导入的所有依赖包。")

if __name__ == "__main__":
    main() 