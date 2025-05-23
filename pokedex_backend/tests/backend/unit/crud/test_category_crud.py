import pytest
from sqlmodel import Session
from pokedex_backend.app.models.category_models import CategoryCreate, Category
from pokedex_backend.app.crud.category_crud import (
    create_category,
    get_category,
    delete_category,
)


def test_create_category(session: Session):
    """测试创建分类功能"""
    category_data = CategoryCreate(name="Test Category", description="Test description")
    created_category = create_category(session, category_data)

    assert created_category.id is not None
    assert created_category.name == "Test Category"
    assert created_category.description == "Test description"


def test_get_category(session: Session):
    """测试获取分类详情"""
    # 先创建测试数据
    category_data = CategoryCreate(name="Test Get", description="For get test")
    created_category = create_category(session, category_data)

    # 测试获取
    fetched_category = get_category(session, created_category.id)
    assert fetched_category.name == "Test Get"
    assert fetched_category.description == "For get test"


def test_delete_category(session: Session):
    """测试删除分类功能"""
    # 创建测试数据
    category_data = CategoryCreate(name="To Delete", description="Will be deleted")
    created_category = create_category(session, category_data)

    # 执行删除
    deleted = delete_category(session, created_category.id)
    assert deleted is True

    # 验证删除后无法查询
    assert get_category(session, created_category.id) is None


def test_create_duplicate_category(session: Session):
    """测试创建重复分类名称的异常处理"""
    category_data = CategoryCreate(name="Unique Category", description="First")
    create_category(session, category_data)

    # 再次创建同名分类应引发异常
    with pytest.raises(ValueError) as exc_info:
        create_category(session, category_data)
    assert "Category name already exists" in str(exc_info.value)
