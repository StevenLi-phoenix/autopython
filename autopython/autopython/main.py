#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
autopython - 自动导入和安装Python模块的工具
"""

import os
import sys
import ast
import re
import importlib
import subprocess
import logging
import tempfile
import json
from typing import List, Set, Dict, Optional, Tuple, Any
from pathlib import Path
import site

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('autopython')

# 是否启用调试模式
DEBUG_MODE = os.environ.get('AUTOPYTHON_DEBUG', '').lower() in ('1', 'true', 'yes')
if DEBUG_MODE:
    logger.setLevel(logging.DEBUG)

# 配置文件路径
CONFIG_DIR = os.environ.get('AUTOPYTHON_CONFIG_DIR', os.path.join(str(Path.home()), '.autopython'))
CONFIG_FILE = os.environ.get('AUTOPYTHON_CONFIG_FILE', os.path.join(CONFIG_DIR, 'config.json'))

# 标准库列表
STDLIB_MODULES = set(sys.builtin_module_names)
STDLIB_MODULES.update([
    'abc', 'argparse', 'asyncio', 'base64', 'collections', 'copy', 'datetime',
    'functools', 'hashlib', 'http', 'io', 'itertools', 'json', 'logging', 'math', 
    'os', 'pickle', 'random', 're', 'shutil', 'socket', 'sys', 'tempfile', 
    'threading', 'time', 'traceback', 'urllib', 'warnings', 'zipfile'
])

# 包与模块的映射关系，有些模块名与包名不同
PACKAGE_MAPPING = {
    'PIL': 'pillow',
    'cv2': 'opencv-python',
    'sklearn': 'scikit-learn',
    'bs4': 'beautifulsoup4',
    'yaml': 'pyyaml',
    'Image': 'pillow',
    'tkinter': None,  # 标准库但可能需要额外安装
    'matplotlib.pyplot': 'matplotlib',
    'numpy.linalg': 'numpy',
    'pandas.DataFrame': 'pandas',
    'tensorflow.keras': 'tensorflow',
    'torch.nn': 'torch',
    'transformers': 'transformers',
    'seaborn': 'seaborn',
    'plotly.express': 'plotly',
    'dash': 'dash',
    'requests': 'requests',
    'flask': 'flask',
    'django': 'django',
    'sqlalchemy': 'sqlalchemy',
    'scipy': 'scipy',
    'nltk': 'nltk',
    'spacy': 'spacy',
    'gensim': 'gensim',
    'xgboost': 'xgboost',
    'lightgbm': 'lightgbm',
    'catboost': 'catboost',
    'scrapy': 'scrapy',
    'kivy': 'kivy',
    'pydantic': 'pydantic',
    'fastapi': 'fastapi',
}

# 默认配置
DEFAULT_CONFIG = {
    'auto_install': False,    # 是否自动安装包
    'auto_update_pip': False, # 是否自动更新pip
    'check_requirements': True, # 是否检查requirements.txt文件
}

def levenshtein_distance(s1: str, s2: str) -> int:
    """计算两个字符串之间的编辑距离"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def parse_imports(code: str) -> List[Tuple[str, Optional[str]]]:
    """解析代码中的导入语句，返回所有导入的模块名
    
    返回: [(模块名, 别名), ...]
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
    except SyntaxError:
        pass  # 忽略语法错误
    
    return modules

def is_local_module(module_name: str, file_path: str) -> bool:
    """检查模块是否是本地模块
    
    参数:
        module_name: 模块名
        file_path: 当前Python文件路径
        
    返回: 如果模块是本地模块，则返回True
    """
    if not file_path or not module_name:
        return False
    
    current_dir = os.path.dirname(os.path.abspath(file_path))
    
    # 检查是否是标准库或内置模块
    if module_name in STDLIB_MODULES or module_name in sys.builtin_module_names:
        return False
    
    # 处理点分隔的模块名
    parts = module_name.split('.')
    base_module = parts[0]  # 基础模块名
    
    # 1. 检查当前目录
    # 检查是py文件
    module_path = os.path.join(current_dir, f"{base_module}.py")
    if os.path.exists(module_path):
        return True
    
    # 检查是否是包 (有__init__.py的目录)
    package_dir = os.path.join(current_dir, base_module)
    init_file = os.path.join(package_dir, "__init__.py")
    if os.path.exists(package_dir) and os.path.isdir(package_dir) and os.path.exists(init_file):
        return True
    
    # 2. 检查所有Python路径
    for path in sys.path:
        # 检查是否是文件
        module_path = os.path.join(path, f"{base_module}.py")
        if os.path.exists(module_path) and os.path.abspath(path) != os.path.abspath(os.path.dirname(sys.executable)):
            # 不考虑Python安装目录中的模块(它们是已安装的包,不是本地模块)
            return True
        
        # 检查是否是用户定义的包
        package_dir = os.path.join(path, base_module)
        init_file = os.path.join(package_dir, "__init__.py")
        if (os.path.exists(package_dir) and os.path.isdir(package_dir) and os.path.exists(init_file) and 
            os.path.abspath(path) != os.path.abspath(os.path.dirname(sys.executable))):
            return True
    
    return False

def get_installed_packages() -> Dict[str, str]:
    """获取当前环境中已安装的包
    
    返回: {包名: 版本号, ...}
    """
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--format=json'],
            capture_output=True,
            text=True,
            check=True
        )
        
        import json
        packages = json.loads(result.stdout)
        return {pkg['name'].lower(): pkg['version'] for pkg in packages}
    except Exception as e:
        logger.error(f"获取已安装包信息失败: {e}")
        return {}

def get_package_for_module(module_name: str, file_path: str = None) -> Optional[str]:
    """根据模块名获取包名
    
    参数:
        module_name: 模块名
        file_path: 当前文件路径，用于确定上下文
        
    返回: 包名，如果模块不需要安装则返回None
    """
    # 1. 对模块名进行处理，获取基础模块名
    base_module = module_name.split('.')[0]
    
    # 2. 检查是否为本地模块
    if file_path and is_local_module(base_module, file_path):
        if DEBUG_MODE:
            logger.debug(f"模块 {module_name} 是本地模块，无需安装")
        return None
    
    # 3. 检查是否为标准库
    if is_stdlib_module(base_module):
        if DEBUG_MODE:
            logger.debug(f"模块 {module_name} 是标准库，无需安装")
        return None
    
    # 5. 检查模块是否已安装但不是标准库
    if is_module_installed(base_module) and not is_stdlib_module(base_module):
        # 如果已安装但不是标准库，从已安装的模块信息获取包名
        try:
            module_spec = importlib.util.find_spec(base_module)
            if module_spec and module_spec.origin:
                # 从安装路径推断包名
                package_path = os.path.dirname(module_spec.origin)
                site_packages = get_site_packages_dir()
                
                # 检查是否在site-packages中
                if site_packages and package_path.startswith(site_packages):
                    # 尝试使用现有的metadata获取包名
                    try:
                        dist = importlib.metadata.distribution(base_module)
                        package_name = dist.metadata['Name']
                        if DEBUG_MODE:
                            logger.debug(f"通过metadata发现包: {module_name} -> {package_name}")
                        
                        return package_name
                    except:
                        # 如果无法通过metadata获取，返回模块名作为包名
                        if DEBUG_MODE:
                            logger.debug(f"无法获取metadata，使用模块名作为包名: {base_module}")
                        return base_module
        except Exception as e:
            if DEBUG_MODE:
                logger.debug(f"获取已安装包信息时出错 ({base_module}): {e}")
    
    # 6. 检查是否在PACKAGE_MAPPING中有定义
    if base_module in PACKAGE_MAPPING:
        package_name = PACKAGE_MAPPING[base_module]
        if DEBUG_MODE:
            logger.debug(f"从PACKAGE_MAPPING中获取包名: {base_module} -> {package_name}")
        return package_name
    
    # 7. 尝试使用标准命名约定（模块名通常与包名相同）
    if DEBUG_MODE:
        logger.debug(f"假设包名与模块名相同: {base_module}")
    return base_module

def get_site_packages_dir():
    """获取site-packages目录的路径"""
    for path in site.getsitepackages():
        if path.endswith('site-packages'):
            return path
    return None

def search_package(package_name: str) -> List[Dict]:
    """搜索与给定包名相关的包"""
    if not package_name:
        return []
    
    search_url = f"https://pypi.org/search/?q={package_name}"
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # 搜索PyPI
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # 解析搜索结果
        for package in soup.select('.package-snippet'):
            name_elem = package.select_one('.package-snippet__name')
            version_elem = package.select_one('.package-snippet__version')
            desc_elem = package.select_one('.package-snippet__description')
            
            if name_elem:
                pkg_info = {
                    'name': name_elem.text.strip(),
                    'version': version_elem.text.strip() if version_elem else '',
                    'summary': desc_elem.text.strip() if desc_elem else '',
                }
                results.append(pkg_info)
        
        # 如果没有找到精确匹配的包，显示搜索链接
        if not any(r['name'].lower() == package_name.lower() for r in results):
            logger.info(f"💡 提示: 您可以在浏览器中查看更多相关包: {search_url}")
        
        return results
    
    except ImportError:
        logger.error("💔 无法导入BeautifulSoup，请安装: pip install beautifulsoup4")
        return []
    except Exception as e:
        logger.error(f"🔍 搜索包时出错: {e}")
        try:
            import requests
        except ImportError:
            logger.warning("⚠️ 未安装requests库，无法搜索包信息")
        
        logger.info(f"💡 您可以访问以下链接手动搜索相关包：\n{search_url}")
        return []

def install_package(package_name: str, module_name: str = None) -> bool:
    """安装Python包"""
    if not package_name:
        return False
    
    if package_name.lower() == 'tkinter':
        logger.info("tkinter是Python的内置模块，但需要单独安装。请参考您的操作系统文档安装tkinter。")
        return False
    
    try:
        logger.info(f"正在安装: '{package_name}' (对应模块: '{module_name or package_name}' )")
        
        # 使用pip安装包
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', package_name],
            check=False,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"✓ 安装成功: {package_name}")
            return True
        
        # 安装失败，尝试分析错误
        suggested_package = analyze_pip_error(result.stderr, package_name)
        if suggested_package:
            logger.info(f"! 安装建议: '{suggested_package}' 代替 '{package_name}'")
            try:
                # 安装建议的包
                alt_result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', suggested_package],
                    check=False,
                    capture_output=True,
                    text=True
                )
                
                if alt_result.returncode == 0:
                    logger.info(f"✓ 成功安装建议的包: {suggested_package}")
                    return True
                else:
                    logger.error(f"× 安装建议的包失败: {suggested_package}")
            except Exception as e:
                logger.error(f"× 安装建议的包时出错: {e}")
        
        # 原始包和建议包都安装失败，尝试搜索相关包
        logger.info(f"正在搜索与 {package_name} 相关的包...")
        search_results = search_package(package_name)
        
        if search_results:
            # 显示找到的相关包
            fuzzy_match = next((pkg for pkg in search_results 
                               if pkg['name'].lower() != package_name.lower() and 
                               (pkg['name'].lower().startswith(package_name.lower()) or 
                                package_name.lower().startswith(pkg['name'].lower()) or
                                levenshtein_distance(pkg['name'].lower(), package_name.lower()) <= 3)), None)
            
            if fuzzy_match:
                # 尝试安装最匹配的包
                logger.info(f"! 您可能想安装: '{fuzzy_match['name']}' 而不是 '{package_name}'")
                
                try:
                    fuzzy_result = subprocess.run(
                        [sys.executable, '-m', 'pip', 'install', fuzzy_match['name']],
                        check=False,
                        capture_output=True,
                        text=True
                    )
                    
                    if fuzzy_result.returncode == 0:
                        logger.info(f"✓ 成功安装: {fuzzy_match['name']}")
                        return True
                    else:
                        logger.error(f"× 安装失败: {fuzzy_match['name']}")
                except Exception as e:
                    logger.error(f"× 安装时出错: {e}")
            
            # 如果还是失败，显示所有搜索结果供用户选择
            logger.info("相关包列表，您可以尝试手动安装：")
            for i, pkg in enumerate(search_results[:5], 1):
                pkg_info = f"{i}. {pkg['name']} - {pkg['summary'][:80]}..."
                logger.info(f"  {pkg_info}")
            
            install_cmd = f"{sys.executable} -m pip install <包名>"
            logger.info(f"安装命令: {install_cmd}")
        else:
            logger.info(f"未找到与 '{package_name}' 相关的包。请检查包名是否正确。")
            logger.info(f"可尝试: {sys.executable} -m pip install {package_name}")
        
        return False
        
    except Exception as e:
        logger.error(f"× 安装包时出错: {e}")
        return False

def analyze_pip_error(error_msg: str, package_name: str) -> Optional[str]:
    """分析pip安装错误信息，查找建议的包名
    
    参数:
        error_msg: pip安装错误信息
        package_name: 原始包名
        
    返回: 建议的包名，如果没有找到则返回None
    """
    # 常见的错误模式和建议格式
    patterns = [
        # sklearn -> scikit-learn 模式
        (r"No matching distribution found for\s+[\w\-\.]+\s*[\r\n]+[\s\S]*?Perhaps you meant\s+['\"]([\w\-\.]+)['\"]", 1),
        (r"No matching distribution found for\s+[\w\-\.]+\s*[\r\n]+[\s\S]*?use\s+['\"]([\w\-\.]+)['\"]", 1),
        # PyPI中没有此名称的包提示
        (r"No matching distribution found for\s+[\w\-\.]+", None),
        # 依赖冲突提示
        (r"Cannot install [\w\-\.]+ and [\w\-\.]+ because these package versions have conflicting dependencies", None)
    ]
    
    for pattern, group in patterns:
        match = re.search(pattern, error_msg, re.IGNORECASE)
        if match and group is not None:
            return match.group(group)
    
    # 特殊情况的硬编码映射
    special_mappings = {
        "sklearn": "scikit-learn",
        "PIL": "pillow",
        "yaml": "pyyaml",
        "cv2": "opencv-python"
    }
    
    if package_name.lower() in special_mappings:
        return special_mappings[package_name.lower()]
        
    return None

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    if not os.path.exists(CONFIG_FILE):
        # 如果配置目录不存在，创建它
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        # 首次运行，询问用户
        config = first_run_setup()
        save_config(config)
        return config
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 确保配置完整，如有新配置项则添加默认值
        updated = False
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
                updated = True
        
        if updated:
            save_config(config)
        
        return config
    except Exception as e:
        logger.error(f"加载配置文件时出错: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> None:
    """保存配置到文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        logger.error(f"保存配置文件时出错: {e}")

def first_run_setup() -> Dict[str, Any]:
    """首次运行设置"""
    print("\n欢迎使用 AutoPython - 自动导入和安装Python模块的工具\n")
    print("这似乎是您首次运行，我们需要进行一些设置：")
    
    auto_install = input("\n是否允许自动安装缺失的依赖包？(y/n, 默认: n): ").lower() == 'y'
    auto_update_pip = False
    check_requirements = True
    
    if auto_install:
        auto_update_pip = input("是否允许自动更新pip？(y/n, 默认: n): ").lower() == 'y'
        check_requirements = input("是否检查并安装requirements.txt中的依赖？(y/n, 默认: y): ").lower() != 'n'
    
    config = {
        'auto_install': auto_install,
        'auto_update_pip': auto_update_pip,
        'check_requirements': check_requirements,
    }
    
    # 创建配置目录
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    
    # 保存配置
    save_config(config)
    
    print("\n设置已完成！您可以随时修改配置文件：", CONFIG_FILE)
    
    return config

def modify_code_to_autoinstall(code: str, additional_packages: Set[Tuple[str, str]] = None, file_path: str = None) -> str:
    """修改代码，添加自动安装依赖的功能
    
    参数:
        code: 源代码
        additional_packages: 额外需要安装的包 [(模块名, 包名), ...]
        file_path: 源代码文件路径，用于记录日志
        
    返回: 修改后的代码
    """
    # 获取配置
    config = load_config()
    
    # 从代码中提取导入的模块，并映射到包名
    modules = parse_imports(code)
    packages = []
    
    for module_name, _ in modules:
        package_name = get_package_for_module(module_name, file_path)
        if package_name:
            packages.append((module_name, package_name))
    
    # 添加额外的包
    if additional_packages:
        packages.extend(additional_packages)
    
    # 如果没有包需要安装，直接返回原代码
    if not packages:
        return code
    
    # 创建自动安装函数
    autoinstall_code = """
import sys
import subprocess

def _autopython_autoinstall():
    # 自动安装所需的依赖包
    import importlib.util
    import os

    packages = {
"""
    
    # 添加每个包的安装代码
    for module_name, package_name in packages:
        autoinstall_code += f'        "{module_name}": "{package_name}",\n'
    
    autoinstall_code += """    }
    
    missing_packages = []
    
    # 检查哪些包需要安装
    for module_name, package_name in packages.items():
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                missing_packages.append((module_name, package_name))
        except ImportError:
            missing_packages.append((module_name, package_name))
    
    if missing_packages:
        # 加载配置
        try:
            import json
            import os
            from pathlib import Path
            
            config_dir = os.environ.get('AUTOPYTHON_CONFIG_DIR', os.path.join(str(Path.home()), '.autopython'))
            config_file = os.environ.get('AUTOPYTHON_CONFIG_FILE', os.path.join(config_dir, 'config.json'))
            
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
            else:
                # 默认配置
                config = {'auto_install': True, 'auto_update_pip': True}
        except Exception as e:
            print(f"加载配置时出错: {{e}}")
            # 使用默认配置
            config = {'auto_install': True, 'auto_update_pip': True}
        
        # 如果需要自动安装或用户同意，则安装缺失的包
        if config['auto_install'] or input("检测到缺失的依赖包，是否自动安装? (y/n): ").lower() == 'y':
            print("正在安装缺失的依赖包...")
            
            # 检查是否需要更新pip
            if config['auto_update_pip']:
                try:
                    pip_check = subprocess.run(
                        [sys.executable, '-m', 'pip', 'list', '--outdated'],
                        capture_output=True, text=True, check=False
                    )
                    if "pip" in pip_check.stdout:
                        print("检测到pip可更新，正在更新...")
                        subprocess.run(
                            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
                            check=False
                        )
                except Exception as e:
                    print(f"检查pip更新时出错: {{e}}")
            
            # 安装缺失的包
            for module_name, package_name in missing_packages:
                try:
                    print("正在安装:", repr(package_name), "(对应模块:", repr(module_name), ")")
                    install_result = subprocess.run(
                        [sys.executable, '-m', 'pip', 'install', package_name],
                        capture_output=True, text=True, check=False
                    )
                    
                    if install_result.returncode != 0:
                        # 分析错误信息
                        error_msg = install_result.stderr
                        suggestion = None
                        
                        # 尝试从错误中提取建议的包名
                        for pattern in [
                            r'Perhaps you meant "([^"]+)"',
                            r"Perhaps you meant '([^']+)'",
                            r'Did you mean "([^"]+)"',
                            r"Did you mean '([^']+)'",
                            r'use "([^"]+)"',
                            r"use '([^']+)'"
                        ]:
                            match = __import__("re").search(pattern, error_msg)
                            if match:
                                suggestion = match.group(1)
                                break
                        
                        # 特殊映射
                        if not suggestion and module_name.lower() in ["sklearn", "PIL", "yaml", "cv2"]:
                            special_mappings = {
                                "sklearn": "scikit-learn",
                                "PIL": "pillow",
                                "yaml": "pyyaml",
                                "cv2": "opencv-python"
                            }
                            suggestion = special_mappings[module_name.lower()]
                        
                        if suggestion:
                            print("安装", repr(package_name), "失败，尝试安装建议的包:", repr(suggestion))
                            retry_result = subprocess.run(
                                [sys.executable, '-m', 'pip', 'install', suggestion],
                                check=False
                            )
                            if retry_result.returncode == 0:
                                print("成功安装建议的包:", repr(suggestion))
                                # 保存模块名到包名的映射关系
                                try:
                                    import importlib.metadata
                                    importlib.metadata.distribution(module_name)
                                    print("成功导入模块:", repr(module_name))
                                except:
                                    pass
                                continue
                        
                        print("安装包", repr(package_name), "失败！")
                        print("错误信息:", repr(error_msg))
                        print("请尝试手动安装:", repr(sys.executable), "-m pip install", repr(package_name))
                        print("或访问 https://pypi.org/search/?q=" + package_name + " 搜索相关包")
                        
                        if config['auto_install'] or input("是否继续执行代码?(y/n): ").lower() != 'y':
                            sys.exit(1)
                except Exception as e:
                    print("安装包时出错:", repr(e))
                    if config['auto_install'] or input("是否继续执行代码?(y/n): ").lower() != 'y':
                        sys.exit(1)
"""
    
    autoinstall_code += """
_autopython_autoinstall()
del _autopython_autoinstall
"""
    
    # 在导入语句之前插入自动安装代码
    # 尝试找到代码中的第一个非注释、非空行
    lines = code.split('\n')
    insert_pos = 0
    
    # 查找适合插入的位置（跳过文件头的注释和空行）
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            if i > 0 and re.match(r'^""".*', stripped):
                # 如果是文档字符串，找到它的结束位置
                for j in range(i+1, len(lines)):
                    if re.search(r'"""$', lines[j]):
                        insert_pos = j + 1
                        break
                else:
                    insert_pos = i  # 没找到结束，就在开始处插入
            else:
                insert_pos = i
            break
    
    # 插入自动安装代码
    modified_code = '\n'.join(lines[:insert_pos]) + '\n' + autoinstall_code + '\n'.join(lines[insert_pos:])
    return modified_code

def parse_requirements_file(file_path: str) -> List[str]:
    """解析requirements.txt文件，返回所有依赖包
    
    返回: 包名列表
    """
    if not os.path.exists(file_path):
        return []
    
    packages = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        # 跳过注释和空行
        if not line or line.startswith('#'):
            continue
        # 处理带版本号的包 (例如: package==1.0.0)
        package = line.split('==')[0].split('>')[0].split('<')[0].split('~=')[0].strip()
        if package:
            packages.append(package)
    
    return packages

def check_and_install_requirements(directory: str) -> None:
    """检查目录中是否存在requirements.txt并安装依赖"""
    if not directory:
        return
    
    req_file = os.path.join(directory, 'requirements.txt')
    if os.path.exists(req_file):
        logger.info(f"📄 检测到requirements.txt文件: {req_file}")
        
        try:
            packages = parse_requirements_file(req_file)
            if packages:
                logger.info(f"📦 正在安装requirements.txt中的依赖: {', '.join(packages)}")
                
                # 使用subprocess安装依赖
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', '-r', req_file],
                    check=False,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    logger.info("✅ 依赖安装成功")
                else:
                    logger.error(f"❌ 安装依赖失败: {result.stderr}")
        except Exception as e:
            logger.error(f"❌ 安装依赖时出错: {e}")
            logger.info("💡 请尝试手动安装依赖: pip install -r requirements.txt")

def find_local_imports(code: str, file_path: str) -> List[str]:
    """从代码中找出本地导入的模块文件路径
    
    参数:
        code: 源代码
        file_path: 当前文件的路径，用于确定相对导入的基准目录
        
    返回: 本地导入的模块文件列表 [文件路径, ...]
    """
    if not file_path or not os.path.exists(file_path):
        if DEBUG_MODE:
            logger.debug(f"找不到文件或文件路径为空: {file_path}")
        return []
    
    # 获取当前文件的目录
    current_dir = os.path.dirname(os.path.abspath(file_path))
    
    try:
        # 解析代码并收集所有导入节点
        tree = ast.parse(code)
        imports = []
        
        # 收集所有导入节点 (Import 和 ImportFrom)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)
        
        local_imports = []
        processed_modules = set()  # 用于避免重复处理相同的模块
        
        for node in imports:
            if isinstance(node, ast.Import):
                # 处理 "import x, y, z" 形式
                for alias in node.names:
                    module_name = alias.name
                    if module_name in processed_modules:
                        continue
                    processed_modules.add(module_name)
                    
                    # 检查是否为本地模块
                    if is_local_module(module_name, file_path):
                        # 搜索当前目录和Python路径
                        module_path = module_name.replace('.', os.path.sep)
                        
                        # 以下顺序查找模块文件:
                        # 1. 当前目录下的.py文件
                        local_file = os.path.join(current_dir, f"{module_path}.py")
                        if os.path.isfile(local_file):
                            local_imports.append(local_file)
                            continue
                            
                        # 2. 当前目录下作为包的子目录
                        package_dir = os.path.join(current_dir, module_path)
                        init_file = os.path.join(package_dir, "__init__.py")
                        if os.path.isdir(package_dir) and os.path.isfile(init_file):
                            local_imports.append(init_file)
                            continue
                            
                        # 3. 查找sys.path中的本地模块
                        for path_dir in sys.path:
                            # 跳过标准库路径
                            if any(std_path in path_dir for std_path in 
                                  ['site-packages', 'dist-packages', os.path.sep + 'lib' + os.path.sep]):
                                continue
                                
                            # 检查.py文件
                            module_file = os.path.join(path_dir, f"{module_path}.py")
                            if os.path.isfile(module_file):
                                local_imports.append(module_file)
                                break
                                
                            # 检查包目录
                            pkg_dir = os.path.join(path_dir, module_path)
                            pkg_init = os.path.join(pkg_dir, "__init__.py")
                            if os.path.isdir(pkg_dir) and os.path.isfile(pkg_init):
                                local_imports.append(pkg_init)
                                break
                    
            elif isinstance(node, ast.ImportFrom):
                if node.module is None:  # 相对导入
                    # 处理相对导入 (如 "from . import x" 或 "from .. import y")
                    level = node.level
                    target_dir = current_dir
                    
                    # 根据相对层级向上查找目录
                    for _ in range(level):
                        parent_dir = os.path.dirname(target_dir)
                        if parent_dir == target_dir:  # 已到达根目录
                            break
                        target_dir = parent_dir
                    
                    for alias in node.names:
                        module_name = alias.name
                        if module_name in processed_modules:
                            continue
                        processed_modules.add(module_name)
                        
                        # 检查目标目录中的.py文件和包
                        module_file = os.path.join(target_dir, f"{module_name}.py")
                        if os.path.isfile(module_file):
                            local_imports.append(module_file)
                            continue
                            
                        # 检查是否为包
                        pkg_dir = os.path.join(target_dir, module_name)
                        pkg_init = os.path.join(pkg_dir, "__init__.py")
                        if os.path.isdir(pkg_dir) and os.path.isfile(pkg_init):
                            local_imports.append(pkg_init)
                
                else:  # 正常from导入
                    # 处理 "from module import x" 形式
                    module_name = node.module
                    
                    # 对于from导入，我们只关注父模块是否为本地模块
                    if is_local_module(module_name, file_path):
                        # 将模块名转换为路径
                        module_path = module_name.replace('.', os.path.sep)
                        
                        # 搜索模块文件
                        module_file = os.path.join(current_dir, f"{module_path}.py")
                        if os.path.isfile(module_file):
                            if module_file not in local_imports:
                                local_imports.append(module_file)
                            continue
                        
                        # 搜索包目录
                        pkg_dir = os.path.join(current_dir, module_path)
                        pkg_init = os.path.join(pkg_dir, "__init__.py")
                        if os.path.isdir(pkg_dir) and os.path.isfile(pkg_init):
                            if pkg_init not in local_imports:
                                local_imports.append(pkg_init)
                            continue
                        
                        # 在sys.path中查找
                        for path_dir in sys.path:
                            # 跳过标准库路径
                            if any(std_path in path_dir for std_path in 
                                  ['site-packages', 'dist-packages', os.path.sep + 'lib' + os.path.sep]):
                                continue
                                
                            # 检查.py文件
                            path_file = os.path.join(path_dir, f"{module_path}.py")
                            if os.path.isfile(path_file):
                                if path_file not in local_imports:
                                    local_imports.append(path_file)
                                break
                                
                            # 检查包目录
                            path_pkg_dir = os.path.join(path_dir, module_path)
                            path_pkg_init = os.path.join(path_pkg_dir, "__init__.py")
                            if os.path.isdir(path_pkg_dir) and os.path.isfile(path_pkg_init):
                                if path_pkg_init not in local_imports:
                                    local_imports.append(path_pkg_init)
                                break
        
        # 返回去重后的本地导入列表
        return list(dict.fromkeys(local_imports))
        
    except SyntaxError as e:
        logger.warning(f"解析文件时出现语法错误 ({os.path.basename(file_path)}): {e}")
        return []
    except Exception as e:
        logger.error(f"查找本地导入时出错 ({os.path.basename(file_path)}): {e}")
        if DEBUG_MODE:
            import traceback
            logger.debug(traceback.format_exc())
        return []

def process_recursive_imports(file_path: str, processed_files: Set[str] = None) -> Set[Tuple[str, str]]:
    """递归处理文件中的导入，找出所有需要安装的包"""
    if processed_files is None:
        processed_files = set()
    
    required_packages = set()
    
    # 规范化文件路径
    abs_path = os.path.abspath(file_path)
    if abs_path in processed_files:
        logger.debug(f"🔄 跳过已处理的文件: {os.path.basename(file_path)}")
        return required_packages
    
    processed_files.add(abs_path)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        logger.warning(f"⚠️ 文件不存在: {file_path}")
        return required_packages
    
    logger.debug(f"📁 递归处理导入: {os.path.basename(file_path)}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 解析导入
        imports = parse_imports(code)
        
        # 检查每个导入是否需要安装
        for module_name, alias in imports:
            base_module = module_name.split('.')[0]
            
            # 检查是否是本地模块
            if is_local_module(base_module, file_path):
                continue
            
            # 检查是否是标准库
            if is_stdlib_module(base_module):
                continue
            
            # 获取包名
            package_name = get_package_for_module(base_module, file_path)
            if package_name and not is_module_installed(base_module):
                logger.debug(f"📦 发现需要的包: {module_name} -> {package_name}")
                required_packages.add((base_module, package_name))
        
        # 查找本地导入并递归处理
        local_imports = find_local_imports(code, file_path)
        if local_imports:
            file_dir = os.path.dirname(file_path)
            logger.debug(f"🔗 在 {os.path.basename(file_path)} 中发现本地导入: {', '.join(os.path.basename(f) for f in local_imports)}")
            
            for local_import in local_imports:
                # 避免重复处理
                abs_local_import = os.path.abspath(local_import)
                if abs_local_import in processed_files:
                    continue
                
                logger.debug(f"⏩ 递归处理本地导入: {os.path.basename(local_import)}")
                
                # 递归处理导入
                nested_required = process_recursive_imports(local_import, processed_files)
                if nested_required:
                    logger.debug(f"↪️ 从 {os.path.basename(local_import)} 发现嵌套依赖: " +
                                f"{', '.join([f'{mod} -> {pkg}' for mod, pkg in nested_required])}")
                    required_packages.update(nested_required)
        
        return required_packages
    
    except Exception as e:
        logger.error(f"❌ 处理递归导入时出错 ({os.path.basename(file_path)}): {e}")
        if DEBUG_MODE:
            logger.debug(traceback.format_exc())
        return required_packages

def process_file(file_path: str, run: bool = True) -> None:
    """处理Python文件，添加自动导入功能并执行"""
    if not os.path.exists(file_path):
        logger.error(f"❌ 文件不存在: {file_path}")
        return
    
    try:
        # 检查目录中是否有requirements.txt文件
        config = load_config()
        if config.get('check_requirements', True):
            check_and_install_requirements(os.path.dirname(file_path))
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 包含递归导入的处理
        logger.info("🔍 开始检测递归导入...")
        required_packages = process_recursive_imports(file_path)
        if required_packages:
            logger.info(f"📦 通过递归分析发现需要安装的包: {', '.join([pkg[1] for pkg in required_packages])}")
        
        # 修改代码，添加自动安装功能
        modified_code = modify_code_to_autoinstall(code, required_packages, file_path)
        
        # 创建临时文件来运行修改后的代码
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w', encoding='utf-8', delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(modified_code)
        
        if run:
            logger.info(f"🚀 正在执行文件: {file_path}")
            # 设置环境变量，传递原始文件路径
            env = os.environ.copy()
            
            # 执行修改后的代码
            # 传递原脚本的参数
            cmd = [sys.executable, temp_path] + sys.argv[2:]
            result = subprocess.run(cmd, check=False, env=env)
        
        # 删除临时文件
        os.unlink(temp_path)
            
    except Exception as e:
        logger.error(f"❌ 处理文件时出错: {e}")
        if DEBUG_MODE:
            import traceback
            logger.debug(traceback.format_exc())

def handle_main_problem(file_path: str) -> None:
    """处理if __name__ == '__main__'的问题"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 检查代码中是否有if __name__ == '__main__'
        has_main_block = re.search(r'if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:', code) is not None
        
        # 检查目录中是否有requirements.txt文件
        config = load_config()
        if config.get('check_requirements', True):
            check_and_install_requirements(os.path.dirname(file_path))
        
        # 处理递归导入
        required_packages = process_recursive_imports(file_path)
        
        if has_main_block:
            # 有main块，需要特殊处理
            modified_code = modify_code_to_autoinstall(code, required_packages, file_path)
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.py', mode='w', encoding='utf-8', delete=False) as temp_file:
                temp_path = temp_file.name
                temp_file.write(modified_code)
            
            # 设置__name__='__main__'来执行临时文件，同时设置__file__变量
            absolute_path = os.path.abspath(file_path)
            cmd = [sys.executable, '-c', f"__file__ = '{absolute_path}'; __name__ = '__main__'; exec(open('{temp_path}').read())"]
            subprocess.run(cmd, check=False)
            
            # 删除临时文件
            os.unlink(temp_path)
        else:
            # 没有main块，直接处理
            process_file(file_path)
    
    except Exception as e:
        logger.error(f"处理main块时出错: {e}")

def main():
    """命令行入口函数"""
    if len(sys.argv) < 2:
        print(f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        🚀 AutoPython 使用说明                              ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ 用法: autopython [文件名] [参数...]                                         ┃
┃                                                                           ┃
┃ 示例:                                                                      ┃
┃   autopython example.py                 # 运行一个Python脚本               ┃
┃   autopython example.py arg1 arg2       # 传递参数                         ┃
┃                                                                           ┃
┃ 功能:                                                                      ┃
┃   - 自动检测并安装缺少的依赖包                                               ┃
┃   - 支持递归处理导入关系                                                     ┃
┃   - 智能识别模块与包名的映射                                                 ┃
┃   - 支持requirements.txt安装                                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """)
        return
    
    # 获取文件路径
    file_path = os.path.abspath(sys.argv[1])
    
    # 检查是否是Python文件
    if not file_path.endswith('.py'):
        logger.warning(f"⚠️ 文件 {file_path} 不是Python文件")
    
    # 处理该Python文件
    process_file(file_path)

def is_stdlib_module(module_name: str) -> bool:
    """检查模块是否为Python标准库
    
    参数:
        module_name: 模块名
        
    返回: 如果模块是标准库则返回True，否则返回False
    """
    # 检查是否为内置模块
    if module_name in sys.builtin_module_names:
        return True
    
    # 检查是否在标准库路径中
    spec = None
    try:
        spec = importlib.util.find_spec(module_name)
    except (ModuleNotFoundError, ValueError):
        return False
    
    if spec is None or spec.origin is None:
        return False
    
    # 检查模块路径是否在标准库目录中
    origin = spec.origin
    return any(
        stdlib_path in origin for stdlib_path in 
        [
            os.path.sep + "lib" + os.path.sep + f"python{sys.version_info.major}.{sys.version_info.minor}",
            os.path.sep + "lib" + os.path.sep + f"python{sys.version_info.major}",
            "lib-dynload",
            "site-python"
        ]
    ) and "site-packages" not in origin

def is_module_installed(module_name: str) -> bool:
    """检查模块是否已安装
    
    参数:
        module_name: 模块名
        
    返回: 如果模块已安装则返回True，否则返回False
    """
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except (ModuleNotFoundError, ValueError):
        return False

if __name__ == "__main__":
    main() 