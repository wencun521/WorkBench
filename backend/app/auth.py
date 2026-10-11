"""
认证工具：密码哈希 + JWT 签发/校验

密码哈希直接使用 bcrypt 库（避免 passlib 与新版 bcrypt 的兼容性问题）。
"""
import os
import warnings
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

# JWT 配置：密钥通过环境变量 JWT_SECRET_KEY 注入
# 生产环境务必设置强随机密钥，否则启动时会输出警告
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-please-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 天

if SECRET_KEY.startswith("dev-secret"):
    warnings.warn(
        "JWT_SECRET_KEY 未设置，正在使用开发默认密钥，切勿在生产环境使用！",
        stacklevel=1,
    )


def hash_password(password: str) -> str:
    """对密码进行 bcrypt 哈希，返回字符串。"""
    # bcrypt 限制密码长度 72 字节，超长部分截断
    pwd_bytes = password.encode("utf-8")[:72]
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验密码是否匹配。"""
    pwd_bytes = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """签发 JWT，subject 为用户 id（字符串）。"""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    """解析 JWT，返回用户 id；失败返回 None。"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
