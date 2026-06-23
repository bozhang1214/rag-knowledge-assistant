#!/bin/bash
# =====================================================
# 前端启动脚本（在宿主机执行，实际运行在 shared-frontend 容器内）
# =====================================================

set -e

# 加载项目 ID
if [ -f ".env.project" ]; then
    source .env.project
fi
PROJECT_ID=${PROJECT_ID:-0}
FRONTEND_PORT=$((3000 + PROJECT_ID))
BACKEND_PORT=$((8000 + PROJECT_ID))

# 获取当前项目名称
PROJECT_NAME=$(basename "$(pwd)")
PROJECT_PATH="/workspaces/$PROJECT_NAME"

echo "🚀 启动前端服务 (项目: $PROJECT_NAME, ID=$PROJECT_ID, 端口=$FRONTEND_PORT)"
echo "项目容器内路径: $PROJECT_PATH"
echo "后端端口 (宿主机计算): $BACKEND_PORT"

# 检查容器是否运行
if ! docker ps --format '{{.Names}}' | grep -q "^shared-frontend$"; then
    echo "❌ 容器 shared-frontend 未运行，请先执行 docker-compose up -d"
    exit 1
fi

# 在容器内执行安装和启动
docker exec -it shared-frontend sh -c "
    set -e
    cd $PROJECT_PATH/frontend
    echo '📦 安装前端依赖...'
    npm install
    echo '✅ 依赖安装完成'
    echo '🚀 启动 Next.js 开发服务器...'
    export NEXT_PUBLIC_API_BASE=http://localhost:$BACKEND_PORT
    echo '🔍 容器内环境变量 NEXT_PUBLIC_API_BASE='\$NEXT_PUBLIC_API_BASE
    npm run dev -- --port $FRONTEND_PORT
"
