#!/usr/bin/env python3
"""物种信息模块的CRUD (Create, Read, Update, Delete) 操作

包含与数据库交互以检索和操作物种数据的功能。
"""
from typing import List, Optional
from sqlmodel import Session, select, or_
from sqlalchemy import func  # 用于数据库端的 lower 函数

# 从当前应用的models模块中导入物种模型
from ..models.species_info_models import Species


def search_species_names_by_term(
    db: Session, search_term: str, limit: int = 10
) -> List[str]:
    """
    根据用户提供的单个 search_term 字符串，进行前缀匹配搜索。
    匹配字段：中文名 (name_chinese), 中文名全拼 (pinyin_full), 中文名拼音首字母 (pinyin_initials)。
    返回匹配到的物种中文名列表。

    参数:
        db (Session): 数据库会话。
        search_term (str): 用户输入的搜索词。
        limit (int): 返回结果的最大数量。

    返回:
        List[str]: 匹配到的物种中文名列表。
    """
    if not search_term:
        return []

    term_lower = search_term.lower()

    conditions = or_(
        func.lower(Species.name_chinese).startswith(term_lower),
        Species.pinyin_full.startswith(term_lower),  # 假设已小写存储
        Species.pinyin_initials.startswith(term_lower),  # 假设已小写存储
    )

    statement = select(Species.name_chinese).where(conditions).limit(limit)
    matched_chinese_names = db.exec(statement).all()
    return matched_chinese_names


def get_species_by_exact_chinese_name(
    db: Session, name_chinese: str
) -> Optional[Species]:
    """
    根据精确的物种中文名查找并返回完整的物种信息对象 (忽略大小写)。

    参数:
        db (Session): 数据库会话。
        name_chinese (str): 要查询的物种精确中文名。

    返回:
        Optional[Species]: 匹配到的物种对象，如果未找到则返回 None。
    """
    statement = select(Species).where(
        func.lower(Species.name_chinese) == name_chinese.lower()
    )
    result = db.exec(statement).first()
    return result


# 未来可以添加创建物种的CRUD函数，例如:
# from ..models.species_info_models import SpeciesCreate, populate_pinyin_for_species_create
#
# def create_species(
#     db: Session,
#     species_in: SpeciesCreate
# ) -> Species:
#     """
#     创建新的物种记录。
#     在存入数据库前，会自动处理 pinyin_full 和 pinyin_initials 字段。
#     """
#     # 填充拼音字段
#     species_data_with_pinyin = populate_pinyin_for_species_create(species_in)
#
#     # 使用 model_dump (Pydantic v2) 或 dict (Pydantic v1) 转换
#     # 注意：如果 SpeciesCreate 和 Species 有字段差异 (除了table=True和id)
#     # 可能需要更细致的转换或直接使用 Species(**species_data_with_pinyin.model_dump())
#     db_species = Species.model_validate(species_data_with_pinyin)
#     db.add(db_species)
#     # session.commit() 和 session.refresh(db_species) 通常在 get_session() 中处理或由调用者处理
#     # 此处仅添加，事务管理由 get_session 装饰器或上下文管理器负责
#     return db_species
