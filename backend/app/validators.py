"""
业务错误码与数据校验规则

校验规则与前端 mock/user.js 中的 RULES 保持一致，
确保前后端校验口径统一。
"""
import re
from datetime import datetime

# 业务错误码（与前端 src/api/user.js 中的 BIZ_CODE 对齐）
BIZ_CODE = {
    "USERNAME_INVALID": 40001,
    "PASSWORD_INVALID": 40002,
    "EMAIL_INVALID": 40003,
    "PASSWORD_NOT_MATCH": 40004,
    "USER_NOT_FOUND": 40401,
    "PASSWORD_INCORRECT": 40101,
    "USERNAME_EXISTS": 40901,
    "EMAIL_EXISTS": 40902,
    "UNAUTHORIZED": 40100,
    "TODO_TITLE_INVALID": 40005,
    "TODO_NOT_FOUND": 40402,
    "TODO_STATUS_INVALID": 40007,
    "NOTE_CONTENT_INVALID": 40006,
    "NOTE_NOT_FOUND": 40403,
    "SCHEDULE_TITLE_INVALID": 40008,
    "SCHEDULE_DATE_INVALID": 40009,
    "SCHEDULE_NOT_FOUND": 40404,
    "HABIT_NAME_INVALID": 40010,
    "HABIT_COLOR_INVALID": 40011,
    "HABIT_NOT_FOUND": 40405,
}

# 便签允许的颜色（与前端 notes.vue 的色板一致）
NOTE_COLORS = ("yellow", "blue", "green", "pink")

# 习惯允许的颜色（复用便签色板，与前端 habits.vue 一致）
HABIT_COLORS = NOTE_COLORS

# 待办看板允许的状态（与前端 kanban.vue 的三列一致）
TODO_STATUSES = ("todo", "doing", "done")

# 校验规则
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def validate_username(username: str) -> str:
    """返回错误信息，空字符串表示校验通过。"""
    if not username:
        return "请输入用户名"
    if len(username) < 3 or len(username) > 20:
        return "用户名长度为 3 ~ 20 个字符"
    if not USERNAME_PATTERN.match(username):
        return "仅支持字母、数字、下划线"
    return ""


def validate_password(password: str) -> str:
    if not password:
        return "请输入密码"
    if len(password) < 6 or len(password) > 20:
        return "密码长度为 6 ~ 20 个字符"
    return ""


def validate_email(email: str) -> str:
    if not email:
        return "请输入邮箱"
    if not EMAIL_PATTERN.match(email):
        return "邮箱格式不正确"
    return ""


def validate_todo_title(title: str) -> str:
    """Todo 标题校验：返回错误信息，空字符串表示校验通过。"""
    if not title or not title.strip():
        return "请输入待办标题"
    if len(title.strip()) > 100:
        return "待办标题不能超过 100 个字符"
    return ""


def validate_todo_status(status: str) -> str:
    """Todo 状态校验：返回错误信息，空字符串表示校验通过。"""
    if status not in TODO_STATUSES:
        return "待办状态不合法"
    return ""


def validate_schedule_title(title: str) -> str:
    """日程标题校验：返回错误信息，空字符串表示校验通过。"""
    if not title or not title.strip():
        return "请输入日程标题"
    if len(title.strip()) > 100:
        return "日程标题不能超过 100 个字符"
    return ""


def validate_schedule_date(date: str) -> str:
    """日程日期校验（'YYYY-MM-DD'）：返回错误信息，空字符串表示校验通过。"""
    if not date or not DATE_PATTERN.match(date):
        return "日期格式不正确"
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "日期不存在"
    return ""


def validate_schedule_time(time_str: str, field: str) -> str:
    """日程时间校验（'HH:MM'）：返回错误信息，空字符串表示校验通过。"""
    if time_str and not TIME_PATTERN.match(time_str):
        return f"{field}格式不正确"
    return ""


def validate_note_content(content: str) -> str:
    """便签内容校验：返回错误信息，空字符串表示校验通过。"""
    if not content or not content.strip():
        return "请输入便签内容"
    if len(content.strip()) > 500:
        return "便签内容不能超过 500 个字符"
    return ""


def validate_habit_name(name: str) -> str:
    """习惯名称校验：返回错误信息，空字符串表示校验通过。"""
    if not name or not name.strip():
        return "请输入习惯名称"
    if len(name.strip()) > 50:
        return "习惯名称不能超过 50 个字符"
    return ""
