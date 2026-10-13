"""
数据库连接配置

使用 SQLite 作为轻量级数据库，文件存放在 backend/app.db。
通过 SQLAlchemy ORM 操作数据，无需额外安装数据库服务。
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 多线程支持
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI 依赖：每个请求获取一个独立的数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
