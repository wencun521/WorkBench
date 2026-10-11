"""
日程路由：列表 / 新增 / 编辑 / 删除

统一响应格式：{ code: 0, message, data }
业务错误通过 code != 0 表达，HTTP 状态码保持 200。
所有接口均需登录（Depends(get_current_user)），且只能操作本人数据。
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import ScheduleCreateRequest, ScheduleUpdateRequest, ApiResponse
from ..crud import create_schedule, list_schedules, get_schedule_by_id, update_schedule, delete_schedule
from ..deps import get_current_user
from ..models import User
from ..validators import BIZ_CODE, validate_schedule_title, validate_schedule_date, validate_schedule_time

router = APIRouter(prefix="/api/schedule", tags=["schedule"])


@router.get("/list", response_model=ApiResponse)
def get_schedule_list(
    start: str | None = Query(None, description="起始日期 YYYY-MM-DD"),
    end: str | None = Query(None, description="结束日期 YYYY-MM-DD"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 范围参数传了才校验
    if start:
        err = validate_schedule_date(start)
        if err:
            return ApiResponse(code=BIZ_CODE["SCHEDULE_DATE_INVALID"], message=err)
    if end:
        err = validate_schedule_date(end)
        if err:
            return ApiResponse(code=BIZ_CODE["SCHEDULE_DATE_INVALID"], message=err)

    schedules = list_schedules(db, current_user.id, start, end)
    return ApiResponse(code=0, message="OK", data={"list": [s.to_dict() for s in schedules]})


@router.post("", response_model=ApiResponse)
def add_schedule(
    payload: ScheduleCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    err = validate_schedule_title(payload.title)
    if err:
        return ApiResponse(code=BIZ_CODE["SCHEDULE_TITLE_INVALID"], message=err)

    err = validate_schedule_date(payload.date)
    if err:
        return ApiResponse(code=BIZ_CODE["SCHEDULE_DATE_INVALID"], message=err)

    # 全天日程忽略时间；非全天才校验时间格式与先后
    start, end = (None, None) if payload.allDay else (payload.start, payload.end)
    if not payload.allDay:
        err = validate_schedule_time(start or "", "开始时间")
        if err:
            return ApiResponse(code=BIZ_CODE["SCHEDULE_DATE_INVALID"], message=err)
        err = validate_schedule_time(end or "", "结束时间")
        if err:
            return ApiResponse(code=BIZ_CODE["SCHEDULE_DATE_INVALID"], message=err)
        if start and end and end < start:
            return ApiResponse(code=BIZ_CODE["SCHEDULE_DATE_INVALID"], message="结束时间不能早于开始时间")

    schedule = create_schedule(
        db, current_user.id, payload.title.strip(), payload.date,
        start, end, payload.allDay, payload.note.strip(),
    )
    return ApiResponse(code=0, message="新增成功", data=schedule.to_dict())


@router.put("/{schedule_id}", response_model=ApiResponse)
def edit_schedule(
    schedule_id: int,
    payload: ScheduleUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 传了才校验
    if payload.title is not None:
        err = validate_schedule_title(payload.title)
        if err:
            return ApiResponse(code=BIZ_CODE["SCHEDULE_TITLE_INVALID"], message=err)
    if payload.date is not None:
        err = validate_schedule_date(payload.date)
        if err:
            return ApiResponse(code=BIZ_CODE["SCHEDULE_DATE_INVALID"], message=err)
    for field_name, value in (("开始时间", payload.start), ("结束时间", payload.end)):
        if value is not None:
            err = validate_schedule_time(value, field_name)
            if err:
                return ApiResponse(code=BIZ_CODE["SCHEDULE_DATE_INVALID"], message=err)

    schedule = get_schedule_by_id(db, current_user.id, schedule_id)
    if not schedule:
        return ApiResponse(code=BIZ_CODE["SCHEDULE_NOT_FOUND"], message="日程不存在")

    # 合并后的时间先后校验（部分更新时与库中现值比较）
    all_day = payload.allDay if payload.allDay is not None else schedule.all_day
    if not all_day:
        start = payload.start if payload.start is not None else schedule.start
        end = payload.end if payload.end is not None else schedule.end
        if start and end and end < start:
            return ApiResponse(code=BIZ_CODE["SCHEDULE_DATE_INVALID"], message="结束时间不能早于开始时间")

    fields = {}
    if payload.title is not None:
        fields["title"] = payload.title.strip()
    if payload.date is not None:
        fields["date"] = payload.date
    if payload.start is not None:
        fields["start"] = payload.start
    if payload.end is not None:
        fields["end"] = payload.end
    if payload.allDay is not None:
        fields["all_day"] = payload.allDay
        if payload.allDay:
            fields["start"] = None
            fields["end"] = None
    if payload.note is not None:
        fields["note"] = payload.note.strip()

    schedule = update_schedule(db, schedule, **fields)
    return ApiResponse(code=0, message="更新成功", data=schedule.to_dict())


@router.delete("/{schedule_id}", response_model=ApiResponse)
def remove_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    schedule = get_schedule_by_id(db, current_user.id, schedule_id)
    if not schedule:
        return ApiResponse(code=BIZ_CODE["SCHEDULE_NOT_FOUND"], message="日程不存在")

    delete_schedule(db, schedule)
    return ApiResponse(code=0, message="删除成功", data=None)
