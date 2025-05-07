"""图片API路由模块

提供与图片资源相关的HTTP接口，包括图片上传、元数据管理和删除。
"""

from typing import List, Optional
from pathlib import Path
import asyncio

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
    Response,
)
from sqlmodel import Session

from app.database import get_session
from app.models import ImageCreate, ImageRead, ImageUpdate, Category
from app.crud import image_crud, category_crud
from app.services.file_storage_service import FileStorageService  # 假设服务已实现
from app.services.image_processing_service import (
    ImageProcessingService,
)  # 假设服务已实现
from app.core.config import settings

router = APIRouter(
    prefix="/api/images",
    tags=["图片管理"],
    responses={404: {"description": "未找到"}},
)

# 服务实例化 (后续可考虑通过依赖注入)
file_storage = FileStorageService()
image_processor = ImageProcessingService()


@router.post(
    "/upload/",
    response_model=ImageRead,
    status_code=status.HTTP_201_CREATED,
    summary="上传新图片",
)
async def upload_image(
    *,
    session: Session = Depends(get_session),
    file: UploadFile = File(..., description="要上传的图片文件"),
    category_id: int = Form(..., description="图片所属的类别ID"),
    description: Optional[str] = Form(None, description="图片的可选描述"),
    tags: Optional[str] = Form(None, description="图片的标签，逗号分隔"),
) -> ImageRead:
    """
    上传一张新的图片到指定的类别。

    - **file**: 图片文件本身。
    - **category_id**: 图片将归属的类别ID，必须有效。
    - **description**: 对图片的可选文字描述。
    - **tags**: 以逗号分隔的字符串，用于标记图片。
    """
    # 1. 校验类别ID是否存在
    db_category = category_crud.get_category_by_id(
        session=session, category_id=category_id
    )
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"类别ID {category_id} 不存在",
        )

    # 2. 保存原始文件 (FileStorageService 应处理文件名唯一化和分级目录)
    try:
        # filename type ignore due to UploadFile.filename potentially being None, though FastAPI usually ensures it for File(...)
        image_absolute_path, stored_filename = await file_storage.save_upload_file(
            upload_file=file, filename=file.filename  # type: ignore
        )
    except HTTPException as e:  # Catch specific HTTPExceptions from service
        raise e
    except Exception as e:
        print(f"文件保存服务发生意外错误: {e}")  # 日志记录
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存过程中发生意外错误。",
        )

    # 3. 获取相对子目录以生成缩略图
    try:
        relative_sub_dir = await file_storage.get_relative_sub_directory_for_file(
            stored_filename
        )
    except Exception as e:
        print(f"获取文件相对子目录失败: {e}")  # 日志记录
        # 清理已保存的原图，因为没有子目录信息无法继续生成缩略图或记录正确路径
        await file_storage.delete_file(image_absolute_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="处理文件路径信息时出错。",
        )

    # 4. 生成缩略图
    thumbnail_absolute_path: Optional[Path] = None
    try:
        thumbnail_absolute_path = await image_processor.generate_thumbnail(
            source_image_path=image_absolute_path,
            relative_sub_dir=relative_sub_dir,
            stored_filename=stored_filename,
        )
    except HTTPException as e:  # Catch specific HTTPExceptions from service
        # 如果缩略图生成失败，是否删除原图是一个策略问题
        # 此处不删除原图，但记录一个错误，图片将没有缩略图
        print(
            f"警告: 缩略图生成失败 ({e.detail}) 对于文件 {stored_filename}. 图片仍会保存但无缩略图。"
        )
        # 可以选择不抛出异常，允许图片无缩略图，或者按原样抛出
        # raise e # 如果要求必须有缩略图，则重新抛出
    except Exception as e:
        print(f"缩略图服务发生意外错误: {e}")  # 日志记录
        # 同上，策略问题
        print(
            f"警告: 缩略图生成发生意外错误对于文件 {stored_filename}. 图片仍会保存但无缩略图。"
        )

    # 5. 创建数据库记录
    image_create_data = ImageCreate(
        original_filename=file.filename,  # type: ignore
        stored_filename=stored_filename,
        relative_file_path=str(
            image_absolute_path.relative_to(settings.image_storage_root)
        ),
        relative_thumbnail_path=(
            str(thumbnail_absolute_path.relative_to(settings.thumbnail_storage_root))
            if thumbnail_absolute_path and settings.thumbnail_storage_root
            else None
        ),
        mime_type=file.content_type,  # type: ignore
        size_bytes=(
            await asyncio.os.stat(image_absolute_path)
        ).st_size,  # 异步获取文件大小
        description=description,
        tags=tags,
        category_id=category_id,
    )

    db_image = image_crud.create_image(
        session=session, image_create_data=image_create_data
    )
    return db_image


@router.get("/{image_id}/", response_model=ImageRead, summary="获取图片元数据")
def read_image(*, session: Session = Depends(get_session), image_id: int) -> ImageRead:
    """
    根据ID获取指定图片的元数据。
    """
    db_image = image_crud.get_image_by_id(session=session, image_id=image_id)
    if not db_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片未找到")
    return db_image  # type: ignore


@router.put("/{image_id}/", response_model=ImageRead, summary="更新图片元数据")
def update_image_metadata(
    *, session: Session = Depends(get_session), image_id: int, image_in: ImageUpdate
) -> ImageRead:
    """
    更新指定图片的元数据，如描述、标签或所属类别。
    """
    db_image = image_crud.get_image_by_id(session=session, image_id=image_id)
    if not db_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片未找到")

    if image_in.category_id is not None:
        db_category = category_crud.get_category_by_id(
            session=session, category_id=image_in.category_id
        )
        if not db_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"目标类别ID {image_in.category_id} 不存在",
            )

    updated_image = image_crud.update_image_metadata(
        session=session, db_image=db_image, image_in=image_in
    )
    return updated_image  # type: ignore


@router.delete(
    "/{image_id}/", status_code=status.HTTP_204_NO_CONTENT, summary="删除图片"
)
async def delete_image(*, session: Session = Depends(get_session), image_id: int):
    """
    删除指定的图片，包括其元数据和存储的物理文件（原图和缩略图）。
    """
    db_image = image_crud.get_image_by_id(session=session, image_id=image_id)
    if not db_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片未找到")

    # 1. 删除物理文件 (原图和缩略图)
    # 路径应从数据库记录中获取，并构造成服务可用的形式
    paths_to_delete_tasks = []
    if db_image.relative_file_path:
        original_image_abs_path = (
            settings.image_storage_root / db_image.relative_file_path
        )
        paths_to_delete_tasks.append(file_storage.delete_file(original_image_abs_path))

    if db_image.relative_thumbnail_path:
        thumbnail_abs_path = (
            settings.thumbnail_storage_root / db_image.relative_thumbnail_path
        )
        paths_to_delete_tasks.append(file_storage.delete_file(thumbnail_abs_path))

    delete_results = await asyncio.gather(
        *paths_to_delete_tasks, return_exceptions=True
    )
    for result in delete_results:
        if isinstance(result, Exception):
            print(f"删除物理文件时发生错误: {result}")  # 日志记录
        # elif not result: # 如果delete_file返回False表示失败
        # print(f"尝试删除某个文件失败或文件不存在") # 日志记录

    # 2. 删除数据库记录
    image_crud.delete_image(session=session, image_id=image_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
