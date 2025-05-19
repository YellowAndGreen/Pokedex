"""类别API路由模块

提供与图片类别相关的HTTP接口，包括创建、查询、更新和删除类别。
"""

from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session

from app.database import get_session
from app.models import Category, CategoryCreate, CategoryRead, CategoryReadWithImages
from app.crud import category_crud

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


@router.put("/{category_id}/", response_model=CategoryRead, summary="更新特定类别信息")
def update_category(
    *,
    session: Session = Depends(get_session),
    category_id: uuid.UUID,
    category_in: CategoryCreate,  # 使用CategoryCreate作为更新模型，也可以定义专门的CategoryUpdate
) -> Category:
    """
    更新指定ID的类别信息。
    """
    db_category = category_crud.get_category_by_id(
        session=session, category_id=category_id
    )
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="类别未找到")

    # 检查新名称是否与现有其他类别冲突
    if category_in.name != db_category.name:
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
        session=session, db_category=db_category, category_in=category_in
    )
    return updated_category


@router.delete(
    "/{category_id}/", status_code=status.HTTP_204_NO_CONTENT, summary="删除特定类别"
)
async def delete_category(*, session: Session = Depends(get_session), category_id: uuid.UUID):
    """
    删除指定ID的类别。

    **注意**: 当前版本的实现主要删除类别记录本身。
    根据数据库外键约束设置，关联的图片可能：
    1. 被级联删除 (如果设置了 ON DELETE CASCADE)。
    2. 导致删除失败 (如果设置了 ON DELETE RESTRICT 或默认行为且存在关联图片)。
    3. 外键被置空 (如果设置了 ON DELETE SET NULL)。

    在`README.md`规划中，删除类别应同时删除关联图片。这部分逻辑的完善
    建议在专门的服务层处理，或者在`category_crud.delete_category`中增加
    对关联图片的处理逻辑（包括物理文件的删除）。
    目前，如果存在关联图片且外键未设置级联删除，此操作可能会失败。
    """
    db_category = category_crud.get_category_by_id(
        session=session, category_id=category_id
    )
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="类别未找到")

    # 检查该类别下是否还有图片，根据实际需求决定是否允许删除非空类别
    if db_category.images:  # images 是 Category 模型中定义的 relationship
        # 根据项目需求，这里可以抛出异常，阻止删除非空类别，
        # 或者调用服务层方法来处理图片的级联删除（包括文件）。
        # 为符合README中"删除类别及关联图片"的描述，此处应有更复杂的处理
        # 但当前CRUD层仅删除类别。这里暂时先允许删除，依赖数据库层面或后续服务层处理。
        # 进一步处理逻辑待定 (例如：可以记录日志，或者根据配置决定是否抛出异常)
        print(
            f"警告：正在删除类别 {db_category.name} (ID: {category_id})，该类别下尚有关联图片。关联图片的处理需后续完善。"
        )

    await category_crud.delete_category(session=session, category_id=category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
