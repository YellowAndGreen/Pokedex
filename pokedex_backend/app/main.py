"""主应用入口模块

配置FastAPI应用实例，初始化数据库，并集成所有API路由。
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path  # 确保导入 Path

from app.database import create_db_and_tables, engine  # 引入数据库初始化函数和引擎
from app.routers import categories, images  # 引入API路由模块
from app.core.config import settings

# 在应用启动时创建数据库表 (如果尚不存在)
# 注意：对于更复杂的迁移管理，应考虑使用 Alembic
# @app.on_event("startup") # FastAPI < 0.95.0
# def on_startup():
#     create_db_and_tables()
# SQLModel.metadata.create_all(engine) # 另一种方式，如果不在 on_startup 中


def create_application() -> FastAPI:
    """创建并配置FastAPI应用实例

    返回:
        FastAPI: 配置完成的应用程序实例
    """
    # 确保基础存储目录存在 (服务层也会检查，但这里作为启动保障)
    settings.image_storage_root.mkdir(parents=True, exist_ok=True)
    settings.thumbnail_storage_root.mkdir(parents=True, exist_ok=True)

    create_db_and_tables()  # 创建数据库表 (如果尚不存在)

    app = FastAPI(
        title=settings.project_name,
        description=settings.project_description,
        version=settings.project_version,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",  # API文档路径
        docs_url=f"{settings.api_v1_prefix}/docs",  # Swagger UI
        redoc_url=f"{settings.api_v1_prefix}/redoc",  # ReDoc UI
    )

    # 配置CORS (跨源资源共享)
    if settings.backend_cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.backend_cors_origins],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # 根据README.md, 图片存储在 static/uploads/images 和 static/uploads/thumbnails
    # 因此，我们应该将 static/uploads 目录挂载，以便能通过URL访问其下的内容。
    # 例如: /static_uploads/images/aa/bb/uuid.jpg
    #       /static_uploads/thumbnails/aa/bb/uuid_thumb.jpg
    # 这里的 `settings.static_files_directory` 应指向 `static/uploads` 所在的物理路径。
    # 如果 settings.image_storage_root 是 "app/static/uploads/images",
    # 那么 settings.static_files_directory 应该是 "app/static/uploads" (或其父目录，取决于挂载点)
    # 假设 settings.static_files_directory = Path("app/static/uploads")
    # 并且 settings.static_files_mount_path = "/static/uploads" (与README一致)

    # 更直接的方式是使用 image_storage_root.parent 作为 StaticFiles 的目录
    # 这样，如果 image_storage_root = "static/uploads/images", parent是 "static/uploads"
    # URL 仍将从挂载点开始，例如 /static_mounted/images/... 或 /static_mounted/thumbnails/...
    # 根据README 4.4，API响应中的URL会基于 /static/uploads/images/... 构建
    # 所以，我们需要挂载 "static/uploads" 目录到 "/static/uploads" URL路径

    # 假设项目根目录下有 static/uploads 结构
    # 如果 settings.image_storage_root = Path("static/uploads/images")
    # 则其父目录 settings.image_storage_root.parent 是 Path("static/uploads")
    # 这是我们想要作为静态服务根的目录
    static_serve_directory = settings.image_storage_root.parent
    static_mount_url = "/static/uploads"  # 与README中的URL结构一致

    app.mount(
        static_mount_url,
        StaticFiles(directory=static_serve_directory),
        name="uploaded_content",
    )

    # 包含API路由
    # 所有来自 categories 和 images 路由器的路径都将以 settings.api_v1_prefix 为前缀
    app.include_router(categories.router, prefix=settings.api_v1_prefix)
    app.include_router(images.router, prefix=settings.api_v1_prefix)

    return app


# 创建应用实例供uvicorn调用
app = create_application()

# 可选：添加应用启动和关闭事件 (FastAPI >= 0.95.0 推荐使用 lifespan)
# from contextlib import asynccontextmanager
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("应用启动中...")
#     create_db_and_tables() # 确保表已创建
#     yield
#     print("应用关闭中...")
# app = FastAPI(lifespan=lifespan, ...)
