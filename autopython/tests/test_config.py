#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试配置功能
"""
import os
import unittest
import tempfile
import json
from unittest.mock import patch
from pathlib import Path
import sys
import importlib

# 临时修改sys.path以导入autopython模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入模块
from autopython.main import load_config, save_config, first_run_setup, DEFAULT_CONFIG

class TestConfig(unittest.TestCase):
    """测试配置功能"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录用于测试
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = os.path.join(self.temp_dir.name, '.autopython')
        self.config_file = os.path.join(self.config_dir, 'config.json')
        
        # 备份原始路径
        self.original_config_dir = os.environ.get('AUTOPYTHON_CONFIG_DIR')
        self.original_config_file = os.environ.get('AUTOPYTHON_CONFIG_FILE')
        
        # 设置测试环境
        os.environ['AUTOPYTHON_CONFIG_DIR'] = self.config_dir
        os.environ['AUTOPYTHON_CONFIG_FILE'] = self.config_file
        
        # 确保配置目录存在
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 重新加载模块以确保使用新的环境变量
        importlib.reload(sys.modules['autopython.main'])
    
    def tearDown(self):
        """测试后清理"""
        # 恢复原始环境
        if self.original_config_dir:
            os.environ['AUTOPYTHON_CONFIG_DIR'] = self.original_config_dir
        else:
            os.environ.pop('AUTOPYTHON_CONFIG_DIR', None)
            
        if self.original_config_file:
            os.environ['AUTOPYTHON_CONFIG_FILE'] = self.original_config_file
        else:
            os.environ.pop('AUTOPYTHON_CONFIG_FILE', None)
        
        # 清理临时目录
        self.temp_dir.cleanup()
    
    def test_save_and_load_config(self):
        """测试保存和加载配置"""
        test_config = {
            'auto_install': True,
            'auto_update_pip': False
        }
        
        # 保存配置
        save_config(test_config)
        
        # 验证文件存在
        self.assertTrue(os.path.exists(self.config_file))
        
        # 验证文件内容
        with open(self.config_file, 'r') as f:
            saved_config = json.load(f)
        
        self.assertEqual(saved_config, test_config)
        
        # 测试加载配置
        loaded_config = load_config()
        self.assertEqual(loaded_config, test_config)
    
    @patch('builtins.input', side_effect=['y', 'n'])
    def test_first_run_setup(self, mock_input):
        """测试首次运行设置"""
        # 运行首次设置
        config = first_run_setup()
        
        # 验证配置值
        self.assertTrue(config['auto_install'])
        self.assertFalse(config['auto_update_pip'])
        
        # 验证询问了正确的问题
        self.assertEqual(mock_input.call_count, 2)

if __name__ == "__main__":
    unittest.main() 