#!/bin/bash
# =====================================================
# 后端启动脚本（在宿主机执行，实际运行在 shared-backend 容器内）
# =====================================================

set -e

# 加载项目 ID（用于分配端口）
if [ -f ".env.project" ]; then
    source .env.project
fi
PROJECT_ID=${PROJECT_ID:-0}
BACKEND_PORT=$((8000 + PROJECT_ID))

# 获取当前项目名称（即当前目录名，用于定位容器内路径）
PROJECT_NAME=$(basename "$(pwd)")
PROJECT_PATH="/workspaces/$PROJECT_NAME"

echo "🚀 启动后端服务 (项目: $PROJECT_NAME, ID=$PROJECT_ID, 端口=$BACKEND_PORT)"
echo "项目容器内路径: $PROJECT_PATH"

# 检查容器是否运行
if ! docker ps --format '{{.Names}}' | grep -q "^shared-backend$"; then
    echo "❌ 容器 shared-backend 未运行，请先执行 docker-compose up -d"
    exit 1
fi

# 在容器内执行安装和启动
docker exec -it shared-backend bash -c "
    set -e
    # 设置 Hugging Face 镜像源[reference:4][reference:5]
    export HF_ENDPOINT=https://hf-mirror.com
    cd $PROJECT_PATH/backend
    echo '📦 安装 Python 依赖（使用清华镜像）...'
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 120 -r requirements.txt
    echo '✅ 依赖安装完成'
    echo '🚀 启动 uvicorn...'
    export PYTHONPATH=\$PYTHONPATH:$PROJECT_PATH/backend
    uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload
"
