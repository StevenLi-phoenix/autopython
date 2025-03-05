#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试requirements.txt文件处理"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

def main():
    """主函数"""
    # 生成分类数据集
    X, y = make_classification(
        n_samples=1000, 
        n_features=10,
        n_informative=5,
        n_redundant=2,
        n_classes=3,
        random_state=42
    )
    
    # 分割数据集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    # 训练随机森林分类器
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # 预测和评估
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"模型准确率: {accuracy:.4f}\n")
    print("分类报告:")
    print(classification_report(y_test, y_pred))
    
    # 特征重要性可视化
    feature_importance = clf.feature_importances_
    indices = np.argsort(feature_importance)[::-1]
    
    plt.figure(figsize=(10, 6))
    plt.title("特征重要性")
    plt.bar(range(X.shape[1]), feature_importance[indices], align='center')
    plt.xticks(range(X.shape[1]), [f'特征 {i}' for i in indices])
    plt.xlim([-1, X.shape[1]])
    plt.tight_layout()
    plt.savefig('feature_importance.png')
    plt.close()
    
    print("特征重要性图已保存为feature_importance.png")

if __name__ == "__main__":
    main() 