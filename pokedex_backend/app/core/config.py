"""
应用配置模块

包含所有环境相关配置设置，使用 Pydantic-Settings 进行验证和加载。
配置可以从环境变量或 .env 文件中读取。
"""

from pathlib import Path
from typing import List, Tuple, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根目录的确定 (假设config.py在 app/core/ 下)
APP_DIR = Path(__file__).resolve().parent.parent  # app/
PROJECT_ROOT = APP_DIR.parent  # pokedex_backend/
PROJECT_PARENT = PROJECT_ROOT.parent  # illustrated-photo-library/ (项目根目录)
# STATIC_ROOT = PROJECT_ROOT / "static" # pokedex_backend/static/ (如果static在项目根)
# 或者，如果 static 在 app/ 目录下，则：
APP_STATIC_ROOT = Path(__file__).resolve().parent.parent / "static"  # app/static/


class Settings(BaseSettings):
    """全局配置类

    属性将自动从环境变量或 .env 文件中加载。
    环境变量名通常是字段名的大写版本（如果 model_config 中 case_sensitive=False）。
    """

    # 项目信息
    project_name: str = "图鉴式图片管理工具"
    project_description: str = "一个使用FastAPI和Vue构建的图鉴式图片管理和展示工具"
    project_version: str = "1.0.0"

    # API 配置
    api_v1_prefix: str = "/api"  # 根据README.md 4.3节，统一前缀为 /api

    # 数据库配置 (环境变量: DATABASE_URL)
    # database_url: str = "sqlite:///./pokedex.db"  # SQLite文件将创建在运行命令的目录下
    # 使用项目根目录的绝对路径，确保始终使用同一个数据库文件
    database_url: str = f"sqlite:///{PROJECT_PARENT}/pokedex.db"

    # 文件存储路径 (基于 app/static/uploads/ 结构)
    # image_storage_root: Path = APP_STATIC_ROOT / "uploads" / "images"
    # thumbnail_storage_root: Path = APP_STATIC_ROOT / "uploads" / "thumbnails"
    # 为了与 main.py 中的 static_serve_directory = settings.image_storage_root.parent 兼容：
    # image_storage_root 的父目录即为包含 uploads 的目录，或者直接指向 uploads
    # README.md 6.1 后端项目目录结构: app/static/uploads/images/
    # 所以，基准点应该是 app/static/
    base_static_dir: Path = APP_STATIC_ROOT
    image_storage_root: Path = base_static_dir / "uploads" / "images"
    thumbnail_storage_root: Path = base_static_dir / "uploads" / "thumbnails"

    # 文件上传限制
    allowed_mime_types: List[str] = ["image/jpeg", "image/png", "image/gif"]
    max_image_size: int = 10 * 1024 * 1024  # 10MB

    # 缩略图参数
    thumbnail_size: Tuple[int, int] = (256, 256)
    thumbnail_quality: int = 85  # JPEG 缩略图质量

    # CORS 配置 (环境变量: BACKEND_CORS_ORIGINS - 逗号分隔的字符串)
    # pydantic-settings 会自动将环境变量中逗号分隔的字符串转换为 List[str]
    backend_cors_origins: List[str] = ["*"]

    # 环境配置 (development, production, staging, etc.)
    environment: str = "development"

    # 静态文件服务 (指南推荐方式)
    IMAGES_DIR_NAME: str = "uploaded_images" # URL路径名，对应指南前端 VITE_IMAGES_DIR_NAME
    IMAGES_DIR: Path = image_storage_root # 服务器上实际存储图片的文件夹路径
    THUMBNAILS_DIR_NAME: str = "thumbnails" # URL路径名，对应指南前端 VITE_THUMBNAILS_DIR_NAME
    THUMBNAILS_DIR: Path = thumbnail_storage_root # 服务器上实际存储缩略图的文件夹路径

    # 现有静态文件服务相关配置 (main.py 中会用到这些来推断挂载点和目录) - 这些可以保留，但下方挂载将优先使用上面的新配置
    # static_files_mount_url: str = "/static/uploads" # 由main.py硬编码或推断
    # static_files_serve_dir: Path = base_static_dir / "uploads" # 由main.py推断

    # Uvicorn服务器配置 (可选，用于main.py中的if __name__ == "__main__":)
    server_host: str = "127.0.0.1"
    server_port: int = 8000
    log_level: str = "info"

    # Pydantic-Settings 配置
    model_config = SettingsConfigDict(
        env_file=".env",  # 指定 .env 文件名
        env_file_encoding="utf-8",  # .env 文件编码
        case_sensitive=False,  # 环境变量名不区分大小写
        extra="ignore",  # 忽略 .env 文件中未在Settings类中定义的额外变量
    )


settings = Settings()

# 在这里可以添加一些启动时的路径检查或创建，但更推荐在main.py或服务初始化时进行
# settings.image_storage_root.mkdir(parents=True, exist_ok=True)
# settings.thumbnail_storage_root.mkdir(parents=True, exist_ok=True)
