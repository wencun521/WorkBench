"""
工作台仪表盘聚合接口

一次返回各模块摘要，供首页单请求渲染。
只读聚合，不做任何写操作；仅 40100 认证场景（走全局异常处理器）。
"""
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..crud import (
    list_todos,
    list_notes,
    list_schedules_by_date,
    count_habits_done_on,
    today_pomodoro_count,
    list_bookmarks,
)
from ..deps import get_current_user
from ..models import User

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = datetime.utcnow().strftime("%Y-%m-%d")

    todos = list_todos(db, current_user.id)
    notes = list_notes(db, current_user.id)
    schedules = list_schedules_by_date(db, current_user.id, today)
    bookmarks = list_bookmarks(db, current_user.id)
    habits_done, habits_total = count_habits_done_on(db, current_user.id, today)
    pomodoros_today = today_pomodoro_count(db, current_user.id, today)

    return {
        "code": 0,
        "message": "OK",
        "data": {
            "today": today,
            "todo": {
                "total": len(todos),
                "doing": sum(1 for t in todos if t.status == "doing"),
                "done": sum(1 for t in todos if t.status == "done"),
            },
            # 今日待办：未完成的在前，最多 5 条（只读摘要，操作去 /todo 页）
            "todayTodos": [
                {"id": t.id, "title": t.title, "status": t.status}
                for t in sorted(todos, key=lambda x: x.status == "done")[:5]
            ],
            "noteCount": len(notes),
            "recentNotes": [
                {
                    "id": n.id,
                    "content": n.content,
                    "color": n.color,
                    "createdAt": n.created_at.isoformat() if n.created_at else None,
                }
                for n in notes[:3]
            ],
            "scheduleCount": len(schedules),
            "todaySchedules": [
                {"id": s.id, "title": s.title, "start": s.start, "allDay": s.all_day}
                for s in schedules[:5]
            ],
            "habit": {"total": habits_total, "doneToday": habits_done},
            "pomodoro": {"todayCount": pomodoros_today},
            "bookmark": {"total": len(bookmarks)},
        },
    }
