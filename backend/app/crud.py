"""
数据操作（CRUD）
"""
from sqlalchemy.orm import Session

from .models import User, Todo
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
def create_todo(db: Session, user_id: int, title: str, note: str = "") -> Todo:
    todo = Todo(user_id=user_id, title=title, note=note)
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
