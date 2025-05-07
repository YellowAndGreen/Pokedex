"""图像处理服务模块

提供缩略图生成等图像处理功能
"""

from pathlib import Path
from typing import Tuple
from PIL import Image as PILImage
from app.core.config import settings


class ImageProcessor:
    """图像处理器
    
    职责：
        - 生成和管理图片缩略图
        - 保证图像处理过程的安全性和可靠性
    """
    
    @staticmethod
    async def generate_thumbnail(source_path: Path, max_size: Tuple[int, int] = (256, 256)) -> Path:
        """生成并保存缩略图
        
        参数:
            source_path (Path): 原始图片的绝对路径
            max_size (Tuple[int, int]): 缩略图最大尺寸，默认(256, 256)
            
        返回:
            Path: 生成的缩略图绝对路径
            
        异常:
            ValueError: 当输入非图片文件时
            IOError: 当图片处理失败时
        """
        # 创建缩略图存储目录
        thumbnail_path = settings.thumbnail_storage_root / source_path.relative_to(settings.image_storage_root).parent
        thumbnail_path.mkdir(parents=True, exist_ok=True)
        
        # 生成缩略图文件名
        thumb_filename = f"{source_path.stem}_thumb{source_path.suffix}"
        dest_path = thumbnail_path / thumb_filename

        # 使用Pillow处理图像
        with PILImage.open(source_path) as img:
            img.thumbnail(max_size)
            img.save(dest_path, quality=85)
            
        return dest_path
