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
    Query,
)
from sqlmodel import Session

from app.database import get_session
from app.models import (
    ImageCreate,
    ImageRead,
    ImageUpdate,
    Category,
    ExifData,
    Image,
    Tag,
)
from app.crud import image_crud, category_crud, tag_crud
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
    tags: Optional[str] = Form(None),  # 接收逗号分隔的字符串
    set_as_category_thumbnail: Optional[bool] = Form(
        False, description="是否将此图片设置为类别的缩略图"
    ),
    file_service: FileStorageService = Depends(),
) -> ImageRead:
    """
    上传新图片，并关联到类别和标签。
    - **file**: 必须是图片文件。
    - **title**: 图片标题。
    - **description**: 图片描述 (可选)。
    - **category_id**: 图片所属的类别ID。
    - **tags**: 逗号分隔的标签字符串 (例如 "风景,旅行") (可选)。
    """
    # 检查类别是否存在
    category = category_crud.get_category_by_id(
        session=session, category_id=category_id
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # 处理标签字符串，将其拆分为一个标签名称列表
    # 如果 tags 字符串非空，则按逗号分割并去除首尾空格
    tag_names = [name.strip() for name in tags.split(",")] if tags else []
    # 过滤掉空的标签名 (例如 "tag1,,tag2" 的情况)
    tag_names = [name for name in tag_names if name]

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
    exif_data_raw = {}
    parsed_exif_object: Optional[ExifData] = None
    try:
        with open(image_absolute_path, "rb") as f:
            tags_exif = exifread.process_file(
                f, details=False
            )  # details=False 避免提取过多信息
            if tags_exif:
                # 临时存储原始提取的、经过基本过滤的EXIF数据，用于 file_metadata
                exif_data_raw = {
                    str(key): str(value)
                    for key, value in tags_exif.items()
                    if key
                    not in (
                        "JPEGThumbnail",
                        "TIFFThumbnail",
                        "Filename",
                        "EXIF MakerNote",
                    )
                }

                # Helper function to safely get string value of a tag or None
                def get_tag_str_value(tag_key: str) -> Optional[str]:
                    tag_value = tags_exif.get(tag_key)
                    return str(tag_value) if tag_value is not None else None

                def get_alternative_tag_str_value(
                    key1: str, key2: str
                ) -> Optional[str]:
                    val = tags_exif.get(key1)
                    if val is not None:
                        return str(val)
                    val = tags_exif.get(key2)
                    return str(val) if val is not None else None

                # Structured EXIF data for exif_info field
                parsed_exif_object = ExifData(
                    make=get_tag_str_value("Image Make"),  # Camera Make
                    model=get_tag_str_value("Image Model"),  # Camera Model
                    lens_make=get_tag_str_value(
                        "Image LensMake"
                    ),  # Populate new lens_make field
                    bits_per_sample=get_alternative_tag_str_value(
                        "Image BitsPerSample", "EXIF BitsPerSample"
                    ),
                    date_time_original=get_tag_str_value("EXIF DateTimeOriginal"),
                    exposure_time=get_tag_str_value("EXIF ExposureTime"),
                    f_number=get_tag_str_value("EXIF FNumber"),
                    exposure_program=get_tag_str_value("EXIF ExposureProgram"),
                    iso_speed_rating=get_tag_str_value("EXIF ISOSpeedRatings"),
                    focal_length=get_tag_str_value("EXIF FocalLength"),
                    lens_specification=get_alternative_tag_str_value(
                        "EXIF LensSpecification", "Image LensSpecification"
                    ),
                    lens_model=get_alternative_tag_str_value(
                        "EXIF LensModel", "Image LensModel"
                    ),
                    exposure_mode=get_tag_str_value("EXIF ExposureMode"),
                    cfa_pattern=get_tag_str_value(
                        "EXIF CFAPattern"
                    ),  # Consider adding "EXIF CVAPattern" if needed
                    color_space=get_tag_str_value("EXIF ColorSpace"),
                    white_balance=get_tag_str_value("EXIF WhiteBalance"),
                )
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
        # tags=tag_names,  # Tags are now handled by create_image_with_tags
        category_id=category_id,
        file_metadata=(
            exif_data_raw if exif_data_raw else None
        ),  # 将原始提取的EXIF存入 file_metadata
        exif_info=parsed_exif_object,  # 将结构化的 ExifData 实例存入 exif_info
    )

    # 调用重构后的CRUD函数，分别传入 image 模型和 tag 名称列表
    db_image = image_crud.create_image_with_tags(
        db=session, image_create=image_create_data, tag_names=tag_names
    )

    # 6. 如果需要，设置类别缩略图
    if set_as_category_thumbnail and db_image.relative_thumbnail_path and category:
        category.thumbnail_path = db_image.relative_thumbnail_path
        session.add(category)
        session.commit()
        session.refresh(category)
        # session.refresh(db_image) # db_image 本身没有改变，但如果需要最新的 category 信息可以考虑

    return db_image


@router.get("/by-tags/", response_model=List[ImageRead], summary="根据标签名称搜索图片")
def search_images_by_tags(
    *,
    session: Session = Depends(get_session),
    tag_names: List[str] = Query(
        ...,
        description="要搜索的标签名称列表 (例如: tag_names=夏天&tag_names=风景)",
        alias="tag",
    ),
    match_all: bool = Query(False, description="是否要求匹配所有提供的标签 (AND逻辑)"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(
        100, ge=1, le=200, description="返回的最大记录数"
    ),  # Max 200 to prevent overload
) -> List[ImageRead]:
    """
    根据一个或多个标签的名称搜索图片。

    - **tag_names**: 一个或多个标签名称。
    - **match_all**: 如果为 `true`，则只返回包含所有指定标签的图片 (AND查询)。
                     如果为 `false` (默认)，则返回包含任何一个指定标签的图片 (OR查询)。
    """
    if not tag_names:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="至少需要提供一个标签名称进行搜索。",
        )
    images = image_crud.get_images_by_tag_names(
        session=session,
        tag_names=tag_names,
        match_all=match_all,
        skip=skip,
        limit=limit,
    )
    return images


@router.get("/{image_id}/", response_model=ImageRead)
def read_image(
    *,
    session: Session = Depends(get_session),
    image_id: uuid.UUID,
):
    """
    根据ID获取指定图片的元数据。
    """
    db_image = image_crud.get_image_by_id(session=session, image_id=image_id)
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")
    return db_image


@router.put("/{image_id}/", response_model=ImageRead)
def update_image_metadata(
    *,
    session: Session = Depends(get_session),
    image_id: uuid.UUID,
    image_in: ImageUpdate,
):
    """
    更新指定图片的元数据，如描述、标签或所属类别。
    可以附带指定是否将此图片设置为其所属类别的缩略图。
    """
    db_image = image_crud.get_image_by_id(session=session, image_id=image_id)
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")

    # 处理标签更新
    new_tags = []
    if image_in.tags is not None and image_in.tags.strip():
        tag_names = [name.strip() for name in image_in.tags.split(",") if name.strip()]
        for tag_name in tag_names:
            tag = tag_crud.get_or_create_tag(session=session, tag_name=tag_name)
            new_tags.append(tag)

    # 更新图片元数据
    updated_image = image_crud.update_image_metadata(
        session=session,
        image=db_image,
        image_in=image_in,
        new_tags=new_tags
    )
    return updated_image


@router.delete(
    "/{image_id}/", status_code=status.HTTP_204_NO_CONTENT, summary="删除图片"
)
async def delete_image(*, session: Session = Depends(get_session), image_id: uuid.UUID):
    """
    从数据库中删除一张图片及其相关文件。
    如果图片不存在，则不执行任何操作并返回204。
    """
    deleted_image = await image_crud.delete_image(session=session, image_id=image_id)
    if not deleted_image:
        # The image might have already been deleted, or never existed.
        # Returning 204 is appropriate in either case as the client's desired state
        # (the image being gone) is met.
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/", response_model=List[ImageRead])
def get_all_images(
    session: Session = Depends(get_session), skip: int = 0, limit: int = 100
):
    """
    获取所有图片的列表 (支持分页)。
    """
    images = image_crud.get_all_images(session=session, skip=skip, limit=limit)
    return images


@router.get("/{image_id}", response_model=ImageRead)
def get_image_by_id(image_id: uuid.UUID, session: Session = Depends(get_session)):
    """
    根据ID获取单个图片对象的详细信息。
    """
    db_image = image_crud.get_image_by_id(session=session, image_id=image_id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return db_image
