"""
FastAPI 应用入口

启动方式：
    cd backend
    uvicorn app.main:app --reload --port 8000
或：
    python run.py

生产部署：
    cd frontend && npm run build 生成 frontend/dist/ 后，本应用会自动将其挂载在 /，
    单进程即可同时提供前端页面与 /api 接口。
"""
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from .database import engine, Base
from .models import (  # noqa: F401  确保模型被注册
    User,
    Todo,
    Note,
    Schedule,
    Habit,
    HabitCheckin,
    PomodoroSession,
    Bookmark,
)
from .routers import (
    user_router,
    todo_router,
    note_router,
    schedule_router,
    dashboard_router,
    habit_router,
    pomodoro_router,
    bookmark_router,
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
app.include_router(bookmark_router)


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


# 生产部署：若 frontend/dist 存在前端打包产物，则由本应用统一对外服务。
# 注意必须在所有 API 路由注册之后执行，避免拦截 /api 与 /health。
# SPA 回退：dist 中真实存在的文件（js/css/图标等）直接返回，
# 其余路径（如 /bookmarks）统一返回 index.html，交给前端路由处理。
_dist_dir = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if _dist_dir.is_dir():

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        candidate = (_dist_dir / full_path).resolve()
        if full_path and candidate.is_file() and candidate.is_relative_to(_dist_dir):
            return FileResponse(candidate)
        return FileResponse(_dist_dir / "index.html")
