"""类别数据模型模块

定义类别相关的数据模型和API Schema
"""

from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime # 导入 datetime
import uuid # 导入 uuid
from pydantic import computed_field # 导入 computed_field
from app.core.config import settings # 导入 settings

# 延迟导入或使用字符串引用以避免循环导入
from .image_models import ImageRead

class CategoryBase(SQLModel):
    name: str = Field(..., max_length=50, unique=True, index=True, description="类别名称") # 之前缺失 ...
    description: Optional[str] = Field(None, max_length=300, description="类别描述") # 之前是 default=None
    # thumbnail_path 将在 Category (DB model) 中定义


class Category(CategoryBase, table=True):
    # id: Optional[int] = Field(default=None, primary_key=True) # 改为UUID
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False)
    thumbnail_path: Optional[str] = Field(None, description="存储缩略图的相对路径") # 新增，对应文档数据库模型
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False) # 新增
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, sa_column_kwargs={"onupdate": datetime.utcnow}) # 新增

    images: List["Image"] = Relationship(back_populates="category")


class CategoryCreate(CategoryBase):
    """创建类别时使用的模型 (主要用于JSON体，文件通常由API端点参数处理)
    根据文档，前端可能发送包含 name 和 description 的JSON，thumbnail文件作为独立部分。
    """
    # name: str # 从CategoryBase继承
    # description: Optional[str] # 从CategoryBase继承
    # 如果需要Pydantic模型接收thumbnail元数据（而不是文件本身），可以在此添加，但不常见
    pass


class CategoryUpdate(SQLModel): # 新增，使用SQLModel或BaseModel均可，取决于是否与DB字段直接映射
    """更新类别时使用的模型"""
    name: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=300)
    # thumbnail_url: Optional[str] = Field(default=None, description="新的完整缩略图URL，或由后端逻辑处理") # 对应文档
    # ^^^ 在Update模型中，通常不直接提供thumbnail_url，而是上传新文件，后端处理路径和URL生成
    # 如果要允许直接修改thumbnail_path（不推荐），则应在此处添加 thumbnail_path: Optional[str]


class CategoryRead(CategoryBase):
    """读取类别信息时使用的模型 (不包含图片列表)"""
    # id: int # 改为UUID
    id: uuid.UUID
    # thumbnail_url: Optional[str] = None # 将被替换为 computed_field
    created_at: datetime # 新增
    updated_at: datetime # 新增
    thumbnail_path: Optional[str] # 确保 CategoryRead 能访问到 thumbnail_path
                                  # 如果 CategoryBase 没有它，而 Category (ORM) 有，
                                  # 并且 CategoryRead.from_orm(Category_instance) 被调用，
                                  # 那么 thumbnail_path 应该能被填充。
                                  # 或者从 Category 继承此字段。为了明确，这里加上。
                                  # 如果 CategoryBase 已有，则重复。
                                  # 检查后，CategoryBase没有，Category有，所以这里是必须的。

    @computed_field
    @property
    def thumbnail_url(self) -> Optional[str]:
        if self.thumbnail_path:
            # 假设 settings.server_host 是 "127.0.0.1", settings.server_port 是 8000
            # settings.THUMBNAILS_DIR_NAME 是 "thumbnails"
            # self.thumbnail_path 是类似 "category_slug/thumb.jpg"
            base_url = f"http://{settings.server_host}:{settings.server_port}"
            thumbnails_segment = settings.THUMBNAILS_DIR_NAME.strip('/')
            path_segment = self.thumbnail_path.strip('/')
            return f"{base_url}/{thumbnails_segment}/{path_segment}"
        return None

    class Config:
        # orm_mode = True
        from_attributes = True # 更改为 from_attributes


class CategoryReadWithImages(CategoryRead):
    """读取类别信息及其关联图片列表时使用的模型"""
    # images: List[ImageRead] = [] # 需要确保 ImageRead 类型已定义或正确导入
    # 暂时使用字符串引用，或导入简化的 ImageReadSimple (如果定义在本文档中)
    # 假设 ImageRead 会从 image_models.py 导入
    images: List[ImageRead] = [] # ImageRead 已经有动态的 image_url 和 thumbnail_url

# 注意: "ImageRead" 的定义在 image_models.py 中。
# 如果CategoryReadWithImages直接返回给客户端，确保ImageRead模型中的字段也与前端期望一致。
