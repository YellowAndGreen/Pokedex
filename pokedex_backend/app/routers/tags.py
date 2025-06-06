#!/usr/bin/env python3

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.crud import tag_crud
from app.models import TagRead

router = APIRouter(prefix="/tags", tags=["标签管理"])

# 你可以在这里添加标签相关的API端点


@router.get("/", response_model=List[TagRead])
def get_all_tags(
    session: Session = Depends(get_session), skip: int = 0, limit: int = 100
):
    """
    获取所有标签的列表 (支持分页)。
    """
    tags = tag_crud.get_all_tags(session=session, skip=skip, limit=limit)
    return tags
