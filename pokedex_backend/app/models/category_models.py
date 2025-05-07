"""类别数据模型模块

定义类别相关的数据模型和API Schema
"""

from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from app.models.image_models import (
    ImageRead,
)  # 前向引用由SQLModel/Pydantic处理


class CategoryBase(SQLModel):
    """类别基础模型

    属性:
        name (str): 类别名称
        description (Optional[str]): 类别描述
    """

    name: str = Field(unique=True, index=True, description="类别名称")
    description: Optional[str] = Field(default=None, description="类别描述")


class Category(CategoryBase, table=True):
    """类别数据库表模型

    属性:
        id (Optional[int]): 主键ID
        images (List["Image"]): 该类别下的图片列表 (通过关系定义)
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    images: List["Image"] = Relationship(back_populates="category")  # type: ignore


class CategoryCreate(CategoryBase):
    """创建类别时使用的模型"""

    pass


class CategoryRead(CategoryBase):
    """读取类别信息时使用的模型 (不包含图片列表)"""

    id: int


class CategoryReadWithImages(CategoryRead):
    """读取类别信息及其关联图片列表时使用的模型"""

    images: List[ImageRead] = []


# 有关前向引用的处理，请参考 models/__init__.py 中的说明
