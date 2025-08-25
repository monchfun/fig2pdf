#!/bin/bash

# 创建上传目录
mkdir -p uploads

# 设置环境变量
export GRADIO_SERVER_NAME="0.0.0.0"
export GRADIO_SERVER_PORT="$PORT"

# 启动Gradio应用
echo "Starting Figma2PDF on port $PORT..."
python gradio_app.py