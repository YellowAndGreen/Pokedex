"""文件存储服务模块

处理图片文件的上传、存储路径生成和路径转换逻辑
"""

import uuid
from pathlib import Path
from typing import Tuple
import aiofiles
from app.core.config import settings


class FileStorageService:
    """文件存储服务类
    
    职责：
        - 生成分级存储路径
        - 保存上传文件到指定位置
        - 处理文件路径转换
    """
    
    def __init__(self) -> None:
        """初始化存储路径"""
        self.image_storage: Path = settings.image_storage_root
        self.thumbnail_storage: Path = settings.thumbnail_storage_root
        
    def generate_file_path(self, filename: str) -> Tuple[Path, str]:
        """生成分级存储路径以防止单个目录文件过多
        
        参数:
            filename (str): 原始文件名，用于保留扩展名
            
        返回:
            Tuple[Path, str]: (存储目录路径, 生成的文件名)
        """
        file_uuid: str = uuid.uuid4().hex
        dir_levels: Tuple[str, str] = (file_uuid[:2], file_uuid[2:4])
        relative_path: Path = Path(dir_levels[0]) / dir_levels[1]
        
        storage_path: Path = self.image_storage / relative_path
        storage_path.mkdir(parents=True, exist_ok=True)
        
        return storage_path, f"{file_uuid}{Path(filename).suffix}"

    async def save_upload_file(self, file, filename: str) -> Tuple[Path, str]:
        """异步保存上传文件
        
        参数:
            file: 上传文件对象
            filename (str): 原始文件名
            
        返回:
            Tuple[Path, str]: (保存后的完整文件路径, 存储的文件名)
            
        异常:
            IOError: 当文件写入失败时抛出
        """
        storage_path, stored_filename = self.generate_file_path(filename)
        file_path: Path = storage_path / stored_filename
        
        try:
            async with aiofiles.open(file_path, "wb") as buffer:
                while chunk := await file.read(1024 * 1024):  # 1MB chunks
                    await buffer.write(chunk)
        except OSError as e:
            raise IOError(f"文件保存失败: {str(e)}") from e
                
        return file_path, stored_filename

    def get_relative_path(self, file_path: Path) -> str:
        """获取相对于存储根目录的路径
        
        参数:
            file_path (Path): 绝对路径
            
        返回:
            str: 相对于存储根目录的路径字符串
        """
        try:
            return str(file_path.relative_to(settings.image_storage_root))
        except ValueError:
            return str(file_path.relative_to(settings.image_storage_root.parent))
