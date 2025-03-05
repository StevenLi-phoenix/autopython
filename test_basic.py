#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试pythonrun基本功能的脚本"""

import os
import sys

def main():
    print("测试pythonrun基本功能")
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"脚本路径: {__file__}")
    print(f"命令行参数: {sys.argv}")
    print("测试成功!")

if __name__ == "__main__":
    main() 