#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试pythonrun处理器模块"""

import os
import sys
import tempfile
import unittest
import subprocess
from unittest.mock import patch, MagicMock

from pythonrun.processor import process_recursive_imports, process_file

class TestProcessor(unittest.TestCase):
    """测试处理器功能"""
    
    def setUp(self):
        """测试准备工作"""
        # 创建临时测试目录
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = self.temp_dir.name
        
        # 创建测试文件结构
        self.create_test_files()
    
    def tearDown(self):
        """测试清理工作"""
        self.temp_dir.cleanup()
    
    def create_test_files(self):
        """创建测试文件结构"""
        # 主测试文件
        self.main_file = os.path.join(self.test_dir, "main_test.py")
        with open(self.main_file, 'w') as f:
            f.write("""
            import os
            import sys
            import numpy as np
            from helper_test import helper_func
            
            def main():
                data = np.array([1, 2, 3])
                print(f"数据: {data}")
                print(f"辅助函数结果: {helper_func(data)}")
            
            if __name__ == "__main__":
                main()
            """)
        
        # 辅助测试文件
        self.helper_file = os.path.join(self.test_dir, "helper_test.py")
        with open(self.helper_file, 'w') as f:
            f.write("""
            import pandas as pd
            
            def helper_func(data):
                return pd.Series(data).mean()
            """)
        
        # 测试requirements.txt文件
        self.req_file = os.path.join(self.test_dir, "requirements.txt")
        with open(self.req_file, 'w') as f:
            f.write("""
            numpy>=1.20.0
            pandas>=1.2.0
            """)
    
    @patch('pythonrun.processor.get_package_for_module')
    @patch('pythonrun.processor.is_module_installed')
    def test_process_recursive_imports(self, mock_is_installed, mock_get_package):
        """测试递归处理导入"""
        # 模拟标准库已安装，其他模块未安装
        def is_installed_side_effect(module_name):
            return module_name in ('os', 'sys')
        
        # 模拟获取包名
        def get_package_side_effect(module_name, file_path=None):
            packages = {
                'numpy': 'numpy',
                'pandas': 'pandas'
            }
            return packages.get(module_name)
        
        mock_is_installed.side_effect = is_installed_side_effect
        mock_get_package.side_effect = get_package_side_effect
        
        # 测试递归导入处理
        packages = process_recursive_imports(self.main_file)
        
        # 验证结果
        self.assertIsInstance(packages, set)
        self.assertEqual(len(packages), 2)
        
        package_names = {pkg for _, pkg in packages}
        self.assertIn('numpy', package_names)
        self.assertIn('pandas', package_names)
        
        # 验证调用
        mock_is_installed.assert_any_call('numpy')
        mock_is_installed.assert_any_call('pandas')
    
    @patch('pythonrun.processor.check_and_install_requirements')
    @patch('pythonrun.processor.process_recursive_imports')
    @patch('pythonrun.processor.install_package')
    @patch('pythonrun.processor.load_config')
    @patch('subprocess.run')
    def test_process_file(self, mock_run, mock_load_config, mock_install,
                        mock_process_imports, mock_check_req):
        """测试文件处理功能"""
        # 模拟配置
        mock_load_config.return_value = {
            'auto_install': True,
            'check_requirements': True
        }
        
        # 模拟递归导入结果
        mock_process_imports.return_value = {
            ('numpy', 'numpy'),
            ('pandas', 'pandas')
        }
        
        # 模拟子进程运行
        mock_run.return_value = MagicMock(returncode=0)
        
        # 测试处理文件
        process_file(self.main_file)
        
        # 验证调用
        mock_check_req.assert_called_once_with(os.path.dirname(os.path.abspath(self.main_file)))
        mock_process_imports.assert_called_once_with(os.path.abspath(self.main_file))
        
        # 验证安装调用
        self.assertEqual(mock_install.call_count, 2)
        
        # 验证subprocess.run调用
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        cmd = args[0]
        self.assertEqual(cmd[0], sys.executable)  # Python解释器
        self.assertEqual(cmd[1], os.path.abspath(self.main_file))  # 脚本路径


if __name__ == '__main__':
    unittest.main() 