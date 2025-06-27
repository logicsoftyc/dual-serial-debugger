#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本信息管理文件
"""

from datetime import datetime

# 版本信息
VERSION = "1.0.0"
BUILD_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 版本历史
VERSION_HISTORY = [
    {
        "version": "1.0.0",
        "date": "2025-06-27",
        "changes": [
            "版本更新",
            "功能优化",
            "Bug修复"
        ]
    },
    {
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
    }
]

def get_version_info():
    """获取版本信息"""
    return {
        "version": VERSION,
        "build_time": BUILD_TIME,
        "history": VERSION_HISTORY
    }

def get_version_string():
    """获取版本字符串"""
    return f"v{VERSION}"

def get_build_time_string():
    """获取构建时间字符串"""
    return BUILD_TIME

if __name__ == "__main__":
    info = get_version_info()
    print(f"版本: {info['version']}")
    print(f"构建时间: {info['build_time']}")
    print("\n版本历史:")
    for version in info['history']:
        print(f"\n{version['version']} ({version['date']}):")
        for change in version['changes']:
            print(f"  - {change}")
