"""分类数据模型模块

定义分类相关的数据模型和API Schema
"""

from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel

class CategoryBase(SQLModel):
    """分类基础模型
    
    属性:
        name (str): 分类名称（唯一）
        description (Optional[str]): 分类描述
    """
    name: str = Field(index=True, unique=True, description="分类名称")
    description: Optional[str] = Field(default=None, description="分类描述")

class Category(CategoryBase, table=True):
    """数据库分类模型
    
    继承自CategoryBase并添加数据库特定字段
    """
    id: Optional[int] = Field(default=None, primary_key=True, description="主键ID")
    images: List["Image"] = Relationship(back_populates="category")

class CategoryCreate(CategoryBase):
    """分类创建模型
    
    用于API创建接口的请求模型
    """
    pass

class CategoryRead(CategoryBase):
    """分类响应模型
    
    用于API响应数据的模型，包含完整字段
    """
    id: int = Field(description="分类ID")

class CategoryReadWithImages(CategoryRead):
    """包含图片的分类响应模型"""
    images: List["ImageRead"] = []
