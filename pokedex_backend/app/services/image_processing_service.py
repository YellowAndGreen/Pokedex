"""图像处理服务模块

提供缩略图生成等图像处理功能
"""

import asyncio
from pathlib import Path
from typing import Tuple
from PIL import Image as PILImage
from fastapi import HTTPException, status
from app.core.config import settings


class ImageProcessingService:
    """图像处理器

    职责：
        - 生成和管理图片缩略图
        - 保证图像处理过程的安全性和可靠性
    """

    def __init__(self):
        self.thumbnail_storage_root: Path = settings.thumbnail_storage_root
        self.default_thumbnail_size: Tuple[int, int] = (
            settings.thumbnail_size
        )  # e.g. (256, 256)
        # 确保缩略图根目录存在 (也可由FileStorageService或main.py保证)
        self.thumbnail_storage_root.mkdir(parents=True, exist_ok=True)

    async def generate_thumbnail(
        self,
        source_image_path: Path,  # 原图的绝对路径
        relative_sub_dir: Path,  # 原图存储的相对子目录 (e.g., "ab/cd")
        stored_filename: str,  # 原图存储的文件名 (e.g., "uuid.jpg")
    ) -> Path:
        """
        异步生成并保存图片的缩略图。

        参数:
            source_image_path (Path): 原始图片的绝对路径。
            relative_sub_dir (Path): 图片在存储系统中的相对子目录 (例如 Path("ab/cd"))。
            stored_filename (str): 图片存储时使用的唯一文件名 (包含扩展名)。

        返回:
            Path: 生成的缩略图的绝对路径。

        可能抛出 HTTPException:
            - 500 INTERNAL_SERVER_ERROR: 如果图像处理或保存失败。
        """
        if not await asyncio.to_thread(source_image_path.is_file):
            # Log error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"生成缩略图失败：源文件不存在于 {source_image_path}",
            )

        thumbnail_target_directory = self.thumbnail_storage_root / relative_sub_dir
        await asyncio.to_thread(
            thumbnail_target_directory.mkdir, parents=True, exist_ok=True
        )

        original_stem = Path(stored_filename).stem
        original_suffix = Path(stored_filename).suffix
        thumbnail_filename = f"{original_stem}_thumb{original_suffix}"
        thumbnail_absolute_path = thumbnail_target_directory / thumbnail_filename

        try:
            # Pillow的图像操作是同步阻塞的，使用asyncio.to_thread在单独线程中运行
            def process_image():
                with PILImage.open(source_image_path) as img:
                    # 保持宽高比进行缩放
                    img.thumbnail(self.default_thumbnail_size)
                    # 可以根据图片类型选择不同的保存选项，例如JPEG的quality
                    if img.mode == "RGBA" and original_suffix.lower() in [
                        ".jpg",
                        ".jpeg",
                    ]:
                        # JPEG不支持alpha通道，转换为RGB
                        img = img.convert("RGB")
                    img.save(
                        thumbnail_absolute_path, quality=settings.thumbnail_quality
                    )

            await asyncio.to_thread(process_image)

        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"生成缩略图失败：源文件处理时未找到 {source_image_path}",
            )
        except Exception as e:
            # Log e in detail
            # 尝试清理可能已创建的损坏的缩略图文件
            if await asyncio.to_thread(thumbnail_absolute_path.exists):
                try:
                    await asyncio.to_thread(thumbnail_absolute_path.unlink)
                except Exception as cleanup_e:
                    # Log cleanup_e
                    pass  # 忽略清理错误
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"生成缩略图时发生未知错误: {e}",
            )

        return thumbnail_absolute_path
