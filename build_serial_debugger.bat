@echo off
echo 正在构建COM口串口调试器...

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 安装依赖
echo 正在安装依赖...
pip install -r requirements.txt

REM 使用PyInstaller构建可执行文件
echo 正在构建可执行文件...
pyinstaller --onefile --windowed --name "COM口串口调试器" serial_debugger.py

echo 构建完成！
echo 可执行文件位置：dist\COM口串口调试器.exe
pause 