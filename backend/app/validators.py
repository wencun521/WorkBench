"""
业务错误码与数据校验规则

校验规则与前端 mock/user.js 中的 RULES 保持一致，
确保前后端校验口径统一。
"""
import re

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
}

# 校验规则
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


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
