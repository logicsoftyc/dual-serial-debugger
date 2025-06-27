# 双串口调试器 - GitHub上传脚本 (PowerShell版本)
# 作者: logicsoft@qq.com
# GitHub: logicsoftyc

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "双串口调试器 - GitHub上传脚本" -ForegroundColor Yellow
Write-Host "作者: logicsoft@qq.com" -ForegroundColor Green
Write-Host "GitHub: logicsoftyc" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查Git是否安装
Write-Host "[1/8] 检查Git是否安装..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✓ Git已安装: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 未找到Git，请先安装Git" -ForegroundColor Red
    Write-Host "下载地址: https://git-scm.com/downloads" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

# 2. 配置Git用户信息
Write-Host ""
Write-Host "[2/8] 配置Git用户信息..." -ForegroundColor Yellow
git config --global user.name "logicsoftyc"
git config --global user.email "logicsoft@qq.com"
Write-Host "✓ Git用户信息配置完成" -ForegroundColor Green

# 3. 初始化Git仓库
Write-Host ""
Write-Host "[3/8] 初始化Git仓库..." -ForegroundColor Yellow
if (Test-Path ".git") {
    Write-Host "✓ Git仓库已存在" -ForegroundColor Green
} else {
    git init
    Write-Host "✓ Git仓库初始化完成" -ForegroundColor Green
}

# 4. 添加文件到暂存区
Write-Host ""
Write-Host "[4/8] 添加文件到暂存区..." -ForegroundColor Yellow
git add .
Write-Host "✓ 文件已添加到暂存区" -ForegroundColor Green

# 5. 提交代码
Write-Host ""
Write-Host "[5/8] 提交代码..." -ForegroundColor Yellow
$commitMessage = "Initial commit: Dual Serial Debugger v1.0.0 - Support dual serial ports, multiple encodings, SSCOM compatibility, quick strings, history records, and complete logging functionality - Author: logicsoft@qq.com"

git commit -m $commitMessage
Write-Host "✓ 代码提交完成" -ForegroundColor Green

# 6. 设置远程仓库
Write-Host ""
Write-Host "[6/8] 设置远程仓库..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin https://github.com/logicsoftyc/dual-serial-debugger.git
Write-Host "✓ 远程仓库设置完成" -ForegroundColor Green

# 7. 推送到GitHub
Write-Host ""
Write-Host "[7/8] 推送到GitHub..." -ForegroundColor Yellow
git branch -M main
$pushResult = git push -u origin main 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "错误: 推送失败" -ForegroundColor Red
    Write-Host "请确保:" -ForegroundColor Yellow
    Write-Host "1. 已在GitHub创建仓库: https://github.com/logicsoftyc/dual-serial-debugger" -ForegroundColor Yellow
    Write-Host "2. 已配置GitHub身份验证" -ForegroundColor Yellow
    Write-Host "3. 网络连接正常" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "手动创建仓库步骤:" -ForegroundColor Cyan
    Write-Host "1. 访问: https://github.com/new" -ForegroundColor White
    Write-Host "2. 仓库名: dual-serial-debugger" -ForegroundColor White
    Write-Host "3. 描述: 功能完整的双串口调试工具，支持多种编码、历史记录、快速字符串等功能" -ForegroundColor White
    Write-Host "4. 选择Public" -ForegroundColor White
    Write-Host "5. 不要勾选Initialize this repository with a README" -ForegroundColor White
    Write-Host "6. 点击Create repository" -ForegroundColor White
    Write-Host ""
    Read-Host "按任意键退出"
    exit 1
}

Write-Host "✓ 代码推送成功" -ForegroundColor Green

# 8. 设置仓库信息
Write-Host ""
Write-Host "[8/8] 设置仓库信息..." -ForegroundColor Yellow
Write-Host "请在GitHub仓库页面设置以下信息:" -ForegroundColor Cyan
Write-Host "- 描述: 功能完整的双串口调试工具，支持多种编码、历史记录、快速字符串等功能" -ForegroundColor White
Write-Host "- 网站: https://github.com/logicsoftyc/dual-serial-debugger" -ForegroundColor White
Write-Host "- 主题标签: python, serial, debugger, pyqt5, sscom" -ForegroundColor White

# 9. 创建Release
Write-Host ""
Write-Host "[9/8] 创建Release..." -ForegroundColor Yellow
Write-Host "请在GitHub仓库页面:" -ForegroundColor Cyan
Write-Host "1. 点击'Releases'" -ForegroundColor White
Write-Host "2. 点击'Create a new release'" -ForegroundColor White
Write-Host "3. 标签: v1.0.0" -ForegroundColor White
Write-Host "4. 标题: 双串口调试器 v1.0.0" -ForegroundColor White
Write-Host "5. 复制以下描述内容:" -ForegroundColor White

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Release描述内容:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

$releaseContent = @"
## 功能特性

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
logicsoft@qq.com
"@

Write-Host $releaseContent -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ GitHub上传完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "仓库地址: https://github.com/logicsoftyc/dual-serial-debugger" -ForegroundColor Yellow
Write-Host "作者邮箱: logicsoft@qq.com" -ForegroundColor Yellow
Write-Host ""
Write-Host "项目已成功上传到GitHub，可以分享给其他人使用了！" -ForegroundColor Green
Write-Host ""
Read-Host "按任意键退出" 