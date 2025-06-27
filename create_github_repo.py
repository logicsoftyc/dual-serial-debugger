#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动创建GitHub仓库脚本
作者: logicsoft@qq.com
GitHub: logicsoftyc
"""

import os
import sys
import json
import requests
import subprocess
from pathlib import Path

def check_git_installed():
    """检查Git是否安装"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Git已安装")
            return True
        else:
            print("✗ Git未安装")
            return False
    except FileNotFoundError:
        print("✗ Git未安装")
        return False

def check_github_cli():
    """检查GitHub CLI是否安装"""
    try:
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ GitHub CLI已安装")
            return True
        else:
            print("✗ GitHub CLI未安装")
            return False
    except FileNotFoundError:
        print("✗ GitHub CLI未安装")
        return False

def check_github_auth():
    """检查GitHub身份验证"""
    try:
        result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ GitHub身份验证成功")
            return True
        else:
            print("✗ GitHub身份验证失败")
            return False
    except FileNotFoundError:
        print("✗ GitHub CLI未安装")
        return False

def create_repo_with_cli():
    """使用GitHub CLI创建仓库"""
    print("\n[3/6] 使用GitHub CLI创建仓库...")
    
    # 检查仓库是否已存在
    result = subprocess.run(['gh', 'repo', 'view', 'logicsoftyc/dual-serial-debugger'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("⚠ 仓库已存在，跳过创建")
        return True
    
    # 创建仓库
    cmd = [
        'gh', 'repo', 'create', 'dual-serial-debugger',
        '--public',
        '--description', '功能完整的双串口调试工具，支持多种编码、历史记录、快速字符串等功能',
        '--source', '.',
        '--remote', 'origin',
        '--push'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ GitHub仓库创建成功")
        return True
    else:
        print(f"✗ 创建仓库失败: {result.stderr}")
        return False

def setup_git():
    """设置Git配置"""
    print("\n[2/6] 配置Git...")
    
    # 设置用户信息
    subprocess.run(['git', 'config', '--global', 'user.name', 'logicsoftyc'])
    subprocess.run(['git', 'config', '--global', 'user.email', 'logicsoft@qq.com'])
    
    # 初始化仓库
    if not Path('.git').exists():
        subprocess.run(['git', 'init'])
        print("✓ Git仓库初始化完成")
    else:
        print("✓ Git仓库已存在")
    
    # 添加文件
    subprocess.run(['git', 'add', '.'])
    
    # 提交代码
    subprocess.run(['git', 'commit', '-m', 'Initial commit: Dual Serial Debugger v1.0.0'])
    print("✓ 代码提交完成")

def main():
    """主函数"""
    print("=" * 50)
    print("自动创建GitHub仓库脚本")
    print("作者: logicsoft@qq.com")
    print("GitHub: logicsoftyc")
    print("=" * 50)
    
    # 检查Git
    print("\n[1/6] 检查Git...")
    if not check_git_installed():
        print("请先安装Git: https://git-scm.com/downloads")
        return False
    
    # 检查GitHub CLI
    print("\n[2/6] 检查GitHub CLI...")
    if not check_github_cli():
        print("请先安装GitHub CLI: https://cli.github.com/")
        print("安装后运行: gh auth login")
        return False
    
    # 检查身份验证
    if not check_github_auth():
        print("请先登录GitHub: gh auth login")
        return False
    
    # 设置Git
    setup_git()
    
    # 创建仓库
    if not create_repo_with_cli():
        return False
    
    # 显示后续步骤
    print("\n[4/6] 设置仓库信息...")
    print("请在GitHub仓库页面设置以下信息:")
    print("- 描述: 功能完整的双串口调试工具，支持多种编码、历史记录、快速字符串等功能")
    print("- 网站: https://github.com/logicsoftyc/dual-serial-debugger")
    print("- 主题标签: python, serial, debugger, pyqt5, sscom")
    
    print("\n[5/6] 创建Release...")
    print("请在GitHub仓库页面:")
    print("1. 点击'Releases'")
    print("2. 点击'Create a new release'")
    print("3. 标签: v1.0.0")
    print("4. 标题: 双串口调试器 v1.0.0")
    print("5. 复制以下描述内容:")
    
    print("\n" + "=" * 50)
    print("Release描述内容:")
    print("=" * 50)
    
    release_content = """## 功能特性

### 核心功能
- 双串口支持：同时连接两个独立串口
- 多种编码：支持UTF-8、GBK、GB2312、BIG5等
- 数据格式：支持文本和十六进制数据发送接收
- 实时显示：实时数据显示，支持时间戳和十六进制显示
- 数据统计：发送/接收字节计数

### 高级功能
- 发送历史：自动保存发送历史，支持快速重新发送
- 快速字符串：40个预设字符串按钮，支持文本和十六进制
- SSCOM兼容：完全兼容SSCOM的多条字符串功能
- 配置导入：支持从SSCOM.ini文件导入词条配置
- 词条编辑：右键编辑和删除词条，操作方式与SSCOM一致
- 自动记忆：所有配置自动保存和恢复

### 界面特性
- 标签页设计：两个串口界面用标签页分开，界面清晰
- 程序日志：统一的程序日志区域，显示所有串口数据
- 日志管理：支持日志清除、保存和串口选择显示
- 版本信息：标题栏显示版本号、构建时间和作者信息

## 安装使用

```bash
pip install PyQt5 pyserial
python serial_debugger.py
```

## 作者
logicsoft@qq.com"""
    
    print(release_content)
    print("=" * 50)
    
    print("\n" + "=" * 50)
    print("✓ GitHub仓库创建完成！")
    print("=" * 50)
    print("\n仓库地址: https://github.com/logicsoftyc/dual-serial-debugger")
    print("作者邮箱: logicsoft@qq.com")
    print("\n项目已成功上传到GitHub，可以分享给其他人使用了！")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ 操作失败，请检查错误信息")
        else:
            print("\n✅ 操作成功完成！")
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
    
    input("\n按任意键退出...") 