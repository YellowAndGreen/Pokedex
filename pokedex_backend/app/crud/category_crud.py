"""类别CRUD操作模块

包含针对Category模型的数据库增删改查函数。
"""

from typing import List, Optional
from fastapi.concurrency import run_in_threadpool  # 用于在异步函数中运行同步IO操作
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload  # 用于预加载关联数据，避免N+1查询问题
import uuid

# 确保CategoryUpdate在模型中已定义并按需导入
from app.models import (
    Category,
    CategoryCreate,
    CategoryReadWithImages,
    Image,
    CategoryUpdate,
    Tag,
    ImageTagLink,
)
from app.services.file_storage_service import FileStorageService

# from app.core.config import settings # settings 似乎未在此文件中直接使用，可考虑移除
# from pathlib import Path # Path 似乎未在此文件中直接使用，可考虑移除


def create_category(*, session: Session, category_create: CategoryCreate) -> Category:
    """
    在数据库中创建一个新的类别。

    参数:
        session (Session): 数据库会话对象。
        category_create (CategoryCreate): 包含类别数据的Pydantic模型。

    返回:
        Category: 创建成功后的SQLModel类别对象。
    """
    # model_validate 从Pydantic模型创建SQLModel实例
    db_category = Category.model_validate(category_create)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)  # 刷新以获取数据库生成的值 (如默认时间戳)
    return db_category


def get_category_by_id(
    *, session: Session, category_id: uuid.UUID
) -> Optional[Category]:
    """
    根据ID从数据库中获取一个类别。

    参数:
        session (Session): 数据库会话对象。
        category_id (uuid.UUID): 要获取的类别的ID。

    返回:
        Optional[Category]: 如果找到则返回类别SQLModel对象，否则返回None。
    """
    category = session.get(Category, category_id)  # session.get 通过主键获取对象
    return category


def get_category_by_name(*, session: Session, name: str) -> Optional[Category]:
    """
    根据名称从数据库中获取一个类别。

    参数:
        session (Session): 数据库会话对象。
        name (str): 要获取的类别的名称。

    返回:
        Optional[Category]: 如果找到则返回类别SQLModel对象，否则返回None。
    """
    statement = select(Category).where(Category.name == name)
    category = session.exec(statement).first()  # 执行查询并获取第一个结果
    return category


def get_all_categories(
    *, session: Session, skip: int = 0, limit: int = 100
) -> List[Category]:
    """
    从数据库中获取所有类别 (支持分页)。

    参数:
        session (Session): 数据库会话对象。
        skip (int): 跳过的记录数 (用于分页)。
        limit (int): 返回的最大记录数 (用于分页)。

    返回:
        List[Category]: 类别SQLModel对象列表。
    """
    statement = select(Category).offset(skip).limit(limit)
    categories = session.exec(statement).all()  # 执行查询并获取所有结果
    return categories


def get_category_with_images_by_id(
    *, session: Session, category_id: uuid.UUID
) -> Optional[CategoryReadWithImages]:
    """
    根据ID获取类别及其关联的所有图片。
    使用 `selectinload` 预加载图片数据以优化性能，避免N+1查询问题。

    参数:
        session (Session): 数据库会话对象。
        category_id (uuid.UUID): 类别的ID。

    返回:
        Optional[CategoryReadWithImages]: 包含图片列表的Pydantic类别对象 (用于API响应)，如果未找到则为None。
    """
    # 使用 selectinload 预加载 'images' 关系
    category_db = session.exec(
        select(Category)
        .options(
            selectinload(Category.images)
        )  # 指示SQLAlchemy在查询Category时同时加载其关联的images
        .where(Category.id == category_id)
    ).first()

    if not category_db:
        return None

    # 将从数据库获取的SQLModel对象转换为Pydantic模型 (CategoryReadWithImages) 以便API返回
    return CategoryReadWithImages.model_validate(category_db)


# 注意: CategoryUpdate 模型应该从 app.models 导入
def update_category(
    *,
    session: Session,
    db_category: Category,
    category_update: CategoryUpdate  # 参数类型改为CategoryUpdate
) -> Category:
    """
    更新数据库中现有类别的信息。

    参数:
        session (Session): 数据库会话对象。
        db_category (Category): 从数据库获取的待更新的类别SQLModel对象。
        category_update (CategoryUpdate): 包含更新后类别数据的Pydantic模型。

    返回:
        Category: 更新成功后的类别SQLModel对象。
    """
    # exclude_unset=True 表示只获取在 category_update 中明确设置了值的字段
    category_data = category_update.model_dump(exclude_unset=True)
    for key, value in category_data.items():
        setattr(db_category, key, value)  # 动态设置db_category对象的属性
    session.add(db_category)  # 将更改添加到会话
    session.commit()  # 提交事务以保存更改
    session.refresh(db_category)  # 刷新对象以获取数据库中的最新状态
    return db_category


async def delete_category(
    *, session: Session, category_id: uuid.UUID
) -> Optional[Category]:
    """
    从数据库中删除一个类别，并级联删除该类别下的所有图片数据库记录及其对应的物理文件。
    同时会检查并删除不再被任何图片使用的标签。
    此函数设计为异步执行，文件IO和数据库操作通过 `run_in_threadpool` 在单独线程中运行，
    以避免阻塞FastAPI的事件循环。

    参数:
        session (Session): 数据库会话对象。
        category_id (uuid.UUID): 要删除的类别的ID。

    返回:
        Optional[Category]: 如果删除成功则返回被删除的类别对象 (在从数据库删除前获取的状态)，
                          如果未找到要删除的类别，则返回None。
    """
    # 在线程池中执行同步的数据库get操作
    def get_category_sync():
        return session.get(Category, category_id)

    category_to_delete = await run_in_threadpool(get_category_sync)

    if not category_to_delete:
        return None

    file_service = FileStorageService()  # 初始化文件存储服务

    # 定义一个同步函数来获取类别下的所有图片，以便在线程池中运行
    def get_images_sync():
        return session.exec(select(Image).where(Image.category_id == category_id)).all()

    images_in_category = await run_in_threadpool(get_images_sync)

    # 收集所有需要检查的标签（使用列表存储）
    all_tags_to_check = []
    for img in images_in_category:
        for tag in img.tags:
            if tag not in all_tags_to_check:  # 手动去重
                all_tags_to_check.append(tag)

    # 级联删除图片文件和数据库记录
    for img in images_in_category:
        # 首先尝试删除物理文件
        if img.relative_file_path:
            original_image_full_path = (
                file_service.image_storage_root / img.relative_file_path
            )
            # 文件删除是异步的IO操作，直接await
            await file_service.delete_file(original_image_full_path)
        if img.relative_thumbnail_path:
            thumbnail_full_path = (
                file_service.thumbnail_storage_root / img.relative_thumbnail_path
            )
            await file_service.delete_file(thumbnail_full_path)

        # 在线程池中执行同步的数据库delete操作 (针对单个图片)
        # 注意：这里只是标记为删除，真正的事务提交在最后统一进行
        await run_in_threadpool(session.delete, img)

    # 在线程池中执行同步的数据库delete操作 (针对类别本身)
    await run_in_threadpool(session.delete, category_to_delete)

    # 检查并删除未使用的标签
    def cleanup_unused_tags_sync(tags_to_check: List[Tag]):
        for tag in tags_to_check:
            # 检查标签是否还被其他图片使用
            link_statement = select(ImageTagLink).where(ImageTagLink.tag_id == tag.id)
            first_link = session.exec(link_statement).first()
            if not first_link:
                # 如果没有其他图片使用此标签，则删除标签
                session.delete(tag)

    await run_in_threadpool(cleanup_unused_tags_sync, all_tags_to_check)

    # 将所有数据库更改（图片删除、类别删除和标签清理）在单个原子事务中统一提交
    await run_in_threadpool(session.commit)

    return category_to_delete  # 返回删除前获取到的类别对象信息
