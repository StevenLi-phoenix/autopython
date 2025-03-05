#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
这是一个测试sklearn模块导入的示例脚本。
sklearn模块实际对应的包名是scikit-learn，这是一个需要特殊处理的例子。
"""

import numpy as np
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# 加载示例数据集
iris = datasets.load_iris()
X, y = iris.data, iris.target

# 拆分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 训练随机森林模型
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 预测并评估模型
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("测试sklearn自动安装功能")
print(f"使用的模块: sklearn")
print(f"实际需要安装的包: scikit-learn")
print(f"模型准确率: {accuracy:.4f}")
print("\n如果成功运行，说明autopython能够正确识别并安装sklearn对应的scikit-learn包。") 