"""配置管理模块"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger('pythonrun')

# 配置文件路径
CONFIG_DIR = os.environ.get('PYTHONRUN_CONFIG_DIR', os.path.join(str(Path.home()), '.pythonrun'))
CONFIG_FILE = os.environ.get('PYTHONRUN_CONFIG_FILE', os.path.join(CONFIG_DIR, 'config.json'))

# 默认配置
DEFAULT_CONFIG = {
    'auto_install': False,    # 是否自动安装包
    'auto_update_pip': False, # 是否自动更新pip
    'check_requirements': True, # 是否检查requirements.txt文件
}

def load_config() -> Dict[str, Any]:
    """加载配置文件，如果不存在则创建默认配置"""
    try:
        # 检查配置目录是否存在，不存在则创建
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
            logger.info(f"创建配置目录: {CONFIG_DIR}")
        
        # 检查配置文件是否存在，不存在则创建默认配置
        if not os.path.exists(CONFIG_FILE):
            return first_run_setup()
        
        # 加载配置文件
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.debug(f"已加载配置: {config}")
            return config
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> None:
    """保存配置到文件"""
    try:
        # 确保配置目录存在
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        
        # 保存配置
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
            logger.debug(f"已保存配置: {config}")
    except Exception as e:
        logger.error(f"保存配置失败: {e}")

def first_run_setup() -> Dict[str, Any]:
    """首次运行设置向导"""
    print("欢迎使用 pythonrun！")
    print("这是您首次运行，请回答以下问题以完成初始设置：")
    
    config = DEFAULT_CONFIG.copy()
    
    # 询问是否自动安装缺少的包
    while True:
        answer = input("是否默认自动安装缺少的包？ (y/n): ").lower().strip()
        if answer in ('y', 'yes'):
            config['auto_install'] = True
            break
        elif answer in ('n', 'no'):
            config['auto_install'] = False
            break
        else:
            print("请输入 y 或 n")
    
    # 询问是否自动更新pip
    while True:
        answer = input("是否在检测到新版本时自动更新pip？ (y/n): ").lower().strip()
        if answer in ('y', 'yes'):
            config['auto_update_pip'] = True
            break
        elif answer in ('n', 'no'):
            config['auto_update_pip'] = False
            break
        else:
            print("请输入 y 或 n")
    
    # 保存配置
    save_config(config)
    print(f"配置已保存至: {CONFIG_FILE}")
    
    return config 