@echo off
chcp 65001 >nul
echo ========================================
echo 自动创建GitHub仓库脚本
echo 作者: logicsoft@qq.com
echo GitHub: logicsoftyc
echo ========================================
echo.

echo [1/6] 检查GitHub CLI是否安装...
gh --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到GitHub CLI，请先安装
    echo 下载地址: https://cli.github.com/
    echo 安装后需要运行: gh auth login
    pause
    exit /b 1
)
echo ✓ GitHub CLI已安装

echo.
echo [2/6] 检查GitHub身份验证...
gh auth status >nul 2>&1
if errorlevel 1 (
    echo 错误: 未登录GitHub，请先登录
    echo 运行: gh auth login
    pause
    exit /b 1
)
echo ✓ GitHub身份验证成功

echo.
echo [3/6] 创建GitHub仓库...
gh repo create dual-serial-debugger --public --description "功能完整的双串口调试工具，支持多种编码、历史记录、快速字符串等功能" --source=. --remote=origin --push
if errorlevel 1 (
    echo 错误: 创建仓库失败
    echo 可能原因:
    echo 1. 仓库已存在
    echo 2. 网络连接问题
    echo 3. 权限不足
    pause
    exit /b 1
)
echo ✓ GitHub仓库创建成功

echo.
echo [4/6] 设置仓库信息...
echo 请在GitHub仓库页面设置以下信息:
echo - 描述: 功能完整的双串口调试工具，支持多种编码、历史记录、快速字符串等功能
echo - 网站: https://github.com/logicsoftyc/dual-serial-debugger
echo - 主题标签: python, serial, debugger, pyqt5, sscom

echo.
echo [5/6] 创建Release...
echo 请在GitHub仓库页面:
echo 1. 点击"Releases"
echo 2. 点击"Create a new release"
echo 3. 标签: v1.0.0
echo 4. 标题: 双串口调试器 v1.0.0
echo 5. 复制以下描述内容:

echo.
echo ========================================
echo Release描述内容:
echo ========================================
echo ## 功能特性
echo.
echo ### 核心功能
echo - 双串口支持：同时连接两个独立串口
echo - 多种编码：支持UTF-8、GBK、GB2312、BIG5等
echo - 数据格式：支持文本和十六进制数据发送接收
echo - 实时显示：实时数据显示，支持时间戳和十六进制显示
echo - 数据统计：发送/接收字节计数
echo.
echo ### 高级功能
echo - 发送历史：自动保存发送历史，支持快速重新发送
echo - 快速字符串：40个预设字符串按钮，支持文本和十六进制
echo - SSCOM兼容：完全兼容SSCOM的多条字符串功能
echo - 配置导入：支持从SSCOM.ini文件导入词条配置
echo - 词条编辑：右键编辑和删除词条，操作方式与SSCOM一致
echo - 自动记忆：所有配置自动保存和恢复
echo.
echo ### 界面特性
echo - 标签页设计：两个串口界面用标签页分开，界面清晰
echo - 程序日志：统一的程序日志区域，显示所有串口数据
echo - 日志管理：支持日志清除、保存和串口选择显示
echo - 版本信息：标题栏显示版本号、构建时间和作者信息
echo.
echo ## 安装使用
echo.
echo ```bash
echo pip install PyQt5 pyserial
echo python serial_debugger.py
echo ```
echo.
echo ## 作者
echo logicsoft@qq.com
echo ========================================

echo.
echo ========================================
echo ✓ GitHub仓库创建完成！
echo ========================================
echo.
echo 仓库地址: https://github.com/logicsoftyc/dual-serial-debugger
echo 作者邮箱: logicsoft@qq.com
echo.
echo 项目已成功上传到GitHub，可以分享给其他人使用了！
echo.
pause 