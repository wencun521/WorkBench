"""
待办事项路由：列表 / 新增 / 编辑 / 删除

统一响应格式：{ code: 0, message, data }
业务错误通过 code != 0 表达，HTTP 状态码保持 200。
所有接口均需登录（Depends(get_current_user)），且只能操作本人数据。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import TodoCreateRequest, TodoUpdateRequest, ApiResponse
from ..crud import create_todo, list_todos, get_todo_by_id, update_todo, delete_todo
from ..deps import get_current_user
from ..models import User
from ..validators import BIZ_CODE, validate_todo_title, validate_todo_status

router = APIRouter(prefix="/api/todo", tags=["todo"])


@router.get("/list", response_model=ApiResponse)
def get_todo_list(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    todos = list_todos(db, current_user.id)
    return ApiResponse(code=0, message="OK", data={"list": [t.to_dict() for t in todos]})


@router.post("", response_model=ApiResponse)
def add_todo(
    payload: TodoCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    err = validate_todo_title(payload.title)
    if err:
        return ApiResponse(code=BIZ_CODE["TODO_TITLE_INVALID"], message=err)

    err = validate_todo_status(payload.status)
    if err:
        return ApiResponse(code=BIZ_CODE["TODO_STATUS_INVALID"], message=err)

    todo = create_todo(db, current_user.id, payload.title.strip(), payload.note.strip(), payload.status)
    return ApiResponse(code=0, message="新增成功", data=todo.to_dict())


@router.put("/{todo_id}", response_model=ApiResponse)
def edit_todo(
    todo_id: int,
    payload: TodoUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # title 传了才校验
    if payload.title is not None:
        err = validate_todo_title(payload.title)
        if err:
            return ApiResponse(code=BIZ_CODE["TODO_TITLE_INVALID"], message=err)

    # status 传了才校验
    if payload.status is not None:
        err = validate_todo_status(payload.status)
        if err:
            return ApiResponse(code=BIZ_CODE["TODO_STATUS_INVALID"], message=err)

    todo = get_todo_by_id(db, current_user.id, todo_id)
    if not todo:
        return ApiResponse(code=BIZ_CODE["TODO_NOT_FOUND"], message="待办不存在")

    fields = {}
    if payload.title is not None:
        fields["title"] = payload.title.strip()
    if payload.note is not None:
        fields["note"] = payload.note.strip()
    if payload.status is not None:
        fields["status"] = payload.status

    todo = update_todo(db, todo, **fields)
    return ApiResponse(code=0, message="更新成功", data=todo.to_dict())


@router.delete("/{todo_id}", response_model=ApiResponse)
def remove_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    todo = get_todo_by_id(db, current_user.id, todo_id)
    if not todo:
        return ApiResponse(code=BIZ_CODE["TODO_NOT_FOUND"], message="待办不存在")

    delete_todo(db, todo)
    return ApiResponse(code=0, message="删除成功", data=None)
