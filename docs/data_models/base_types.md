# 基础类型定义

## 通用字段规范
```typescript
// 前端基础类型 pokedex_frontend/src/types/index.ts:5-10
interface BaseEntity {
  id: string;
  createdDate: string;
  updatedDate: string;
}
```

```python
# 后端基础模型 pokedex_backend/app/models/__init__.py:32-38
class BaseSchema(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
```

## 类型转换规则
| 前端类型 | 后端类型 | 转换方式                  |
|----------|----------|--------------------------|
| string   | UUID     | 使用uuidv4生成并验证格式  |
| string   | datetime | ISO 8601格式双向转换      |
| File     | UploadFile| 通过multipart/form-data上传 |

## 通用错误类型
```mermaid
classDiagram
    class ErrorResponse {
        <<interface>>
        +number code
        +string message
        +any details?
    }
    
    ErrorResponse <|-- ValidationError
    ErrorResponse <|-- DatabaseError
    ErrorResponse <|-- AuthError
