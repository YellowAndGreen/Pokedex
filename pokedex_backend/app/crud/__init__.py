"""CRUD (数据库操作) 模块包

此包聚合了所有与数据库模型直接交互的函数（增删改查）。
每个模型通常有对应的CRUD模块，如 `category_crud.py`。

这些函数由API路由调用，实现业务逻辑与数据库访问的分离。
"""

from . import category_crud
from . import image_crud
from . import species_info_crud

# 可选择性暴露具体CRUD函数，以便其他模块更清晰地导入
# 例如:
# from .category_crud import create_category, get_category_by_id
# from .image_crud import create_image, get_image_by_id

__all__ = [
    "category_crud",
    "image_crud",
    "species_info_crud",
]

# This file makes Python treat the directory as a package.
