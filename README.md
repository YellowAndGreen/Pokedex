# Pokedex 项目

Pokedex 是一个全栈宝可梦图鉴应用程序，允许用户浏览、搜索和查看各种宝可梦的详细信息和图片。它采用现代化的前后端技术栈构建。

## 目录

- [技术方案](#技术方案)
- [项目结构](#项目结构)
- [环境准备](#环境准备)
- [后端设置与运行](#后端设置与运行)
- [前端设置与运行](#前端设置与运行)
- [数据导入](#数据导入)
- [API 文档](#api-文档)
- [运行测试](#运行测试)

## 技术方案

本项目采用前后端分离的架构。

**后端 (Backend):**

* **语言/框架:** Python 3.9+, FastAPI
* **ORM/数据库:** SQLModel (构建于 Pydantic 和 SQLAlchemy 之上), 默认使用 SQLite，支持 PostgreSQL
* **数据校验:** Pydantic (SQLModel 内建支持)
* **异步处理:** `async/await`
* **Web 服务器:** Uvicorn
* **主要依赖:**
    * `fastapi>=0.68.0`: Web 框架
    * `sqlmodel>=0.0.8`: ORM 及数据模型定义
    * `uvicorn>=0.15.0`: ASGI 服务器
    * `pydantic>=2.0.0` (由 SQLModel 和 FastAPI 使用)
    * `pydantic-settings>=1.0.0`: 配置管理
    * `aiofiles>=0.7.0`: 异步文件操作
    * `python-multipart>=0.0.5`: 用于文件上传
    * `httpx`: HTTP 客户端 (用于脚本或服务间通信)
    * `pillow>=9.0.0`: 图像处理
    * `pypinyin>=0.39.0` (可能用于特定中文字符串处理)
    * `aiosqlite` (用于 SQLite 异步, 通常作为 SQLModel/SQLAlchemy 的可选依赖安装)
    * `psycopg2-binary` (可选, 用于 PostgreSQL, 通常作为 SQLModel/SQLAlchemy 的可选依赖安装)
    * `asyncpg` (可选, 用于 PostgreSQL 异步, 通常作为 SQLModel/SQLAlchemy 的可选依赖安装)


**前端 (Frontend):**

* **语言/框架:** TypeScript, Vue.js (Vue 3)
* **构建工具:** Vite
* **状态管理:** Pinia
* **路由:** Vue Router
* **HTTP 客户端:** Axios
* **UI (推断):** 根据 `style.css` 和标准 Vue 项目结构，可能使用原生 CSS 或特定 UI 库（未明确指定）。
* **主要依赖 (`package.json`):**
    * `vue`:核心框架
    * `vue-router`: 路由
    * `pinia`: 状态管理
    * `axios`: HTTP 请求
    * `vite`: 构建工具
    * `typescript`: 语言

**API 文档:**

* OpenAPI (通过 FastAPI 自动生成 Swagger UI 和 ReDoc)

**测试:**

* **后端:** Pytest
* **前端:** Vitest

## 项目结构
```
.
├── docs/                      # 项目文档 (设计文档, API 定义, 数据模型等)
│   ├── api/
│   └── data_models/
│   └── design/
├── pokedex_backend/           # 后端 FastAPI 应用
│   ├── app/                   # 后端核心代码
│   │   ├── core/              # 配置 (config.py)
│   │   ├── crud/              # CRUD 数据库操作逻辑
│   │   ├── models/            # SQLModel 数据模型
│   │   ├── routers/           # API 路由定义
│   │   ├── services/          # 业务逻辑服务 (如文件存储, 图像处理)
│   │   ├── database.py        # 数据库连接与初始化 (使用 SQLModel)
│   │   └── main.py            # FastAPI 应用入口
│   ├── requirements.txt       # 后端 Python 依赖
│   └── .env.example           # 后端环境变量示例
├── pokedex_frontend/          # 前端 Vue.js 应用
│   ├── public/                # Vite public 目录
│   ├── src/                   # 前端源码
│   │   ├── assets/            # 静态资源 (如图片, 字体)
│   │   ├── components/        # Vue 组件 (推断的标准结构)
│   │   ├── router/            # Vue Router 配置 (index.ts)
│   │   ├── services/          # API 服务 (apiService.ts)
│   │   ├── store/             # Pinia 状态管理 (categoryStore.ts, imageStore.ts)
│   │   ├── types/             # TypeScript 类型定义
│   │   ├── views/             # Vue 页面/视图组件 (推断的标准结构)
│   │   ├── App.vue            # 根 Vue 组件
│   │   ├── main.ts            # 前端应用入口
│   │   └── style.css          # 全局样式
│   ├── tests/                 # 前端单元测试和集成测试
│   ├── index.html             # HTML 入口文件
│   ├── package.json           # 前端项目元数据和依赖
│   ├── vite.config.ts         # Vite 配置文件
│   ├── tsconfig.json          # TypeScript 配置文件
│   └── .env.example           # 前端环境变量示例
├── scripts/                   # 数据导入、迁移等辅助脚本
│   ├── folder2db/             # 将文件夹中的图片和分类数据导入数据库的脚本
│   │   ├── README.md
│   │   └── folder2db.py
│   ├── import_species_data.py # 导入宝可梦物种数据的脚本
│   └── ...
└── tests/                     # 包含后端测试的目录
├── backend/               # 后端测试 (单元测试, 集成测试)
│   ├── conftest.py
│   └── ...
└── requirements.txt       # 后端测试相关的依赖
```

## 环境准备

* **Python:** 3.9 或更高版本。
* **Node.js:** LTS 版本 (例如 v18.x 或 v20.x)，同时会安装 npm。或者您也可以使用 yarn。
* **Git:** 用于克隆项目。

## 后端设置与运行

1.  **克隆项目 (如果尚未克隆):**
    ```bash
    git clone <your-repository-url>
    cd <project-root-directory>/pokedex_backend
    ```

2.  **创建虚拟环境、安装依赖:**
    ```bash
    conda create -n pokedex python=3.9
    conda activate pokedex
    python -m pip install --upgrade pip setuptools -i https://pypi.tuna.tsinghua.edu.cn/simple
    pip install -r pokedex_backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    ```

3.  **配置环境变量:**
    * 复制 `.env.example` (如果存在，否则手动创建) 为 `.env` 文件。
        ```bash
        cp .env.example .env  # 如果 .env.example 不存在，请根据 pokedex_backend/app/core/config.py 手动创建 .env
        ```
    * 编辑 `.env` 文件。对于 SQLModel，SQLite 连接字符串通常是 `sqlite+aiosqlite:///./pokedex.db` 或 `sqlite:///./pokedex.db` (取决于是否使用异步驱动)。
        * 示例 SQLite (异步): `DATABASE_URL="sqlite+aiosqlite:///./pokedex.db"`
        * 示例 SQLite (同步): `DATABASE_URL="sqlite:///./pokedex.db"`
4.  **数据库初始化:**
    FastAPI 应用启动时，如果配置了 SQLModel 的 `create_db_and_tables` 功能 (通常在 `main.py` 或 `database.py` 中调用)，会自动创建数据库表。

5.  **运行后端开发服务器:**
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    后端服务将在 `http://localhost:8000` 上运行。

## 前端设置与运行

1.  **导航到前端目录:**
    ```bash
    cd <project-root-directory>/pokedex_frontend
    ```

2.  **安装依赖:**
    ```bash
    npm install
    # 或者如果您使用 yarn
    # yarn install
    ```

3.  **配置环境变量:**
    * 复制 `pokedex_frontend/.env.example` (如果存在) 为 `.env`。如果不存在，则手动创建一个 `.env` 文件。
    * 在 `pokedex_frontend/.env` 文件中设置后端 API 的基础 URL:
        ```env
        VITE_API_BASE_URL=http://localhost:8000/api/v1
        ```
        (请确保此 URL 与您的后端配置匹配，特别是 `API_V1_STR` 在 `pokedex_backend/app/core/config.py` 中的定义)。

4.  **运行前端开发服务器:**
    ```bash
    npm run dev
    # 或者如果您使用 yarn
    # yarn dev
    ```
    前端应用通常会在 `http://localhost:5173` (Vite 默认端口) 上运行。请检查终端输出以获取确切的 URL。

## 数据导入

项目包含用于填充数据库的脚本。这些脚本通常需要在后端服务运行后执行，或者配置为直接连接到数据库。

1.  **导入分类和图片数据:**
    * 脚本位于 `scripts/folder2db/`。
    * 请参考 `scripts/folder2db/README.md` 获取详细的使用说明。
    * 通常，您可能需要运行类似以下的命令 (确保 Python 环境已激活，并且您在项目根目录或 `scripts/folder2db/` 目录中):
        ```bash
        # 示例：假设您在 scripts/folder2db 目录下
        python folder2db.py --images_path /path/to/your/pokemon_images --categories_path /path/to/your/categories_definition.json
        ```
        此脚本使用 `ApiClient` (`scripts/folder2db/api_client.py`) 与后端 API 交互，因此后端服务需要正在运行。

2.  **导入宝可梦物种数据:**
    * 使用 `scripts/import_species_data.py` 脚本。
    * 此脚本可能需要配置数据库连接或 API 端点。请查看脚本内容以了解其具体要求。
    * 运行示例 (确保 Python 环境已激活):
        ```bash
        python scripts/import_species_data.py --file_path /path/to/your/species_data.csv
        ```

**注意:** 数据导入脚本的具体用法和所需数据源的格式应在各自的 README 文件或脚本注释中有更详细的说明。

## API 文档

后端服务启动后，可以通过以下路径访问自动生成的 API 文档：

* **Swagger UI:** `http://localhost:8000/api/docs`
* **ReDoc:** `http://localhost:8000/api/redoc`

## 运行测试

**后端测试:**

1.  确保已安装测试依赖 (通常包含在主 `requirements.txt` 或 `tests/requirements.txt` 中)。您提供的依赖列表中已包含 `pytest-cov`。
    ```bash
    pip install -r tests/requirements.txt # 如果测试依赖是分开的
    # 或者 pip install pytest pytest-cov (如果未在 requirements.txt 中)
    ```
2.  导航到 `tests/backend/` 目录或项目根目录 (取决于 Pytest 配置)。
3.  运行测试:
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    pytest
    ```
    (可能需要根据 `pokedex_backend/app/core/config.py` 中的 `TEST_DATABASE_URL` 配置测试数据库。)

**前端测试:**

1.  导航到前端目录:
    ```bash
    cd <project-root-directory>/pokedex_frontend
    ```
2.  运行单元测试 (Vitest):
    ```bash
    npm run test
    ```