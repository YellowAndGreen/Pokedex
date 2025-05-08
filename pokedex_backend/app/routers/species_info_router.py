#!/usr/bin/env python3
"""物种信息模块的API路由

定义与物种信息相关的HTTP端点。
"""
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlmodel import Session

# 从当前应用的模块中导入依赖
from ..database import get_session  # 使用现有应用定义的数据库会话依赖
from ..models.species_info_models import SpeciesRead  # API响应模型
from ..crud import species_info_crud  # CRUD操作函数

# 创建一个新的APIRouter实例用于物种信息API
# 使用独特的tag使其在API文档中易于区分
router = APIRouter(
    tags=["Species Information"],  # 用于API文档分组
)


@router.get("/suggestions", response_model=List[str])
def get_species_suggestions_endpoint(
    *,
    db: Session = Depends(get_session),  # 依赖注入数据库会话
    q: str = Query(
        ..., min_length=1, description="搜索词 (可为中文、全拼或拼音首字母)"
    ),
    limit: int = Query(10, gt=0, le=20, description="返回建议结果的最大数量"),
):
    """
    获取物种中文名搜索建议列表。

    后端将使用查询词 `q` 同时对物种的中文名、中文名全拼、
    以及中文名拼音首字母进行前缀匹配搜索。
    """
    species_names_list = species_info_crud.search_species_names_by_term(
        db=db, search_term=q, limit=limit
    )
    # 对于建议列表，即使没有结果，通常也返回空列表而不是404
    return species_names_list


@router.get("/details/{chinese_name}", response_model=SpeciesRead)
def get_species_details_endpoint(
    *,
    db: Session = Depends(get_session),  # 依赖注入数据库会话
    chinese_name: str = Path(
        ..., description="要查询物种的精确中文名 (需URL编码若含特殊字符)"
    ),
):
    """
    根据物种的精确中文名获取其完整的详细信息。
    """
    species_instance = species_info_crud.get_species_by_exact_chinese_name(
        db=db, name_chinese=chinese_name
    )

    if not species_instance:
        raise HTTPException(
            status_code=404, detail=f"未找到名为 '{chinese_name}' 的物种。"
        )
    return species_instance
