from .user import router as user_router
from .todo import router as todo_router
from .note import router as note_router
from .schedule import router as schedule_router
from .dashboard import router as dashboard_router
from .habit import router as habit_router
from .pomodoro import router as pomodoro_router
from .bookmark import router as bookmark_router

__all__ = [
    "user_router",
    "todo_router",
    "note_router",
    "schedule_router",
    "dashboard_router",
    "habit_router",
    "pomodoro_router",
    "bookmark_router",
]
