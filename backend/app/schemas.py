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


# ---------- Todo ----------
class TodoCreateRequest(BaseModel):
    title: str = Field(..., description="待办标题")
    note: str = Field("", description="备注（可选）")
    status: str = Field("todo", description="任务状态（可选，默认 todo）")


class TodoUpdateRequest(BaseModel):
    title: str | None = Field(None, description="待办标题")
    note: str | None = Field(None, description="备注")
    status: str | None = Field(None, description="任务状态（todo/doing/done）")


# ---------- Note ----------
class NoteCreateRequest(BaseModel):
    content: str = Field(..., description="便签内容")
    color: str = Field("yellow", description="便签颜色")


class NoteUpdateRequest(BaseModel):
    content: str | None = Field(None, description="便签内容")
    color: str | None = Field(None, description="便签颜色")
    pinned: bool | None = Field(None, description="置顶状态")


# ---------- 统一响应 ----------
class ApiResponse(BaseModel):
    code: int = 0
    message: str = "OK"
    data: dict | None = None
