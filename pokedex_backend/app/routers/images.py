"""图片路由模块

提供图片上传、管理和元数据操作相关API端点
"""

from pathlib import Path
from fastapi import (
    APIRouter, 
    UploadFile, 
    File, 
    Form, 
    Depends, 
    HTTPException, 
    status,
    Response
)
from typing import Optional
from app.core.config import settings
from sqlmodel import Session
from app import models
from app.database import get_session
from app.services.file_storage_service import FileStorageService
from app.services.image_processing_service import ImageProcessor
from pathlib import Path
import aiofiles

router = APIRouter(
    tags=["images"],
    prefix="/api/images",
    responses={status.HTTP_404_NOT_FOUND: {"description": "资源未找到"}}
)

file_storage: FileStorageService = FileStorageService()

@router.post(
    "/upload/",
    response_model=models.ImageRead,
    status_code=status.HTTP_201_CREATED,
    summary="上传图片文件",
    responses={
        status.HTTP_201_CREATED: {"description": "图片上传成功"},
        status.HTTP_400_BAD_REQUEST: {"description": "无效的文件类型"},
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: {"description": "文件大小超过限制"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "文件处理错误"}
    }
)
async def upload_image(
    file: UploadFile = File(...),
    category_id: int = Form(...),
    description: str = Form(None),
    tags: str = Form(None),
    db: Session = Depends(get_session)
):
    # 验证文件类型和大小
    if file.content_type not in settings.allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，允许的类型：{', '.join(settings.allowed_mime_types)}"
        )

    # 保存原始文件
    file_path, stored_filename = await file_storage.save_upload_file(file.file, file.filename)
    
    # 生成缩略图
    thumbnail_path = await ImageProcessor.generate_thumbnail(file_path)
    
    # 创建数据库记录
    db_image = models.Image(
        original_filename=file.filename,
        stored_filename=stored_filename,
        relative_file_path=str(file_path.relative_to(settings.image_storage_root)),
        relative_thumbnail_path=str(thumbnail_path.relative_to(settings.thumbnail_storage_root)),
        mime_type=file.content_type,
        size_bytes=file_path.stat().st_size,
        description=description,
        tags=tags,
        category_id=category_id
    )
    
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

@router.put(
    "/{image_id}",
    response_model=models.ImageRead,
    summary="更新图片元数据",
    responses={
        status.HTTP_200_OK: {"description": "元数据更新成功"},
        status.HTTP_404_NOT_FOUND: {"description": "图片不存在"}
    }
)
async def update_image(
    image_id: int,
    image_data: models.ImageUpdate,
    db: Session = Depends(get_session)
):
    db_image = db.get(models.Image, image_id)
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    update_data = image_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_image, key, value)
    
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

@router.delete(
    "/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除图片记录和文件",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "删除成功"},
        status.HTTP_404_NOT_FOUND: {"description": "图片不存在"}
    }
)
async def delete_image(image_id: int, db: Session = Depends(get_session)):
    image = db.get(models.Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # 删除物理文件
    image_path = settings.image_storage_root / image.relative_file_path
    thumbnail_path = settings.thumbnail_storage_root / image.relative_thumbnail_path
    
    if image_path.exists():
        image_path.unlink()
    if thumbnail_path and thumbnail_path.exists():
        thumbnail_path.unlink()
    
    db.delete(image)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
