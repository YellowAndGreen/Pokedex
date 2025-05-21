"""SQLModel模型定义包

此包包含项目中所有数据库表模型及API数据交互模型。

处理SQLModel中的Forward References (前向引用):
当模型A引用模型B，模型B也引用模型A时，可能产生循环导入。
SQLModel通过字符串类型提示和`model_rebuild()`解决此问题。
确保在所有相关模型定义完毕后，调用各模型的`model_rebuild()`方法，
通常在`models/__init__.py`（如此文件）或应用启动时（如`main.py`）执行。
"""

from .category_models import (
    Category,
    CategoryBase,
    CategoryCreate,
    CategoryRead,
    CategoryReadWithImages,
    CategoryUpdate,
)
from .image_models import Image, ImageBase, ImageCreate, ImageRead, ImageUpdate
from .species_info_models import (
    Species,
    SpeciesBase,
    SpeciesCreate,
    SpeciesRead,
    get_pinyin_full,
    get_pinyin_initials,
    populate_pinyin_for_species_create,
)

# 解析所有模型导入后的前向引用
# 这对于使用字符串类型提示（如 List["Image"]）定义的关系至关重要
Category.model_rebuild()
Image.model_rebuild()
CategoryReadWithImages.model_rebuild()
ImageRead.model_rebuild()
Species.model_rebuild()
SpeciesRead.model_rebuild()

__all__ = [
    "Category",
    "CategoryBase",
    "CategoryCreate",
    "CategoryRead",
    "CategoryReadWithImages",
    "CategoryUpdate",
    "Image",
    "ImageBase",
    "ImageCreate",
    "ImageRead",
    "ImageUpdate",
    "Species",
    "SpeciesBase",
    "SpeciesCreate",
    "SpeciesRead",
    "get_pinyin_full",
    "get_pinyin_initials",
    "populate_pinyin_for_species_create",
]
