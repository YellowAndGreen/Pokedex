"""类别API路由模块

提供与图片类别相关的HTTP接口，包括创建、查询、更新和删除类别。
"""

from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session

from app.database import get_session
from app.models import (
    Category,
    CategoryCreate,
    CategoryRead,
    CategoryReadWithImages,
    CategoryUpdate,
    ImageRead,
)
from app.crud import category_crud
from app.crud import image_crud
from app.utils import run_sync

router = APIRouter(
    prefix="/categories",
    tags=["类别管理"],
    responses={404: {"description": "未找到"}},
)


@router.post(
    "/",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="创建新类别",
)
def create_category(
    *, session: Session = Depends(get_session), category_in: CategoryCreate
) -> Category:
    """
    创建一个新的图片类别。

    - **name**: 类别名称，必须唯一。
    - **description**: 类别的可选描述。
    """
    db_category_by_name = category_crud.get_category_by_name(
        session=session, name=category_in.name
    )
    if db_category_by_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="具有相同名称的类别已存在"
        )
    created_category = category_crud.create_category(
        session=session, category_create=category_in
    )
    return created_category


@router.get("/", response_model=List[CategoryRead], summary="获取所有类别列表")
def read_categories(
    *, session: Session = Depends(get_session), skip: int = 0, limit: int = 100
) -> List[Category]:
    """
    检索所有图片类别，支持分页。
    """
    categories = category_crud.get_all_categories(
        session=session, skip=skip, limit=limit
    )
    return categories


@router.get(
    "/{category_id}/",
    response_model=CategoryReadWithImages,
    summary="获取特定类别及其图片",
)
def read_category_with_images(
    *, session: Session = Depends(get_session), category_id: uuid.UUID
) -> CategoryReadWithImages:
    """
    根据ID获取一个特定类别及其包含的所有图片的元数据。
    """
    db_category = category_crud.get_category_with_images_by_id(
        session=session, category_id=category_id
    )
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="类别未找到")
    return db_category


@router.patch(
    "/{category_id}/", response_model=CategoryRead, summary="更新特定类别信息"
)
def update_category(
    *,
    session: Session = Depends(get_session),
    category_id: uuid.UUID,
    category_in: CategoryUpdate,
) -> Category:
    """
    更新指定ID的类别信息。
    如果提供了名称，会检查新名称是否与现有其他类别冲突。
    """
    db_category = category_crud.get_category_by_id(
        session=session, category_id=category_id
    )
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="类别未找到")

    if category_in.name is not None and category_in.name != db_category.name:
        existing_category_with_new_name = category_crud.get_category_by_name(
            session=session, name=category_in.name
        )
        if (
            existing_category_with_new_name
            and existing_category_with_new_name.id != category_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="更新后的类别名称已存在"
            )

    updated_category = category_crud.update_category(
        session=session, db_category=db_category, category_update=category_in
    )
    return updated_category


@router.delete(
    "/{category_id}/", status_code=status.HTTP_204_NO_CONTENT, summary="删除特定类别"
)
async def delete_category(
    *, session: Session = Depends(get_session), category_id: uuid.UUID
):
    """
    删除指定ID的类别。

    重要提示:
    此操作会级联删除类别下的所有图片记录及其对应的物理文件。
    在执行删除前，会首先检查类别是否存在。
    """
    # 检查类别是否存在
    db_category = await run_sync(
        category_crud.get_category_by_id, session=session, category_id=category_id
    )
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="类别未找到")

    # 执行删除操作，CRUD函数中已包含完整的级联删除逻辑
    await category_crud.delete_category(session=session, category_id=category_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{category_id}/images/", response_model=List[ImageRead])
def get_images_in_category(
    category_id: uuid.UUID,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
):
    """
    获取指定类别下的所有图片 (支持分页)。
    """
    # 首先校验类别是否存在
    db_category = category_crud.get_category_by_id(
        session=session, category_id=category_id
    )
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    # 获取该类别下的图片
    images = image_crud.get_images_by_category_id(
        session=session, category_id=category_id, skip=skip, limit=limit
    )
    return images
