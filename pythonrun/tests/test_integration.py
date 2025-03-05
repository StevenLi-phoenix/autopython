#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试pythonrun完整工作流程的集成测试"""

import os
import sys
import unittest
import tempfile
import subprocess
from pathlib import Path

class TestIntegration(unittest.TestCase):
    """集成测试类"""
    
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
        self.main_file = os.path.join(self.test_dir, "integration_test.py")
        with open(self.main_file, 'w') as f:
            f.write("""
            #!/usr/bin/env python
            # -*- coding: utf-8 -*-
            \"\"\"集成测试主脚本\"\"\"
            
            import os
            import sys
            import json
            from pathlib import Path
            
            # 导入可能需要安装的模块
            import requests
            
            # 导入本地模块
            from integration_utils import get_system_info
            
            def main():
                \"\"\"主函数\"\"\"
                print("集成测试脚本运行中...")
                
                # 获取系统信息
                system_info = get_system_info()
                print(f"系统信息: {json.dumps(system_info, indent=2, ensure_ascii=False)}")
                
                # 使用requests获取一些数据
                try:
                    response = requests.get("https://httpbin.org/get", timeout=5)
                    data = response.json()
                    print(f"HTTP请求成功: {data.get('url')}")
                except Exception as e:
                    print(f"HTTP请求失败: {e}")
                
                return 0
            
            if __name__ == "__main__":
                sys.exit(main())
            """)
        
        # 工具模块
        utils_file = os.path.join(self.test_dir, "integration_utils.py")
        with open(utils_file, 'w') as f:
            f.write("""
            #!/usr/bin/env python
            # -*- coding: utf-8 -*-
            \"\"\"集成测试工具模块\"\"\"
            
            import os
            import sys
            import platform
            
            def get_system_info():
                \"\"\"获取系统信息\"\"\"
                info = {
                    "python_version": sys.version,
                    "platform": platform.platform(),
                    "system": platform.system(),
                    "python_path": sys.executable,
                    "cwd": os.getcwd()
                }
                return info
            """)
        
        # requirements.txt文件
        req_file = os.path.join(self.test_dir, "requirements.txt")
        with open(req_file, 'w') as f:
            f.write("""
            # 测试依赖
            requests>=2.25.0
            """)
    
    def test_full_workflow(self):
        """测试完整工作流程"""
        # 切换到测试目录
        original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        try:
            # 运行集成测试脚本
            cmd = [sys.executable, '-m', 'pythonrun.main', 'integration_test.py']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            # 输出结果以便于调试
            print("\n集成测试输出:")
            print("-" * 40)
            print(result.stdout)
            if result.stderr:
                print("\n错误输出:")
                print("-" * 40)
                print(result.stderr)
            
            # 验证执行成功
            self.assertEqual(result.returncode, 0, "集成测试应当成功执行")
            
            # 验证关键输出
            expected_outputs = [
                "集成测试脚本运行中",
                "系统信息",
                "HTTP请求成功"
            ]
            
            for expected in expected_outputs:
                self.assertIn(expected, result.stdout, 
                            f"输出应包含: {expected}")
            
        finally:
            # 恢复原目录
            os.chdir(original_dir)


if __name__ == '__main__':
    unittest.main() 