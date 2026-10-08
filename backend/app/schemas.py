"""
Pydantic 请求/响应模型
"""
from pydantic import BaseModel, Field


# ---------- 登录 ----------
class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


# ---------- 注册 ----------
class RegisterRequest(BaseModel):
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    password: str = Field(..., description="密码")
    confirmPassword: str = Field(..., description="确认密码")


# ---------- 统一响应 ----------
class ApiResponse(BaseModel):
    code: int = 0
    message: str = "OK"
    data: dict | None = None
