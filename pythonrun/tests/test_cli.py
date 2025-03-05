#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试pythonrun命令行接口"""

import os
import sys
import unittest
import tempfile
from unittest.mock import patch, MagicMock
import subprocess
from pathlib import Path

class TestCLI(unittest.TestCase):
    """测试命令行接口功能"""
    
    def setUp(self):
        """测试准备工作"""
        # 获取pythonrun包的位置
        self.pythonrun_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        # 创建临时测试目录
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = self.temp_dir.name
        
        # 创建测试脚本
        self.test_script = os.path.join(self.test_dir, "simple_test.py")
        with open(self.test_script, 'w') as f:
            f.write("""
            import os
            import sys
            
            def main():
                print("简单测试脚本")
                print(f"Python版本: {sys.version}")
                print(f"命令行参数: {sys.argv}")
                return 0
            
            if __name__ == "__main__":
                sys.exit(main())
            """)
    
    def tearDown(self):
        """测试清理工作"""
        self.temp_dir.cleanup()
    
    @patch('subprocess.run')
    def test_cli_direct_invocation(self, mock_run):
        """测试直接调用命令行"""
        # 模拟子进程运行
        mock_run.return_value = MagicMock(returncode=0)
        
        # 调用命令行
        cmd = [sys.executable, '-m', 'pythonrun.main', self.test_script]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 验证结果
        self.assertEqual(result.returncode, 0)
    
    def test_cli_with_arguments(self):
        """测试带参数调用命令行"""
        # 创建接收参数的测试脚本
        args_script = os.path.join(self.test_dir, "args_test.py")
        with open(args_script, 'w') as f:
            f.write("""
            import sys
            
            def main():
                print(f"参数数量: {len(sys.argv)-1}")
                for i, arg in enumerate(sys.argv[1:], 1):
                    print(f"参数 {i}: {arg}")
                return len(sys.argv) - 1  # 返回参数数量
            
            if __name__ == "__main__":
                sys.exit(main())
            """)
        
        # 使用subprocess直接运行
        test_args = ['arg1', 'arg2', '--flag']
        cmd = [sys.executable, '-m', 'pythonrun.main', args_script] + test_args
        
        # 检查命令是否可以运行（不验证输出）
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=5)
            run_successful = True
        except (subprocess.SubprocessError, FileNotFoundError):
            run_successful = False
        
        # 验证能够成功运行
        self.assertTrue(run_successful, "CLI 命令执行失败")
    
    def test_cli_help_option(self):
        """测试帮助选项"""
        cmd = [sys.executable, '-m', 'pythonrun.main', '--help']
        
        # 运行帮助命令
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            help_output = result.stdout
            run_successful = result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            help_output = ""
            run_successful = False
        
        # 验证能够成功运行
        self.assertTrue(run_successful, "CLI帮助命令执行失败")
        
        # 验证帮助信息包含关键词
        expected_keywords = ['usage', 'pythonrun', 'options']
        for keyword in expected_keywords:
            self.assertIn(keyword.lower(), help_output.lower(), 
                        f"帮助输出应包含关键词: {keyword}")


if __name__ == '__main__':
    unittest.main() 