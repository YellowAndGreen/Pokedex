"""类别路由模块

提供类别相关的API端点，包括创建、读取、更新和删除操作
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from app import models
from app.database import get_session


router = APIRouter(tags=["categories"], prefix="/api/categories")

@router.post("/", response_model=models.CategoryRead)
async def create_category(category: models.CategoryCreate, db: Session = Depends(get_session)):
    db_category = models.Category(**category.dict())
    db.add(db_category)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Category already exists")
    db.refresh(db_category)
    return db_category

@router.get("/", response_model=list[models.CategoryRead])
async def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    return db.query(models.Category).offset(skip).limit(limit).all()

@router.get("/{category_id}", response_model=models.CategoryReadWithImages)
async def read_category(category_id: int, db: Session = Depends(get_session)):
    category = db.get(models.Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/{category_id}", response_model=models.CategoryRead)
async def update_category(
    category_id: int, category: models.CategoryCreate, db: Session = Depends(get_session)
):
    db_category = db.get(models.Category, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    for key, value in category.dict().items():
        setattr(db_category, key, value)
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_session)):
    category = db.get(models.Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(category)
    db.commit()
    return {"ok": True}
