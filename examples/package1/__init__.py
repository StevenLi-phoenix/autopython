"""
测试包导入递归功能的示例包
"""

import sklearn
from sklearn.preprocessing import StandardScaler

def normalize_data(data):
    """标准化数据"""
    scaler = StandardScaler()
    return scaler.fit_transform(data) 