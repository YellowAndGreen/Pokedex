"""主应用入口模块

配置FastAPI应用实例并初始化核心组件
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import create_db_and_tables
from app.routers import categories, images
from app.core.config import settings


def create_app() -> FastAPI:
    """创建并配置FastAPI应用实例
    
    返回:
        FastAPI: 配置完成的应用程序实例
    """
    app = FastAPI(
        title="图鉴图片管理系统",
        description="基于FastAPI和SQLModel的图片管理后端系统",
        version="1.0.0"
    )
    
    # 挂载静态文件路由
    app.mount(
        "/static", 
        StaticFiles(directory=str(settings.image_storage_root.parent)), 
        name="uploads"
    )
    
    # 包含API路由
    app.include_router(categories.router)
    app.include_router(images.router)
    
    return app


app: FastAPI = create_app()


@app.on_event("startup")
async def startup_event() -> None:
    """应用启动事件处理
    
    初始化数据库和存储目录
    """
    create_db_and_tables()
    settings.image_storage_root.mkdir(parents=True, exist_ok=True)
    settings.thumbnail_storage_root.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.server_host,
        port=settings.server_port,
        log_level=settings.log_level.lower()
    )
