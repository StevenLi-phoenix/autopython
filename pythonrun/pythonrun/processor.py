"""核心处理器模块，负责处理文件和递归导入"""

import os
import sys
import tempfile
import logging
from typing import Set, Tuple, Dict, Any, List, Optional
import importlib.util

from .utils.package_manager import (
    get_package_for_module, install_package, is_module_installed,
    check_and_install_requirements
)
from .utils.code_analyzer import (
    parse_imports, find_local_imports, modify_code_to_autoinstall
)
from .utils.config import load_config

logger = logging.getLogger('pythonrun')

def process_recursive_imports(file_path: str, processed_files: Set[str] = None) -> Set[Tuple[str, str]]:
    """递归处理Python文件的导入，返回所有需要安装的包
    
    参数:
        file_path: 要处理的Python文件路径
        processed_files: 已处理的文件集合，避免循环导入
        
    返回:
        需要安装的包集合 (模块名, 包名)
    """
    if processed_files is None:
        processed_files = set()
    
    # 防止重复处理
    if file_path in processed_files:
        return set()
    
    processed_files.add(file_path)
    
    # 读取文件内容
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        logger.error(f"读取文件 {file_path} 失败: {e}")
        return set()
    
    # 解析导入
    imports = parse_imports(code)
    packages_to_install = set()
    
    # 处理每个导入
    for module_name, _ in imports:
        # 获取要安装的包名
        package_name = get_package_for_module(module_name, file_path)
        
        # 检查是否需要安装
        if package_name and not is_module_installed(module_name):
            packages_to_install.add((module_name, package_name))
    
    # 查找并处理本地导入
    local_imports = find_local_imports(code, file_path)
    for local_module in local_imports:
        # 递归处理
        sub_packages = process_recursive_imports(local_module, processed_files)
        packages_to_install.update(sub_packages)
    
    return packages_to_install

def handle_main_problem(file_path: str) -> None:
    """处理 __name__ == "__main__" 的情况
    
    参数:
        file_path: 要处理的Python文件路径
    """
    try:
        # 读取原始文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp:
            temp_path = temp.name
            
            # 修改内容，添加自动安装代码
            modified_code = modify_code_to_autoinstall(content, None, file_path)
            temp.write(modified_code.encode('utf-8'))
        
        # 执行临时文件
        logger.info(f"运行修改后的脚本: {file_path}")
        
        # 构建命令行参数
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else []
        
        # 保存当前参数，设置新的参数
        old_argv = sys.argv.copy()
        sys.argv = [temp_path] + cmd_args
        
        # 执行代码
        with open(temp_path, 'r', encoding='utf-8') as f:
            exec(f.read(), {'__name__': '__main__', '__file__': temp_path})
        
        # 恢复参数
        sys.argv = old_argv
    except Exception as e:
        logger.error(f"执行 {file_path} 失败: {e}")
    finally:
        # 删除临时文件
        try:
            if 'temp_path' in locals():
                os.unlink(temp_path)
        except:
            pass

def process_file(file_path: str, run: bool = True) -> None:
    """处理Python文件，安装依赖并运行
    
    参数:
        file_path: 要处理的Python文件路径
        run: 是否执行文件
    """
    # 加载配置
    config = load_config()
    
    # 绝对路径
    abs_path = os.path.abspath(file_path)
    
    # 检查requirements.txt文件
    if config.get('check_requirements', True):
        check_and_install_requirements(os.path.dirname(abs_path))
    
    # 处理递归导入
    logger.info(f"处理文件: {file_path}")
    packages_to_install = process_recursive_imports(abs_path)
    
    # 如果启用了自动安装，安装缺少的包
    if config.get('auto_install', False) and packages_to_install:
        for module_name, package_name in packages_to_install:
            logger.info(f"安装依赖包: {package_name} (从模块 {module_name})")
            install_package(package_name, module_name)
    
    # 如果发现需要安装的包但未启用自动安装，提示用户
    elif packages_to_install:
        logger.info("检测到缺少的依赖包:")
        for module_name, package_name in packages_to_install:
            logger.info(f"  {package_name} (从模块 {module_name})")
        
        while True:
            answer = input("是否安装这些依赖包？ (y/n): ").lower().strip()
            if answer in ('y', 'yes'):
                for module_name, package_name in packages_to_install:
                    install_package(package_name, module_name)
                break
            elif answer in ('n', 'no'):
                logger.info("跳过安装依赖包，可能导致运行失败")
                break
            else:
                print("请输入 y 或 n")
    
    # 如果需要运行代码
    if run:
        handle_main_problem(abs_path) 