"""类别CRUD操作模块

包含针对Category模型的数据库增删改查函数。
"""

from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload  # 用于预加载关联的图片数据，避免N+1查询问题
import uuid # 确保导入uuid

from app.models import Category, CategoryCreate, CategoryReadWithImages, Image


def create_category(*, session: Session, category_create: CategoryCreate) -> Category:
    """
    在数据库中创建一个新的类别。

    参数:
        session (Session):数据库会话对象。
        category_create (CategoryCreate):包含类别数据的模型。

    返回:
        Category:创建成功后的类别对象。
    """
    db_category = Category.from_orm(category_create)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


def get_category_by_id(*, session: Session, category_id: uuid.UUID) -> Optional[Category]:
    """
    根据ID从数据库中获取一个类别。

    参数:
        session (Session):数据库会话对象。
        category_id (uuid.UUID):要获取的类别的ID。

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
    *, session: Session, category_id: uuid.UUID
) -> Optional[CategoryReadWithImages]:
    """
    根据ID获取类别及其关联的所有图片。

    参数:
        session (Session): 数据库会话对象。
        category_id (uuid.UUID): 类别的ID。

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

    return CategoryReadWithImages.from_orm(category_db)


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


def delete_category(*, session: Session, category_id: uuid.UUID) -> Optional[Category]:
    """
    从数据库中删除一个类别。
    注意：此函数仅删除类别记录本身。
    在实际应用中，需要明确处理关联图片的策略（例如级联删除或置空外键）。

    参数:
        session (Session):数据库会话对象。
        category_id (uuid.UUID):要删除的类别的ID。

    返回:
        Optional[Category]: 如果删除成功则返回被删除的类别对象，否则返回None (如果未找到)。
    """
    category_to_delete = session.get(Category, category_id)
    if not category_to_delete:
        return None

    # 此处未处理关联图片：
    # 根据外键约束（例如 ON DELETE CASCADE 或 RESTRICT），直接删除类别可能失败或产生副作用。
    # 推荐做法是明确处理关联实体，例如先删除或重新分配该类别下的所有图片。
    # 示例：
    # images_in_category = session.exec(select(Image).where(Image.category_id == category_id)).all()
    # for img in images_in_category:
    #     session.delete(img) # 或更新 img.category_id = new_category_id
    # session.commit() # 如有图片更改，则提交

    session.delete(category_to_delete)
    session.commit()
    return category_to_delete
