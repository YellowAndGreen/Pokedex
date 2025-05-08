# 统一数据模型规范

## 目录结构
```
docs/
├── data_models/
│   ├── category.md      # 分类数据模型
│   ├── image.md         # 图片数据模型
│   └── base_types.md    # 基础类型定义
```

## 模型关系图
```mermaid
classDiagram
    direction LR
    
    class FrontendCategory {
        +string id
        +string name
        +string thumbnailUrl
    }
    
    class BackendCategoryCreate {
        +string name
        +file thumbnail
    }
    
    class BackendCategoryDB {
        +UUID id
        +string name
        +string thumbnail_path
    }
    
    FrontendCategory --|> BackendCategoryDB : 数据转换
    BackendCategoryCreate --|> BackendCategoryDB : 持久化
