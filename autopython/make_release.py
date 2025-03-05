#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建和发布autopython包到PyPI的脚本
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = [
        "dist",
        "build",
        "*.egg-info",
    ]
    
    print("清理旧的构建文件...")
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"已删除: {path}")
            else:
                path.unlink()
                print(f"已删除: {path}")

def run_tests():
    """运行测试"""
    print("\n运行测试...")
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print("测试失败！")
        print(result.stdout)
        print(result.stderr)
        return False
    
    print("测试通过！")
    return True

def build_package():
    """构建包"""
    print("\n构建包...")
    result = subprocess.run([sys.executable, "-m", "build"], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print("构建失败！")
        print(result.stdout)
        print(result.stderr)
        return False
    
    print("构建成功！")
    return True

def upload_to_pypi(test=True):
    """上传到PyPI"""
    if test:
        print("\n上传到TestPyPI...")
        cmd = [sys.executable, "-m", "twine", "upload", "--repository-url", "https://test.pypi.org/legacy/", "dist/*"]
    else:
        print("\n上传到PyPI...")
        cmd = [sys.executable, "-m", "twine", "upload", "dist/*"]
    
    print(f"运行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("上传失败！")
        print(result.stdout)
        print(result.stderr)
        return False
    
    print("上传成功！")
    return True

def main():
    """主函数"""
    # 确保我们在正确的目录
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # 解析命令行参数
    test_pypi = True
    if len(sys.argv) > 1 and sys.argv[1] == "--production":
        test_pypi = False
    
    # 清理旧的构建文件
    clean_build_dirs()
    
    # 运行测试
    if not run_tests():
        sys.exit(1)
    
    # 构建包
    if not build_package():
        sys.exit(1)
    
    # 上传到PyPI
    if not upload_to_pypi(test=test_pypi):
        sys.exit(1)
    
    # 提示下一步
    if test_pypi:
        print("\n发布到TestPyPI成功！")
        print("可以使用以下命令进行安装测试：")
        print("pip install --index-url https://test.pypi.org/simple/ autopython")
        print("\n如果测试无问题，可以发布到正式PyPI：")
        print("python make_release.py --production")
    else:
        print("\n发布到PyPI成功！")
        print("可以使用以下命令进行安装：")
        print("pip install autopython")

if __name__ == "__main__":
    main() 