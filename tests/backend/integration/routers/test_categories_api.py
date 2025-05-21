import pytest
from fastapi import status

import requests  # 新增
import uuid  # 用于生成唯一名称
from pathlib import Path  # 新增导入

BASE_URL = "http://localhost:8000/api"  # API 基础 URL
TEST_IMAGE_PATH = (
    Path(__file__).parent.parent.parent.parent / "assets" / "test_image.png"
)  # 修正图片路径


def generate_unique_name(base_name: str) -> str:
    """生成一个唯一的名称，用于测试中创建资源。

    通过在基础名称后附加UUID的前8位字符来确保唯一性。

    参数:
        base_name (str): 要附加唯一后缀的基础字符串。

    返回:
        str: 带有唯一后缀的字符串。
    """
    return f"{base_name}_{uuid.uuid4().hex[:8]}"


def test_create_category():
    """测试 POST /categories/ API 端点以成功创建一个新的类别。

    流程:
    1. 生成一个唯一的类别名称和描述。
    2. 发送 POST 请求到 /api/categories/ 端点创建新类别。
    3.断言响应状态码为 201 Created。
    4.断言返回的JSON数据包含正确的名称和存在的ID。
    5. 在测试结束时，尝试通过API删除创建的类别以进行清理。

    参数:
        无

    返回:
        无

    可能引发:
        AssertionError: 如果API响应状态码不为201，或者响应数据不符合预期。
    """
    unique_name = generate_unique_name("API Test Category")
    payload = {"name": unique_name, "description": "From API test using requests"}
    created_category_id = None
    try:
        response = requests.post(f"{BASE_URL}/categories/", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == unique_name
        assert "id" in data
        created_category_id = data["id"]
    finally:
        if created_category_id:
            delete_response = requests.delete(
                f"{BASE_URL}/categories/{created_category_id}/"
            )
            # 打印一些信息以帮助调试，如果删除失败，测试不应因此失败，但应记录
            if delete_response.status_code != status.HTTP_204_NO_CONTENT:
                print(
                    f"Cleanup Warning: Failed to delete category {created_category_id}. Status: {delete_response.status_code}"
                )


def test_get_category_list():
    """测试 GET /categories/ API 端点以检索类别列表。

    流程:
    1. 创建两个具有唯一名称的新类别作为测试数据。
    2. 发送 GET 请求到 /api/categories/ 端点。
    3.断言响应状态码为 200 OK。
    4.断言返回的数据是一个列表。
    5.断言列表中包含了刚刚创建的两个类别。
    6. 在测试结束时，尝试通过API删除创建的类别以进行清理。

    参数:
        无

    返回:
        无

    可能引发:
        AssertionError: 如果API响应状态码不为200，或者返回的数据格式不正确，或者未找到预期的类别。
    """
    # 为了确保列表测试的可靠性，我们创建几个唯一的类别
    cat1_name = generate_unique_name("List Test Cat 1")
    cat2_name = generate_unique_name("List Test Cat 2")
    cat1_id, cat2_id = None, None
    try:
        payload1 = {"name": cat1_name, "description": ""}
        res1 = requests.post(f"{BASE_URL}/categories/", json=payload1)
        assert res1.status_code == status.HTTP_201_CREATED
        cat1_id = res1.json()["id"]

        payload2 = {"name": cat2_name, "description": ""}
        res2 = requests.post(f"{BASE_URL}/categories/", json=payload2)
        assert res2.status_code == status.HTTP_201_CREATED
        cat2_id = res2.json()["id"]

        response = requests.get(f"{BASE_URL}/categories/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # 由于可能有其他类别存在，我们检查我们刚创建的是否在列表中
        found_cat1 = any(
            item["name"] == cat1_name and item["id"] == cat1_id for item in data
        )
        found_cat2 = any(
            item["name"] == cat2_name and item["id"] == cat2_id for item in data
        )
        assert found_cat1, f"Category {cat1_name} not found in list"
        assert found_cat2, f"Category {cat2_name} not found in list"
    finally:
        if cat1_id:
            requests.delete(f"{BASE_URL}/categories/{cat1_id}/")  # Cleanup
        if cat2_id:
            requests.delete(f"{BASE_URL}/categories/{cat2_id}/")  # Cleanup


# ... (其他测试函数也需要类似修改) ...
# 原有的 test_delete_category, test_create_duplicate_category,
# test_read_category_with_images, test_update_category,
# test_update_category_not_found, test_get_category_not_found
# 都需要被重写以使用 requests 和 BASE_URL，并管理好测试数据的创建和清理。

# 为了演示，我将继续修改 test_delete_category


def test_delete_category():
    """测试 DELETE /categories/{category_id}/ API 端点以成功删除一个类别。

    流程:
    1. 创建一个新类别以供删除。
    2. 发送 DELETE 请求到 /api/categories/{category_id}/ 端点删除该类别。
    3.断言响应状态码为 204 No Content。
    4. 发送 GET 请求到同一端点以验证类别是否确实已被删除。
    5.断言GET请求的响应状态码为 404 Not Found。

    参数:
        无

    返回:
        无

    可能引发:
        AssertionError: 如果创建、删除或验证删除的API调用未返回预期的状态码。
    """
    category_name = generate_unique_name("To Delete Category")
    payload = {
        "name": category_name,
        "description": "Category to be deleted via requests",
    }

    create_res = requests.post(f"{BASE_URL}/categories/", json=payload)
    assert create_res.status_code == status.HTTP_201_CREATED
    category_id = create_res.json()["id"]

    delete_res = requests.delete(f"{BASE_URL}/categories/{category_id}/")
    assert delete_res.status_code == status.HTTP_204_NO_CONTENT

    # 验证是否真的被删除了
    get_res = requests.get(f"{BASE_URL}/categories/{category_id}/")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND
    # 注意：如果删除失败，这条测试本身就会失败，所以不需要在 finally 中再次尝试删除


def test_create_duplicate_category():
    """测试当尝试创建同名类别时 POST /categories/ API 端点的行为。

    流程:
    1. 创建一个具有唯一名称的新类别。
    2. 再次尝试使用完全相同的 payload 创建同名类别。
    3.断言第二次请求的响应状态码为 400 Bad Request (或应用定义的其他冲突错误码)。
    4. (可选) 检查错误响应体中是否包含指示名称重复的特定消息。
    5. 在测试结束时，尝试通过API删除最初创建的类别以进行清理。

    参数:
        无

    返回:
        无

    可能引发:
        AssertionError: 如果第一次类别创建不成功，或者第二次重复创建未返回预期的冲突状态码。
    """
    unique_name = generate_unique_name("UniqueNameCategory")
    payload = {"name": unique_name, "description": "First instance"}
    category_id_to_delete = None
    try:
        response1 = requests.post(f"{BASE_URL}/categories/", json=payload)
        assert response1.status_code == status.HTTP_201_CREATED
        category_id_to_delete = response1.json()["id"]

        response2 = requests.post(f"{BASE_URL}/categories/", json=payload)
        # 根据 OpenAPI 和之前的测试，重复名称可能返回 400 或其他特定错误码
        # 假设后端对重复名称返回 400 Bad Request (或者更合适的如 409 Conflict, 422 Unprocessable Entity)
        assert (
            response2.status_code == status.HTTP_400_BAD_REQUEST
        )  # 或者其他应用实际返回的冲突码
        # 检查错误响应体中是否有预期信息，例如：
        # assert "already exists" in response2.json().get("detail", "").lower()
    finally:
        if category_id_to_delete:
            requests.delete(f"{BASE_URL}/categories/{category_id_to_delete}/")


def test_read_category_with_images():
    """测试 GET /categories/{category_id}/ API 端点以获取特定类别及其关联图片信息。

    注意：此测试目前不实际创建图片，仅验证类别结构中存在 'images' 字段且为列表。

    流程:
    1. 创建一个新类别。
    2. 发送 GET 请求到 /api/categories/{category_id}/ 端点获取该类别详情。
    3.断言响应状态码为 200 OK。
    4.断言返回的数据包含正确的类别名称和ID。
    5.断言返回的数据中包含一个名为 'images' 的键，其值为一个列表。
    6. 在测试结束时，尝试通过API删除创建的类别以进行清理。

    参数:
        无

    返回:
        无

    可能引发:
        AssertionError: 如果API调用未返回预期状态码，或响应数据结构不符合预期。
    """
    category_name = generate_unique_name("CategoryForReadWithImages")
    payload = {
        "name": category_name,
        "description": "Test reading with images via requests",
    }
    category_id = None
    try:
        response = requests.post(f"{BASE_URL}/categories/", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        category_id = response.json()["id"]

        get_response = requests.get(f"{BASE_URL}/categories/{category_id}/")
        assert get_response.status_code == status.HTTP_200_OK
        data = get_response.json()
        assert data["name"] == category_name
        assert data["id"] == category_id
        assert "images" in data
        assert isinstance(data["images"], list)
    finally:
        if category_id:
            requests.delete(f"{BASE_URL}/categories/{category_id}/")


def test_update_category():
    """测试 PUT /categories/{category_id}/ API 端点以成功更新一个现有类别的信息。

    流程:
    1. 创建一个新类别。
    2. 准备包含新名称和描述的 payload。
    3. 发送 PUT 请求到 /api/categories/{category_id}/ 端点以更新类别信息。
    4.断言响应状态码为 200 OK。
    5.断言返回的数据反映了更新后的名称和描述。
    6. 再次发送 GET 请求获取该类别，验证持久化的信息也是更新后的。
    7. 在测试结束时，尝试通过API删除创建（并更新）的类别以进行清理。

    参数:
        无

    返回:
        无

    可能引发:
        AssertionError: 如果API调用未返回预期状态码，或更新后的数据未正确反映和持久化。
    """
    initial_name = generate_unique_name("CategoryToUpdate")
    updated_name = generate_unique_name("UpdatedCategoryName")
    category_id = None
    try:
        create_payload = {"name": initial_name, "description": "Initial Description"}
        response = requests.post(f"{BASE_URL}/categories/", json=create_payload)
        assert response.status_code == status.HTTP_201_CREATED
        category_id = response.json()["id"]

        update_payload = {"name": updated_name, "description": "Updated Description"}
        put_response = requests.put(
            f"{BASE_URL}/categories/{category_id}/", json=update_payload
        )
        assert put_response.status_code == status.HTTP_200_OK
        data = put_response.json()
        assert data["name"] == updated_name
        assert data["description"] == "Updated Description"

        get_response = requests.get(f"{BASE_URL}/categories/{category_id}/")
        assert get_response.status_code == status.HTTP_200_OK
        data = get_response.json()
        assert data["name"] == updated_name
    finally:
        if category_id:
            requests.delete(f"{BASE_URL}/categories/{category_id}/")


def test_update_category_not_found():
    """测试当尝试更新一个不存在的类别时 PUT /categories/{category_id}/ API 端点的行为。

    流程:
    1. 使用一个预定义的、不存在的UUID。
    2. 准备更新用的 payload。
    3. 发送 PUT 请求到 /api/categories/{non_existent_uuid}/ 端点。
    4.断言响应状态码为 404 Not Found。

    参数:
        无

    返回:
        无

    可能引发:
        AssertionError: 如果API响应状态码不为404。
    """
    non_existent_uuid = "00000000-0000-0000-0000-000000000000"
    update_payload = {"name": "NonExistentUpdate"}
    response = requests.put(
        f"{BASE_URL}/categories/{non_existent_uuid}/", json=update_payload
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_category_not_found():
    """测试当尝试获取一个不存在的类别时 GET /categories/{category_id}/ API 端点的行为。

    流程:
    1. 生成一个随机的、极可能不存在的类别ID。
    2. 发送 GET 请求到 /api/categories/{category_id}/ 端点。
    3.断言响应状态码为 404 Not Found。

    参数:
        无

    返回:
        无

    可能引发:
        AssertionError: 如果API未返回预期的404状态码。
    """
    random_id = uuid.uuid4()
    response = requests.get(f"{BASE_URL}/categories/{random_id}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_category_with_multiple_images():
    """
    测试删除一个包含多个图片的类别时，该类别及其所有关联的图片是否都被正确删除。

    流程:
    1. 创建一个新的唯一名称的类别。
    2. 在该类别下上传至少两张不同的测试图片。
    3. 调用 API 删除该类别。
    4. 断言类别删除成功 (204 No Content)。
    5. 断言尝试获取已删除类别返回 404 Not Found。
    6. 断言尝试获取之前上传的每张图片均返回 404 Not Found。
    """
    category_name = generate_unique_name("CategoryWithMultipleImages")
    category_payload = {
        "name": category_name,
        "description": "Category to be deleted with its images",
    }
    created_category_id = None
    uploaded_image_ids = []
    # 初始化响应变量以避免 NameError in finally block
    cat_response = None
    delete_cat_response = None
    get_cat_response = None

    try:
        # 1. 创建类别
        cat_response = requests.post(f"{BASE_URL}/categories/", json=category_payload)
        assert cat_response.status_code == status.HTTP_201_CREATED
        created_category_id = cat_response.json()["id"]

        # 2. 上传图片到该类别
        for i in range(2):  # 上传两张图片
            # 确保 TEST_IMAGE_PATH 在文件顶部定义
            # TEST_IMAGE_PATH = Path(__file__).parent.parent / "assets" / "test_image.png"
            if not TEST_IMAGE_PATH.exists():
                pytest.skip(
                    f"Test image not found at {TEST_IMAGE_PATH}, skipping image upload part of test."
                )
            with open(TEST_IMAGE_PATH, "rb") as f:
                files = {"file": (f"test_image_{i}.png", f, "image/png")}
                image_payload = {
                    "category_id": created_category_id,
                    "title": f"Image {i} for category {category_name}",
                }
                upload_response = requests.post(
                    f"{BASE_URL}/images/upload/", files=files, data=image_payload
                )
            assert (
                upload_response.status_code == status.HTTP_201_CREATED
            ), f"Failed to upload image {i}: {upload_response.text}"
            uploaded_image_ids.append(upload_response.json()["id"])

        assert len(uploaded_image_ids) == 2, "Should have uploaded 2 images"

        # 3. 删除类别
        delete_cat_response = requests.delete(
            f"{BASE_URL}/categories/{created_category_id}/"
        )
        # 4. 断言类别删除成功
        assert (
            delete_cat_response.status_code == status.HTTP_204_NO_CONTENT
        ), f"Failed to delete category: {delete_cat_response.text}"

        # 5. 断言尝试获取已删除类别返回 404
        get_cat_response = requests.get(f"{BASE_URL}/categories/{created_category_id}/")
        assert get_cat_response.status_code == status.HTTP_404_NOT_FOUND

        # 6. 断言尝试获取之前上传的每张图片均返回 404
        for image_id in uploaded_image_ids:
            get_image_response = requests.get(f"{BASE_URL}/images/{image_id}/")
            assert (
                get_image_response.status_code == status.HTTP_404_NOT_FOUND
            ), f"Image {image_id} was not deleted after category deletion."

    finally:
        # 清理：如果类别删除失败，尝试单独删除图片（如果已上传）
        if (
            delete_cat_response is not None
            and delete_cat_response.status_code != status.HTTP_204_NO_CONTENT
        ):
            for image_id in uploaded_image_ids:
                requests.delete(f"{BASE_URL}/images/{image_id}/")
        # 如果类别创建成功但删除测试失败（例如，类别未被正确删除），最后也要尝试删除类别
        if created_category_id and (
            get_cat_response is None
            or get_cat_response.status_code != status.HTTP_404_NOT_FOUND
        ):
            requests.delete(f"{BASE_URL}/categories/{created_category_id}/")


# End of file additions, ensure no existing code is duplicated or removed unintentionally
