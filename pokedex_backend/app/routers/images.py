"""图片API路由模块

提供与图片资源相关的HTTP接口，包括图片上传、元数据管理和删除。
"""

from typing import List, Optional
from pathlib import Path

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

    # 2. 校验文件类型和大小
    if file.content_type not in settings.allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {file.content_type}. 允许的类型: {', '.join(settings.allowed_mime_types)}",
        )

    # 异步读取文件内容以检查大小 (更准确的方式是直接使用 UploadFile.size 属性，如果可用且可靠)
    # content = await file.read()
    # await file.seek(0) # 重置文件指针，以便后续服务可以读取
    # if len(content) > settings.max_image_size:
    #     raise HTTPException(
    #         status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    #         detail=f"文件大小超过限制 ({settings.max_image_size // 1024 // 1024}MB)"
    #     )
    # 注意: FastAPI的UploadFile在读取后可能不会自动重置指针，服务层需注意。
    # 更推荐的方式是在FileStorageService内部处理文件读取和大小检查。

    # 3. 保存原始文件 (FileStorageService 应处理文件名唯一化和分级目录)
    try:
        (
            original_file_path,
            stored_filename,
            thumbnail_dir_path,
        ) = await file_storage.save_upload_file(
            upload_file=file, filename=file.filename  # type: ignore
        )
    except Exception as e:
        # log e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {e}",
        )

    # 4. 生成缩略图
    try:
        thumbnail_file_path = await image_processor.generate_thumbnail(
            source_image_path=original_file_path,
            # thumbnail_dir_path=thumbnail_dir_path, # 假设服务内部处理
            # stored_filename=stored_filename # 假设服务内部处理
        )
    except Exception as e:
        # log e
        # 如果缩略图生成失败，考虑是否回滚原图保存，或允许无缩略图
        # 此处简单起见，抛出错误。实际项目中可能需要更复杂的错误处理策略。
        # 也可以尝试删除已保存的原图
        # await file_storage.delete_file(original_file_path.name) # 注意这里的参数应该是相对路径或可定位的标识
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"缩略图生成失败: {e}",
        )

    # 5. 创建数据库记录
    image_create_data = ImageCreate(
        original_filename=file.filename,  # type: ignore
        stored_filename=stored_filename,
        relative_file_path=str(
            original_file_path.relative_to(settings.image_storage_root)
        ),
        relative_thumbnail_path=(
            str(thumbnail_file_path.relative_to(settings.thumbnail_storage_root))
            if thumbnail_file_path
            else None
        ),
        mime_type=file.content_type,  # type: ignore
        size_bytes=original_file_path.stat().st_size,  # 获取已保存文件的大小
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
    paths_to_delete = []
    if db_image.relative_file_path:
        paths_to_delete.append(
            settings.image_storage_root / db_image.relative_file_path
        )
    if db_image.relative_thumbnail_path:
        paths_to_delete.append(
            settings.thumbnail_storage_root / db_image.relative_thumbnail_path
        )

    for file_path_to_delete in paths_to_delete:
        try:
            if await file_storage.delete_file(file_path_to_delete):
                print(f"已删除物理文件: {file_path_to_delete}")  # 记录日志
            else:
                print(
                    f"尝试删除文件失败或文件不存在: {file_path_to_delete}"
                )  # 记录日志
        except Exception as e:
            # 记录文件删除失败的日志，但继续尝试删除数据库记录
            print(f"删除物理文件 {file_path_to_delete} 时发生错误: {e}")

    # 2. 删除数据库记录
    image_crud.delete_image(session=session, image_id=image_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
