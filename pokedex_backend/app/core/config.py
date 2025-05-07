"""
应用配置模块

包含所有环境相关配置设置，使用 Pydantic 进行验证和加载。
配置可以从环境变量或 .env 文件中读取。
"""

from pathlib import Path
from typing import List, Tuple, Optional

from pydantic import BaseSettings, validator

# 项目根目录的确定 (假设config.py在 app/core/ 下)
# APP_DIR = Path(__file__).resolve().parent.parent # app/
# PROJECT_ROOT = APP_DIR.parent # pokedex_backend/
# STATIC_ROOT = PROJECT_ROOT / "static" # pokedex_backend/static/ (如果static在项目根)
# 或者，如果 static 在 app/ 目录下，则：
APP_STATIC_ROOT = Path(__file__).resolve().parent.parent / "static"  # app/static/


class Settings(BaseSettings):
    """全局配置类，继承自 Pydantic 的 BaseSettings

    属性将自动从环境变量或 .env 文件中加载（注意大小写敏感性，通常环境变量为大写）。
    """

    # 项目信息
    project_name: str = "图鉴式图片管理工具"
    project_description: str = "一个使用FastAPI和Vue构建的图鉴式图片管理和展示工具"
    project_version: str = "1.0.0"

    # API 配置
    api_v1_prefix: str = "/api"  # 根据README.md 4.3节，统一前缀为 /api

    # 数据库配置
    database_url: str = "sqlite:///./pokedex.db"  # SQLite文件将创建在运行命令的目录下
    # 若要固定位置，例如在 pokedex_backend 目录下: "sqlite:///pokedex.db"
    # 或者绝对路径: f"sqlite:///{PROJECT_ROOT}/pokedex.db"

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

    # CORS 配置 (从环境变量加载，例如 BACKEND_CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173")
    backend_cors_origins_str: Optional[str] = None  # 从环境变量读取为字符串
    backend_cors_origins: List[str] = []

    @validator("backend_cors_origins", pre=True, always=True)
    def assemble_cors_origins(cls, v, values):
        if isinstance(v, list) and v:  # 如果直接在代码中提供了列表
            return v
        origins_str = values.get("backend_cors_origins_str")
        if isinstance(origins_str, str):
            return [origin.strip() for origin in origins_str.split(",")]
        return []  # 默认空列表，表示不启用或按FastAPI默认处理

    # 静态文件服务 (main.py 中会用到这些来推断挂载点和目录)
    # static_files_mount_url: str = "/static/uploads" # 由main.py硬编码或推断
    # static_files_serve_dir: Path = base_static_dir / "uploads" # 由main.py推断

    # Uvicorn服务器配置 (可选，用于main.py中的if __name__ == "__main__":)
    server_host: str = "127.0.0.1"
    server_port: int = 8000
    log_level: str = "info"

    class Config:
        """Pydantic BaseSettings 配置类
        告诉 Pydantic 从 .env 文件加载环境变量，并使其不区分大小写（如果需要）。
        """

        env_file: str = ".env"
        env_file_encoding: str = "utf-8"
        case_sensitive: bool = False  # 环境变量通常是大写的


settings = Settings()

# 在这里可以添加一些启动时的路径检查或创建，但更推荐在main.py或服务初始化时进行
# settings.image_storage_root.mkdir(parents=True, exist_ok=True)
# settings.thumbnail_storage_root.mkdir(parents=True, exist_ok=True)
