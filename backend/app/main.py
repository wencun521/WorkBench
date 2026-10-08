"""
FastAPI 应用入口

启动方式：
    cd backend
    uvicorn app.main:app --reload --port 8000
或：
    python run.py
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .models import User  # noqa: F401  确保模型被注册
from .routers import user_router

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


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}
