#!/usr/bin/env python3
import pytest
import requests  # 新增导入
import uuid  # 新增导入
from fastapi import status

# from httpx import AsyncClient # 不再需要，因为我们使用 requests
from pathlib import Path
import shutil
import time  # 用于可能的重试或延迟

# 假设项目根目录下有 tests/assets/test_image.png
# 如果没有，请创建一个小的PNG文件用于测试
TEST_IMAGE_PATH = Path(__file__).parent.parent.parent / "assets" / "test_image.png"
TEST_IMAGE_NAME = "test_image.png"
BASE_URL = "http://localhost:8000/api"  # 新增基础URL


# 辅助函数，用于生成唯一的分类名称
def generate_unique_category_name(base_name: str = "Test Category") -> str:
    """生成一个唯一的分类名称，用于测试。"""
    return f"{base_name} {uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="module", autouse=True)
def setup_test_image():
    """
    在测试模块开始前确保测试图片存在。
    如果 assets 目录或测试图片不存在，则尝试创建它们。
    """
    assets_dir = Path(__file__).parent.parent.parent / "assets"
    if not assets_dir.exists():
        assets_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {assets_dir}")

    if not TEST_IMAGE_PATH.exists():
        try:
            from PIL import Image

            img = Image.new("RGB", (1, 1), color="white")
            img.save(TEST_IMAGE_PATH, "PNG")
            print(f"Created dummy test image: {TEST_IMAGE_PATH}")
        except ImportError:
            print(
                f"Pillow library not found. Cannot create dummy image. "
                f"Please manually create a small PNG file at: {TEST_IMAGE_PATH}"
            )
            TEST_IMAGE_PATH.touch()
            print(
                f"Created empty placeholder file (tests might fail): {TEST_IMAGE_PATH}"
            )


@pytest.fixture
def temp_image_file(tmp_path: Path):
    """
    提供一个临时的图片文件用于上传测试。

    参数:
        tmp_path (Path): Pytest 提供的临时路径 fixture。

    返回:
        Path: 指向临时复制的测试图片文件的路径。
    """
    if not TEST_IMAGE_PATH.exists() or TEST_IMAGE_PATH.stat().st_size == 0:
        pytest.skip(
            f"Test image {TEST_IMAGE_PATH} not found or is empty. Skipping image upload tests."
        )

    temp_file = tmp_path / TEST_IMAGE_NAME
    shutil.copy(TEST_IMAGE_PATH, temp_file)
    return temp_file


@pytest.fixture
def created_category_id():
    """
    创建一个类别并返回其ID，用于图片API测试。
    测试结束后会尝试删除该类别。

    返回:
        str: 创建的类别的ID。
    """
    category_name = generate_unique_category_name("Image Test Category")
    payload = {
        "name": category_name,
        "description": "Category for image API tests",
    }
    created_id = None
    try:
        response = requests.post(f"{BASE_URL}/categories/", json=payload)
        response.raise_for_status()  # 如果发生错误则抛出异常
        assert response.status_code == status.HTTP_201_CREATED
        created_id = response.json()["id"]
        yield created_id
    finally:
        if created_id:
            delete_response = requests.delete(f"{BASE_URL}/categories/{created_id}/")
            if delete_response.status_code not in [
                status.HTTP_204_NO_CONTENT,
                status.HTTP_404_NOT_FOUND,
            ]:
                print(
                    f"Warning: Failed to cleanup category {created_id}. Status: {delete_response.status_code}"
                )


def test_upload_image(created_category_id: str, temp_image_file: Path):
    """
    测试上传新图片，并验证响应中包含有效的相对文件路径和缩略图路径。

    参数:
        created_category_id (str): 已创建类别的ID。
        temp_image_file (Path): 临时图片文件的路径。
    """
    image_id_to_delete = None
    try:
        with open(temp_image_file, "rb") as f:
            files = {"file": (temp_image_file.name, f, "image/png")}
            data = {
                "category_id": created_category_id,
                "title": "Test Upload Image Paths",
                "description": "Testing relative paths in upload response",
                "tags": "test, upload, paths",
                "set_as_category_thumbnail": "false",
            }
            response = requests.post(
                f"{BASE_URL}/images/upload/", files=files, data=data
            )

        assert response.status_code == status.HTTP_201_CREATED
        image_data = response.json()
        image_id_to_delete = image_data.get("id")

        assert image_data["title"] == "Test Upload Image Paths"
        assert image_data["category_id"] == created_category_id
        assert "id" in image_data

        # 验证 relative_file_path
        relative_file_path = image_data.get("relative_file_path")
        assert (
            relative_file_path is not None
        ), "relative_file_path should exist in response"
        assert (
            isinstance(relative_file_path, str) and relative_file_path.strip() != ""
        ), "relative_file_path should be a non-empty string"
        # 假设文件名中包含原始文件名或其变体，并以 .png 结尾
        # 实际存储的文件名可能经过唯一化处理，但至少扩展名应该保留
        assert relative_file_path.endswith(
            Path(temp_image_file.name).suffix
        ), f"relative_file_path '{relative_file_path}' should end with '{Path(temp_image_file.name).suffix}'"
        assert (
            len(relative_file_path.split("/")) >= 1
        )  # 至少有一个文件名，可能是多级目录

        # 验证 relative_thumbnail_path
        relative_thumbnail_path = image_data.get("relative_thumbnail_path")
        assert (
            relative_thumbnail_path is not None
        ), "relative_thumbnail_path should exist in response"
        assert (
            isinstance(relative_thumbnail_path, str)
            and relative_thumbnail_path.strip() != ""
        ), "relative_thumbnail_path should be a non-empty string"
        assert relative_thumbnail_path.endswith(
            f"_thumb{Path(temp_image_file.name).suffix}"
        ), f"relative_thumbnail_path '{relative_thumbnail_path}' should end with '_thumb{Path(temp_image_file.name).suffix}'"
        assert (
            len(relative_thumbnail_path.split("/")) >= 1
        )  # 至少有一个文件名，可能是多级目录

        # 原有的 image_url 和 thumbnail_url 检查 (如果它们仍然在响应中)
        # 这些可能是基于相对路径和配置中的基础URL构建的完整URL
        if "image_url" in image_data:
            assert image_data["image_url"].endswith(
                relative_file_path
            ), "image_url should correspond to relative_file_path"
        if "thumbnail_url" in image_data:
            assert image_data["thumbnail_url"].endswith(
                relative_thumbnail_path
            ), "thumbnail_url should correspond to relative_thumbnail_path"

    finally:
        if image_id_to_delete:
            requests.delete(f"{BASE_URL}/images/{image_id_to_delete}/")


def test_upload_image_missing_category(temp_image_file: Path):
    """
    测试上传图片到不存在的类别。

    参数:
        temp_image_file (Path): 临时图片文件的路径。
    """
    with open(temp_image_file, "rb") as f:
        files = {"file": (temp_image_file.name, f, "image/png")}
        non_existent_uuid = str(uuid.uuid4())  # 生成一个有效的但不存在的UUID
        data = {"category_id": non_existent_uuid, "title": "Test Fail Image"}
        response = requests.post(f"{BASE_URL}/images/upload/", files=files, data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_image_metadata(created_category_id: str, temp_image_file: Path):
    """
    测试获取图片元数据。

    参数:
        created_category_id (str): 已创建类别的ID。
        temp_image_file (Path): 临时图片文件的路径。
    """
    image_id = None
    try:
        # 先上传一张图片
        with open(temp_image_file, "rb") as f:
            files = {"file": (temp_image_file.name, f, "image/png")}
            data = {
                "category_id": created_category_id,
                "title": "Image For Get Test (Requests)",
            }
            upload_response = requests.post(
                f"{BASE_URL}/images/upload/", files=files, data=data
            )
        assert upload_response.status_code == status.HTTP_201_CREATED
        image_id = upload_response.json()["id"]

        # 获取该图片的元数据
        response = requests.get(f"{BASE_URL}/images/{image_id}/")
        assert response.status_code == status.HTTP_200_OK
        image_data = response.json()
        assert image_data["id"] == image_id
        assert image_data["title"] == "Image For Get Test (Requests)"
        assert image_data["category_id"] == created_category_id
    finally:
        if image_id:
            requests.delete(f"{BASE_URL}/images/{image_id}/")  # 清理


def test_get_image_not_found():
    """测试获取不存在的图片。"""
    non_existent_uuid = str(uuid.uuid4())
    response = requests.get(f"{BASE_URL}/images/{non_existent_uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_image_metadata(created_category_id: str, temp_image_file: Path):
    """
    测试更新图片元数据，并验证类别缩略图的设置和取消设置。

    参数:
        created_category_id (str): 已创建类别的ID。
        temp_image_file (Path): 临时图片文件的路径。
    """
    image_id = None
    image_thumbnail_relative_path = None
    try:
        # 先上传一张图片
        with open(temp_image_file, "rb") as f:
            files = {"file": (temp_image_file.name, f, "image/png")}
            initial_data = {
                "category_id": created_category_id,
                "title": "Initial Title (Requests)",
                "description": "Desc1 (Requests)",
                "set_as_category_thumbnail": "false",  # 初始不设为缩略图
            }
            upload_response = requests.post(
                f"{BASE_URL}/images/upload/", files=files, data=initial_data
            )
        assert upload_response.status_code == status.HTTP_201_CREATED
        uploaded_image_data = upload_response.json()
        image_id = uploaded_image_data["id"]
        image_thumbnail_relative_path = uploaded_image_data.get(
            "relative_thumbnail_path"
        )
        assert (
            image_thumbnail_relative_path
        ), "Uploaded image must have a relative_thumbnail_path"

        # 验证初始时类别缩略图未设置 (或不是此图片)
        category_response = requests.get(
            f"{BASE_URL}/categories/{created_category_id}/"
        )
        assert category_response.status_code == status.HTTP_200_OK
        initial_category_data = category_response.json()
        assert (
            initial_category_data.get("thumbnail_path") != image_thumbnail_relative_path
        ), "Category thumbnail should not be this image initially."

        # 更新元数据并将图片设为类别缩略图
        update_payload_set_thumbnail = {
            "title": "Updated Title - Set Thumbnail",
            "description": "Updated description - Set Thumbnail",
            "tags": "updated, test, thumbnail",
            "set_as_category_thumbnail": True,
        }
        response_set = requests.put(
            f"{BASE_URL}/images/{image_id}/", json=update_payload_set_thumbnail
        )
        assert response_set.status_code == status.HTTP_200_OK
        updated_data_set = response_set.json()
        assert updated_data_set["title"] == "Updated Title - Set Thumbnail"
        assert (
            updated_data_set.get("relative_thumbnail_path")
            == image_thumbnail_relative_path
        )

        # 验证类别缩略图是否已设置为此图片的缩略图
        time.sleep(0.1)  # 短暂等待，以防数据库异步操作或缓存
        category_response_after_set = requests.get(
            f"{BASE_URL}/categories/{created_category_id}/"
        )
        assert category_response_after_set.status_code == status.HTTP_200_OK
        category_data_after_set = category_response_after_set.json()
        assert (
            category_data_after_set.get("thumbnail_path")
            == image_thumbnail_relative_path
        ), f"Category thumbnail_path expected {image_thumbnail_relative_path}, got {category_data_after_set.get('thumbnail_path')}"

        # 再次更新元数据并将图片从类别缩略图上取消
        update_payload_unset_thumbnail = {
            "title": "Updated Title - Unset Thumbnail",
            "set_as_category_thumbnail": False,
        }
        response_unset = requests.put(
            f"{BASE_URL}/images/{image_id}/", json=update_payload_unset_thumbnail
        )
        assert response_unset.status_code == status.HTTP_200_OK
        updated_data_unset = response_unset.json()
        assert updated_data_unset["title"] == "Updated Title - Unset Thumbnail"

        # 验证类别缩略图是否已清除 (或不再是此图片)
        time.sleep(0.1)
        category_response_after_unset = requests.get(
            f"{BASE_URL}/categories/{created_category_id}/"
        )
        assert category_response_after_unset.status_code == status.HTTP_200_OK
        category_data_after_unset = category_response_after_unset.json()
        assert (
            category_data_after_unset.get("thumbnail_path")
            != image_thumbnail_relative_path
        ), "Category thumbnail_path should have been unset or changed."
        # 根据当前后端逻辑，取消设置会将 thumbnail_path 设为 null/None
        assert (
            category_data_after_unset.get("thumbnail_path") is None
        ), f"Category thumbnail_path expected to be None, got {category_data_after_unset.get('thumbnail_path')}"

    finally:
        if image_id:
            requests.delete(f"{BASE_URL}/images/{image_id}/")  # 清理图片


def test_update_image_not_found():
    """测试更新不存在的图片元数据。"""
    non_existent_uuid = str(uuid.uuid4())
    update_payload = {"title": "NonExistent Update (Requests)"}
    response = requests.put(
        f"{BASE_URL}/images/{non_existent_uuid}/", json=update_payload
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_image(created_category_id: str, temp_image_file: Path):
    """
    测试删除图片。

    参数:
        created_category_id (str): 已创建类别的ID。
        temp_image_file (Path): 临时图片文件的路径。
    """
    # 先上传一张图片
    with open(temp_image_file, "rb") as f:
        files = {"file": (temp_image_file.name, f, "image/png")}
        data = {
            "category_id": created_category_id,
            "title": "Image To Delete (Requests)",
        }
        upload_response = requests.post(
            f"{BASE_URL}/images/upload/", files=files, data=data
        )
    assert upload_response.status_code == status.HTTP_201_CREATED
    image_id = upload_response.json()["id"]

    # 删除图片
    delete_response = requests.delete(f"{BASE_URL}/images/{image_id}/")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # 验证图片是否真的被删除
    get_response = requests.get(f"{BASE_URL}/images/{image_id}/")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
    # 图片已被删除，不需要在 finally 中再次删除


def test_delete_image_not_found():
    """测试删除不存在的图片。"""
    non_existent_uuid = str(uuid.uuid4())
    response = requests.delete(f"{BASE_URL}/images/{non_existent_uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# 注意：
# 1. 文件上传测试依赖于项目中 `tests/assets/test_image.png` 文件的存在。
#    `setup_test_image` fixture 会尝试创建一个虚拟图片如果它不存在且 Pillow 安装了。
# 2. 与外部API交互时，测试的独立性和数据清理非常重要。
#    `created_category_id` fixture 和各个测试用例中的 try/finally 块尝试处理这个问题。
# 3. `set_as_category_thumbnail` 的验证在 `test_update_image_metadata` 中进行了尝试，
#    其准确性取决于API如何处理缩略图的更新和类别关联。
# 4. `str(uuid.uuid4())` 用于生成符合UUID格式的随机字符串，用于测试 "not found" 场景。
# 5. `set_as_category_thumbnail` 在上传时（`test_upload_image`）API期望的是字符串 "true" 或 "false"。
#    在更新时（`test_update_image_metadata`），FastAPI通常能将布尔值 `True`/`False` 自动转换。
#    如果API严格要求字符串，则 `update_payload` 中也应使用 `"true"`/`"false"`。已修改为布尔值，依赖FastAPI转换。
