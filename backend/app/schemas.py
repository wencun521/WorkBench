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


# ---------- Schedule ----------
class ScheduleCreateRequest(BaseModel):
    title: str = Field(..., description="日程标题")
    date: str = Field(..., description="日期（YYYY-MM-DD）")
    start: str | None = Field(None, description="开始时间（HH:MM，全天为空）")
    end: str | None = Field(None, description="结束时间（HH:MM）")
    allDay: bool = Field(False, description="是否全天")
    note: str = Field("", description="备注")


class ScheduleUpdateRequest(BaseModel):
    title: str | None = Field(None, description="日程标题")
    date: str | None = Field(None, description="日期（YYYY-MM-DD）")
    start: str | None = Field(None, description="开始时间（HH:MM）")
    end: str | None = Field(None, description="结束时间（HH:MM）")
    allDay: bool | None = Field(None, description="是否全天")
    note: str | None = Field(None, description="备注")


# ---------- Habit ----------
class HabitCreateRequest(BaseModel):
    name: str = Field(..., description="习惯名称")
    color: str = Field("blue", description="颜色标记")


class HabitUpdateRequest(BaseModel):
    name: str | None = Field(None, description="习惯名称")
    color: str | None = Field(None, description="颜色标记")


# ---------- Pomodoro ----------
class PomodoroSessionRequest(BaseModel):
    todoId: int | None = Field(None, description="关联待办（可选）")


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
