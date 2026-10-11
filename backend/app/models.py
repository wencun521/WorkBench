"""
数据模型

User 表：id, username, password_hash, email, role, created_at
Todo 表：id, user_id, title, note, status(todo/doing/done), created_at
         completed 列已废弃（保留声明防止 INSERT 违反 NOT NULL，全链路停止读写）
Note 表：id, user_id, content, color, pinned, created_at
Schedule 表：id, user_id, title, date, start, end, all_day, note, created_at
Habit 表：id, user_id, name, color, created_at
HabitCheckin 表：id, habit_id, user_id, date, created_at（habit_id+date 唯一）
PomodoroSession 表：id, user_id, todo_id, todo_title, duration_minutes, date, created_at
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index, UniqueConstraint

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
    # 三态任务状态；completed 为废弃列，仅保留声明（原表无 SQL DEFAULT，删声明会破坏 INSERT）
    status = Column(String(10), nullable=False, default="todo")
    completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "note": self.note or "",
            "status": self.status,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class Note(Base):
    __tablename__ = "notes"
    __table_args__ = (
        Index("ix_notes_user_created", "user_id", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String(500), nullable=False)
    color = Column(String(10), nullable=False, default="yellow")
    pinned = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # 由 crud.update_note 显式维护：仅内容/颜色变更时刷新（置顶变更不算编辑）
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "color": self.color,
            "pinned": self.pinned,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


class Schedule(Base):
    __tablename__ = "schedules"
    __table_args__ = (
        Index("ix_schedules_user_date", "user_id", "date"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=False)
    # date 存 'YYYY-MM-DD' 字符串：字典序即时间序，天然支持范围过滤
    date = Column(String(10), nullable=False)
    start = Column(String(5), nullable=True)  # 'HH:MM'，全天日程为空
    end = Column(String(5), nullable=True)
    all_day = Column(Boolean, nullable=False, default=False)
    note = Column(String(500), nullable=True, default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date,
            "start": self.start,
            "end": self.end,
            "allDay": self.all_day,
            "note": self.note or "",
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(50), nullable=False)
    color = Column(String(10), nullable=False, default="blue")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class HabitCheckin(Base):
    __tablename__ = "habit_checkins"
    __table_args__ = (
        UniqueConstraint("habit_id", "date", name="uq_habit_checkin_habit_date"),
        Index("ix_habit_checkins_user_date", "user_id", "date"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PomodoroSession(Base):
    __tablename__ = "pomodoro_sessions"
    __table_args__ = (
        Index("ix_pomodoro_sessions_user_date", "user_id", "date"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    todo_id = Column(Integer, ForeignKey("todos.id"), nullable=True)
    # 待办标题快照：待办删除后历史记录仍可读，列表免 join
    todo_title = Column(String(100), nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    date = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "todoId": self.todo_id,
            "todoTitle": self.todo_title,
            "durationMinutes": self.duration_minutes,
            "date": self.date,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
