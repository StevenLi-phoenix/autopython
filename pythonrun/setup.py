#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import re
import os

# 从__init__.py中读取版本号
with open(os.path.join("pythonrun", "__init__.py"), "r", encoding="utf-8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pythonrun",
    version=version,
    author="lishuyu",
    author_email="premix-styles.7g@icloud.com",
    description="自动导入和安装Python模块的工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StevenLi-phoenix/pythonrun",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="import, package management, dependency, automation",
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "pythonrun=pythonrun.main:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/StevenLi-phoenix/pythonrun/issues",
        "Source": "https://github.com/StevenLi-phoenix/pythonrun",
    },
) 