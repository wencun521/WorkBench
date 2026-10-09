"""
公共依赖：当前登录用户

沿用项目「HTTP 恒 200 + code 表达业务结果」的约定：
认证失败不返回裸 401，而是抛出 UnauthorizedError，
由 main.py 的异常处理器统一输出 { code: 40100, ... }，
前端 axios 拦截器无需任何改动即可识别。
"""
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .auth import decode_access_token
from .database import get_db
from .models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login", auto_error=False)


class UnauthorizedError(Exception):
    """认证失败（未携带 token / token 无效或过期）。"""


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    user_id = None
    if token:
        user_id = decode_access_token(token)

    if not user_id:
        raise UnauthorizedError()

    user = db.get(User, int(user_id))
    if not user:
        raise UnauthorizedError()

    return user
