"""代码分析模块，处理导入解析和代码修改"""

import os
import ast
import re
import logging
from typing import List, Set, Dict, Optional, Tuple, Any

from .package_manager import is_local_module, is_stdlib_module

logger = logging.getLogger('pythonrun')

def parse_imports(code: str) -> List[Tuple[str, Optional[str]]]:
    """解析代码中的导入语句，返回所有导入的模块名
    
    参数:
        code: Python代码字符串
    
    返回: 
        [(模块名, 别名), ...]
    """
    modules = []
    
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            # 处理 import X 格式
            if isinstance(node, ast.Import):
                for name in node.names:
                    # 排除特定的本地模块
                    if name.name not in ['helper_module']:
                        modules.append((name.name, name.asname))
            
            # 处理 from X import Y 格式
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0:  # 不处理相对导入
                    module_name = node.module
                    if module_name and module_name not in ['helper_module']:
                        # 只添加主模块名，不添加子模块
                        main_module = module_name.split('.')[0]
                        modules.append((main_module, None))
    except SyntaxError as e:
        logger.error(f"解析代码时遇到语法错误: {e}")
    
    return modules

def find_local_imports(code: str, file_path: str) -> List[str]:
    """查找代码中导入的本地模块
    
    参数:
        code: Python代码字符串
        file_path: 当前代码文件的路径
        
    返回:
        本地模块路径列表
    """
    if not file_path or not code:
        return []
    
    # 解析导入语句
    imports = parse_imports(code)
    
    # 查找当前目录
    current_dir = os.path.dirname(os.path.abspath(file_path))
    
    local_modules = []
    for module_name, _ in imports:
        # 跳过标准库
        if is_stdlib_module(module_name):
            continue
        
        # 只处理基础模块名
        base_module = module_name.split('.')[0]
        
        # 检查是否是本地模块
        if is_local_module(base_module, file_path):
            # 检查.py文件
            py_path = os.path.join(current_dir, f"{base_module}.py")
            if os.path.exists(py_path):
                local_modules.append(py_path)
                continue
            
            # 检查包目录
            pkg_path = os.path.join(current_dir, base_module)
            pkg_init = os.path.join(pkg_path, "__init__.py")
            if os.path.exists(pkg_path) and os.path.isdir(pkg_path) and os.path.exists(pkg_init):
                local_modules.append(pkg_init)
                continue
            
            # 检查其他可能的Python路径
            for path in [p for p in os.sys.path if 'site-packages' not in p]:
                py_path = os.path.join(path, f"{base_module}.py")
                if os.path.exists(py_path):
                    local_modules.append(py_path)
                    break
                
                pkg_path = os.path.join(path, base_module)
                pkg_init = os.path.join(pkg_path, "__init__.py")
                if os.path.exists(pkg_path) and os.path.isdir(pkg_path) and os.path.exists(pkg_init):
                    local_modules.append(pkg_init)
                    break
    
    return local_modules

def modify_code_to_autoinstall(code: str, additional_packages: Set[Tuple[str, str]] = None, file_path: str = None) -> str:
    """修改代码，添加自动安装功能
    
    参数:
        code: 原始Python代码
        additional_packages: 额外需要安装的包 (模块名, 包名)
        file_path: 文件路径（用于日志）
    
    返回:
        修改后的代码
    """
    # 避免重复修改已经修改过的代码
    if "# 自动安装依赖 - 由pythonrun添加" in code:
        return code
    
    try:
        # 解析代码
        tree = ast.parse(code)
        
        imports = []
        main_block = None
        has_imports = False
        
        # 收集所有导入语句
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                has_imports = True
            
            # 检查是否有 if __name__ == "__main__" 块
            if (isinstance(node, ast.If) and 
                isinstance(node.test, ast.Compare) and
                isinstance(node.test.left, ast.Name) and 
                node.test.left.id == '__name__' and
                isinstance(node.test.comparators[0], ast.Constant) and
                node.test.comparators[0].value == '__main__'):
                main_block = node
        
        if not has_imports and not additional_packages:
            return code  # 没有导入语句，无需修改
        
        # 准备自动安装代码
        auto_install_code = """
# 自动安装依赖 - 由pythonrun添加
def _ensure_installed(packages):
    import importlib.util
    import subprocess
    import sys
    
    for module_name, package_name in packages:
        if package_name is None:
            continue
        
        is_installed = False
        try:
            # 检查模块是否已安装
            if importlib.util.find_spec(module_name):
                is_installed = True
        except (ImportError, ValueError):
            is_installed = False
        
        if not is_installed:
            print(f"正在安装依赖包: {package_name} (来自模块 {module_name})...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                print(f"安装成功: {package_name}")
            except Exception as e:
                print(f"安装 {package_name} 失败，请手动安装。错误: {e}")
                sys.exit(1)

# 检查依赖
_packages_to_check = [
"""
        
        # 添加导入的模块
        for module_name, alias in parse_imports(code):
            # 跳过标准库和本地模块
            if is_stdlib_module(module_name) or (file_path and is_local_module(module_name, file_path)):
                continue
            
            # 获取包名，可以是与模块名相同或者不同
            package_name = module_name
            auto_install_code += f'    ("{module_name}", "{package_name}"),\n'
        
        # 添加额外的包
        if additional_packages:
            for module_name, package_name in additional_packages:
                if package_name:  # 只添加有包名的模块
                    auto_install_code += f'    ("{module_name}", "{package_name}"),\n'
        
        auto_install_code += """
]
_ensure_installed(_packages_to_check)
"""
        
        # 如果有main块，在其前面添加自动安装代码
        if main_block:
            main_start = main_block.lineno - 1  # 转换为0索引
            new_code = code[:main_start] + auto_install_code + code[main_start:]
        else:
            # 否则，在所有导入语句之后添加
            # 尝试找到导入语句的最后位置
            import_end = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    import_end = max(import_end, node.end_lineno)
            
            if import_end > 0:
                # 找到导入语句块的末尾位置
                lines = code.split('\n')
                line_index = import_end
                while line_index < len(lines) and (not lines[line_index].strip() or lines[line_index].strip().startswith('#')):
                    line_index += 1
                
                # 在所有导入语句之后添加自动安装代码
                new_code = '\n'.join(lines[:line_index]) + auto_install_code + '\n'.join(lines[line_index:])
            else:
                # 没有找到导入语句的末尾，在代码开头添加
                new_code = auto_install_code + code
        
        return new_code
    except Exception as e:
        logger.error(f"修改代码添加自动安装功能失败: {e}")
        return code  # 发生错误时返回原始代码 