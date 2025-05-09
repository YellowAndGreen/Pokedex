"""类别数据模型模块

定义类别相关的数据模型和API Schema
"""

from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime # 导入 datetime
import uuid # 导入 uuid

# 延迟导入或使用字符串引用以避免循环导入
from .image_models import ImageRead

class CategoryBase(SQLModel):
    name: str = Field(..., max_length=50, unique=True, index=True, description="类别名称") # 之前缺失 ...
    description: Optional[str] = Field(None, max_length=300, description="类别描述") # 之前是 default=None


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
    thumbnail_url: Optional[str] = Field(default=None, description="新的完整缩略图URL，或由后端逻辑处理") # 对应文档


class CategoryRead(CategoryBase):
    """读取类别信息时使用的模型 (不包含图片列表)"""
    # id: int # 改为UUID
    id: uuid.UUID
    thumbnail_url: Optional[str] = None # 新增，对应文档，由thumbnail_path转换而来
    created_at: datetime # 新增
    updated_at: datetime # 新增

    class Config:
        # orm_mode = True
        from_attributes = True # 更改为 from_attributes


class CategoryReadWithImages(CategoryRead):
    """读取类别信息及其关联图片列表时使用的模型"""
    # images: List[ImageRead] = [] # 需要确保 ImageRead 类型已定义或正确导入
    # 暂时使用字符串引用，或导入简化的 ImageReadSimple (如果定义在本文档中)
    # 假设 ImageRead 会从 image_models.py 导入
    images: List["ImageRead"] = [] # 使用字符串类型提示避免循环导入，SQLModel/Pydantic会处理

# 注意: "ImageRead" 的定义在 image_models.py 中。
# 如果CategoryReadWithImages直接返回给客户端，确保ImageRead模型中的字段也与前端期望一致。
