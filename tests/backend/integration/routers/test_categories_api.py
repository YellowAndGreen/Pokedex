import pytest
from fastapi import status
from sqlmodel import Session
from pokedex_backend.app.models.category_models import CategoryCreate


def test_create_category(client):
    """测试分类创建API"""
    payload = {"name": "API Test", "description": "From API test"}
    response = client.post("/api/categories/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "API Test"
    assert "id" in data


def test_get_category_list(client):
    """测试获取分类列表"""
    # 创建测试数据
    client.post("/api/categories/", json={"name": "List Test 1", "description": ""})
    client.post("/api/categories/", json={"name": "List Test 2", "description": ""})

    response = client.get("/api/categories/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2
    assert any(item["name"] == "List Test 1" for item in data)


def test_delete_category(client):
    """测试删除分类"""
    create_res = client.post(
        "/api/categories/", json={"name": "To Delete", "description": ""}
    )
    category_id = create_res.json()["id"]

    delete_res = client.delete(f"/api/categories/{category_id}")
    assert delete_res.status_code == status.HTTP_204_NO_CONTENT

    get_res = client.get(f"/api/categories/{category_id}")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND


def test_create_duplicate_category(client):
    """测试创建重复分类名称"""
    payload = {"name": "Unique", "description": "First"}
    client.post("/api/categories/", json=payload)

    response = client.post("/api/categories/", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]
