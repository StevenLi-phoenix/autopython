#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分类器模块
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

def train_model(X, y, test_size=0.3, random_state=42):
    """
    训练随机森林分类器
    
    参数:
        X: 特征矩阵
        y: 目标变量
        test_size: 测试集比例
        random_state: 随机种子
        
    返回:
        模型、准确率和分类报告
    """
    # 分割数据集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    # 创建并训练模型
    model = RandomForestClassifier(n_estimators=100, random_state=random_state)
    model.fit(X_train, y_train)
    
    # 预测
    y_pred = model.predict(X_test)
    
    # 评估性能
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    
    return model, accuracy, report 