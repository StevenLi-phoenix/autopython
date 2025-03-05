#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pythonrun - 自动导入和安装Python模块的工具
"""

import os
import sys
import logging
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pythonrun')

# 是否启用调试模式
DEBUG_MODE = os.environ.get('PYTHONRUN_DEBUG', '').lower() in ('1', 'true', 'yes')
if DEBUG_MODE:
    logger.setLevel(logging.DEBUG)

from .processor import process_file

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: pythonrun <script.py> [arg1 arg2 ...]")
        return
    
    file_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    # 处理文件
    process_file(file_path)

if __name__ == "__main__":
    main() 