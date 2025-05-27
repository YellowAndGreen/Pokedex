import pytest
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

# pokedex_backend 相关的导入如果仅由 client_fixture 使用，则可以移除或移到别处
# from pokedex_backend.app.main import app
# from pokedex_backend.app.database import get_session


@pytest.fixture(scope="session", autouse=True)
def engine_fixture():
    # 关键: 确保在创建引擎和表之前，所有模型都已加载到SQLModel.metadata中
    # 通常，这通过在项目早期导入所有模型模块来实现（例如在 app/models/__init__.py 或 app/main.py 中）
    # 这里我们显式导入，以确保测试环境的独立性和可靠性。
    try:
        # 导入 app.models 会触发 app/models/__init__.py 中的模型加载和 model_rebuild
        import pokedex_backend.app.models
    except ImportError as e:
        print(f"ERROR: Failed to import models in conftest.py: {e}")
        raise

    engine = create_engine(
        "sqlite:///:memory:",  # 使用内存数据库进行测试
        connect_args={"check_same_thread": False},  # SQLite 特定配置
        poolclass=StaticPool,  # 推荐用于 SQLite 测试
    )

    # 在创建表之前，确保所有模型都已注册到 SQLModel.metadata
    # 这一步通常由 `import pokedex_backend.app.models` 间接触发
    # 如果遇到 "no such table" 或 "no such column" 错误，请首先检查模型是否在 SQLModel.metadata 中正确注册
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine_fixture):  # 依赖于 engine_fixture
    with Session(engine_fixture) as session:
        yield session


# 移除 client_fixture，因为集成测试现在直接与运行中的服务器交互
# @pytest.fixture(name="client")
# def client_fixture(session: Session):
#     from pokedex_backend.app.main import app
#     from pokedex_backend.app.database import get_session
#
#     def get_session_override():
#         return session
#
#     app.dependency_overrides[get_session] = get_session_override
#     client = TestClient(app)
#     yield client
#     app.dependency_overrides.clear()


@pytest.fixture
def tmp_upload_dir(tmp_path):  # tmp_path 是 pytest 内置的 fixture
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)  # 确保目录被创建
    return upload_dir
