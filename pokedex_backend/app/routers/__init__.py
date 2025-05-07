"""API路由聚合模块

此模块导入并聚合项目中所有API路由，方便主应用统一注册。
"""

from fastapi import APIRouter

from . import categories  # 导入类别路由模块
from . import images  # 导入图片路由模块

# 创建一个主路由或者直接导出子路由供main.py使用
# 方式一：创建一个聚合的总路由 (如果希望所有路由有共同前缀或配置)
# api_router = APIRouter(prefix="/api/v1") # 示例：统一前缀
# api_router.include_router(categories.router)
# api_router.include_router(images.router)

# 方式二：直接暴露子路由，由main.py分别包含
# (这种方式更常见，如果各模块路由前缀不同或独立性强)

__all__ = [
    "categories",
    "images",
]
