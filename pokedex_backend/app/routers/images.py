"""图片API路由模块

提供与图片资源相关的HTTP接口，包括图片上传、元数据管理和删除。
"""

from typing import List, Optional
from pathlib import Path
import asyncio
import aiofiles.os as aio_os
import uuid
import exifread

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
    prefix="/images",
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
    category_id: uuid.UUID = Form(..., description="图片所属的类别ID"),
    title: Optional[str] = Form(None, description="图片的可选标题"),
    description: Optional[str] = Form(None, description="图片的可选描述"),
    tags: Optional[str] = Form(None, description="图片的标签，逗号分隔"),
    set_as_category_thumbnail: Optional[bool] = Form(
        False, description="是否将此图片设置为类别的缩略图"
    ),
) -> ImageRead:
    """
    上传一张新的图片到指定的类别。

    - **file**: 图片文件本身。
    - **category_id**: 图片将归属的类别ID，必须有效。
    - **title**: 图片的可选标题。
    - **description**: 对图片的可选文字描述。
    - **tags**: 以逗号分隔的字符串，用于标记图片。
    - **set_as_category_thumbnail**: 是否将此图片设置为类别的缩略图。
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
    except HTTPException as e:
        print(
            f"警告: 缩略图生成失败 ({e.detail}) 对于文件 {stored_filename}. 图片仍会保存但无缩略图。"
        )
    except Exception as e:
        print(f"缩略图服务发生意外错误: {e}")
        print(
            f"警告: 缩略图生成发生意外错误对于文件 {stored_filename}. 图片仍会保存但无缩略图。"
        )

    # 新增：提取 EXIF 信息
    exif_data = {}
    try:
        with open(image_absolute_path, "rb") as f:
            tags_exif = exifread.process_file(
                f, details=False
            )  # details=False 避免提取过多信息
            if tags_exif:
                exif_data = {
                    str(key): str(value)
                    for key, value in tags_exif.items()
                    if key
                    not in (
                        "JPEGThumbnail",
                        "TIFFThumbnail",
                        "Filename",
                        "EXIF MakerNote",
                    )  # 排除一些不需要或可能很大的字段
                }
    except Exception as e:
        print(f"提取 EXIF 信息时发生错误: {e}")  # 记录错误，但不中断流程

    # 5. 创建数据库记录 for Image
    # 构建 image_create_data 时，使用 thumbnail_absolute_path 计算 relative_thumbnail_path
    calculated_relative_thumbnail_path = (
        str(thumbnail_absolute_path.relative_to(settings.thumbnail_storage_root))
        if thumbnail_absolute_path
        and settings.thumbnail_storage_root
        and thumbnail_absolute_path.exists()
        else None
    )
    print(
        f"thumbnail_absolute_path: {thumbnail_absolute_path}, settings.thumbnail_storage_root: {settings.thumbnail_storage_root}, thumbnail_absolute_path.exists(): {thumbnail_absolute_path.exists()}, calculated_relative_thumbnail_path: {calculated_relative_thumbnail_path}"
    )
    image_create_data = ImageCreate(
        title=title,
        original_filename=file.filename,  # type: ignore
        stored_filename=stored_filename,
        relative_file_path=str(
            image_absolute_path.relative_to(settings.image_storage_root)
        ),
        relative_thumbnail_path=calculated_relative_thumbnail_path,  # 使用计算好的值
        mime_type=file.content_type,  # type: ignore
        size_bytes=(await aio_os.stat(image_absolute_path)).st_size,
        description=description,
        tags=tags,
        category_id=category_id,
    )
    # 将EXIF数据添加到image_create_data的file_metadata中
    if exif_data:
        image_create_data.file_metadata = (
            exif_data  # 这里假设ImageCreate模型中已经有file_metadata字段
        )

    db_image = image_crud.create_image(
        session=session, image_create_data=image_create_data
    )

    # 6. 如果需要，设置类别缩略图
    print(
        f"set_as_category_thumbnail: {set_as_category_thumbnail}, db_image.relative_thumbnail_path: {db_image.relative_thumbnail_path}, db_category: {db_category}"
    )
    if set_as_category_thumbnail and db_image.relative_thumbnail_path and db_category:
        db_category.thumbnail_path = db_image.relative_thumbnail_path
        session.add(db_category)
        session.commit()
        session.refresh(db_category)
        # session.refresh(db_image) # db_image 本身没有改变，但如果需要最新的 category 信息可以考虑

    return db_image


@router.get("/{image_id}/", response_model=ImageRead, summary="获取图片元数据")
def read_image(
    *, session: Session = Depends(get_session), image_id: uuid.UUID
) -> ImageRead:
    """
    根据ID获取指定图片的元数据。
    """
    db_image = image_crud.get_image_by_id(session=session, image_id=image_id)
    if not db_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片未找到")
    return db_image  # type: ignore


@router.put("/{image_id}/", response_model=ImageRead, summary="更新图片元数据")
def update_image_metadata(
    *,
    session: Session = Depends(get_session),
    image_id: uuid.UUID,
    image_in: ImageUpdate,
) -> ImageRead:
    """
    更新指定图片的元数据，如描述、标签或所属类别。
    可以附带指定是否将此图片设置为其所属类别的缩略图。
    """
    db_image = image_crud.get_image_by_id(session=session, image_id=image_id)
    if not db_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片未找到")

    original_category_id = db_image.category_id
    original_thumbnail_path_of_this_image = (
        db_image.relative_thumbnail_path
    )  # 图片自身的缩略图路径

    # 1. 处理类别更改的校验 (如果提供了 new_category_id)
    new_category_id_from_input = image_in.category_id
    if (
        new_category_id_from_input is not None
        and new_category_id_from_input != original_category_id
    ):
        db_new_target_category = category_crud.get_category_by_id(
            session=session, category_id=new_category_id_from_input
        )
        if not db_new_target_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"目标类别ID {new_category_id_from_input} 不存在",
            )

    # 2. 更新图片本身的元数据 (包括可能的 category_id 更改)
    updated_image = image_crud.update_image_metadata(
        session=session, db_image=db_image, image_in=image_in
    )
    # `updated_image` 现在包含了最新的数据，包括它的 category_id 和 relative_thumbnail_path

    categories_to_commit = []  # 修改: 从 set 改为 list

    # 3. 清理旧类别的缩略图 (如果图片被移动，且它曾是旧类别的缩略图)
    if (
        new_category_id_from_input is not None
        and new_category_id_from_input != original_category_id
    ):
        original_category = category_crud.get_category_by_id(
            session=session, category_id=original_category_id
        )
        if (
            original_category
            and original_category.thumbnail_path
            == original_thumbnail_path_of_this_image
        ):
            original_category.thumbnail_path = None
            session.add(original_category)
            if original_category not in categories_to_commit:  # 修改: 条件添加
                categories_to_commit.append(original_category)

    # 4. 处理目标/当前类别的缩略图设置
    target_category_for_thumbnail_logic = category_crud.get_category_by_id(
        session=session,
        category_id=updated_image.category_id,  # 使用 updated_image 的 category_id
    )

    if target_category_for_thumbnail_logic:
        if image_in.set_as_category_thumbnail is True:
            if updated_image.relative_thumbnail_path:
                if (
                    target_category_for_thumbnail_logic.thumbnail_path
                    != updated_image.relative_thumbnail_path
                ):
                    target_category_for_thumbnail_logic.thumbnail_path = (
                        updated_image.relative_thumbnail_path
                    )
                    session.add(target_category_for_thumbnail_logic)
                    if (
                        target_category_for_thumbnail_logic not in categories_to_commit
                    ):  # 修改: 条件添加
                        categories_to_commit.append(target_category_for_thumbnail_logic)
            else:
                # 图片本身没有缩略图，不能设为类别缩略图，可以考虑警告或忽略
                print(
                    f"警告: 图片 {updated_image.id} 没有缩略图，无法将其设置为类别 {target_category_for_thumbnail_logic.id} 的缩略图。"
                )

        elif image_in.set_as_category_thumbnail is False:
            # 如果指令是取消设为缩略图，并且当前类别的缩略图确实是这张图片
            if (
                target_category_for_thumbnail_logic.thumbnail_path
                == updated_image.relative_thumbnail_path
            ):
                target_category_for_thumbnail_logic.thumbnail_path = None
                session.add(target_category_for_thumbnail_logic)
                if (
                    target_category_for_thumbnail_logic not in categories_to_commit
                ):  # 修改: 条件添加
                    categories_to_commit.append(target_category_for_thumbnail_logic)
        # 如果 image_in.set_as_category_thumbnail is None (未提供)，则不主动修改目标类别的缩略图，
        # 除非因图片移动导致旧类别缩略图被清理（已在步骤3处理）。

    # 5. 统一提交并刷新
    if categories_to_commit:
        session.commit()
        for cat in categories_to_commit:
            session.refresh(cat)

    session.refresh(updated_image)  # 确保返回的图片对象是最新的
    return updated_image


@router.delete(
    "/{image_id}/", status_code=status.HTTP_204_NO_CONTENT, summary="删除图片"
)
async def delete_image(*, session: Session = Depends(get_session), image_id: uuid.UUID):
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
    await image_crud.delete_image(session=session, image_id=image_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
