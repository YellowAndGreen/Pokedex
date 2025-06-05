#!/usr/bin/env python3
"""标签数据模型模块

定义标签相关的数据模型和API Schema
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
import uuid

if TYPE_CHECKING:
    from .image_models import Image

# 实际导入，用于运行时
from .link_models import ImageTagLink


class TagBase(SQLModel):
    """标签基础模型"""

    name: str = Field(max_length=100, unique=True, index=True, description="标签名称")


class Tag(TagBase, table=True):
    """标签数据库表模型"""

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

    # Relationship to Image through ImageTagLink
    images: List["Image"] = Relationship(
        back_populates="tags",
        link_model=ImageTagLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class TagCreate(TagBase):
    """创建新标签时使用的模型"""

    pass


class TagRead(TagBase):
    """读取标签信息时使用的模型"""

    id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TagUpdate(SQLModel):
    """更新标签信息时使用的模型"""

    name: Optional[str] = Field(
        default=None, max_length=100, description="新的标签名称"
    )
