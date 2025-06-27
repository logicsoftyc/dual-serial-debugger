@echo off
chcp 65001 >nul
echo ========================================
echo 双串口调试器 - GitHub上传脚本
echo 作者: logicsoft@qq.com
echo GitHub: logicsoftyc
echo ========================================
echo.

echo [1/8] 检查Git是否安装...
git --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Git，请先安装Git
    echo 下载地址: https://git-scm.com/downloads
    pause
    exit /b 1
)
echo ✓ Git已安装

echo.
echo [2/8] 配置Git用户信息...
git config --global user.name "logicsoftyc"
git config --global user.email "logicsoft@qq.com"
echo ✓ Git用户信息配置完成

echo.
echo [3/8] 初始化Git仓库...
if exist .git (
    echo ✓ Git仓库已存在
) else (
    git init
    echo ✓ Git仓库初始化完成
)

echo.
echo [4/8] 添加文件到暂存区...
git add .
echo ✓ 文件已添加到暂存区

echo.
echo [5/8] 提交代码...
git commit -m "Initial commit: Dual Serial Debugger v1.0.0 - Support dual serial ports, multiple encodings, SSCOM compatibility, quick strings, history records, and complete logging functionality - Author: logicsoft@qq.com"
echo ✓ 代码提交完成

echo.
echo [6/8] 设置远程仓库...
git remote remove origin 2>nul
git remote add origin https://github.com/logicsoftyc/dual-serial-debugger.git
echo ✓ 远程仓库设置完成

echo.
echo [7/8] 推送到GitHub...
git branch -M main
git push -u origin main
if errorlevel 1 (
    echo.
    echo 错误: 推送失败
    echo 请确保:
    echo 1. 已在GitHub创建仓库: https://github.com/logicsoftyc/dual-serial-debugger
    echo 2. 已配置GitHub身份验证
    echo 3. 网络连接正常
    echo.
    echo 手动创建仓库步骤:
    echo 1. 访问: https://github.com/new
    echo 2. 仓库名: dual-serial-debugger
    echo 3. 描述: 功能完整的双串口调试工具，支持多种编码、历史记录、快速字符串等功能
    echo 4. 选择Public
    echo 5. 不要勾选Initialize this repository with a README
    echo 6. 点击Create repository
    echo.
    pause
    exit /b 1
)
echo ✓ 代码推送成功

echo.
echo [8/8] 设置仓库信息...
echo 请在GitHub仓库页面设置以下信息:
echo - 描述: 功能完整的双串口调试工具，支持多种编码、历史记录、快速字符串等功能
echo - 网站: https://github.com/logicsoftyc/dual-serial-debugger
echo - 主题标签: python, serial, debugger, pyqt5, sscom

echo.
echo [9/8] 创建Release...
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
echo ✓ GitHub上传完成！
echo ========================================
echo.
echo 仓库地址: https://github.com/logicsoftyc/dual-serial-debugger
echo 作者邮箱: logicsoft@qq.com
echo.
echo 项目已成功上传到GitHub，可以分享给其他人使用了！
echo.
pause 