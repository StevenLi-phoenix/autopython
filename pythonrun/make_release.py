#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发布pythonrun包到PyPI的辅助脚本
"""

import os
import re
import subprocess
import argparse
import shutil
from pathlib import Path

# 解析命令行参数
parser = argparse.ArgumentParser(description='发布pythonrun包到PyPI')
parser.add_argument('--production', action='store_true', help='发布到生产PyPI而不是TestPyPI')
args = parser.parse_args()

# 确定当前版本
init_file = os.path.join('pythonrun', 'pythonrun', '__init__.py')
with open(init_file, 'r', encoding='utf-8') as f:
    content = f.read()
    match = re.search(r'__version__ = [\'"]([^\'"]+)[\'"]', content)
    if not match:
        raise ValueError(f"无法从{init_file}中提取版本号")
    current_version = match.group(1)

print(f"当前版本: {current_version}")

# 询问新版本
parts = current_version.split('.')
if len(parts) == 3:
    major, minor, patch = map(int, parts)
    suggested_version = f"{major}.{minor}.{patch + 1}"
else:
    suggested_version = f"{current_version}.1"

new_version = input(f"请输入新版本号 [{suggested_version}]: ") or suggested_version

# 更新版本号
with open(init_file, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(
    r'__version__ = [\'"]([^\'"]+)[\'"]',
    f'__version__ = "{new_version}"',
    content
)

with open(init_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"版本已更新为 {new_version}")

# 清理旧的构建文件
print("清理旧的构建文件...")
for dir_name in ['build', 'dist', '*.egg-info']:
    for path in Path('.').glob(dir_name):
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

# 构建包
print("构建包...")
subprocess.run(['python', '-m', 'build'], check=True)

# 上传到PyPI
print("上传到PyPI...")
if args.production:
    subprocess.run(['python', '-m', 'twine', 'upload', 'dist/*'], check=True)
    print(f"pythonrun {new_version} 已发布到 PyPI!")
else:
    subprocess.run([
        'python', '-m', 'twine', 'upload',
        '--repository-url', 'https://test.pypi.org/legacy/',
        'dist/*'
    ], check=True)
    print(f"pythonrun {new_version} 已发布到 TestPyPI!")
    print("安装测试: pip install --index-url https://test.pypi.org/simple/ pythonrun")

print("完成!") 