#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试pythonrun工具函数"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

from pythonrun.utils.code_analyzer import parse_imports, find_local_imports
from pythonrun.utils.package_manager import get_package_for_module, is_module_installed

class TestCodeAnalyzer(unittest.TestCase):
    """测试代码分析器功能"""
    
    def test_parse_imports(self):
        """测试导入解析功能"""
        code = """
        import os
        import sys as system
        from pathlib import Path
        from numpy import array, zeros
        import matplotlib.pyplot as plt
        """
        
        imports = parse_imports(code)
        self.assertIsInstance(imports, list)
        
        # 检查是否找到了所有导入
        found_imports = [module for module, _ in imports]
        self.assertIn('os', found_imports)
        self.assertIn('sys', found_imports)
        self.assertIn('pathlib', found_imports)
        self.assertIn('numpy', found_imports)
        self.assertIn('matplotlib.pyplot', found_imports)
        
    def test_find_local_imports(self):
        """测试查找本地导入功能"""
        # 创建临时目录和文件结构
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建主测试文件
            main_file = os.path.join(temp_dir, "main.py")
            with open(main_file, 'w') as f:
                f.write("""
                import os
                import sys
                from helper import helper_func
                from utils.tools import tool_func
                """)
            
            # 创建helper.py
            helper_file = os.path.join(temp_dir, "helper.py")
            with open(helper_file, 'w') as f:
                f.write("""
                def helper_func():
                    pass
                """)
            
            # 创建utils目录和tools.py
            utils_dir = os.path.join(temp_dir, "utils")
            os.makedirs(utils_dir, exist_ok=True)
            tools_file = os.path.join(utils_dir, "tools.py")
            with open(tools_file, 'w') as f:
                f.write("""
                def tool_func():
                    pass
                """)
            
            # 测试查找本地导入
            local_imports = find_local_imports("""
            import os
            import sys
            from helper import helper_func
            from utils.tools import tool_func
            """, main_file)
            
            self.assertIn(helper_file, local_imports)
            self.assertIn(tools_file, local_imports)


class TestPackageManager(unittest.TestCase):
    """测试包管理器功能"""
    
    def test_is_module_installed(self):
        """测试模块安装检查功能"""
        # 标准库模块应该被识别为已安装
        self.assertTrue(is_module_installed('os'))
        self.assertTrue(is_module_installed('sys'))
        self.assertTrue(is_module_installed('pathlib'))
        
    def test_get_package_for_module(self):
        """测试获取模块对应的包名功能"""
        # 测试标准库
        self.assertIsNone(get_package_for_module('os'))
        self.assertIsNone(get_package_for_module('sys'))
        
        # 测试包名映射
        self.assertEqual(get_package_for_module('PIL'), 'pillow')
        self.assertEqual(get_package_for_module('sklearn'), 'scikit-learn')


if __name__ == '__main__':
    unittest.main() 