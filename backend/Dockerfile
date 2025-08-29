FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖（包括Ghostscript）
RUN apt-get update && apt-get install -y \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
RUN apt-get update && apt-get install -y curl &&     curl -fsSL https://deb.nodesource.com/setup_16.x | bash - &&     apt-get install -y nodejs &&     npm install -g yarn &&     rm -rf /var/lib/apt/lists/*

# Copy entire project (assuming backend and vue-app are siblings)
COPY . /app_root

# Build Vue.js app
WORKDIR /app_root/vue-app
RUN yarn install --frozen-lockfile
RUN yarn build

# Back to backend for Python dependencies and app start
WORKDIR /app_root/backend

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建上传目录
RUN mkdir -p uploads

# 暴露端口
EXPOSE 5000

# 启动应用
CMD ["python", "app.py"]