# 图片数据模型

## 概述
本文档定义了与"图片"相关的各种数据模型，包括前端TypeScript类型和后端Python Pydantic模型。

## 前端类型定义 (示例来自 `pokedex_frontend/src/types/index.ts`)

```typescript
// 用于API读取图片的基础信息
export interface ImageRead {
  id: string;           // UUID字符串
  title: string;
  description?: string;
  imageUrl: string;       // 完整的图片URL
  thumbnailUrl?: string;  // 完整的缩略图URL (如果图片有独立缩略图)
  categoryId: string;     // 所属分类的ID (UUID字符串)
  createdDate: string;    // ISO 8601 日期时间字符串
  // updatedDate?: string; // 如果有更新时间
  file_metadata: {          // 图片文件元数据 (原 metadata)
    width?: number;
    height?: number;
    fileSize?: string; // 例如 "1.2MB"
    format?: string;   // 例如 "jpeg", "png"
    // ... 其他可能的元数据字段
  };
}

// 用于前端上传新图片时准备的数据结构 (基于ImageCreate)
// 在Store或Service层可能定义如下辅助接口，供组件使用
export interface ImageUploadData {
  imageFile: File;        // 图片文件本身
  categoryId: string;     // 目标分类ID
  title?: string;         // 可选标题，若不提供，后端可从文件名生成
  description?: string;
  tags?: string;          // 逗号分隔的标签字符串
}

// 用于前端更新图片信息时提交的数据结构
export interface ImageUpdate {
  title?: string;
  description?: string;
  tags?: string;          // 允许更新标签
  categoryId?: string;    // 允许更换分类
}
```

## 后端模型定义 (Pydantic / SQLModel)

### `ImageBase (SQLModel)`
作为其他图片模型的基础，包含多数数据库存储字段。
```python
from typing import Optional
from sqlmodel import SQLModel, Field
import uuid
from datetime import datetime

class ImageBase(SQLModel):
    title: Optional[str] = Field(None, max_length=100, description="图片标题") # 改为可选，创建时可从文件名生成
    original_filename: Optional[str] = Field(None, description="用户上传时的原始文件名")
    stored_filename: Optional[str] = Field(None, unique=True, index=True, description="服务器存储的UUID文件名")
    relative_file_path: Optional[str] = Field(None, description="相对于图片存储根目录的路径")
    relative_thumbnail_path: Optional[str] = Field(None, description="相对于缩略图存储根目录的路径")
    mime_type: Optional[str] = Field(None, description="如 image/jpeg")
    size_bytes: Optional[int] = Field(None, description="文件大小")
    description: Optional[str] = Field(None, max_length=500, description="图片描述")
    tags: Optional[str] = Field(None, description="逗号分隔的标签字符串")
    # category_id: uuid.UUID # 将在具体表中定义，并带foreign_key
```

### `ImageCreate (BaseModel)`
用于创建新图片记录时，API接收的核心数据（文件通常作为独立参数）。
这个模型主要用于后端服务层逻辑，API端点通常直接接收 `UploadFile` 和 `Form` 数据。
```python
from pydantic import BaseModel
from typing import Optional
import uuid

class ImageCreate(BaseModel):
    title: Optional[str] = None # 后端可根据文件名生成，如果前端未提供
    description: Optional[str] = None
    tags: Optional[str] = None
    category_id: uuid.UUID # 必须提供分类ID
    # 文件相关的元数据 (original_filename, mime_type, size_bytes) 将由后端从 UploadFile 对象中提取
```
*注意：前端通过 `apiService.uploadImage` 发送 `FormData`，包含 `file: File`, `category_id: string`, 及可选的 `title, description, tags`。后端FastAPI端点应定义相应参数：`file: UploadFile = File(...)`, `category_id: uuid.UUID = Form(...)`, `title: Optional[str] = Form(None)` 等。上述 `ImageCreate` 模型可用于在后端服务层将这些分散的参数聚合起来传递给CRUD函数。*

### `ImageUpdate (BaseModel)`
用于更新图片元数据时，API接收的请求体模型。
```python
from pydantic import BaseModel
from typing import Optional
import uuid

class ImageUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    category_id: Optional[uuid.UUID] = None # 允许更换分类
```

### `ImageRead (BaseModel)`
用于API响应，表示从数据库读取的单个图片完整信息。
```python
from pydantic import BaseModel, Json # Json 用于 metadata
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class ImageRead(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    description: Optional[str]
    image_url: str # 后端生成的完整URL
    thumbnail_url: Optional[str] # 后端生成的完整缩略图URL或None
    category_id: uuid.UUID
    tags: Optional[str]
    created_at: datetime # 或 upload_date
    # updated_at: Optional[datetime] # 如果有图片信息更新时间
    file_metadata: Optional[Dict[str, Any]] # (原 metadata) 例如: {"width": 1024, "height": 768, "format": "jpeg"}
    # original_filename: Optional[str] # 根据需要决定是否暴露
    # mime_type: Optional[str]
    # size_bytes: Optional[int]

    class Config:
        orm_mode = True
```

## 数据库表模型 (`Image(SQLModel, table=True)`) (供参考)
```python
from sqlmodel import SQLModel, Field, Relationship, Column, JSON # or JSONB for PostgreSQL
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

# class Category(SQLModel, table=True): # 简化
#     id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
#     images: List["Image"] = Relationship(back_populates="category")

class Image(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False)
    title: Optional[str] = Field(None, max_length=255) # 增加title到数据库
    original_filename: str
    stored_filename: str = Field(unique=True, index=True)
    relative_file_path: str
    relative_thumbnail_path: Optional[str] = Field(None)
    mime_type: str
    size_bytes: int
    description: Optional[str] = Field(None)
    tags: Optional[str] = Field(None) # 可以用Text类型，或JSONB存储标签数组
    metadata: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    upload_date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    # updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    category_id: uuid.UUID = Field(foreign_key="category.id", index=True)
    # category: Optional["Category"] = Relationship(back_populates="images")

```

## 模型转换与字段映射表

| 前端字段 (`ImageRead`)             | 后端Pydantic `ImageRead` 字段 | 数据库 `Image` 字段        | 转换规则/说明                                                                              |
|------------------------------------|---------------------------------|------------------------------|------------------------------------------------------------------------------------------|
| `id: string`                       | `id: uuid.UUID`                 | `id: uuid.UUID`              | 字符串 ↔ UUID 双向转换。                                                                 |
| `title: string`                    | `title: Optional[str]`          | `title: Optional[str]`       |                                                                                          |
| `description?: string`             | `description: Optional[str]`    | `description: Optional[str]` |                                                                                          |
| `imageUrl: string`                 | `image_url: str`                | `relative_file_path: str`    | 后端根据`relative_file_path`和配置的基地址生成完整的`image_url`。                           |
| `thumbnailUrl?: string`            | `thumbnail_url: Optional[str]`  | `relative_thumbnail_path: Optional[str]` | 后端根据`relative_thumbnail_path`生成完整的`thumbnail_url`，如果存在。                      |
| `categoryId: string`               | `category_id: uuid.UUID`        | `category_id: uuid.UUID`     | 字符串 ↔ UUID 双向转换。                                                                 |
| `createdDate: string`              | `created_at: datetime`          | `upload_date: datetime`      | ISO 8601 时间字符串 ↔ Python `datetime` 对象。数据库字段名可能为`upload_date`。            |
| `tags?: string`                    | `tags: Optional[str]`           | `tags: Optional[str]`        | 逗号分隔的字符串或JSON字符串。                                                              |
| `file_metadata: { ... }`           | `file_metadata: Optional[Dict]` | `file_metadata: Optional[Dict]` (原 metadata) | JSON对象 ↔ Python Dict。 数据库字段已改为 file_metadata                                  |

**上传/创建 (`ImageUploadData` -> `ImageCreate`) 时：**
*   前端发送 `imageFile: File`, `categoryId: string`, 及可选的 `title?, description?, tags?` (通常作为`FormData`)。
*   后端API端点接收文件 (`UploadFile`) 和其他表单字段 (`Form(...)`)。后端服务层可将这些字段聚合为内部的`ImageCreate`对象（不含文件本身），文件单独处理。后端从文件名或`title`参数确定标题，提取文件元数据等，填充完整的数据库模型字段。

**更新 (`ImageUpdate`) 时：**
*   前端发送 `title?`, `description?`, `tags?`, `categoryId?`。
*   后端 `ImageUpdate` Pydantic 模型应包含这些可选字段以供更新。
