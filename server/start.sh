#!/bin/bash

echo "启动Chrome翻译插件后端服务..."
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python，请先安装Python 3.8+"
    exit 1
fi

# 检查是否在正确的目录
if [ ! -f "app.py" ]; then
    echo "错误: 请在server目录下运行此脚本"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "检查并安装依赖..."
pip install -r requirements.txt

echo "启动服务器..."
echo "服务地址: http://localhost:8000"
echo "按 Ctrl+C 停止服务"
echo

python app.py