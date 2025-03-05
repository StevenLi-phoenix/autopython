#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试pythonrun配置功能"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, mock_open

# 假设配置模块位于pythonrun.utils.config
from pythonrun.utils.config import load_config, save_config

class TestConfig(unittest.TestCase):
    """测试配置功能"""
    
    def setUp(self):
        """测试准备工作"""
        # 创建临时目录
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = self.temp_dir.name
        
        # 默认配置
        self.default_config = {
            "auto_install": False,
            "check_requirements": True,
            "pip_index_url": None,
            "pip_extra_args": [],
            "log_level": "INFO"
        }
    
    def tearDown(self):
        """测试清理工作"""
        self.temp_dir.cleanup()
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_load_config_existing(self, mock_json_load, mock_file_open, mock_exists):
        """测试加载现有配置"""
        # 模拟配置文件存在
        mock_exists.return_value = True
        
        # 模拟配置内容
        test_config = {
            "auto_install": True,
            "check_requirements": False,
            "pip_index_url": "https://mirrors.aliyun.com/pypi/simple/",
            "pip_extra_args": ["--timeout", "30"],
            "log_level": "DEBUG"
        }
        mock_json_load.return_value = test_config
        
        # 加载配置
        config = load_config()
        
        # 验证结果
        self.assertEqual(config, test_config)
        mock_exists.assert_called_once()
        mock_file_open.assert_called_once()
        mock_json_load.assert_called_once()
    
    @patch('os.path.exists')
    def test_load_config_not_existing(self, mock_exists):
        """测试加载不存在的配置文件"""
        # 模拟配置文件不存在
        mock_exists.return_value = False
        
        # 加载配置
        config = load_config()
        
        # 验证返回默认配置
        self.assertIsInstance(config, dict)
        self.assertIn('auto_install', config)
        self.assertIn('check_requirements', config)
    
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_config(self, mock_json_dump, mock_file_open, mock_makedirs, mock_exists):
        """测试保存配置"""
        # 模拟目录不存在
        mock_exists.return_value = False
        
        # 测试配置
        test_config = {
            "auto_install": True,
            "check_requirements": False,
            "pip_index_url": "https://mirrors.aliyun.com/pypi/simple/",
            "log_level": "DEBUG"
        }
        
        # 保存配置
        save_config(test_config)
        
        # 验证调用
        mock_exists.assert_called_once()
        mock_makedirs.assert_called_once()
        mock_file_open.assert_called_once()
        mock_json_dump.assert_called_once()
        
        # 验证保存的参数
        args, kwargs = mock_json_dump.call_args
        saved_config = args[0]
        self.assertEqual(saved_config, test_config)
        self.assertEqual(kwargs.get('indent'), 4)
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_config_merging(self, mock_json_load, mock_file_open, mock_exists):
        """测试配置合并功能"""
        # 模拟配置文件存在
        mock_exists.return_value = True
        
        # 模拟配置内容 (缺少一些字段)
        partial_config = {
            "auto_install": True,
            "log_level": "DEBUG"
        }
        mock_json_load.return_value = partial_config
        
        # 加载配置
        config = load_config()
        
        # 验证结果
        self.assertEqual(config['auto_install'], True)
        self.assertEqual(config['log_level'], "DEBUG")
        
        # 应该包含默认值
        self.assertIn('check_requirements', config)
        self.assertIn('pip_index_url', config)
        self.assertIn('pip_extra_args', config)


if __name__ == '__main__':
    unittest.main() 