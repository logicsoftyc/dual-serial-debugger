# GitHub上传指南

## 准备工作

### 1. 确保文件完整
以下文件已经准备好：
- ✅ `serial_debugger.py` - 主程序文件
- ✅ `version_info.py` - 版本信息
- ✅ `update_version.py` - 版本更新脚本
- ✅ `requirements.txt` - 依赖库列表
- ✅ `README.md` - 项目说明文档
- ✅ `LICENSE` - MIT许可证
- ✅ `.gitignore` - Git忽略文件
- ✅ `使用说明.txt` - 详细使用说明
- ✅ `词条功能使用说明.md` - 词条功能说明
- ✅ `sscom51_example.ini` - SSCOM配置文件示例

### 2. 需要删除的测试文件
以下测试文件会被.gitignore排除，不会上传：
- `test_*.py` - 所有测试文件
- `demo_*.py` - 演示文件
- `serial_debugger_config.json` - 本地配置文件
- `__pycache__/` - Python缓存目录

## 上传步骤

### 1. 初始化Git仓库
```bash
git init
```

### 2. 添加文件到暂存区
```bash
git add .
```

### 3. 提交初始版本
```bash
git commit -m "Initial commit: 双串口调试器 v1.0.0

- 支持双串口调试功能
- 支持多种编码和格式
- 支持SSCOM配置导入
- 支持快速字符串和词条编辑
- 支持发送历史和自动记忆
- 完整的程序日志功能
- 作者: logicsoft@qq.com"
```

### 4. 在GitHub创建仓库
1. 登录GitHub
2. 点击右上角"+"号，选择"New repository"
3. 仓库名称：`dual-serial-debugger`
4. 描述：`功能完整的双串口调试工具，支持多种编码、历史记录、快速字符串等功能`
5. 选择"Public"（公开）
6. 不要勾选"Initialize this repository with a README"
7. 点击"Create repository"

### 5. 添加远程仓库
```bash
git remote add origin https://github.com/logicsoftyc/dual-serial-debugger.git
```

### 6. 推送到GitHub
```bash
git branch -M main
git push -u origin main
```

## 仓库设置

### 1. 设置仓库描述
在GitHub仓库页面，点击"About"部分，添加：
- 描述：`功能完整的双串口调试工具，支持多种编码、历史记录、快速字符串等功能`
- 网站：`https://github.com/logicsoftyc/dual-serial-debugger`
- 主题标签：`python`, `serial`, `debugger`, `pyqt5`, `sscom`

### 2. 设置README显示
README.md文件会自动显示在仓库主页，包含：
- 项目介绍
- 功能特性
- 安装使用说明
- 项目结构
- 版本信息
- 技术特点
- 应用场景

### 3. 添加Issues模板（可选）
可以创建Issues模板，方便用户反馈问题。

## 版本发布

### 1. 创建Release
1. 在GitHub仓库页面，点击"Releases"
2. 点击"Create a new release"
3. 标签：`v1.0.0`
4. 标题：`双串口调试器 v1.0.0`
5. 描述：
```
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

## 联系方式

- **作者**：logicsoft@qq.com
- **项目地址**：https://github.com/logicsoftyc/dual-serial-debugger
- **问题反馈**：请在GitHub Issues中提交

## 成功标志

上传成功后，你应该看到：
- ✅ GitHub仓库页面显示完整的README
- ✅ 所有源代码文件都已上传
- ✅ 测试文件和配置文件被正确排除
- ✅ 许可证和文档都已就位
- ✅ 仓库描述和标签设置完成

现在你的双串口调试器项目已经准备好分享给全世界了！🎉 