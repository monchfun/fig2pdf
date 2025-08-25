#!/bin/bash

# 卸载旧的Gradio/FastAPI相关依赖，确保环境干净
pip uninstall fastapi starlette uvicorn -y

# 创建上传目录
mkdir -p uploads

# 启动Flask应用
echo "Starting Figma2PDF Flask app on port $PORT..."
gunicorn --bind 0.0.0.0:$PORT app:app