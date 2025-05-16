"""类别CRUD操作模块

包含针对Category模型的数据库增删改查函数。
"""

from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload  # 用于预加载关联的图片数据，避免N+1查询问题
from fastapi.concurrency import run_in_threadpool  # MODIFIED: Added import

from app.models import Category, CategoryCreate, CategoryReadWithImages, Image
from app.services.file_storage_service import FileStorageService
from app.core.config import settings
from pathlib import Path


def create_category(*, session: Session, category_create: CategoryCreate) -> Category:
    """
    在数据库中创建一个新的类别。

    参数:
        session (Session):数据库会话对象。
        category_create (CategoryCreate):包含类别数据的模型。

    返回:
        Category:创建成功后的类别对象。
    """
    db_category = Category.model_validate(category_create)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


def get_category_by_id(*, session: Session, category_id: int) -> Optional[Category]:
    """
    根据ID从数据库中获取一个类别。

    参数:
        session (Session):数据库会话对象。
        category_id (int):要获取的类别的ID。

    返回:
        Optional[Category]:如果找到则返回类别对象，否则返回None。
    """
    category = session.get(Category, category_id)
    return category


def get_category_by_name(*, session: Session, name: str) -> Optional[Category]:
    """
    根据名称从数据库中获取一个类别。

    参数:
        session (Session):数据库会话对象。
        name (str):要获取的类别的名称。

    返回:
        Optional[Category]:如果找到则返回类别对象，否则返回None。
    """
    statement = select(Category).where(Category.name == name)
    category = session.exec(statement).first()
    return category


def get_all_categories(
    *, session: Session, skip: int = 0, limit: int = 100
) -> List[Category]:
    """
    从数据库中获取所有类别 (支持分页)。

    参数:
        session (Session):数据库会话对象。
        skip (int):跳过的记录数。
        limit (int):返回的最大记录数。

    返回:
        List[Category]:类别对象列表。
    """
    statement = select(Category).offset(skip).limit(limit)
    categories = session.exec(statement).all()
    return categories


def get_category_with_images_by_id(
    *, session: Session, category_id: int
) -> Optional[CategoryReadWithImages]:
    """
    根据ID获取类别及其关联的所有图片。

    参数:
        session (Session): 数据库会话对象。
        category_id (int): 类别的ID。

    返回:
        Optional[CategoryReadWithImages]: 包含图片列表的类别对象，如果未找到则为None。
    """
    # 使用 selectinload 预加载 'images' 关系，避免在后续访问 category.images 时产生 N+1 查询问题。
    category_db = session.exec(
        select(Category)
        .options(selectinload(Category.images))
        .where(Category.id == category_id)
    ).first()

    if not category_db:
        return None

    return CategoryReadWithImages.model_validate(category_db)


def update_category(
    *, session: Session, db_category: Category, category_in: CategoryCreate
) -> Category:
    """
    更新数据库中现有类别的信息。

    参数:
        session (Session):数据库会话对象。
        db_category (Category):从数据库获取的现有类别对象。
        category_in (CategoryCreate):包含更新后类别数据的模型。

    返回:
        Category:更新成功后的类别对象。
    """
    category_data = category_in.dict(exclude_unset=True)
    for key, value in category_data.items():
        setattr(db_category, key, value)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


async def delete_category(*, session: Session, category_id: int) -> None:
    """异步删除类别及其关联资源"""
    """
    从数据库中删除一个类别，并级联删除该类别下的所有图片记录及其物理文件。
    注意：此函数仅删除数据库记录，物理文件的删除应由文件服务处理。

    参数:
        session (Session):数据库会话对象。
        category_id (int):要删除的类别的ID。

    返回:
        Optional[Category]: 如果删除成功则返回被删除的类别对象，否则返回None (如果未找到)。
    """
    category_to_delete = session.get(Category, category_id)
    if not category_to_delete:
        return None

    file_service = FileStorageService()

    # MODIFIED: Use run_in_threadpool for sync DB calls
    # Note: .all() should also be part of the threadpool execution if it's a separate call
    # For simplicity, if session.exec already returns an iterable list, this is fine.
    # If session.exec returns a query object and .all() executes it, wrap the whole thing.
    # Assuming session.exec().all() is a combined operation for this example or .all() is non-blocking.
    # A safer approach for .all() if it hits DB:
    # statement = select(Image).where(Image.category_id == category_id)
    # images_in_category_result = await run_in_threadpool(session.exec, statement)
    # images_in_category = images_in_category_result.all() # if .all() is on the result and non-blocking
    # Or more directly:
    def get_images():
        return session.exec(select(Image).where(Image.category_id == category_id)).all()

    images_in_category = await run_in_threadpool(get_images)

    for img in images_in_category:
        # Delete physical files first
        if img.relative_file_path:
            original_image_full_path = (
                file_service.image_storage_root / img.relative_file_path
            )
            await file_service.delete_file(original_image_full_path)
        if img.relative_thumbnail_path:
            thumbnail_full_path = (
                file_service.thumbnail_storage_root / img.relative_thumbnail_path
            )
            await file_service.delete_file(thumbnail_full_path)

        # MODIFIED: Use run_in_threadpool for sync DB calls
        await run_in_threadpool(session.delete, img)

    if images_in_category:
        # MODIFIED: Use run_in_threadpool for sync DB calls
        await run_in_threadpool(session.commit)  # Commit image deletions from DB

    # MODIFIED: Use run_in_threadpool for sync DB calls
    await run_in_threadpool(session.delete, category_to_delete)
    # MODIFIED: Use run_in_threadpool for sync DB calls
    await run_in_threadpool(session.commit)  # Commit category deletion
    return category_to_delete
