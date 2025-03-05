#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试autopython的核心功能"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# 将代码目录添加到路径中
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入要测试的函数
from autopython.main import (
    parse_imports, 
    get_package_for_module, 
    is_stdlib_module,
    is_local_module,
    levenshtein_distance,
    PACKAGE_MAPPING
)

def test_parse_imports():
    """测试导入解析功能"""
    code = """
import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
from os import path
from typing import List, Dict
import sys
    """
    
    imports = parse_imports(code)
    # 检查解析结果
    assert ('numpy', 'np') in imports
    assert ('pandas', None) in imports
    assert ('matplotlib.pyplot', 'plt') in imports
    assert ('os', None) in imports
    assert ('typing', None) in imports
    assert ('sys', None) in imports

def test_is_stdlib_module():
    """测试标准库检测功能"""
    assert is_stdlib_module('os')
    assert is_stdlib_module('sys')
    assert is_stdlib_module('json')
    assert not is_stdlib_module('numpy')
    assert not is_stdlib_module('pandas')
    assert not is_stdlib_module('matplotlib')

def test_package_mapping():
    """测试特殊包名映射功能"""
    # 验证常见的映射关系
    assert 'pillow' == PACKAGE_MAPPING.get('PIL')
    assert 'scikit-learn' == PACKAGE_MAPPING.get('sklearn')
    assert 'opencv-python' == PACKAGE_MAPPING.get('cv2')
    assert 'beautifulsoup4' == PACKAGE_MAPPING.get('bs4')

@patch('autopython.main.importlib.metadata.distribution')
def test_get_package_for_module(mock_distribution):
    """测试根据模块名获取包名功能"""
    # 模拟importlib.metadata的行为
    mock_distribution.side_effect = lambda name: MagicMock(metadata={'Name': name})
    
    # 测试PACKAGE_MAPPING中存在的映射
    assert get_package_for_module('sklearn') == 'scikit-learn'
    assert get_package_for_module('PIL') == 'pillow'
    
    # 测试未映射的普通模块，会返回模块本身的名称
    assert get_package_for_module('requests') == 'requests'
    assert get_package_for_module('pytest') == 'pytest'

def test_levenshtein_distance():
    """测试编辑距离计算"""
    assert levenshtein_distance('kitten', 'sitting') == 3
    assert levenshtein_distance('hello', 'hallo') == 1
    assert levenshtein_distance('python', 'python') == 0
    
    # 相似包名测试
    assert levenshtein_distance('sklearn', 'scikit-learn') > 0
    assert levenshtein_distance('numpy', 'numby') == 1
    assert levenshtein_distance('tensorflow', 'tesnorflow') == 2

if __name__ == '__main__':
    pytest.main(['-v', __file__]) 