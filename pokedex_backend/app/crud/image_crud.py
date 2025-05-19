"""图片CRUD操作模块

包含针对Image模型的数据库增删改查函数。
"""

from typing import List, Optional
from sqlmodel import Session, select
import uuid

from app.models import (
    Image,
    ImageCreate,
    ImageUpdate,
)  # ImageCreate 通常在内部使用
from app.services.file_storage_service import FileStorageService
from app.core.config import settings
from pathlib import Path


def create_image(*, session: Session, image_create_data: ImageCreate) -> Image:
    """
    在数据库中创建一个新的图片记录。通常在文件物理保存后调用。

    参数:
        session (Session): 数据库会话对象。
        image_create_data (ImageCreate): 包含图片元数据的模型。
                                        实际的文件字节流由文件服务处理。

    返回:
        Image: 创建成功后的图片对象。
    """
    db_image = Image.model_validate(image_create_data)
    session.add(db_image)
    session.commit()
    session.refresh(db_image)
    return db_image


def get_image_by_id(*, session: Session, image_id: uuid.UUID) -> Optional[Image]:
    """
    根据ID从数据库中获取一个图片记录。

    参数:
        session (Session): 数据库会话对象。
        image_id (uuid.UUID): 要获取的图片的ID。

    返回:
        Optional[Image]: 如果找到则返回图片对象，否则返回None。
    """
    image = session.get(Image, image_id)
    return image


def get_images_by_category_id(
    *, session: Session, category_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> List[Image]:
    """
    根据类别ID从数据库中获取该类别下的所有图片记录 (支持分页)。

    参数:
        session (Session): 数据库会话对象。
        category_id (uuid.UUID): 类别的ID。
        skip (int): 跳过的记录数。
        limit (int): 返回的最大记录数。

    返回:
        List[Image]: 图片对象列表。
    """
    statement = (
        select(Image).where(Image.category_id == category_id).offset(skip).limit(limit)
    )
    images = session.exec(statement).all()
    return images


def get_all_images(*, session: Session, skip: int = 0, limit: int = 100) -> List[Image]:
    """
    获取数据库中所有的图片记录 (支持分页)。
    此函数通常在管理后台或特定场景使用，一般更推荐按类别查询。

    参数:
        session (Session): 数据库会话对象。
        skip (int): 跳过的记录数。
        limit (int): 返回的最大记录数。

    返回:
        List[Image]: 图片对象列表。
    """
    statement = select(Image).offset(skip).limit(limit)
    images = session.exec(statement).all()
    return images


def update_image_metadata(
    *, session: Session, db_image: Image, image_in: ImageUpdate
) -> Image:
    """
    更新数据库中现有图片的元数据 (如描述、标签、所属类别)。

    参数:
        session (Session): 数据库会话对象。
        db_image (Image): 从数据库获取的现有图片对象。
        image_in (ImageUpdate): 包含更新后图片元数据的模型。

    返回:
        Image: 更新成功后的图片对象。
    """
    update_data = image_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_image, key, value)
    session.add(db_image)
    session.commit()
    session.refresh(db_image)
    return db_image


async def delete_image(*, session: Session, image_id: uuid.UUID) -> Optional[Image]:
    """
    从数据库中删除一个图片记录及其物理文件 (原图和缩略图)。

    参数:
        session (Session): 数据库会话对象。
        image_id (uuid.UUID): 要删除的图片的ID。

    返回:
        Optional[Image]: 如果删除成功则返回被删除的图片对象，否则返回None (如果未找到)。
    """
    db_image = await run_in_threadpool(session.get, Image, image_id)
    if not db_image:
        return None

    file_service = FileStorageService()

    # Delete physical files first
    if db_image.relative_file_path:
        original_image_full_path = (
            file_service.image_storage_root / db_image.relative_file_path
        )
        await file_service.delete_file(original_image_full_path)

    if db_image.relative_thumbnail_path:
        thumbnail_full_path = (
            file_service.thumbnail_storage_root / db_image.relative_thumbnail_path
        )
        await file_service.delete_file(thumbnail_full_path)

    await run_in_threadpool(session.delete, db_image)
    await run_in_threadpool(session.commit)
    return db_image
