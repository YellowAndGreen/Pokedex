"""主应用入口模块

配置FastAPI应用实例，初始化数据库，并集成所有API路由。
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path  # 确保导入 Path

from app.database import create_db_and_tables, engine  # 引入数据库初始化函数和引擎
from app.routers import categories as categories_router  # 使用别名以匹配指南中的变量名
from app.routers import images as images_router  # 使用别名以匹配指南中的变量名
from app.routers import species_info_router
from app.routers import tags
from app.models import (
    species_info_models,  # 导入此模块以确保SQLModel元数据包含Species表
    image_models,  # 新增：确保 Image 和 ExifData 模型被加载
)
from app.core.config import settings

# 在应用启动时创建数据库表 (如果尚不存在)
# 注意：对于更复杂的迁移管理，应考虑使用 Alembic


def create_application() -> FastAPI:
    """创建并配置FastAPI应用实例

    返回:
        FastAPI: 配置完成的应用程序实例
    """
    # 确保基础存储目录存在 (服务层也会检查，但这里作为启动保障)
    settings.image_storage_root.mkdir(parents=True, exist_ok=True)
    settings.thumbnail_storage_root.mkdir(parents=True, exist_ok=True)

    # create_db_and_tables() 会在 on_startup_revised 中调用，这里不再需要重复调用

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
        origins_to_allow_str = [
            str(origin).rstrip("/") for origin in settings.backend_cors_origins
        ]
        processed_origins = []
        if (
            not origins_to_allow_str
            or origins_to_allow_str == [""]
            or origins_to_allow_str == ["*"]
        ):
            if settings.environment != "production":
                processed_origins = [
                    "http://localhost",
                    "http://localhost:5173",
                    "http://localhost:3000",
                    "http://localhost:8080",
                    "http://127.0.0.1:5173",
                    "*",
                ]
                # 保留此开发环境的默认设置警告
                print(
                    f"Info: backend_cors_origins not specifically set (or is '*'), defaulting for non-production: {processed_origins}"
                )
            elif origins_to_allow_str == ["*"]:
                print(
                    "CRITICAL SECURITY WARNING: 'allow_origins' is ['*'] in production based on backend_cors_origins. This is highly permissive."
                )
                processed_origins = ["*"]
            # else: # 生产环境且为空或无效时，processed_origins 仍为 [], 稍后会触发CRITICAL警告
        else:
            processed_origins = origins_to_allow_str

        if processed_origins:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=processed_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        elif settings.environment == "production":  # processed_origins 为空且在生产环境
            print(
                "CRITICAL: No effective CORS origins configured for production. Cross-origin requests will likely fail."
            )
    # else: # backend_cors_origins 未在settings中设置，通常Pydantic会用默认值或报错，这里不额外打印

    # --- 静态文件挂载 ---
    if (
        hasattr(settings, "IMAGES_DIR_NAME")
        and hasattr(settings, "IMAGES_DIR")
        and settings.IMAGES_DIR.exists()
    ):
        app.mount(
            f"/{settings.IMAGES_DIR_NAME.strip('/')}",
            StaticFiles(directory=settings.IMAGES_DIR),
            name="uploaded_images",
        )
    else:
        print(
            f"Warning: IMAGES_DIR_NAME or IMAGES_DIR not configured or directory does not exist. Skipping image static mount. Path: {getattr(settings, 'IMAGES_DIR', 'N/A')}"
        )

    if (
        hasattr(settings, "THUMBNAILS_DIR_NAME")
        and hasattr(settings, "THUMBNAILS_DIR")
        and settings.THUMBNAILS_DIR.exists()
    ):
        app.mount(
            f"/{settings.THUMBNAILS_DIR_NAME.strip('/')}",
            StaticFiles(directory=settings.THUMBNAILS_DIR),
            name="thumbnails",
        )
    else:
        print(
            f"Warning: THUMBNAILS_DIR_NAME or THUMBNAILS_DIR not configured or directory does not exist. Skipping thumbnails static mount. Path: {getattr(settings, 'THUMBNAILS_DIR', 'N/A')}"
        )

    # 包含API路由
    app.include_router(
        categories_router.router, prefix=settings.api_v1_prefix, tags=["Categories"]
    )
    app.include_router(
        images_router.router, prefix=settings.api_v1_prefix, tags=["Images"]
    )
    app.include_router(
        species_info_router.router,
        prefix=settings.api_v1_prefix,
        tags=["Species Information"],
    )
    app.include_router(tags.router, prefix=settings.api_v1_prefix, tags=["Tags"])
    return app


# 创建应用实例供uvicorn调用
app = create_application()


@app.on_event("startup")
def on_startup_revised():
    create_db_and_tables()  # 确保数据库和表已创建
    print(f"Application startup complete. Environment: {settings.environment}.")
    # CORS 配置日志现在在 create_application 中处理，如果需要确认最终配置，可以在这里添加简单的日志
    # 例如: print(f"CORS middleware added for origins: {app.user_middleware[...]} " if any cors middleware)


# 清理旧的事件处理器，避免重复执行
app.router.on_startup = []
app.add_event_handler("startup", on_startup_revised)


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.project_name}! Environment: {settings.environment}"
    }
