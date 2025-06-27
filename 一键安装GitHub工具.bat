@echo off
chcp 65001 >nul
echo ========================================
echo GitHub工具一键安装脚本
echo 作者: logicsoft@qq.com
echo ========================================
echo.

echo [1/4] 检查GitHub CLI是否已安装...
gh --version >nul 2>&1
if errorlevel 1 (
    echo GitHub CLI未安装，正在下载安装...
    
    echo [2/4] 下载GitHub CLI...
    echo 请访问: https://cli.github.com/
    echo 下载Windows版本的GitHub CLI
    echo 或者使用winget安装: winget install GitHub.cli
    echo.
    echo 下载完成后，请重新运行此脚本
    pause
    exit /b 1
) else (
    echo ✓ GitHub CLI已安装
)

echo.
echo [3/4] 检查GitHub身份验证...
gh auth status >nul 2>&1
if errorlevel 1 (
    echo GitHub身份验证失败，正在启动登录...
    echo 请在浏览器中完成GitHub登录
    gh auth login
) else (
    echo ✓ GitHub身份验证成功
)

echo.
echo [4/4] 运行自动创建仓库脚本...
echo 现在将运行自动创建仓库脚本...
echo.
call 自动创建仓库.bat

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 如果遇到问题，请检查:
echo 1. 网络连接是否正常
echo 2. GitHub账号是否正确
echo 3. 是否有足够的权限
echo.
pause 