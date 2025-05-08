#!/usr/bin/env python3
"""物种信息模块的数据模型

定义物种信息相关的SQLModel类，用于数据库交互和API数据校验。
同时包含中文名到拼音转换的工具函数。
"""
from typing import Optional
from sqlmodel import Field, SQLModel
from pypinyin import pinyin, Style  # 用于生成拼音


# --- 拼音处理工具函数 ---
def get_pinyin_full(text: str) -> str:
    """
    将中文文本转换为全拼 (小写)

    参数:
        text (str): 中文文本

    返回:
        str: 全拼字符串 (小写)
    """
    if not text:
        return ""
    return "".join(
        item[0] for item in pinyin(text, style=Style.NORMAL, heteronym=False)
    ).lower()


def get_pinyin_initials(text: str) -> str:
    """
    将中文文本转换为拼音首字母 (小写)

    参数:
        text (str): 中文文本

    返回:
        str: 拼音首字母字符串 (小写)
    """
    if not text:
        return ""
    return "".join(
        item[0][0] for item in pinyin(text, style=Style.FIRST_LETTER, heteronym=False)
    ).lower()


# --- SQLModel 定义 ---
class SpeciesBase(SQLModel):
    """物种基础模型，包含共享字段"""

    order_details: str = Field(description="目信息 (例如: 雀形目Passeriformes)")
    family_details: str = Field(description="科信息 (例如: 裸鼻雀科 Thraupidae)")
    genus_details: str = Field(description="属信息 (例如: 印加雀属Incaspiza)")

    name_chinese: str = Field(index=True, unique=True, description="中文种名")
    name_english: Optional[str] = Field(default=None, description="英文种名")
    name_latin: Optional[str] = Field(default=None, description="学名 (拉丁文学名)")
    href: Optional[str] = Field(default=None, description="相关链接")

    # 衍生字段，用于高效搜索，在数据入库时生成
    pinyin_full: Optional[str] = Field(
        default=None, index=True, description="中文名全拼 (小写)"
    )
    pinyin_initials: Optional[str] = Field(
        default=None, index=True, description="中文名拼音首字母 (小写)"
    )


class Species(SpeciesBase, table=True):
    """数据库中的物种表模型"""

    # __tablename__ = "species_info" # 如果希望表名与类名不同或更明确
    id: Optional[int] = Field(default=None, primary_key=True, index=True)


class SpeciesCreate(SpeciesBase):
    """用于创建新物种记录时的数据模型 (API输入)

    pinyin_full 和 pinyin_initials 将在服务层根据 name_chinese 计算填充后存入数据库。
    """

    pass  # 继承自SpeciesBase，拼音字段将在入库前生成


class SpeciesRead(SpeciesBase):
    """用于从API读取/返回物种信息的数据模型 (API输出)"""

    id: int
    # 默认情况下，SpeciesBase 中的所有字段都会被包含。


# 辅助函数：用于在创建Species实例前自动填充拼音 (通常在CRUD或服务层调用)
def populate_pinyin_for_species_create(
    species_create_data: SpeciesCreate,
) -> SpeciesCreate:
    """
    接收一个 SpeciesCreate 对象 (通常来自API请求体)，
    为其填充 pinyin_full 和 pinyin_initials 字段。
    返回更新后的 SpeciesCreate 对象，准备用于创建 Species 数据库记录。

    注意：此函数修改并返回传入的对象，或者可以设计为返回新对象。
           为保持简单，这里直接修改。
    """
    if species_create_data.name_chinese:
        species_create_data.pinyin_full = get_pinyin_full(
            species_create_data.name_chinese
        )
        species_create_data.pinyin_initials = get_pinyin_initials(
            species_create_data.name_chinese
        )
    return species_create_data
