# 开发环境服务启停脚本说明

本目录包含用于在开发环境中便捷启动和停止 Pokedex 应用前后端服务的脚本。这些脚本使用 `tmux` 在后台管理服务进程，确保即使终端关闭，服务也能继续运行。

## 目录结构

- `start_services.sh`: 启动前端和后端服务的脚本。
- `stop_services.sh`: 关闭由 `start_services.sh` 启动的服务脚本。
- `README.md`: 本说明文件。

## 先决条件

在运行这些脚本之前，请确保您的开发环境满足以下条件：

1.  **`tmux` 已安装**:
    脚本使用 `tmux` 来管理后台会话。如果未安装，请根据您的操作系统进行安装（例如，在 Ubuntu/Debian 上：`sudo apt update && sudo apt install tmux`）。
2.  **后端环境**:
    *   Python 环境已配置，且 `pokedex_backend` 项目的依赖已安装（通常通过 `pip install -r requirements.txt` 在 `pokedex_backend` 目录下完成）。
    *   `uvicorn` 已安装并可执行。
3.  **前端环境**:
    *   Node.js 和 npm (或 yarn) 已安装。
    *   `pokedex_frontend` 项目的依赖已安装（通常通过在 `pokedex_frontend` 目录下运行 `npm install` 或 `yarn install` 完成）。
4.  **`realpath` 命令**:
    脚本使用 `realpath` 来解析路径，这在大多数 Linux 发行版中是标准命令。

## 使用步骤

### 1. 赋予脚本执行权限

在首次使用之前，您需要给这两个脚本添加执行权限。在项目根目录的终端中执行：

```bash
chmod +x deploy/dev/start_services.sh
chmod +x deploy/dev/stop_services.sh
```

### 2. 启动服务 (`start_services.sh`)

此脚本会分别在名为 `pokedex_dev_backend` 和 `pokedex_dev_frontend` 的 `tmux` 会话中启动后端和前端服务。

**默认启动**:
从项目根目录运行：
```bash
./deploy/dev/start_services.sh
```
这将使用以下默认配置：
- 后端服务主机: `127.0.0.1`
- 后端服务端口: `8000`
- 前端开发服务器端口: `5173`

**自定义参数启动**:
您可以传递参数来覆盖默认配置：
```bash
./deploy/dev/start_services.sh <BACKEND_HOST> <BACKEND_PORT> <FRONTEND_PORT>
```
例如，要让后端监听所有接口 (`0.0.0.0`) 的 `8080` 端口，前端使用 `3000` 端口：
```bash
./deploy/dev/start_services.sh 0.0.0.0 8080 3000
```
脚本会自动配置后端的 `CSRF_ORIGINS` 和前端的 `VITE_API_BASE_URL`、`VITE_STATIC_FILES_BASE_URL`。

### 3. 停止服务 (`stop_services.sh`)

此脚本会终止由 `start_services.sh` 创建的 `tmux` 会话，从而停止服务。

从项目根目录运行：
```bash
./deploy/dev/stop_services.sh
```

### 4. 查看日志

服务启动后，其标准输出和错误输出会被重定向到项目根目录下的 `logs/` 文件夹中：
- 后端日志: `logs/backend.log`
- 前端日志: `logs/frontend.log`

## 注意事项

- 如果脚本提示 `tmux: command not found`，请确保 `tmux` 已正确安装并在您的 `PATH` 中。
- 如果后端或前端启动失败，请检查对应的日志文件 (`logs/backend.log` 或 `logs/frontend.log`) 以及 `tmux` 会话内的输出（通过附加到会话查看）以获取详细错误信息。
- 脚本会尝试在启动前终止同名的旧 `tmux` 会话，以避免冲突。
- 前端服务启动时，会在 `pokedex_frontend/` 目录下创建一个临时的 `.env.development.local` 文件，用于注入 API 地址等配置。此文件会在服务停止时被 `stop_services.sh` 脚本清理。 