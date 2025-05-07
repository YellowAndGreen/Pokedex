"""SQLModel模型定义包

此包包含项目中所有数据库表模型及API数据交互模型。

处理SQLModel中的Forward References (前向引用):
当模型A引用模型B，模型B也引用模型A时，可能产生循环导入。
SQLModel通过字符串类型提示和`update_forward_refs()`解决此问题。
确保在所有相关模型定义完毕后，调用各模型的`update_forward_refs()`方法，
通常在`models/__init__.py`（如此文件）或应用启动时（如`main.py`）执行。
"""

from .category_models import (
    Category,
    CategoryBase,
    CategoryCreate,
    CategoryRead,
    CategoryReadWithImages,
)
from .image_models import Image, ImageBase, ImageCreate, ImageRead, ImageUpdate

# 解析所有模型导入后的前向引用
# 这对于使用字符串类型提示（如 List["Image"]）定义的关系至关重要
Category.update_forward_refs()
Image.update_forward_refs()
CategoryReadWithImages.update_forward_refs()
ImageRead.update_forward_refs()

__all__ = [
    "Category",
    "CategoryBase",
    "CategoryCreate",
    "CategoryRead",
    "CategoryReadWithImages",
    "Image",
    "ImageBase",
    "ImageCreate",
    "ImageRead",
    "ImageUpdate",
]
