@echo off
echo 启动Chrome翻译插件后端服务...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查是否在正确的目录
if not exist "app.py" (
    echo 错误: 请在server目录下运行此脚本
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo 检查依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

echo 启动服务器...
echo 服务地址: http://localhost:8000
echo 按 Ctrl+C 停止服务
echo.

python app.py

pause