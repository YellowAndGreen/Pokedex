"""图片数据模型模块

定义图片相关的数据模型和API Schema
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship


class ImageBase(SQLModel):
    """图片基础模型
    
    属性:
        original_filename (str): 原始文件名
        stored_filename (str): 存储文件名（唯一）
        relative_file_path (str): 相对存储路径
        relative_thumbnail_path (Optional[str]): 缩略图相对路径
        mime_type (str): 文件MIME类型
        size_bytes (int): 文件大小（字节）
        description (Optional[str]): 图片描述
        tags (Optional[str]): 标签（逗号分隔）
        upload_date (datetime): 上传时间
        category_id (int): 所属分类ID
    """
    original_filename: str = Field(index=True, description="原始文件名")
    stored_filename: str = Field(unique=True, index=True, description="存储文件名（唯一）")
    relative_file_path: str = Field(description="相对存储路径")
    relative_thumbnail_path: Optional[str] = Field(default=None, description="缩略图相对路径")
    mime_type: str = Field(description="文件MIME类型")
    size_bytes: int = Field(description="文件大小（字节）")
    description: Optional[str] = Field(default=None, description="图片描述")
    tags: Optional[str] = Field(default=None, description="标签（逗号分隔）")
    upload_date: datetime = Field(default_factory=datetime.utcnow, description="上传时间")
    category_id: int = Field(foreign_key="category.id", description="所属分类ID")


class Image(ImageBase, table=True):
    """数据库图片模型
    
    继承自ImageBase并添加数据库特定字段
    """
    id: Optional[int] = Field(default=None, primary_key=True, description="主键ID")
    category: "Category" = Relationship(back_populates="images", description="关联分类")


class ImageCreate(ImageBase):
    """图片创建模型
    
    用于API创建接口的请求模型
    """
    pass


class ImageRead(ImageBase):
    """图片响应模型
    
    用于API响应数据的模型，包含完整字段
    """
    id: int = Field(description="图片ID")


class ImageUpdate(SQLModel):
    """图片更新模型
    
    定义允许更新的字段
    """
    description: Optional[str] = Field(default=None, description="更新描述信息")
    tags: Optional[str] = Field(default=None, description="更新标签信息")
    category_id: Optional[int] = Field(default=None, description="更新分类ID")
