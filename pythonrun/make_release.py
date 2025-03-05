#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发布pythonrun包到PyPI的脚本"""

import os
import sys
import re
import subprocess
from pathlib import Path
import argparse

def update_version(release_type='patch'):
    """更新版本号
    
    参数:
        release_type: 'major', 'minor' 或 'patch'
    
    返回:
        新的版本号
    """
    # 读取当前版本
    with open("pythonrun/pythonrun/__init__.py", "r", encoding="utf-8") as f:
        content = f.read()
        version_match = re.search(r'__version__ = "(.*?)"', content)
        current_version = version_match.group(1)
    
    # 解析版本号
    major, minor, patch = map(int, current_version.split('.'))
    
    # 增加版本号
    if release_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif release_type == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    new_version = f"{major}.{minor}.{patch}"
    
    # 写回新版本号
    with open("pythonrun/pythonrun/__init__.py", "w", encoding="utf-8") as f:
        f.write(content.replace(current_version, new_version))
    
    print(f"版本从 {current_version} 更新到 {new_version}")
    return new_version

def clean_build_files():
    """清理构建文件"""
    dirs_to_remove = [
        "build",
        "dist",
        "pythonrun.egg-info",
        "pythonrun/pythonrun.egg-info",
    ]
    
    for dir_name in dirs_to_remove:
        try:
            if os.path.exists(dir_name):
                subprocess.run(["rm", "-rf", dir_name], check=True)
                print(f"已删除 {dir_name}")
        except Exception as e:
            print(f"删除 {dir_name} 时出错: {e}")

def build_package():
    """构建包"""
    try:
        subprocess.run([sys.executable, "-m", "build"], check=True)
        print("构建成功")
        return True
    except Exception as e:
        print(f"构建失败: {e}")
        return False

def publish_to_pypi(production=False):
    """发布到PyPI
    
    参数:
        production: 如果为True，发布到PyPI，否则发布到TestPyPI
    """
    try:
        if production:
            subprocess.run([
                sys.executable, "-m", "twine", "upload", "dist/*"
            ], check=True)
            print("成功发布到PyPI")
        else:
            subprocess.run([
                sys.executable, "-m", "twine", "upload", "--repository-url", 
                "https://test.pypi.org/legacy/", "dist/*"
            ], check=True)
            print("成功发布到TestPyPI")
        return True
    except Exception as e:
        print(f"发布失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="发布pythonrun包到PyPI")
    parser.add_argument('--production', action='store_true', help='发布到生产PyPI而不是TestPyPI')
    parser.add_argument('--release-type', choices=['major', 'minor', 'patch'], 
                        default='patch', help='版本升级类型')
    args = parser.parse_args()
    
    # 更新版本
    new_version = update_version(args.release_type)
    
    # 清理旧的构建文件
    clean_build_files()
    
    # 构建包
    if not build_package():
        return 1
    
    # 发布到PyPI
    if not publish_to_pypi(args.production):
        return 1
    
    print(f"pythonrun v{new_version} 发布完成!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 