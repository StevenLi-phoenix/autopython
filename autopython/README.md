# autopython

自动导入和安装Python模块的工具

## 功能

- 自动检测Python脚本中导入的模块
- 自动安装缺少的依赖包
- 处理 `if __name__ == "__main__"` 的情况
- 支持命令行参数传递
- 安装失败时搜索相关包并提供安装建议
- 配置功能，可以设置是否自动安装包和更新pip

## 安装

```bash
pip install autopython
```

或者从源码安装：

```bash
git clone https://github.com/StevenLi-phoenix/autopython.git
cd autopython
pip install -e .
```

## 使用方法

```bash
autopython your_script.py [arg1 arg2 ...]
```

### 示例

假设你有一个名为 `example.py` 的脚本，它使用了numpy和matplotlib：

```python
import numpy as np
import matplotlib.pyplot as plt

data = np.random.rand(100)
plt.plot(data)
plt.title('Random Data')
plt.show()
```

如果你的系统没有安装numpy或matplotlib，使用autopython会自动安装它们：

```bash
autopython example.py
```

首次运行时，会询问一些配置选项:

1. 是否默认自动安装缺少的包？(y/n)
2. 是否在检测到新版本时自动更新pip？(y/n)

配置会保存在 `~/.autopython/config.json` 文件中，您可以随时手动修改。

### 支持的功能

- 自动解析和安装普通导入语句 `import X`
- 自动解析和安装from导入语句 `from X import Y`
- 处理包与模块名不一致的情况 (如 `PIL` -> `pillow`)
- 支持 `if __name__ == "__main__"` 结构
- 传递命令行参数到目标脚本
- 安装失败时搜索相关包并提供安装建议
- 配置是否自动安装包和自动更新pip

## 开发指南

### 安装开发依赖

```bash
pip install -r dev-requirements.txt
```

### 运行测试

```bash
python -m unittest discover -s tests
```

### 代码格式化

```bash
black autopython tests
isort autopython tests
```

### 构建包

```bash
python -m build
```

### 发布到TestPyPI

```bash
python make_release.py
```

### 发布到PyPI

```bash
python make_release.py --production
```

## 环境变量

- `AUTOPYTHON_CONFIG_DIR`: 配置目录路径，默认为 `~/.autopython`
- `AUTOPYTHON_CONFIG_FILE`: 配置文件路径，默认为 `~/.autopython/config.json`

## 贡献

欢迎通过Issue或Pull Request提供反馈和建议。

## 许可证

MIT 