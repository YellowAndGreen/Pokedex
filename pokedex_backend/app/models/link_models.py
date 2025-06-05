#!/usr/bin/env python3
"""链接模型模块

定义用于多对多关系的链接表模型
"""

from sqlmodel import SQLModel, Field
import uuid


class ImageTagLink(SQLModel, table=True):
    """图片和标签之间的多对多关系链接表"""

    image_id: uuid.UUID = Field(default=None, primary_key=True, foreign_key="image.id")
    tag_id: uuid.UUID = Field(default=None, primary_key=True, foreign_key="tag.id")
