"""
数据模型

User 表：id, username, password_hash, email, role, created_at
Todo 表：id, user_id, title, note, completed, created_at
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(20), unique=True, index=True, nullable=False)
    # 存储 bcrypt 哈希后的密码，绝不存明文
    password_hash = Column(String(128), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    role = Column(String(20), nullable=False, default="user")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class Todo(Base):
    __tablename__ = "todos"
    __table_args__ = (
        Index("ix_todos_user_created", "user_id", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=False)
    note = Column(String(500), nullable=True, default="")
    completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "note": self.note or "",
            "completed": self.completed,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
