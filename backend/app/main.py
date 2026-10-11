"""
FastAPI 应用入口

启动方式：
    cd backend
    uvicorn app.main:app --reload --port 8000
或：
    python run.py
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .database import engine, Base
from .models import User, Todo, Note, Schedule, Habit, HabitCheckin, PomodoroSession  # noqa: F401  确保模型被注册
from .routers import (
    user_router,
    todo_router,
    note_router,
    schedule_router,
    dashboard_router,
    habit_router,
    pomodoro_router,
)
from .deps import UnauthorizedError
from .validators import BIZ_CODE

# 创建所有表（首次启动时自动建表）
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Admin Pro Backend", version="0.1.0")

# CORS：允许前端开发服务器跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境放开，生产环境应指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(user_router)
app.include_router(todo_router)
app.include_router(note_router)
app.include_router(schedule_router)
app.include_router(dashboard_router)
app.include_router(habit_router)
app.include_router(pomodoro_router)


# 认证失败：沿用「HTTP 恒 200 + code 表达业务结果」约定，
# 前端 axios 拦截器按 code !== 0 统一处理，无需感知 401 状态码
@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(request: Request, exc: UnauthorizedError):
    return JSONResponse(
        status_code=200,
        content={
            "code": BIZ_CODE["UNAUTHORIZED"],
            "message": "未登录或登录已过期，请重新登录",
            "data": None,
        },
    )


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}
