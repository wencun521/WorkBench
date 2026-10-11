"""
便签路由：列表 / 新增 / 编辑 / 删除 / 置顶

统一响应格式：{ code: 0, message, data }
业务错误通过 code != 0 表达，HTTP 状态码保持 200。
所有接口均需登录（Depends(get_current_user)），且只能操作本人数据。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import NoteCreateRequest, NoteUpdateRequest, ApiResponse
from ..crud import create_note, list_notes, get_note_by_id, update_note, delete_note
from ..deps import get_current_user
from ..models import User
from ..validators import BIZ_CODE, NOTE_COLORS, validate_note_content

router = APIRouter(prefix="/api/note", tags=["note"])


@router.get("/list", response_model=ApiResponse)
def get_note_list(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notes = list_notes(db, current_user.id)
    return ApiResponse(code=0, message="OK", data={"list": [n.to_dict() for n in notes]})


@router.post("", response_model=ApiResponse)
def add_note(
    payload: NoteCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    err = validate_note_content(payload.content)
    if err:
        return ApiResponse(code=BIZ_CODE["NOTE_CONTENT_INVALID"], message=err)

    color = payload.color if payload.color in NOTE_COLORS else "yellow"
    note = create_note(db, current_user.id, payload.content.strip(), color)
    return ApiResponse(code=0, message="新增成功", data=note.to_dict())


@router.put("/{note_id}", response_model=ApiResponse)
def edit_note(
    note_id: int,
    payload: NoteUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # content 传了才校验
    if payload.content is not None:
        err = validate_note_content(payload.content)
        if err:
            return ApiResponse(code=BIZ_CODE["NOTE_CONTENT_INVALID"], message=err)

    # color 传了才校验
    if payload.color is not None and payload.color not in NOTE_COLORS:
        return ApiResponse(code=BIZ_CODE["NOTE_CONTENT_INVALID"], message="便签颜色不合法")

    note = get_note_by_id(db, current_user.id, note_id)
    if not note:
        return ApiResponse(code=BIZ_CODE["NOTE_NOT_FOUND"], message="便签不存在")

    # 只收集显式传入的字段（update_note 按 key 判断是否刷新 updated_at）
    fields = {}
    if payload.content is not None:
        fields["content"] = payload.content.strip()
    if payload.color is not None:
        fields["color"] = payload.color
    if payload.pinned is not None:
        fields["pinned"] = payload.pinned

    note = update_note(db, note, **fields)
    return ApiResponse(code=0, message="更新成功", data=note.to_dict())


@router.delete("/{note_id}", response_model=ApiResponse)
def remove_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = get_note_by_id(db, current_user.id, note_id)
    if not note:
        return ApiResponse(code=BIZ_CODE["NOTE_NOT_FOUND"], message="便签不存在")

    delete_note(db, note)
    return ApiResponse(code=0, message="删除成功", data=None)
