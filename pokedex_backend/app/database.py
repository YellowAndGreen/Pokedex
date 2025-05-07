"""数据库连接与会话管理模块

提供数据库引擎初始化、会话管理和表创建功能
"""

from contextlib import contextmanager
from typing import Generator
from sqlmodel import Session, SQLModel, create_engine
from app.core.config import settings


# 初始化数据库引擎
engine = create_engine(settings.database_url)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """获取数据库会话的上下文管理器
    
    Yields:
        Session: SQLModel数据库会话对象
        
    示例:
        with get_session() as session:
            session.add(...)
            session.commit()
    """
    with Session(engine) as session:
        yield session


def create_db_and_tables() -> None:
    """创建数据库表结构
    
    根据SQLModel元数据创建所有数据库表
    应在应用启动时调用
    """
    SQLModel.metadata.create_all(engine)
