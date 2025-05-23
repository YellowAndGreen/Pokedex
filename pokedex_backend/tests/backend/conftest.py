import pytest

# from fastapi.testclient import TestClient # 不再需要 TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

# pokedex_backend 相关的导入如果仅由 client_fixture 使用，则可以移除或移到别处
# from pokedex_backend.app.main import app
# from pokedex_backend.app.database import get_session


@pytest.fixture(scope="session", autouse=True)
def engine_fixture():
    print("DEBUG: engine_fixture started.")
    SQLModel.metadata.clear()
    print(
        f"DEBUG: SQLModel.metadata cleared. Tables: {list(SQLModel.metadata.tables.keys())}"
    )

    print("DEBUG: Attempting to import pokedex_backend.app.models...")
    try:
        import pokedex_backend.app.models

        print(f"DEBUG: pokedex_backend.app.models imported successfully.")
        print(
            f"DEBUG: Tables in SQLModel.metadata after import: {list(SQLModel.metadata.tables.keys())}"
        )
    except ImportError as e:
        print(f"DEBUG: Error importing pokedex_backend.app.models: {e}")
        raise

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    try:
        print(
            f"DEBUG: Calling SQLModel.metadata.create_all(engine). Tables to create: {list(SQLModel.metadata.tables.keys())}"
        )
        SQLModel.metadata.create_all(engine)
        print("DEBUG: SQLModel.metadata.create_all(engine) completed.")
    except Exception as e:
        print(f"DEBUG: Error during SQLModel.metadata.create_all(engine): {e}")
        existing_tables_before_error = []
        try:
            with engine.connect() as connection:
                from sqlalchemy import inspect

                inspector = inspect(engine)
                existing_tables_before_error = inspector.get_table_names()
        except Exception as inspect_e:
            print(f"DEBUG: Could not inspect existing tables: {inspect_e}")
        print(
            f"DEBUG: Existing tables in DB (if any) before create_all error: {existing_tables_before_error}"
        )
        raise

    return engine


@pytest.fixture(name="session")
def session_fixture(engine_fixture):
    with Session(engine_fixture) as session:
        yield session


# 移除 client_fixture
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
def tmp_upload_dir(tmp_path):
    return tmp_path / "uploads"
