"""
数据操作（CRUD）
"""
from datetime import datetime

from sqlalchemy.orm import Session

from .models import User, Todo, Note, Schedule, Habit, HabitCheckin, PomodoroSession, Bookmark
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
    # 番茄钟会话不级联删除：解除关联（保留 todo_title 快照供历史查看）
    db.query(PomodoroSession).filter(PomodoroSession.todo_id == todo.id).update(
        {PomodoroSession.todo_id: None}
    )
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


# ---------- Habit ----------
def create_habit(db: Session, user_id: int, name: str, color: str = "blue") -> Habit:
    habit = Habit(user_id=user_id, name=name, color=color)
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


def list_habits(db: Session, user_id: int) -> list[Habit]:
    return db.query(Habit).filter(Habit.user_id == user_id).order_by(Habit.created_at.asc()).all()


def get_habit_by_id(db: Session, user_id: int, habit_id: int) -> Habit | None:
    # 强制限定 user_id：不存在与非本人统一按不存在处理，防泄露
    return db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user_id).first()


def update_habit(db: Session, habit: Habit, **fields) -> Habit:
    for key, value in fields.items():
        if value is not None:
            setattr(habit, key, value)
    db.commit()
    db.refresh(habit)
    return habit


def delete_habit(db: Session, habit: Habit) -> None:
    # 显式先删打卡记录（SQLite 不依赖 DB 级联）
    db.query(HabitCheckin).filter(HabitCheckin.habit_id == habit.id).delete()
    db.delete(habit)
    db.commit()


def get_checkin(db: Session, habit_id: int, date: str) -> HabitCheckin | None:
    return (
        db.query(HabitCheckin)
        .filter(HabitCheckin.habit_id == habit_id, HabitCheckin.date == date)
        .first()
    )


def add_checkin(db: Session, habit_id: int, user_id: int, date: str) -> HabitCheckin | None:
    """打卡（幂等：当天已打卡返回 None 表示无变化）。"""
    if get_checkin(db, habit_id, date):
        return None
    checkin = HabitCheckin(habit_id=habit_id, user_id=user_id, date=date)
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin


def remove_checkin(db: Session, habit_id: int, date: str) -> bool:
    """取消打卡：返回是否有删除发生。"""
    checkin = get_checkin(db, habit_id, date)
    if not checkin:
        return False
    db.delete(checkin)
    db.commit()
    return True


def count_habits_done_on(db: Session, user_id: int, date: str) -> tuple[int, int]:
    """返回 (今日已打卡习惯数, 习惯总数)。"""
    total = db.query(Habit).filter(Habit.user_id == user_id).count()
    done = (
        db.query(HabitCheckin)
        .join(Habit, Habit.id == HabitCheckin.habit_id)
        .filter(Habit.user_id == user_id, HabitCheckin.date == date)
        .count()
    )
    return done, total


# ---------- Pomodoro ----------
def create_pomodoro_session(
    db: Session, user_id: int, todo_id: int | None, todo_title: str | None, duration_minutes: int
) -> PomodoroSession:
    session = PomodoroSession(
        user_id=user_id,
        todo_id=todo_id,
        todo_title=todo_title,
        duration_minutes=duration_minutes,
        date=datetime.utcnow().strftime("%Y-%m-%d"),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def today_pomodoro_count(db: Session, user_id: int, date: str) -> int:
    return (
        db.query(PomodoroSession)
        .filter(PomodoroSession.user_id == user_id, PomodoroSession.date == date)
        .count()
    )


def recent_pomodoro_sessions(db: Session, user_id: int, limit: int = 10) -> list[PomodoroSession]:
    return (
        db.query(PomodoroSession)
        .filter(PomodoroSession.user_id == user_id)
        .order_by(PomodoroSession.created_at.desc())
        .limit(limit)
        .all()
    )


# ---------- Bookmark ----------
def create_bookmark(
    db: Session, user_id: int, url: str,
    title: str | None = None, category: str = "未分类", note: str | None = None,
) -> Bookmark:
    bookmark = Bookmark(
        user_id=user_id, url=url, title=title, category=category, note=note
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


def list_bookmarks(db: Session, user_id: int) -> list[Bookmark]:
    return (
        db.query(Bookmark)
        .filter(Bookmark.user_id == user_id)
        .order_by(Bookmark.created_at.desc())
        .all()
    )


def get_bookmark_by_id(db: Session, user_id: int, bookmark_id: int) -> Bookmark | None:
    # 强制限定 user_id：不存在与非本人统一按不存在处理，防泄露
    return (
        db.query(Bookmark)
        .filter(Bookmark.id == bookmark_id, Bookmark.user_id == user_id)
        .first()
    )


def update_bookmark(db: Session, bookmark: Bookmark, **fields) -> Bookmark:
    for key, value in fields.items():
        if value is not None:
            setattr(bookmark, key, value)
    db.commit()
    db.refresh(bookmark)
    return bookmark


def delete_bookmark(db: Session, bookmark: Bookmark) -> None:
    db.delete(bookmark)
    db.commit()
