from .user import router as user_router
from .todo import router as todo_router
from .note import router as note_router
from .schedule import router as schedule_router
from .dashboard import router as dashboard_router

__all__ = ["user_router", "todo_router", "note_router", "schedule_router", "dashboard_router"]
