"""图片数据模型模块

定义图片相关的数据模型和API Schema
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
import uuid
from pydantic import computed_field

from app.core.config import settings

# Import Tag and TagRead for relationships and schema definitions
from .tag_models import Tag, TagRead
from .link_models import ImageTagLink

# 避免循环导入，CategoryRead 在需要时以字符串形式提示，或按需导入
# from app.models.category_models import CategoryRead


class ExifData(SQLModel):
    """图片的详细EXIF元数据"""

    make: Optional[str] = Field(default=None, description="相机制造商")
    model: Optional[str] = Field(default=None, description="相机型号")
    lens_make: Optional[str] = Field(default=None, description="镜头制造商")
    bits_per_sample: Optional[str] = Field(
        default=None, description="每像素位数"
    )  # 例如 '8 8 8'
    date_time_original: Optional[str] = Field(
        default=None, description="原始拍摄日期时间"
    )
    exposure_time: Optional[str] = Field(default=None, description="曝光时间")
    f_number: Optional[str] = Field(default=None, description="F值")
    exposure_program: Optional[str] = Field(default=None, description="曝光程序")
    iso_speed_rating: Optional[str] = Field(default=None, description="ISO速度")
    focal_length: Optional[str] = Field(default=None, description="焦距")
    lens_specification: Optional[str] = Field(default=None, description="镜头规格")
    lens_model: Optional[str] = Field(default=None, description="镜头型号")
    exposure_mode: Optional[str] = Field(default=None, description="曝光模式")
    cfa_pattern: Optional[str] = Field(
        default=None, description="CFA模式"
    )  # 注意：这可能是二进制数据，转为字符串可能需要特定处理
    color_space: Optional[str] = Field(default=None, description="色彩空间")
    white_balance: Optional[str] = Field(default=None, description="白平衡")


class ImageBase(SQLModel):
    """图片基础模型 (大部分字段由后端在文件处理后填充)
    文档建议的 ImageBase 字段已调整并整合到这里或具体的 Read/DB 模型中。
    """

    title: Optional[str] = Field(None, max_length=255, description="图片标题")
    original_filename: Optional[str] = Field(None, description="用户上传时的原始文件名")
    stored_filename: Optional[str] = Field(
        None, unique=True, index=True, description="服务器存储的UUID文件名"
    )
    relative_file_path: Optional[str] = Field(
        None, description="相对于图片存储根目录的路径"
    )
    relative_thumbnail_path: Optional[str] = Field(
        None, description="相对于缩略图存储根目录的路径"
    )
    mime_type: Optional[str] = Field(None, description="如 image/jpeg")
    size_bytes: Optional[int] = Field(None, description="文件大小")
    description: Optional[str] = Field(None, max_length=500, description="图片描述")
    # category_id 将在 Image (DB model) 和 ImageRead 中定义，并使用 uuid.UUID
    # exif_info 将在 Image (DB model), ImageCreate 和 ImageRead 中定义


class Image(ImageBase, table=True):
    """图片数据库表模型"""

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow, nullable=False, description="创建日期"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="最后更新日期",
    )

    file_metadata: Optional[Dict[str, Any]] = Field(
        default={},
        sa_column=Column(JSON),
        description="图片文件元数据，可包含例如 EXIF 信息",
    )

    exif_info: Optional[ExifData] = Field(
        default=None, sa_column=Column(JSON), description="结构化的EXIF信息"
    )

    category_id: uuid.UUID = Field(
        foreign_key="category.id", index=True, description="所属类别ID"
    )
    category: Optional["Category"] = Relationship(back_populates="images")

    # Add relationship to Tag model
    tags: List["Tag"] = Relationship(
        back_populates="images",
        link_model=ImageTagLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class ImageCreate(SQLModel):
    """创建新图片时，API端点可能接收的元数据 (文件本身是 UploadFile)
    或者服务层用于聚合数据的模型。
    """

    title: Optional[str] = Field(
        None, max_length=255, description="图片标题，若不提供可由文件名生成"
    )
    description: Optional[str] = Field(None, max_length=500, description="图片描述")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签名称列表")
    category_id: uuid.UUID
    # 文件相关的原始名称、mime类型、大小等现在是此模型的一部分，由后端填充。
    original_filename: str = Field(description="用户上传时的原始文件名")
    stored_filename: str = Field(description="服务器存储的UUID文件名")
    relative_file_path: str = Field(description="相对于图片存储根目录的路径")
    relative_thumbnail_path: Optional[str] = Field(
        None, description="相对于缩略图存储根目录的路径"
    )
    mime_type: str = Field(description="如 image/jpeg")
    size_bytes: int = Field(description="文件大小")
    file_metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="图片文件元数据，例如 EXIF 信息"
    )
    exif_info: Optional[ExifData] = Field(default=None, description="结构化的EXIF信息")


class ImageRead(ImageBase):
    """读取图片信息时使用的模型"""

    id: uuid.UUID
    category_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    file_metadata: Optional[Dict[str, Any]] = None
    exif_info: Optional[ExifData] = None
    tags: Optional[List["TagRead"]] = Field(default_factory=list)

    @computed_field
    @property
    def image_url(self) -> str:
        if self.relative_file_path:
            # 确保 IMAGES_DIR_NAME 不以斜杠开头（如果 settings.server_host 已包含尾部斜杠，则需要调整）
            # 假设 settings.server_host 是类似 "http://localhost:8000"
            return f"http://{settings.server_host}:{settings.server_port}/{settings.IMAGES_DIR_NAME.strip('/')}/{self.relative_file_path.strip('/')}"
        # 根据实际情况，如果 relative_file_path 为 None，可能需要返回一个默认图片URL或抛出错误
        # 但 ImageRead 的 image_url 是非可选的，因此这里假设 relative_file_path 总是有效
        # 如果 self.relative_file_path 可以为 None，则 image_url 应该定义为 Optional[str]
        # 或者在这里提供一个默认的 "image not found" URL
        return "default_image_url_if_path_is_none"  # 应当有更好的处理

    @computed_field
    @property
    def thumbnail_url(self) -> Optional[str]:
        if self.relative_thumbnail_path:
            return f"http://{settings.server_host}:{settings.server_port}/{settings.THUMBNAILS_DIR_NAME.strip('/')}/{self.relative_thumbnail_path.strip('/')}"
        return None

    class Config:
        from_attributes = True


class ImageUpdate(SQLModel):
    """更新图片元数据时使用的模型"""

    title: Optional[str] = Field(None, max_length=255, description="新的图片标题")
    description: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = Field(default=None, description="要更新的标签名称列表")
    category_id: Optional[uuid.UUID] = None
    set_as_category_thumbnail: Optional[bool] = Field(
        None, description="是否将此图片设置为其所属类别的缩略图"
    )


class ImageReadWithTags(ImageRead):
    tags: List["TagRead"] = []


# 有关前向引用的处理，请参考 models/__init__.py 中的说明
