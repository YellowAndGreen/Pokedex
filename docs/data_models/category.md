# 分类数据模型

## 概述
本文档定义了与"分类"相关的各种数据模型，包括前端TypeScript类型和后端Python Pydantic模型。

## 前端类型定义 (示例来自 `pokedex_frontend/src/types/index.ts`)

```typescript
// 用于API读取单个分类的基础信息
export interface CategoryRead {
  id: string;         // UUID字符串
  name: string;
  description?: string;
  thumbnailUrl: string; // 完整的缩略图URL
  createdDate: string;  // ISO 8601 日期时间字符串
  updatedDate: string;  // ISO 8601 日期时间字符串
}

// 用于API读取单个分类及其包含的图片列表
export interface CategoryReadWithImages extends CategoryRead {
  images: ImageRead[]; // ImageRead 类型定义在 image.md
}

// 用于前端创建新分类时提交的数据结构
export interface CategoryCreate {
  name: string;
  description?: string;
  thumbnail?: File;     // 可选的缩略图文件
}

// 用于前端更新分类时提交的数据结构
export interface CategoryUpdate {
  name?: string;
  description?: string;
  thumbnailUrl?: string; // 允许更新为新的URL，或由后端处理（例如置空或基于新上传）
  // 如果支持通过更新接口上传新缩略图文件，则应添加：
  // newThumbnailFile?: File;
}
```

## 后端模型定义 (Pydantic / SQLModel)

### `CategoryBase (SQLModel)`
作为其他分类模型的基础，包含通用字段。
```python
from typing import Optional
from sqlmodel import SQLModel, Field

class CategoryBase(SQLModel):
    name: str = Field(..., max_length=50, unique=True, index=True, description="类别名称")
    description: Optional[str] = Field(None, max_length=300, description="类别描述")
```

### `CategoryCreate (BaseModel)`
用于创建新分类时，API接收的请求体模型。
```python
from pydantic import BaseModel # 或者如果也用SQLModel，则 from sqlmodel import SQLModel
from fastapi import UploadFile, File
from typing import Optional

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    # thumbnail: Optional[UploadFile] = File(None) # 如果API端点直接通过模型接收文件
    # 通常，FastAPI端点会直接将 UploadFile 作为参数，而不是Pydantic模型字段。
    # 但如果CRUD函数期望模型中有此字段，则应包含。
    # 假设后端端点参数: name: str = Form(...), description: Optional[str] = Form(None), thumbnail: Optional[UploadFile] = File(None)
    # 这种情况下，CategoryCreate模型可能只是 name 和 description。
    # 为与前端发送FormData(含thumbnail)对应，假设后端CRUD辅助函数可能需要此定义：
    # thumbnail: Optional[UploadFile] = None # 这个字段在FastAPI中通常通过Depends或File()在路径操作函数参数中处理
```
*注意：对于包含文件上传（如`thumbnail`）的创建操作，FastAPI通常在路径操作函数参数中直接使用 `thumbnail: Optional[UploadFile] = File(None)`，而不是在Pydantic模型中定义`UploadFile`。Pydantic模型主要用于JSON体。如果创建操作的API端点明确设计为接受`multipart/form-data`，其中文件和文本字段混合，则后端逻辑需要正确解析。前端发送`FormData`时，后端对应参数应为`Form()`和`File()`。*

### `CategoryUpdate (BaseModel)`
用于更新分类信息时，API接收的请求体模型。
```python
from pydantic import BaseModel
from typing import Optional

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    # thumbnail_url: Optional[str] = None # 如果允许通过API更新为新的URL
    # 如果更新时允许上传新文件，则也需要考虑如何处理
```

### `CategoryRead (BaseModel)`
用于API响应，表示从数据库读取的单个分类信息。
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime # 用于类型提示
import uuid # 用于类型提示

class CategoryRead(BaseModel):
    id: uuid.UUID # 后端原始类型
    name: str
    description: Optional[str]
    thumbnail_url: Optional[str] # 后端生成的完整URL或None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True # 如果从ORM对象转换
```

### `CategoryReadWithImages (BaseModel)`
用于API响应，表示分类信息及其关联的图片列表。
```python
from typing import List
# from .image_models import ImageRead # 假设ImageRead定义在image_models.py

class ImageReadSimple(BaseModel): # 临时简化，应从image.md导入或链接
    id: uuid.UUID
    title: str
    image_url: Optional[str]

class CategoryReadWithImages(CategoryRead):
    images: List[ImageReadSimple] = [] # ImageRead应从image模型定义导入
```

## 数据库表模型 (`Category(SQLModel, table=True)`) (供参考)
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
import uuid
from datetime import datetime

# class Image(SQLModel, table=True): # 简化，实际应从image_models导入
#     id: Optional[int] = Field(default=None, primary_key=True)
#     category_id: Optional[int] = Field(default=None, foreign_key="category.id")
#     category: Optional["Category"] = Relationship(back_populates="images")

class Category(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False)
    name: str = Field(max_length=50, unique=True, index=True)
    description: Optional[str] = Field(None, max_length=300)
    thumbnail_path: Optional[str] = Field(None) # 存储相对路径
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, sa_column_kwargs={"onupdate": datetime.utcnow})
    # images: List["Image"] = Relationship(back_populates="category")
```

## 模型转换与字段映射表

| 前端字段 (`CategoryRead`/`WithImages`) | 后端Pydantic `CategoryRead` 字段 | 数据库 `Category` 字段 | 转换规则/说明                                                                 |
|------------------------------------|------------------------------------|--------------------------|-----------------------------------------------------------------------------|
| `id: string`                       | `id: uuid.UUID`                    | `id: uuid.UUID`          | 字符串 ↔ UUID 双向转换。前端通常使用字符串ID。                                |
| `name: string`                     | `name: str`                        | `name: str`              |                                                                             |
| `description?: string`             | `description: Optional[str]`       | `description: Optional[str]` |                                                                             |
| `thumbnailUrl: string`             | `thumbnail_url: Optional[str]`     | `thumbnail_path: Optional[str]` | 后端根据`thumbnail_path`和配置的基地址生成完整的`thumbnail_url`。前端直接使用。 |
| `createdDate: string`              | `created_at: datetime`             | `created_at: datetime`   | ISO 8601 时间字符串 ↔ Python `datetime` 对象。                                |
| `updatedDate: string`              | `updated_at: datetime`             | `updated_at: datetime`   | ISO 8601 时间字符串 ↔ Python `datetime` 对象。                                |
| `images: ImageRead[]`              | `images: List[ImageRead]`          | (关系)                   | 嵌套的ImageRead对象列表。                                                     |

**创建 (`CategoryCreate`) 时：**
*   前端发送 `name`, `description?`, `thumbnail?: File`。
*   后端接收 `name`, `description?`。`thumbnail` 文件通常作为单独的 `UploadFile` 参数在API端点处理，然后保存并生成 `thumbnail_path` 存入数据库。

**更新 (`CategoryUpdate`) 时：**
*   前端发送 `name?`, `description?`, `thumbnailUrl?`。
*   后端需要明确如何处理 `thumbnailUrl` 的更新（例如，是允许客户端指定一个新URL，还是触发内部的缩略图更新/删除逻辑，或通过单独接口处理缩略图文件更新）。
