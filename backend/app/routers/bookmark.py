"""
书签收藏路由：列表 / 新增 / 编辑 / 删除

统一响应格式：{ code: 0, message, data }
业务错误通过 code != 0 表达，HTTP 状态码保持 200。
所有接口均需登录，且只能操作本人数据。列表一次拉全，搜索/分类筛选由前端过滤。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import BookmarkCreateRequest, BookmarkUpdateRequest, ApiResponse
from ..crud import (
    create_bookmark,
    list_bookmarks,
    get_bookmark_by_id,
    update_bookmark,
    delete_bookmark,
)
from ..deps import get_current_user
from ..models import User
from ..validators import (
    BIZ_CODE,
    validate_bookmark_url,
    validate_bookmark_title,
    validate_bookmark_note,
)

router = APIRouter(prefix="/api/bookmark", tags=["bookmark"])

CATEGORY_MAX = 50


@router.get("/list", response_model=ApiResponse)
def get_bookmark_list(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bookmarks = list_bookmarks(db, current_user.id)
    return ApiResponse(code=0, message="OK", data={"list": [b.to_dict() for b in bookmarks]})


@router.post("", response_model=ApiResponse)
def add_bookmark(
    payload: BookmarkCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    err = validate_bookmark_url(payload.url)
    if err:
        return ApiResponse(code=BIZ_CODE["BOOKMARK_URL_INVALID"], message=err)
    err = validate_bookmark_title(payload.title)
    if err:
        return ApiResponse(code=BIZ_CODE["BOOKMARK_TITLE_INVALID"], message=err)
    err = validate_bookmark_note(payload.note)
    if err:
        return ApiResponse(code=BIZ_CODE["BOOKMARK_TITLE_INVALID"], message=err)
    if len(payload.category.strip()) > CATEGORY_MAX:
        return ApiResponse(code=BIZ_CODE["BOOKMARK_TITLE_INVALID"], message="分类名不能超过 50 个字符")

    bookmark = create_bookmark(
        db,
        current_user.id,
        payload.url.strip(),
        payload.title.strip() if payload.title and payload.title.strip() else None,
        payload.category.strip() or "未分类",
        payload.note.strip() if payload.note and payload.note.strip() else None,
    )
    return ApiResponse(code=0, message="新增成功", data=bookmark.to_dict())


@router.put("/{bookmark_id}", response_model=ApiResponse)
def edit_bookmark(
    bookmark_id: int,
    payload: BookmarkUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.url is not None:
        err = validate_bookmark_url(payload.url)
        if err:
            return ApiResponse(code=BIZ_CODE["BOOKMARK_URL_INVALID"], message=err)
    if payload.title is not None:
        err = validate_bookmark_title(payload.title)
        if err:
            return ApiResponse(code=BIZ_CODE["BOOKMARK_TITLE_INVALID"], message=err)
    if payload.note is not None:
        err = validate_bookmark_note(payload.note)
        if err:
            return ApiResponse(code=BIZ_CODE["BOOKMARK_TITLE_INVALID"], message=err)
    if payload.category is not None and len(payload.category.strip()) > CATEGORY_MAX:
        return ApiResponse(code=BIZ_CODE["BOOKMARK_TITLE_INVALID"], message="分类名不能超过 50 个字符")

    bookmark = get_bookmark_by_id(db, current_user.id, bookmark_id)
    if not bookmark:
        return ApiResponse(code=BIZ_CODE["BOOKMARK_NOT_FOUND"], message="书签不存在")

    fields = {}
    if payload.url is not None:
        fields["url"] = payload.url.strip()
    if payload.title is not None:
        fields["title"] = payload.title.strip() or None
    if payload.category is not None:
        fields["category"] = payload.category.strip() or "未分类"
    if payload.note is not None:
        fields["note"] = payload.note.strip() or None

    bookmark = update_bookmark(db, bookmark, **fields)
    return ApiResponse(code=0, message="更新成功", data=bookmark.to_dict())


@router.delete("/{bookmark_id}", response_model=ApiResponse)
def remove_bookmark(
    bookmark_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookmark = get_bookmark_by_id(db, current_user.id, bookmark_id)
    if not bookmark:
        return ApiResponse(code=BIZ_CODE["BOOKMARK_NOT_FOUND"], message="书签不存在")

    delete_bookmark(db, bookmark)
    return ApiResponse(code=0, message="删除成功", data=None)
