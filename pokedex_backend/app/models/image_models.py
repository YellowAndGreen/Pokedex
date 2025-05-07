"""图片数据模型模块

定义图片相关的数据模型和API Schema
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

# 避免循环导入，CategoryRead 在需要时以字符串形式提示，或按需导入
# from app.models.category_models import CategoryRead


class ImageBase(SQLModel):
    """图片基础模型

    属性:
        original_filename (str): 用户上传时的原始文件名
        stored_filename (str): 服务器存储的UUID文件名 (含扩展名)
        relative_file_path (str): 相对于图片存储根目录的路径
        relative_thumbnail_path (Optional[str]): 相对于缩略图存储根目录的路径
        mime_type (str): 图片的MIME类型 (如 image/jpeg)
        size_bytes (int): 图片文件大小 (字节)
        description (Optional[str]): 图片描述
        tags (Optional[str]): 图片标签 (逗号分隔或JSON字符串)
        category_id (int): 图片所属的类别ID
    """

    original_filename: str = Field(description="用户上传时的原始文件名")
    stored_filename: str = Field(
        unique=True, index=True, description="服务器存储的UUID文件名 (含扩展名)"
    )
    relative_file_path: str = Field(
        description="相对于图片存储根目录的路径 (例如 aa/bb/uuid.jpg)"
    )
    relative_thumbnail_path: Optional[str] = Field(
        default=None, description="相对于缩略图存储根目录的路径"
    )
    mime_type: str = Field(description="如 image/jpeg")
    size_bytes: int = Field(description="文件大小")
    description: Optional[str] = Field(default=None, description="图片描述")
    tags: Optional[str] = Field(
        default=None, description="逗号分隔的标签字符串或JSON字符串"
    )
    category_id: int = Field(
        foreign_key="category.id", index=True, description="所属类别ID"
    )


class Image(ImageBase, table=True):
    """图片数据库表模型

    属性:
        id (Optional[int]): 主键ID
        upload_date (datetime): 图片上传日期和时间
        category (Optional["Category"]): 图片所属的类别 (通过关系定义)
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    upload_date: datetime = Field(
        default_factory=datetime.utcnow, nullable=False, description="上传日期"
    )

    category: Optional["Category"] = Relationship(back_populates="images")  # type: ignore


class ImageCreate(ImageBase):
    """创建图片记录时使用的模型 (通常由后端内部使用，因为文件数据分开处理)"""

    pass


class ImageRead(ImageBase):
    """读取图片信息时使用的模型"""

    id: int
    upload_date: datetime
    # 若直接需要类别信息，可选择性包含，但通常通过 CategoryReadWithImages 访问
    # category: Optional[CategoryRead] = None


class ImageUpdate(SQLModel):
    """更新图片元数据时使用的模型

    属性:
        description (Optional[str]): 新的图片描述
        tags (Optional[str]): 新的图片标签
        category_id (Optional[int]): 可选，用于将图片移动到新的类别
    """

    description: Optional[str] = None
    tags: Optional[str] = None
    category_id: Optional[int] = None


# 有关前向引用的处理，请参考 models/__init__.py 中的说明
