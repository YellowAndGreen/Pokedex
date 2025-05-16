"""API路由聚合模块

此模块导入并聚合项目中所有API路由，方便主应用统一注册。
"""

from fastapi import APIRouter

from . import categories  # 导入类别路由模块
from . import images  # 导入图片路由模块
from . import species_info_router  # 导入物种信息路由模块


__all__ = [
    "categories",
    "images",
    "species_info_router",  # 将新的路由模块添加到 __all__
]

# This file makes Python treat the directory as a package.
