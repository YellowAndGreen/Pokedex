#!/bin/bash

# --- 目录定义 ---
SCRIPT_DIR_REALPATH=$(realpath "$(dirname "${BASH_SOURCE[0]}")") # Absolute path to deploy/dev
PROJECT_ROOT_DIR=$(realpath "$SCRIPT_DIR_REALPATH/../../") # Absolute path to project root

FRONTEND_DIR="$PROJECT_ROOT_DIR/pokedex_frontend"

# Tmux 会话名称 (应与 start_services.sh 中的定义一致)
BACKEND_TMUX_SESSION="pokedex_dev_backend"
FRONTEND_TMUX_SESSION="pokedex_dev_frontend"

# 检查 tmux 是否安装
if ! command -v tmux &> /dev/null
then
    echo "错误: tmux 未安装。请先安装 tmux。"
    exit 1
fi

stop_tmux_session() {
    local service_name="$1"
    local session_name="$2"

    if tmux has-session -t "$session_name" 2>/dev/null; then
        echo "正在关闭 $service_name (tmux 会话: $session_name)..."
        tmux kill-session -t "$session_name"
        if [ $? -eq 0 ]; then
            echo "$service_name (tmux 会话: $session_name) 已成功关闭。"
        else
            echo "错误: 关闭 $service_name (tmux 会话: $session_name) 失败。"
        fi
    else
        echo "$service_name tmux 会话 '$session_name' 未找到，可能未运行或未通过脚本启动。"
    fi
}

echo "--- 开始关闭服务 (通过 tmux 会话) ---"

# 关闭后端服务 tmux 会话
stop_tmux_session "后端服务" "$BACKEND_TMUX_SESSION"

# 关闭前端服务 tmux 会话
stop_tmux_session "前端服务" "$FRONTEND_TMUX_SESSION"

# 清理前端临时的 .env 文件 (path is absolute)
ENV_LOCAL_FILE="$FRONTEND_DIR/.env.development.local"
if [ -f "$ENV_LOCAL_FILE" ]; then
    rm "$ENV_LOCAL_FILE"
    echo "已清理前端临时 .env 文件: $ENV_LOCAL_FILE"
fi

echo ""
echo "所有服务已尝试关闭。"
echo "你可以通过 'tmux ls' 检查是否还有残留的 tmux 会话。" 