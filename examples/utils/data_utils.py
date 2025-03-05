#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理工具模块
"""

import pandas as pd
import numpy as np

def load_data(file_path):
    """加载数据文件"""
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {file_path}")

def process_data(df):
    """处理数据框"""
    # 移除缺失值
    df = df.dropna()
    
    # 标准化数值列
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        df[col] = (df[col] - df[col].mean()) / df[col].std()
    
    return df

def generate_sample_data(rows=100, cols=5):
    """生成样本数据"""
    data = np.random.randn(rows, cols)
    columns = [f'feature_{i}' for i in range(cols)]
    return pd.DataFrame(data, columns=columns) 