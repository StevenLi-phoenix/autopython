#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试检测和安装requirements.txt功能的示例文件
"""

import os
import sys

def main():
    """主函数"""
    print("测试requirements.txt自动检测和安装功能")
    
    # 尝试导入requirements.txt中指定的包
    try:
        import numpy
        print(f"成功导入 numpy {numpy.__version__}")
    except ImportError:
        print("无法导入 numpy")
    
    try:
        import pandas
        print(f"成功导入 pandas {pandas.__version__}")
    except ImportError:
        print("无法导入 pandas")
    
    try:
        import matplotlib
        print(f"成功导入 matplotlib {matplotlib.__version__}")
    except ImportError:
        print("无法导入 matplotlib")
    
    try:
        import seaborn
        print(f"成功导入 seaborn {seaborn.__version__}")
    except ImportError:
        print("无法导入 seaborn")
    
    print("\n如果您看到所有包都成功导入，则表示requirements.txt检测和安装功能正常工作！")

if __name__ == "__main__":
    main() 