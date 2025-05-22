"""主应用入口模块

配置FastAPI应用实例，初始化数据库，并集成所有API路由。
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path  # 确保导入 Path

from app.database import create_db_and_tables, engine  # 引入数据库初始化函数和引擎
from app.routers import categories as categories_router # 使用别名以匹配指南中的变量名
from app.routers import images as images_router # 使用别名以匹配指南中的变量名
from app.routers import species_info_router
from app.models import (
    species_info_models,
)  # 导入此模块以确保SQLModel元数据包含Species表
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

    # 调用 create_db_and_tables 之前，确保所有模型（包括species_info_models中的）已被导入
    # 上面的 'from app.models import species_info_models' 应该已确保这一点
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
        # 将 settings.backend_cors_origins (List[AnyHttpUrl]) 转换为 List[str]
        origins_to_allow_str = [str(origin).rstrip('/') for origin in settings.backend_cors_origins]
        
        # 指南中的逻辑包含了更详细的 origins 处理，我们在此应用它
        # 注意：指南中使用 settings.BACKEND_CORS_ORIGINS (可能是字符串列表或逗号分隔的字符串)
        # 现有代码使用 settings.backend_cors_origins (Pydantic的List[AnyHttpUrl])
        # 我们将基于现有代码的类型，但借鉴指南中的逻辑（例如空列表或开发默认值）
        
        processed_origins = []
        if not origins_to_allow_str or origins_to_allow_str == [''] or origins_to_allow_str == ['*']: # 稍微调整了指南的判断逻辑以适应 List[str]
            if settings.environment != "production": # 指南中使用 settings.ENVIRONMENT
                processed_origins = [ # 开发时默认值
                    "http://localhost", "http://localhost:5173",
                    "http://localhost:3000", "http://localhost:8080",
                    "http://127.0.0.1:5173", # 添加此源
                ]
                print(f"Warning: backend_cors_origins not robustly set (or is '*'), defaulting to: {processed_origins} for non-production environment.")
            elif origins_to_allow_str == ['*']:
                 print("CRITICAL SECURITY WARNING: 'allow_origins' is ['*'] in production based on backend_cors_origins.")
                 processed_origins = ["*"] # 明确允许 '*' 如果在生产中这样设置了
            else: # 生产环境且未设置为 '*' 但可能为空或无效
                print("Warning: backend_cors_origins is empty or not properly configured for production. CORS might not work as expected.")
                processed_origins = [] # 明确设置为空列表，表示不允许任何源
        else:
            processed_origins = origins_to_allow_str

        if processed_origins: # 仅当有有效源时才添加中间件
            app.add_middleware(
                CORSMiddleware,
                allow_origins=processed_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        elif settings.environment == "production":
             print("CRITICAL: No CORS origins configured for production. Cross-origin requests will likely fail.")
    else:
        print("Warning: backend_cors_origins not configured in settings. CORS middleware not added.")

    # --- 静态文件挂载 (依照指南) ---
    # 移除旧的静态文件挂载逻辑:
    # static_serve_directory = settings.image_storage_root.parent
    # static_mount_url = "/static/uploads"
    # app.mount(
    #     static_mount_url,
    #     StaticFiles(directory=static_serve_directory),
    #     name="uploaded_content",
    # )
    # print(f"Mounted static content from {static_serve_directory} at {static_mount_url}")

    # 使用指南推荐的挂载方式
    # 确保 settings 中的路径是 Path 对象，如果它们是从字符串解析的
    # (在我们的 config.py 中，IMAGES_DIR 和 THUMBNAILS_DIR 已经是 Path 对象)
    if hasattr(settings, 'IMAGES_DIR_NAME') and hasattr(settings, 'IMAGES_DIR') and settings.IMAGES_DIR.exists():
        app.mount(f"/{settings.IMAGES_DIR_NAME.strip('/')}", StaticFiles(directory=settings.IMAGES_DIR), name="uploaded_images")
        print(f"Mounted images from {settings.IMAGES_DIR} at /{settings.IMAGES_DIR_NAME.strip('/')}")
    else:
        print(f"Warning: settings.IMAGES_DIR_NAME or settings.IMAGES_DIR not configured or directory does not exist. Skipping image static mount. Path: {getattr(settings, 'IMAGES_DIR', 'N/A')}")

    if hasattr(settings, 'THUMBNAILS_DIR_NAME') and hasattr(settings, 'THUMBNAILS_DIR') and settings.THUMBNAILS_DIR.exists():
        app.mount(f"/{settings.THUMBNAILS_DIR_NAME.strip('/')}", StaticFiles(directory=settings.THUMBNAILS_DIR), name="thumbnails")
        print(f"Mounted thumbnails from {settings.THUMBNAILS_DIR} at /{settings.THUMBNAILS_DIR_NAME.strip('/')}")
    else:
        print(f"Warning: settings.THUMBNAILS_DIR_NAME or settings.THUMBNAILS_DIR not configured or directory does not exist. Skipping thumbnails static mount. Path: {getattr(settings, 'THUMBNAILS_DIR', 'N/A')}")

    # 包含API路由
    # 所有来自 categories 和 images 路由器的路径都将以 settings.api_v1_prefix 为前缀
    app.include_router(categories_router.router, prefix=settings.api_v1_prefix, tags=["Categories"])
    app.include_router(images_router.router, prefix=settings.api_v1_prefix, tags=["Images"])
    # 新增：包含物种信息API路由
    # 使用 settings.api_v1_prefix 作为基础，并添加一个特定的路径段 /species
    # The tag "Species Information" is already defined in species_info_router.py
    app.include_router(
        species_info_router.router, prefix=settings.api_v1_prefix, tags=["Species Information"]
    )

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

@app.on_event("startup")
def on_startup_revised():
    create_db_and_tables()
    print(f"Application startup complete. Environment: {settings.environment}")
    if settings.backend_cors_origins:
        temp_origins_for_log = []
        if isinstance(settings.backend_cors_origins, list):
             temp_origins_for_log = [str(origin).rstrip('/') for origin in settings.backend_cors_origins]
        elif isinstance(settings.backend_cors_origins, str):
             temp_origins_for_log = [s.strip() for s in settings.backend_cors_origins.split(',')]

        if not temp_origins_for_log or temp_origins_for_log == [''] or temp_origins_for_log == ['*']:
            if settings.environment != "production":
                default_dev_origins = ["http://localhost", "http://localhost:5173", "http://localhost:3000", "http://localhost:8080"]
                print(f"Configured CORS origins (defaulted for dev): {default_dev_origins}")
            elif temp_origins_for_log == ['*']:
                 print(f"Configured CORS origins: ['*']")
            else:
                print(f"Warning: backend_cors_origins is empty or not properly configured. Logged origins: {temp_origins_for_log}")
        else:
            print(f"Configured CORS origins: {temp_origins_for_log}")
    else:
        print("CORS not configured (BACKEND_CORS_ORIGINS not set).")

app.router.on_startup = []
app.add_event_handler("startup", on_startup_revised)

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.project_name}! Environment: {settings.environment}"}
