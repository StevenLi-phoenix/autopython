#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
autopython 简单示例脚本
"""

# 导入一些常用库
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# 创建一些随机数据
data = np.random.randn(100)
dates = pd.date_range('20250101', periods=100)
df = pd.DataFrame({'value': data}, index=dates)

# 绘制图形
plt.figure(figsize=(10, 6))
plt.plot(df.index, df['value'], label='随机数据')
plt.title('使用autopython自动安装依赖的示例')
plt.xlabel('日期')
plt.ylabel('值')
plt.legend()
plt.grid(True)
plt.tight_layout()

# 保存和显示
plt.savefig('example_plot.png')
print(f"图形已保存为 example_plot.png")
print(f"数据统计信息:\n{df.describe()}")

# 显示前5行数据
print("\n数据前5行:")
print(df.head()) 