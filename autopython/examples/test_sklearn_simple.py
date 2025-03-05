#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""测试sklearn模块导入"""

import sklearn
print("测试sklearn自动安装功能")
print(f"使用的模块: sklearn")
print(f"实际需要安装的包: scikit-learn")
print(f"sklearn版本: {sklearn.__version__}")
print("\n如果成功运行，说明autopython能够正确识别并安装sklearn对应的scikit-learn包。") 