#!/bin/bash

# --- 服务配置 ---
BACKEND_HOST="${1:-127.0.0.1}" # This is the user-specified accessible host
BACKEND_PORT="${2:-8000}"
FRONTEND_PORT="${3:-5173}"

# Determine the actual IP Uvicorn should bind to
UVICORN_BIND_IP="$BACKEND_HOST"
if [[ "$BACKEND_HOST" != "127.0.0.1" && "$BACKEND_HOST" != "localhost" ]]; then
  UVICORN_BIND_IP="0.0.0.0"
fi

# --- Tmux 会话名称 ---
BACKEND_TMUX_SESSION="pokedex_dev_backend" # Added _dev to distinguish
FRONTEND_TMUX_SESSION="pokedex_dev_frontend" # Added _dev to distinguish

# --- 目录定义 ---
SCRIPT_DIR_REALPATH=$(realpath "$(dirname "${BASH_SOURCE[0]}")") # Absolute path to deploy/dev
PROJECT_ROOT_DIR=$(realpath "$SCRIPT_DIR_REALPATH/../../") # Absolute path to project root

BACKEND_DIR="$PROJECT_ROOT_DIR/pokedex_backend"
FRONTEND_DIR="$PROJECT_ROOT_DIR/pokedex_frontend"
LOGS_DIR="$PROJECT_ROOT_DIR/logs" # Logs at project root

# --- 构造 URLs ---
EFFECTIVE_BACKEND_HOST_FOR_FRONTEND_API=$([ "$BACKEND_HOST" = "0.0.0.0" ] && echo "127.0.0.1" || echo "$BACKEND_HOST")
# VITE_API_BASE_URL should NOT end with /api, as apiService.ts appends it.
FRONTEND_VITE_API_BASE_URL_VALUE="http://${EFFECTIVE_BACKEND_HOST_FOR_FRONTEND_API}:${BACKEND_PORT}"
STATIC_FILES_BASE_URL="http://${EFFECTIVE_BACKEND_HOST_FOR_FRONTEND_API}:${BACKEND_PORT}"
FRONTEND_ORIGIN_HOST=$([ "$BACKEND_HOST" = "0.0.0.0" ] && echo "localhost" || echo "$BACKEND_HOST")
CSRF_ORIGINS='["*"]'

# 创建日志目录 (相对于项目根目录)
mkdir -p "$LOGS_DIR"

echo "--- 项目路径 ---"
echo "Project Root: $PROJECT_ROOT_DIR"
echo "Backend Dir: $BACKEND_DIR"
echo "Frontend Dir: $FRONTEND_DIR"
echo "Logs Dir: $LOGS_DIR"
echo "--- 配置详情 ---"
echo "后端服务期望访问主机 (User Arg for BACKEND_HOST): $BACKEND_HOST"
echo "后端服务实际监听IP (Uvicorn --host): $UVICORN_BIND_IP"
echo "后端服务端口 (SERVER_PORT for uvicorn): $BACKEND_PORT"
echo "前端开发服务器端口: $FRONTEND_PORT"
echo "后端 CSRF/CORS 允许来源 (BACKEND_CORS_ORIGINS): $CSRF_ORIGINS"
echo "前端 .env 中 VITE_API_BASE_URL 设置值: $FRONTEND_VITE_API_BASE_URL_VALUE"
echo "前端将调用的实际 API 服务 URL (VITE_API_BASE_URL + '/api'): ${FRONTEND_VITE_API_BASE_URL_VALUE}/api"
echo "前端访问静态文件的基础 URL (VITE_STATIC_FILES_BASE_URL): $STATIC_FILES_BASE_URL"
echo "后端 Tmux 会话名: $BACKEND_TMUX_SESSION"
echo "前端 Tmux 会话名: $FRONTEND_TMUX_SESSION"
echo "--------------------"

# 检查 tmux 是否安装
if ! command -v tmux &> /dev/null
then
    echo "错误: tmux 未安装。请先安装 tmux。"
    exit 1
fi

# ------------------ 后端配置与启动 (Tmux) ------------------
echo ""
echo "正在启动后端服务 (在 tmux 会话 '$BACKEND_TMUX_SESSION' 中)..."

# SERVER_HOST env var for the app should be the publicly accessible BACKEND_HOST
BACKEND_ENV_VARS="BACKEND_CORS_ORIGINS='$CSRF_ORIGINS' SERVER_HOST='$BACKEND_HOST' SERVER_PORT='$BACKEND_PORT'"
# Uvicorn uses UVICORN_BIND_IP for --host
BACKEND_START_CMD="cd '$BACKEND_DIR' && $BACKEND_ENV_VARS uvicorn app.main:app --host '$UVICORN_BIND_IP' --port '$BACKEND_PORT' --reload > '$LOGS_DIR/backend.log' 2>&1"

if tmux has-session -t "$BACKEND_TMUX_SESSION" 2>/dev/null; then
  echo "发现已存在的后端 tmux 会话 '$BACKEND_TMUX_SESSION'，将先终止它..."
  tmux kill-session -t "$BACKEND_TMUX_SESSION"
  sleep 1
fi

tmux new-session -d -s "$BACKEND_TMUX_SESSION" "$BACKEND_START_CMD"

if [ $? -eq 0 ]; then
    echo "后端服务已在 tmux 会话 '$BACKEND_TMUX_SESSION' 中启动。"
    echo "日志: $LOGS_DIR/backend.log"
    echo "要附加到后端会话，请运行: tmux attach-session -t $BACKEND_TMUX_SESSION"
else
    echo "错误: 启动后端服务失败。"
fi
sleep 5

# ------------------ 前端配置与启动 (Tmux) ------------------
echo ""
echo "正在启动前端服务 (在 tmux 会话 '$FRONTEND_TMUX_SESSION' 中)..."

# .env.development.local path is absolute now within FRONTEND_DIR
ENV_LOCAL_FILE="$FRONTEND_DIR/.env.development.local"
echo "VITE_API_BASE_URL=$FRONTEND_VITE_API_BASE_URL_VALUE" > "$ENV_LOCAL_FILE"
echo "VITE_STATIC_FILES_BASE_URL=$STATIC_FILES_BASE_URL" >> "$ENV_LOCAL_FILE"

echo "前端 $ENV_LOCAL_FILE 内容:"
cat "$ENV_LOCAL_FILE"
echo ""

# Log path is now absolute
FRONTEND_START_CMD="cd '$FRONTEND_DIR' && npm run dev -- --port '$FRONTEND_PORT' --host '0.0.0.0' > '$LOGS_DIR/frontend.log' 2>&1"

if tmux has-session -t "$FRONTEND_TMUX_SESSION" 2>/dev/null; then
  echo "发现已存在的前端 tmux 会话 '$FRONTEND_TMUX_SESSION'，将先终止它..."
  tmux kill-session -t "$FRONTEND_TMUX_SESSION"
  sleep 1
fi

tmux new-session -d -s "$FRONTEND_TMUX_SESSION" "$FRONTEND_START_CMD"

if [ $? -eq 0 ]; then
    echo "前端服务已在 tmux 会话 '$FRONTEND_TMUX_SESSION' 中启动。"
    echo "日志: $LOGS_DIR/frontend.log"
    echo "前端服务预计运行在: http://$([ "$BACKEND_HOST" = "0.0.0.0" ] && echo "localhost" || echo "$BACKEND_HOST"):$FRONTEND_PORT"
    echo "要附加到前端会话，请运行: tmux attach-session -t $FRONTEND_TMUX_SESSION"
else
    echo "错误: 启动前端服务失败。"
fi

echo ""
echo "所有服务已尝试在 tmux 会话中启动。"
echo "后端 API 设计访问地址: http://$BACKEND_HOST:$BACKEND_PORT"
echo "要查看所有 tmux 会话，请运行: tmux ls"
echo "要关闭服务，请运行: $SCRIPT_DIR_REALPATH/stop_services.sh (或从项目根目录: ./deploy/dev/stop_services.sh)" 