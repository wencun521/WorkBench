"""
数据操作（CRUD）
"""
from datetime import datetime

from sqlalchemy.orm import Session

from .models import User, Todo, Note, Schedule
from .auth import hash_password


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, username: str, password: str, email: str, role: str = "user") -> User:
    user = User(
        username=username,
        password_hash=hash_password(password),
        email=email,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------- Todo ----------
def create_todo(db: Session, user_id: int, title: str, note: str = "", status: str = "todo") -> Todo:
    todo = Todo(user_id=user_id, title=title, note=note, status=status)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def list_todos(db: Session, user_id: int) -> list[Todo]:
    return (
        db.query(Todo)
        .filter(Todo.user_id == user_id)
        .order_by(Todo.created_at.desc())
        .all()
    )


def get_todo_by_id(db: Session, user_id: int, todo_id: int) -> Todo | None:
    # 强制限定 user_id：不存在与非本人统一按不存在处理，防泄露
    return (
        db.query(Todo)
        .filter(Todo.id == todo_id, Todo.user_id == user_id)
        .first()
    )


def update_todo(db: Session, todo: Todo, **fields) -> Todo:
    for key, value in fields.items():
        if value is not None:
            setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo


def delete_todo(db: Session, todo: Todo) -> None:
    db.delete(todo)
    db.commit()


# ---------- Note ----------
def create_note(db: Session, user_id: int, content: str, color: str = "yellow") -> Note:
    note = Note(user_id=user_id, content=content, color=color)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def list_notes(db: Session, user_id: int) -> list[Note]:
    # 置顶在前，其余按创建时间倒序
    return (
        db.query(Note)
        .filter(Note.user_id == user_id)
        .order_by(Note.pinned.desc(), Note.created_at.desc())
        .all()
    )


def get_note_by_id(db: Session, user_id: int, note_id: int) -> Note | None:
    # 强制限定 user_id：不存在与非本人统一按不存在处理，防泄露
    return (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == user_id)
        .first()
    )


def update_note(db: Session, note: Note, **fields) -> Note:
    for key, value in fields.items():
        setattr(note, key, value)
    # 仅内容/颜色变更视为"编辑"，刷新 updated_at；置顶变更不影响
    if "content" in fields or "color" in fields:
        note.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, note: Note) -> None:
    db.delete(note)
    db.commit()


# ---------- Schedule ----------
def create_schedule(
    db: Session, user_id: int, title: str, date: str,
    start: str | None, end: str | None, all_day: bool, note: str = ""
) -> Schedule:
    schedule = Schedule(
        user_id=user_id, title=title, date=date,
        start=start, end=end, all_day=all_day, note=note,
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def list_schedules(
    db: Session, user_id: int, start: str | None = None, end: str | None = None
) -> list[Schedule]:
    query = db.query(Schedule).filter(Schedule.user_id == user_id)
    if start:
        query = query.filter(Schedule.date >= start)
    if end:
        query = query.filter(Schedule.date <= end)
    # 先按日期升序，同日内按开始时间排序（全天日程排最前：start 为空字典序最小）
    return query.order_by(Schedule.date.asc(), Schedule.start.asc()).all()


def list_schedules_by_date(db: Session, user_id: int, date: str) -> list[Schedule]:
    return (
        db.query(Schedule)
        .filter(Schedule.user_id == user_id, Schedule.date == date)
        .order_by(Schedule.start.asc())
        .all()
    )


def get_schedule_by_id(db: Session, user_id: int, schedule_id: int) -> Schedule | None:
    # 强制限定 user_id：不存在与非本人统一按不存在处理，防泄露
    return (
        db.query(Schedule)
        .filter(Schedule.id == schedule_id, Schedule.user_id == user_id)
        .first()
    )


def update_schedule(db: Session, schedule: Schedule, **fields) -> Schedule:
    for key, value in fields.items():
        setattr(schedule, key, value)
    db.commit()
    db.refresh(schedule)
    return schedule


def delete_schedule(db: Session, schedule: Schedule) -> None:
    db.delete(schedule)
    db.commit()
