"""图片CRUD操作模块

包含针对Image模型的数据库增删改查函数。
"""

from typing import List, Optional
from fastapi.concurrency import run_in_threadpool
from sqlmodel import Session, select, func, col
import uuid
from sqlalchemy.orm import selectinload, joinedload  # 导入 selectinload 和 joinedload

from app.models import (
    Image,
    ImageCreate,
    ImageUpdate,
    ExifData,
    Tag,
    ImageTagLink,
)  # ImageCreate 通常在内部使用
from app.services.file_storage_service import FileStorageService
from app.core.config import settings
from pathlib import Path
from app.crud import tag_crud
from app.crud.tag_crud import get_tag_by_name, create_tag, get_or_create_tag


def create_image_with_tags(
    db: Session, image_create: ImageCreate, tag_names: List[str]
) -> Image:
    """
    Create an image and associate it with tags.
    If a tag does not exist, it will be created.
    """
    # Create the Image instance from the create-schema, but exclude 'tags' for now
    # as we need to handle them separately.
    db_image = Image.model_validate(image_create, update={"tags": []})

    # Add the image to the session to get an ID before creating relationships
    db.add(db_image)
    db.flush()

    # Handle tags
    if tag_names:
        for tag_name in tag_names:
            if tag_name.strip():
                # Get or create the tag
                tag = get_or_create_tag(session=db, tag_name=tag_name.strip())
                db_image.tags.append(tag)

    db.commit()
    db.refresh(db_image)
    return db_image


def get_image_by_id(*, session: Session, image_id: uuid.UUID) -> Optional[Image]:
    """
    根据ID从数据库中获取一个图片记录。
    使用 selectinload 优化，一次性加载关联的标签。
    """
    statement = (
        select(Image).options(selectinload(Image.tags)).where(Image.id == image_id)
    )
    image = session.exec(statement).first()
    return image


def get_images_by_category_id(
    *, session: Session, category_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> List[Image]:
    """
    根据类别ID获取图片记录列表 (支持分页)。
    使用 selectinload 优化，一次性加载所有图片的关联标签，避免N+1查询。
    """
    statement = (
        select(Image)
        .options(selectinload(Image.tags))  # 预加载标签
        .where(Image.category_id == category_id)
        .offset(skip)
        .limit(limit)
    )
    images = session.exec(statement).all()
    return images


def get_all_images(*, session: Session, skip: int = 0, limit: int = 100) -> List[Image]:
    """
    获取数据库中所有的图片记录 (支持分页)。
    使用 selectinload 优化，一次性加载所有图片的关联标签，避免N+1查询。
    """
    statement = (
        select(Image)
        .options(selectinload(Image.tags))  # 预加载标签
        .offset(skip)
        .limit(limit)
    )
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
    # Extract tags before dumping model, as it's handled via relationship
    tags_update_data = image_in.tags
    update_data = image_in.model_dump(
        exclude_unset=True, exclude={"tags", "set_as_category_thumbnail"}
    )

    # Update standard fields
    for key, value in update_data.items():
        setattr(db_image, key, value)

    # Handle tags update if tags_update_data is not None (meaning client wants to update tags)
    if tags_update_data is not None:
        db_image.tags.clear()  # Clear existing tags first
        for tag_name in tags_update_data:
            tag = tag_crud.get_or_create_tag(session=session, tag_name=tag_name)
            db_image.tags.append(tag)

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

    # Clear tag associations before deleting the image
    # This should remove entries from ImageTagLink table
    # Needs to be done in a synchronous block if db_image.tags is a sync relationship manager
    def clear_tags_sync(img_to_clear_tags: Image):
        img_to_clear_tags.tags.clear()
        session.add(
            img_to_clear_tags
        )  # Re-add to session if clear() detaches or similar
        session.commit()  # Commit this change specifically for tags

    await run_in_threadpool(clear_tags_sync, db_image)
    # Refresh to ensure the state is current before final delete, though likely not strictly needed here
    # await run_in_threadpool(session.refresh, db_image)

    await run_in_threadpool(session.delete, db_image)
    await run_in_threadpool(session.commit)
    return db_image


def get_images_by_tag_names(
    *,
    session: Session,
    tag_names: List[str],
    match_all: bool = False,
    skip: int = 0,
    limit: int = 100,
) -> List[Image]:
    """
    根据一个或多个标签名称获取图片列表。

    参数:
        session: 数据库会话。
        tag_names: 标签名称列表。
        match_all: 如果为 True，则图片必须匹配所有标签 (AND)；
                   如果为 False (默认)，则图片匹配任何一个标签 (OR)。
        skip: 分页偏移量。
        limit: 每页数量。

    返回:
        符合条件的图片列表。
    """
    # 基础查询，连接 Image 和 ImageTagLink
    statement = select(Image).join(ImageTagLink)

    if not tag_names:
        return []

    # 子查询：找到所有名字匹配的 Tag 的 ID
    tag_ids_stmt = select(Tag.id).where(col(Tag.name).in_(tag_names))
    tag_ids = session.exec(tag_ids_stmt).all()

    if not tag_ids:
        return []

    if match_all:
        # AND 逻辑：图片必须拥有所有指定的标签
        # 筛选出 image_id，这些 image_id 在 ImageTagLink 中与所有找到的 tag_id 相关联
        # 1. 过滤 ImageTagLink，只保留与目标 tag_ids 关联的记录
        # 2. 按 image_id 分组
        # 3. 使用 having 子句，确保每个 image_id 分组中的 tag_id 数量等于目标 tag_id 的总数
        subquery = (
            select(ImageTagLink.image_id)
            .where(col(ImageTagLink.tag_id).in_(tag_ids))
            .group_by(ImageTagLink.image_id)
            .having(func.count(ImageTagLink.tag_id) == len(tag_ids))
        ).alias("matching_images")

        # 主查询只选择 image_id 在子查询结果中的图片
        statement = statement.where(col(Image.id).in_(select(subquery.c.image_id)))

    else:
        # OR 逻辑：图片拥有任何一个指定的标签即可
        # 只需要 image_id 在 ImageTagLink 中与任何一个找到的 tag_id 关联即可
        statement = statement.where(col(ImageTagLink.tag_id).in_(tag_ids))

    # 去重，因为一个图片可能匹配多个标签 (在 OR 模式下)
    # 应用分页
    final_statement = statement.distinct().offset(skip).limit(limit)
    images = session.exec(final_statement).all()
    return images


def update_image_tags(session: Session, *, image: Image, new_tags: List[Tag]) -> Image:
    """
    更新图片的标签。
    这将替换图片所有现有的标签为新提供的标签列表。
    """
    # 清除旧的标签关联
    image.tags.clear()
    # 添加新的标签关联
    image.tags.extend(new_tags)

    session.add(image)
    session.commit()
    session.refresh(image)
    return image
