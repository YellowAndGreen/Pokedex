"""文件存储服务模块

处理图片文件的上传、存储路径生成、物理保存和删除逻辑。
"""

import uuid
import os
from pathlib import Path
from typing import Tuple

import aiofiles
import aiofiles.os as aio_os  # For async file operations like stat and remove
from fastapi import UploadFile, HTTPException, status

from app.core.config import settings


class FileStorageService:
    """文件存储服务类

    负责管理图片文件的物理存储，包括：
    - 生成基于UUID和分级目录的存储路径。
    - 异步保存上传的文件。
    - 异步删除物理文件。
    - 文件大小和类型校验（部分在此处理，部分在路由层）。
    """

    def __init__(self) -> None:
        """初始化存储服务的根路径，并确保它们存在。"""
        self.image_storage_root: Path = settings.image_storage_root
        self.thumbnail_storage_root: Path = settings.thumbnail_storage_root

        # 确保根存储目录存在
        self.image_storage_root.mkdir(parents=True, exist_ok=True)
        self.thumbnail_storage_root.mkdir(parents=True, exist_ok=True)

    async def _generate_structured_path(
        self, original_filename: str, base_path: Path
    ) -> Tuple[Path, str, Path]:
        """
        内部辅助方法：为文件生成一个结构化的存储路径和唯一文件名。

        路径结构: base_path / <uuid_char1_2> / <uuid_char3_4> / <uuid>.<ext>

        参数:
            original_filename (str): 用户上传的原始文件名，用于提取扩展名。
            base_path (Path): 存储文件的基础根目录 (例如 images_root 或 thumbnails_root)。

        返回:
            Tuple[Path, str, Path]:
                - full_file_path (Path): 文件的完整绝对存储路径。
                - stored_filename (str): 包含UUID和扩展名的最终存储文件名。
                - sub_directory (Path): 相对于base_path的子目录路径 (e.g., <uuid_char1_2>/<uuid_char3_4>/)
        """
        file_extension = Path(original_filename).suffix.lower()
        if not file_extension:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="文件名缺少扩展名"
            )

        file_uuid = uuid.uuid4().hex
        stored_filename = f"{file_uuid}{file_extension}"

        # 使用UUID的前4个字符创建两级子目录
        sub_dir_level1 = file_uuid[:2]
        sub_dir_level2 = file_uuid[2:4]

        relative_sub_directory = Path(sub_dir_level1) / sub_dir_level2
        absolute_save_directory = base_path / relative_sub_directory

        # 异步创建目录 (如果不存在)
        await aio_os.makedirs(absolute_save_directory, exist_ok=True)

        full_file_path = absolute_save_directory / stored_filename
        return full_file_path, stored_filename, relative_sub_directory

    async def save_upload_file(
        self, upload_file: UploadFile, filename: str
    ) -> Tuple[Path, str]:
        """
        异步保存上传的图片文件。

        参数:
            upload_file (UploadFile): FastAPI的上传文件对象。
            filename (str): 原始文件名 (通常来自 upload_file.filename)。

        返回:
            Tuple[Path, str]:
                - image_absolute_path (Path): 原图保存的绝对路径。
                - stored_filename (str): 存储时使用的唯一文件名 (含扩展名)。

        可能抛出 HTTPException:
            - 400 BAD_REQUEST: 如果文件类型不允许或无扩展名。
            - 413 REQUEST_ENTITY_TOO_LARGE: 如果文件大小超过限制。
            - 500 INTERNAL_SERVER_ERROR: 如果文件写入失败。
        """
        if upload_file.content_type not in settings.allowed_mime_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型: {upload_file.content_type}.",
            )

        # 文件大小校验 (使用 seek 和 tell 获取大小，避免一次性读入内存)
        upload_file.file.seek(0, os.SEEK_END)
        file_size = upload_file.file.tell()
        if file_size > settings.max_image_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"文件大小 {file_size / 1024 / 1024:.2f}MB 超过限制 ({settings.max_image_size / 1024 / 1024:.0f}MB).",
            )
        await upload_file.seek(0)  # 重置文件指针以供读取

        image_absolute_path, stored_filename, _ = await self._generate_structured_path(
            original_filename=filename, base_path=self.image_storage_root
        )

        try:
            async with aiofiles.open(image_absolute_path, "wb") as out_file:
                content = await upload_file.read()  # 异步读取文件内容
                await out_file.write(content)  # 异步写入磁盘
        except IOError as e:
            # 可以考虑在这里清理已创建的空文件或部分写入的文件
            # await self.delete_file(image_absolute_path) # 如果需要回滚
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"无法保存文件到磁盘: {e}",
            )
        finally:
            await upload_file.close()

        return image_absolute_path, stored_filename

    async def delete_file(self, file_path: Path) -> bool:
        """
        异步删除指定的物理文件。

        参数:
            file_path (Path): 要删除的文件的绝对路径。

        返回:
            bool: 如果文件成功删除或文件原本就不存在，则返回True。
                  如果删除过程中发生IO错误，则返回False (或抛出异常)。
        """
        try:
            if await aio_os.path.isfile(file_path):
                await aio_os.remove(file_path)
                return True
            return True  # 文件不存在也视为删除成功（幂等性）
        except OSError as e:
            print(f"删除文件 {file_path} 时发生错误: {e}")  # 应使用日志记录
            # 根据策略，这里可以返回False或重新抛出异常
            return False

    async def get_relative_sub_directory_for_file(self, stored_filename: str) -> Path:
        """
        根据已存储的文件名（包含UUID）推断其相对子目录结构。
        主要用于在其他服务（如缩略图服务）中确定对应文件的子目录。

        参数:
            stored_filename (str): 包含UUID和扩展名的存储文件名。

        返回:
            Path: 相对子目录路径 (e.g., Path("ab/cd"))。
        """
        file_uuid = Path(stored_filename).stem  # 提取UUID部分
        if len(file_uuid) < 4:
            # 对于非UUID格式的文件名或太短的UUID，返回空路径或抛异常
            # 这里简单返回根，实际应有更鲁棒处理
            return Path(".")
        sub_dir_level1 = file_uuid[:2]
        sub_dir_level2 = file_uuid[2:4]
        return Path(sub_dir_level1) / sub_dir_level2
