"""
用户相关路由：登录 / 注册

统一响应格式：{ code: 0, message, data }
业务错误通过 code != 0 表达，HTTP 状态码保持 200，
前端根据 code 字段判断业务是否成功。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import LoginRequest, RegisterRequest, ApiResponse
from ..crud import get_user_by_username, get_user_by_email, create_user
from ..auth import verify_password, create_access_token
from ..validators import (
    BIZ_CODE,
    validate_username,
    validate_password,
    validate_email,
)

router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("/login", response_model=ApiResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # 1. 入参格式校验
    err = validate_username(payload.username)
    if err:
        return ApiResponse(code=BIZ_CODE["USERNAME_INVALID"], message=err)

    err = validate_password(payload.password)
    if err:
        return ApiResponse(code=BIZ_CODE["PASSWORD_INVALID"], message=err)

    # 2. 用户是否存在
    user = get_user_by_username(db, payload.username)
    if not user:
        # 出于安全考虑，真实后端通常不区分「用户不存在」与「密码错误」
        # 这里为便于联调区分两种场景，分别返回明确文案
        return ApiResponse(code=BIZ_CODE["USER_NOT_FOUND"], message="用户名不存在")

    # 3. 校验密码
    if not verify_password(payload.password, user.password_hash):
        return ApiResponse(code=BIZ_CODE["PASSWORD_INCORRECT"], message="用户名或密码错误")

    # 4. 签发 JWT
    token = create_access_token(str(user.id))
    return ApiResponse(
        code=0,
        message="登录成功",
        data={
            "token": token,
            "userInfo": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
        },
    )


@router.post("/register", response_model=ApiResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    # 1. 入参格式校验
    err = validate_username(payload.username)
    if err:
        return ApiResponse(code=BIZ_CODE["USERNAME_INVALID"], message=err)

    err = validate_email(payload.email)
    if err:
        return ApiResponse(code=BIZ_CODE["EMAIL_INVALID"], message=err)

    err = validate_password(payload.password)
    if err:
        return ApiResponse(code=BIZ_CODE["PASSWORD_INVALID"], message=err)

    if payload.password != payload.confirmPassword:
        return ApiResponse(code=BIZ_CODE["PASSWORD_NOT_MATCH"], message="两次输入的密码不一致")

    # 2. 用户名 / 邮箱查重
    if get_user_by_username(db, payload.username):
        return ApiResponse(code=BIZ_CODE["USERNAME_EXISTS"], message="用户名已存在")
    if get_user_by_email(db, payload.email):
        return ApiResponse(code=BIZ_CODE["EMAIL_EXISTS"], message="邮箱已被注册")

    # 3. 写入数据库
    user = create_user(db, payload.username, payload.password, payload.email)
    return ApiResponse(
        code=0,
        message="注册成功",
        data={"id": user.id, "username": user.username},
    )
