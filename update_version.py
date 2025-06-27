#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本更新脚本
用于更新程序版本号和构建时间
"""

import re
from datetime import datetime

def update_version_info(new_version):
    """更新版本信息"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 更新version_info.py
    version_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本信息管理文件
"""

from datetime import datetime

# 版本信息
VERSION = "{new_version}"
BUILD_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 版本历史
VERSION_HISTORY = [
    {{
        "version": "{new_version}",
        "date": "{datetime.now().strftime('%Y-%m-%d')}",
        "changes": [
            "版本更新",
            "功能优化",
            "Bug修复"
        ]
    }},
    {{
        "version": "1.0.0",
        "date": "2024-12-19",
        "changes": [
            "初始版本发布",
            "支持双串口调试",
            "支持多种字符编码",
            "支持发送历史记录",
            "支持40个快速字符串",
            "支持SSCOM配置文件导入",
            "支持日志串口选择",
            "支持日志清除和保存"
        ]
    }}
]

def get_version_info():
    """获取版本信息"""
    return {{
        "version": VERSION,
        "build_time": BUILD_TIME,
        "history": VERSION_HISTORY
    }}

def get_version_string():
    """获取版本字符串"""
    return f"v{{VERSION}}"

def get_build_time_string():
    """获取构建时间字符串"""
    return BUILD_TIME

if __name__ == "__main__":
    info = get_version_info()
    print(f"版本: {{info['version']}}")
    print(f"构建时间: {{info['build_time']}}")
    print("\\n版本历史:")
    for version in info['history']:
        print(f"\\n{{version['version']}} ({{version['date']}}):")
        for change in version['changes']:
            print(f"  - {{change}}")
'''
    
    with open('version_info.py', 'w', encoding='utf-8') as f:
        f.write(version_content)
    
    print(f"版本已更新为: {new_version}")
    print(f"构建时间: {current_time}")
    print("version_info.py 文件已更新")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        new_version = sys.argv[1]
        update_version_info(new_version)
    else:
        print("使用方法: python update_version.py <新版本号>")
        print("示例: python update_version.py 1.1.0") 