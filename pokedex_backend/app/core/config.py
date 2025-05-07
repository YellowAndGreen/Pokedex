"""
应用配置模块

包含所有环境相关配置设置，使用pydantic进行验证
"""

from pathlib import Path
from typing import List
from pydantic import BaseSettings


class Settings(BaseSettings):
    """全局配置类，继承自pydantic的BaseSettings
    
    属性:
        database_url (str): 数据库连接字符串，默认使用SQLite
        image_storage_root (Path): 图片存储根目录（绝对路径）
        thumbnail_storage_root (Path): 缩略图存储根目录（绝对路径） 
        max_image_size (int): 允许上传的最大图片大小（字节）
        allowed_mime_types (List[str]): 允许的图片MIME类型
    """
    
    database_url: str = "sqlite:///pokedex.db"
    image_storage_root: Path = Path(__file__).parent.parent.parent / "static/uploads/images"
    thumbnail_storage_root: Path = Path(__file__).parent.parent.parent / "static/uploads/thumbnails"
    max_image_size: int = 10 * 1024 * 1024  # 10MB
    allowed_mime_types: List[str] = ["image/jpeg", "image/png", "image/gif"]

    class Config:
        """pydantic配置类
        
        配置项:
            env_file (str): 环境变量文件路径
        """
        env_file: str = ".env"


settings: Settings = Settings()
