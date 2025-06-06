#!/usr/bin/env python3
"""标签CRUD操作模块

包含针对Tag模型的数据库增删改查函数。
"""

from typing import List, Optional
from sqlmodel import Session, select, func, col
import uuid
from sqlalchemy.orm import selectinload

from app.models import Tag, TagCreate, TagUpdate, ImageTagLink, Image
from fastapi import HTTPException, status


def create_tag(*, session: Session, tag_in: TagCreate) -> Tag:
    """
    在数据库中创建一个新的标签。

    参数:
        session (Session): 数据库会话对象。
        tag_in (TagCreate): 包含新标签数据的模型。

    返回:
        Tag: 创建成功后的标签对象。
    """
    # 检查标签名是否已存在 (忽略大小写)
    existing_tag = get_tag_by_name(session=session, name=tag_in.name)
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"标签 '{tag_in.name}' 已存在。",
        )

    db_tag = Tag.model_validate(tag_in)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag


def get_tag_by_id(*, session: Session, tag_id: uuid.UUID) -> Optional[Tag]:
    """
    根据ID从数据库中获取一个标签。

    参数:
        session (Session): 数据库会话对象。
        tag_id (uuid.UUID): 要获取的标签的ID。

    返回:
        Optional[Tag]: 如果找到则返回标签对象，否则返回None。
    """
    return session.get(Tag, tag_id)


def get_tag_by_name(*, session: Session, name: str) -> Optional[Tag]:
    """
    根据名称从数据库中获取一个标签 (忽略大小写)。

    参数:
        session (Session): 数据库会话对象。
        name (str): 要获取的标签的名称。

    返回:
        Optional[Tag]: 如果找到则返回标签对象，否则返回None。
    """
    statement = select(Tag).where(func.lower(Tag.name) == func.lower(name))
    return session.exec(statement).first()


def get_or_create_tag(*, session: Session, tag_name: str) -> Tag:
    """
    根据名称获取标签，如果不存在则创建新标签。
    此函数现在只将新标签添加到会话中，而不提交它。
    提交操作应由调用此函数的上层路由或服务处理。

    参数:
        session (Session): 数据库会话对象。
        tag_name (str): 标签的名称。

    返回:
        Tag: 获取或创建的标签对象。
    """
    db_tag = get_tag_by_name(session=session, name=tag_name)
    if not db_tag:
        tag_create = TagCreate(name=tag_name)
        db_tag = Tag.model_validate(tag_create)
        session.add(db_tag)
        # Flush the session to assign an ID to the new tag without committing the transaction
        session.flush()
        session.refresh(db_tag)
    return db_tag


def get_all_tags(*, session: Session, skip: int = 0, limit: int = 100) -> List[Tag]:
    """
    获取数据库中所有的标签记录 (支持分页)。
    使用 selectinload 优化，一次性加载所有标签的关联图片，避免N+1查询。
    虽然列表API当前不返回图片，但这是一个好的实践，以防未来需要。
    """
    statement = (
        select(Tag)
        .options(selectinload(Tag.images))  # 预加载图片
        .offset(skip)
        .limit(limit)
    )
    tags = session.exec(statement).all()
    return tags


def update_tag(*, session: Session, db_tag: Tag, tag_in: TagUpdate) -> Tag:
    """
    更新数据库中现有标签的名称。

    参数:
        session (Session): 数据库会话对象。
        db_tag (Tag): 从数据库获取的现有标签对象。
        tag_in (TagUpdate): 包含更新后标签数据的模型。

    返回:
        Tag: 更新成功后的标签对象。
    """
    update_data = tag_in.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] != db_tag.name:
        # 检查新名称是否与另一个现有标签冲突 (忽略大小写)
        existing_tag_with_new_name = get_tag_by_name(
            session=session, name=update_data["name"]
        )
        if existing_tag_with_new_name and existing_tag_with_new_name.id != db_tag.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"标签名称 '{update_data['name']}' 已被另一个标签使用。",
            )

    for key, value in update_data.items():
        setattr(db_tag, key, value)

    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag


def delete_tag(*, session: Session, tag_id: uuid.UUID) -> Optional[Tag]:
    """
    从数据库中删除一个标签。
    如果标签仍被任何图片使用，则禁止删除。

    参数:
        session (Session): 数据库会话对象。
        tag_id (uuid.UUID): 要删除的标签的ID。

    返回:
        Optional[Tag]: 如果删除成功则返回被删除的标签对象，否则返回None (如果未找到)。

    异常:
        HTTPException (409 Conflict): 如果标签仍在使用中。
    """
    db_tag = session.get(Tag, tag_id)
    if not db_tag:
        return None

    # 检查标签是否仍被图片使用
    link_statement = select(ImageTagLink).where(ImageTagLink.tag_id == tag_id)
    first_link = session.exec(link_statement).first()

    if first_link:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"标签 '{db_tag.name}' 仍被图片使用，无法删除。",
        )

    session.delete(db_tag)
    session.commit()
    return db_tag
