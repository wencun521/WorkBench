"""
书签收藏路由：列表 / 新增 / 编辑 / 删除 / 抓取网页标题

统一响应格式：{ code: 0, message, data }
业务错误通过 code != 0 表达，HTTP 状态码保持 200。
所有接口均需登录，且只能操作本人数据。列表一次拉全，搜索/分类筛选由前端过滤。
"""
import html
import re

import httpx
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

# fetch-meta 抓取限制：5 秒超时、最多读取 512KB（够解析 head 即可）
FETCH_TIMEOUT = 5.0
FETCH_MAX_BYTES = 512 * 1024
FETCH_TITLE_MAX = 200

TITLE_PATTERN = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
OG_TITLE_PATTERNS = (
    re.compile(
        r"""<meta[^>]+property=["']og:title["'][^>]*content=["']([^"']*)["']""",
        re.IGNORECASE,
    ),
    re.compile(
        r"""<meta[^>]+content=["']([^"']*)["'][^>]*property=["']og:title["']""",
        re.IGNORECASE,
    ),
)


def _clean_title(raw: str) -> str:
    """去除标签、反转义 HTML 实体、压缩空白并截断。"""
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:FETCH_TITLE_MAX]


def _extract_title(page_text: str) -> str | None:
    """解析优先级：<title> 文本 → <meta property="og:title">。"""
    match = TITLE_PATTERN.search(page_text)
    if match:
        title = _clean_title(match.group(1))
        if title:
            return title
    for pattern in OG_TITLE_PATTERNS:
        match = pattern.search(page_text)
        if match:
            title = _clean_title(match.group(1))
            if title:
                return title
    return None


@router.get("/fetch-meta", response_model=ApiResponse)
def fetch_bookmark_meta(url: str, current_user: User = Depends(get_current_user)):
    """抓取目标网页标题供新增书签预填。

    抓取失败不是业务错误：一律 code=0 + title=null，前端保持域名兜底。
    """
    err = validate_bookmark_url(url)
    if err:
        return ApiResponse(code=BIZ_CODE["BOOKMARK_URL_INVALID"], message=err)

    title = None
    try:
        with httpx.Client(follow_redirects=True, timeout=FETCH_TIMEOUT) as client:
            with client.stream("GET", url.strip()) as resp:
                chunks = []
                total = 0
                for chunk in resp.iter_bytes():
                    chunks.append(chunk)
                    total += len(chunk)
                    if total >= FETCH_MAX_BYTES:
                        break
                body = b"".join(chunks)[:FETCH_MAX_BYTES]
                page_text = body.decode(resp.encoding or "utf-8", errors="replace")
        title = _extract_title(page_text)
    except Exception:
        title = None

    return ApiResponse(code=0, message="OK", data={"title": title})


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
