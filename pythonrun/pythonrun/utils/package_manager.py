"""包管理模块，处理包的安装和搜索功能"""

import sys
import subprocess
import json
import logging
import site
import os
import re
from typing import Dict, List, Optional, Tuple
import requests

logger = logging.getLogger('pythonrun')

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
        
        packages = json.loads(result.stdout)
        return {pkg['name'].lower(): pkg['version'] for pkg in packages}
    except Exception as e:
        logger.error(f"获取已安装包列表失败: {e}")
        return {}

def get_site_packages_dir():
    """获取site-packages目录路径"""
    return site.getsitepackages()[0]

def search_package(package_name: str) -> List[Dict]:
    """在PyPI上搜索包
    
    参数:
        package_name: 要搜索的包名
        
    返回:
        匹配的包列表，每个包是一个字典
    """
    if not package_name:
        return []
    
    try:
        # 首先尝试精确匹配
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return [{
                'name': data['info']['name'],
                'version': data['info']['version'],
                'summary': data['info']['summary'],
                'exact_match': True
            }]
        
        # 如果精确匹配失败，使用搜索API
        search_url = f"https://pypi.org/search/?q={package_name}&format=json"
        response = requests.get(search_url, timeout=5)
        
        if response.status_code == 200:
            results = []
            try:
                data = response.json()
                for item in data.get('results', [])[:5]:  # 限制只返回前5个结果
                    results.append({
                        'name': item['name'],
                        'version': item.get('version', 'unknown'),
                        'summary': item.get('summary', ''),
                        'exact_match': False
                    })
            except Exception as e:
                logger.error(f"解析搜索结果失败: {e}")
            
            # 如果没有搜索结果，使用模糊匹配查找相似包名
            if not results:
                # 获取所有安装的包
                installed = get_installed_packages()
                
                # 查找名称相似的包
                for pkg_name in installed.keys():
                    # 简单的字符串包含检查
                    if package_name.lower() in pkg_name or pkg_name in package_name.lower():
                        results.append({
                            'name': pkg_name,
                            'version': installed[pkg_name],
                            'summary': '本地安装的包',
                            'exact_match': False
                        })
            
            return results
        
        return []
    except Exception as e:
        logger.error(f"搜索包 {package_name} 失败: {e}")
        return []

def install_package(package_name: str, module_name: str = None) -> bool:
    """安装指定的包
    
    参数:
        package_name: 要安装的包名
        module_name: 原始模块名（用于日志记录）
        
    返回:
        安装成功返回True，否则返回False
    """
    if not package_name:
        return False
    
    # 如果module_name没有提供，使用package_name
    if not module_name:
        module_name = package_name
    
    logger.info(f"正在安装 {package_name} (来自模块 {module_name})...")
    
    try:
        # 执行pip安装
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', package_name],
            capture_output=True,
            text=True
        )
        
        # 检查安装结果
        if result.returncode == 0:
            logger.info(f"成功安装 {package_name}")
            return True
        else:
            error_msg = result.stderr
            logger.error(f"安装 {package_name} 失败: {error_msg}")
            
            # 分析错误并给出建议
            suggestion = analyze_pip_error(error_msg, package_name)
            if suggestion:
                logger.info(f"建议: {suggestion}")
            
            # 尝试搜索相似的包
            search_results = search_package(package_name)
            if search_results:
                logger.info("找到以下相关包:")
                for i, pkg in enumerate(search_results):
                    exact = " (精确匹配)" if pkg.get('exact_match') else ""
                    logger.info(f"  {i+1}. {pkg['name']}{exact} - {pkg['summary']}")
                
                # 如果找到了精确匹配但安装失败，可能是其他错误
                for pkg in search_results:
                    if pkg.get('exact_match') and pkg['name'].lower() == package_name.lower():
                        logger.info(f"包名正确，但安装失败。可能是网络问题或权限不足。")
                        break
            
            return False
    except Exception as e:
        logger.error(f"安装过程出错: {e}")
        return False

def analyze_pip_error(error_msg: str, package_name: str) -> Optional[str]:
    """分析pip安装错误，提供有用的建议
    
    参数:
        error_msg: pip安装过程中的错误信息
        package_name: 尝试安装的包名
        
    返回:
        有用的建议或None
    """
    if not error_msg:
        return None
    
    # 检查是否是网络错误
    if "HTTPError" in error_msg or "ConnectionError" in error_msg:
        return "网络连接问题。请检查您的网络连接，或尝试使用镜像源: pip install --index-url https://mirrors.aliyun.com/pypi/simple/ " + package_name
    
    # 检查是否是权限错误
    if "Permission denied" in error_msg:
        if sys.platform == 'win32':
            return "权限被拒绝。请尝试以管理员身份运行，或使用 pip install --user " + package_name
        else:
            return "权限被拒绝。请尝试: sudo pip install " + package_name + " 或 pip install --user " + package_name
    
    # 检查是否是包不存在
    if "No matching distribution found" in error_msg:
        return f"未找到匹配的发行版。包名 '{package_name}' 可能不正确，或不支持当前的Python版本。"
    
    # 检查是否是版本冲突
    if "requires" in error_msg and "which is incompatible" in error_msg:
        return "存在依赖版本冲突。请尝试使用虚拟环境或指定兼容的版本。"
    
    return None

def get_package_for_module(module_name: str, file_path: str = None) -> Optional[str]:
    """根据模块名确定对应的包名
    
    参数:
        module_name: 模块名
        file_path: 当前Python文件路径（用于检查本地模块）
        
    返回:
        包名或None（如果是标准库或本地模块）
    """
    # 如果是空模块名，返回None
    if not module_name:
        return None
        
    # 处理模块名，获取基础模块名
    base_module = module_name.split('.')[0]
    
    # 检查是否在标准库中
    if is_stdlib_module(base_module):
        return None
    
    # 检查是否是本地模块
    if file_path and is_local_module(base_module, file_path):
        return None
    
    # 检查模块名映射
    if module_name in PACKAGE_MAPPING:
        return PACKAGE_MAPPING[module_name]
    
    if base_module in PACKAGE_MAPPING:
        return PACKAGE_MAPPING[base_module]
    
    # 如果没有映射关系，将模块名作为包名
    return base_module

def is_stdlib_module(module_name: str) -> bool:
    """检查模块是否是Python标准库的一部分
    
    参数:
        module_name: 模块名
        
    返回:
        如果模块是标准库的一部分，则返回True
    """
    # 定义标准库模块列表
    STDLIB_MODULES = set(sys.builtin_module_names)
    STDLIB_MODULES.update([
        'abc', 'argparse', 'asyncio', 'base64', 'collections', 'copy', 'datetime',
        'functools', 'hashlib', 'http', 'io', 'itertools', 'json', 'logging', 'math', 
        'os', 'pickle', 'random', 're', 'shutil', 'socket', 'sys', 'tempfile', 
        'threading', 'time', 'traceback', 'urllib', 'warnings', 'zipfile'
    ])
    
    # 分离基础模块名
    base_module = module_name.split('.')[0]
    
    # 检查是否在已知的标准库列表中
    if base_module in STDLIB_MODULES:
        return True
    
    # 尝试以不导入的方式检查是否为标准库
    prefixes = sorted(sys.path, key=len, reverse=True)
    
    # 查找标准库路径
    stdlib_paths = []
    for prefix in prefixes:
        # 根据常见的标准库路径模式
        if 'lib' in prefix and 'site-packages' not in prefix:
            stdlib_paths.append(prefix)
    
    # 检查module_name是否存在于标准库路径中的任何一个
    if stdlib_paths:
        for stdlib_path in stdlib_paths:
            module_path = os.path.join(stdlib_path, f"{base_module}.py")
            package_path = os.path.join(stdlib_path, base_module)
            
            if os.path.exists(module_path) or (os.path.exists(package_path) and os.path.isdir(package_path)):
                return True
    
    return False

def is_module_installed(module_name: str) -> bool:
    """检查模块是否已安装
    
    参数:
        module_name: 模块名
        
    返回:
        如果模块已安装，则返回True
    """
    if not module_name:
        return False
    
    # 获取基础模块名
    base_module = module_name.split('.')[0]
    
    try:
        # 尝试导入模块
        __import__(base_module)
        return True
    except ImportError:
        # 检查是否存在于site-packages目录
        site_packages = get_site_packages_dir()
        module_path = os.path.join(site_packages, f"{base_module}.py")
        package_path = os.path.join(site_packages, base_module)
        
        return os.path.exists(module_path) or (os.path.exists(package_path) and os.path.isdir(package_path))

def is_local_module(module_name: str, file_path: str) -> bool:
    """检查模块是否是本地模块
    
    参数:
        module_name: 模块名
        file_path: 当前Python文件路径
        
    返回:
        如果模块是本地模块，则返回True
    """
    if not file_path or not module_name:
        return False
    
    current_dir = os.path.dirname(os.path.abspath(file_path))
    
    # 检查是否是标准库或内置模块
    if is_stdlib_module(module_name):
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
        # 跳过标准库和第三方包路径
        if ('site-packages' in path or 
            'dist-packages' in path or 
            path == os.path.dirname(sys.executable)):
            continue
        
        # 检查是否是文件
        module_path = os.path.join(path, f"{base_module}.py")
        if os.path.exists(module_path):
            return True
        
        # 检查是否是用户定义的包
        package_dir = os.path.join(path, base_module)
        init_file = os.path.join(package_dir, "__init__.py")
        if os.path.exists(package_dir) and os.path.isdir(package_dir) and os.path.exists(init_file):
            return True
    
    return False

def parse_requirements_file(file_path: str) -> List[str]:
    """解析requirements.txt文件
    
    参数:
        file_path: requirements.txt文件路径
        
    返回:
        依赖包列表
    """
    if not os.path.exists(file_path):
        return []
    
    packages = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 跳过注释和空行
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 处理特殊格式（如 -r other-requirements.txt）
                if line.startswith('-r'):
                    include_file = line[2:].strip()
                    include_path = os.path.join(os.path.dirname(file_path), include_file)
                    if os.path.exists(include_path):
                        packages.extend(parse_requirements_file(include_path))
                    continue
                
                # 移除版本标识符和其他选项
                package = re.split(r'[<>=;]', line)[0].strip()
                if package:
                    packages.append(package)
    except Exception as e:
        logger.error(f"解析requirements文件失败: {e}")
    
    return packages

def check_and_install_requirements(directory: str) -> None:
    """检查并安装目录中的requirements.txt文件中的依赖
    
    参数:
        directory: 要检查的目录路径
    """
    req_file = os.path.join(directory, 'requirements.txt')
    if not os.path.exists(req_file):
        return
    
    logger.info(f"检测到requirements.txt文件，正在检查依赖...")
    packages = parse_requirements_file(req_file)
    
    if not packages:
        logger.info("requirements.txt文件为空或格式不正确")
        return
    
    # 获取已安装的包
    installed_packages = get_installed_packages()
    
    # 检查并安装缺少的包
    for package in packages:
        package_lower = package.lower()
        if package_lower not in installed_packages:
            logger.info(f"安装依赖包: {package}")
            install_package(package)
        else:
            logger.debug(f"依赖包已安装: {package} ({installed_packages[package_lower]})")
    
    logger.info("依赖检查完成") 