"""
番茄钟路由：保存专注会话 / 今日统计

统一响应格式：{ code: 0, message, data }
专注时长后端写死 25 分钟（休息会话不入库）；可配置时长后置。
"""
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import PomodoroSessionRequest, ApiResponse
from ..crud import (
    create_pomodoro_session,
    today_pomodoro_count,
    recent_pomodoro_sessions,
    get_todo_by_id,
)
from ..deps import get_current_user
from ..models import User
from ..validators import BIZ_CODE

router = APIRouter(prefix="/api/pomodoro", tags=["pomodoro"])

FOCUS_MINUTES = 25


@router.post("/sessions", response_model=ApiResponse)
def save_session(
    payload: PomodoroSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    todo_id = None
    todo_title = None
    if payload.todoId is not None:
        todo = get_todo_by_id(db, current_user.id, payload.todoId)
        if not todo:
            # 复用待办错误码：仅区分"找不到可关联的待办"
            return ApiResponse(code=BIZ_CODE["TODO_NOT_FOUND"], message="关联的待办不存在")
        todo_id = todo.id
        todo_title = todo.title

    session = create_pomodoro_session(db, current_user.id, todo_id, todo_title, FOCUS_MINUTES)
    return ApiResponse(code=0, message="专注会话已记录", data=session.to_dict())


@router.get("/summary", response_model=ApiResponse)
def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    sessions = recent_pomodoro_sessions(db, current_user.id)
    return ApiResponse(
        code=0,
        message="OK",
        data={
            "todayCount": today_pomodoro_count(db, current_user.id, today),
            "recent": [s.to_dict() for s in sessions],
        },
    )
