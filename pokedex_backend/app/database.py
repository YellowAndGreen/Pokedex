"""数据库连接和会话管理模块

负责初始化SQLModel引擎、创建数据库表以及提供数据库会话依赖。
"""

from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings  # 引入应用配置

# 从配置中读取数据库连接URL
SQLALCHEMY_DATABASE_URL = settings.database_url

# 创建数据库引擎
# connect_args 是SQLite特有的配置，用于允许多线程访问 (FastAPI是异步的，可能在不同线程处理请求)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,  # 在控制台打印SQLAlchemy生成的SQL语句，便于调试
    connect_args={"check_same_thread": False},  # 仅SQLite需要
)


def create_db_and_tables() -> None:
    """创建数据库表结构

    根据SQLModel元数据创建所有数据库表。
    应在应用启动时（例如在 main.py 中）调用。
    """
    # 确保所有模型都已在SQLModel.metadata中注册（通常在models/__init__.py中完成）
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """依赖注入函数，为每个请求提供一个数据库会话。

    使用 try-except-finally 结构确保会话在各种情况下都能正确提交、回滚和关闭。
    """
    with Session(engine) as session:
        try:
            yield session
            session.commit()  # 请求正常处理完毕，提交事务
        except Exception:
            session.rollback()  # 处理请求过程中发生异常，回滚事务
            raise
        finally:
            session.close()  # 无论成功或失败，最终都关闭会话
