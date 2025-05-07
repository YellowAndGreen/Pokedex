"""主应用入口模块

配置FastAPI应用实例，初始化数据库，并集成所有API路由。
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

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
    # 调用数据库表创建函数
    # 这应该在应用启动的早期阶段执行，以确保表存在
    create_db_and_tables()

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

    # 挂载静态文件目录 (用于直接访问上传的图片和缩略图)
    # /static 将映射到 settings.static_dir 定义的目录
    # 注意：settings中可能需要定义 static_dir, image_storage_root, thumbnail_storage_root
    # 这里的路径需要根据实际的图片存储根目录来调整
    # 例如，如果图片存在于 static/uploads/images，则 StaticFiles(directory="static/uploads") 或更具体的路径
    if settings.static_files_mount_path and settings.static_files_directory:
        app.mount(
            settings.static_files_mount_path,
            StaticFiles(directory=settings.static_files_directory),
            name="static_uploads",
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
