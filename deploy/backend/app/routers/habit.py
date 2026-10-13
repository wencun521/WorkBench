"""
习惯打卡路由：习惯 CRUD + 每日打卡

统一响应格式：{ code: 0, message, data }
业务错误通过 code != 0 表达，HTTP 状态码保持 200。
所有接口均需登录，且只能操作本人数据。
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import HabitCreateRequest, HabitUpdateRequest, ApiResponse
from ..crud import (
    create_habit,
    list_habits,
    get_habit_by_id,
    update_habit,
    delete_habit,
    get_checkin,
    add_checkin,
    remove_checkin,
)
from ..deps import get_current_user
from ..models import User, Habit
from ..validators import BIZ_CODE, HABIT_COLORS, validate_habit_name

router = APIRouter(prefix="/api/habit", tags=["habit"])

FOCUS_DAYS_MAX = 3650  # streak 回溯上限，防御异常数据


def _today_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")


def _date_offset(date_str: str, days: int) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=days)
    return d.strftime("%Y-%m-%d")


def _habit_summary(db: Session, habit: Habit) -> dict:
    """habit 基础信息 + todayChecked + streak + last7（后端统一口径）。"""
    today = _today_str()
    today_checked = get_checkin(db, habit.id, today) is not None

    # streak：今日已打从今日回数，未打从昨日回数（一日未打卡不清零历史）
    streak = 0
    cursor = today if today_checked else _date_offset(today, -1)
    while streak < FOCUS_DAYS_MAX and get_checkin(db, habit.id, cursor):
        streak += 1
        cursor = _date_offset(cursor, -1)

    # 近 7 天（含今日）
    last7 = []
    for i in range(6, -1, -1):
        d = _date_offset(today, -i)
        last7.append({"date": d, "checked": get_checkin(db, habit.id, d) is not None})

    data = habit.to_dict()
    data.update({"todayChecked": today_checked, "streak": streak, "last7": last7})
    return data


@router.get("/list", response_model=ApiResponse)
def get_habit_list(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    habits = list_habits(db, current_user.id)
    return ApiResponse(code=0, message="OK", data={"list": [_habit_summary(db, h) for h in habits]})


@router.post("", response_model=ApiResponse)
def add_habit(
    payload: HabitCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    err = validate_habit_name(payload.name)
    if err:
        return ApiResponse(code=BIZ_CODE["HABIT_NAME_INVALID"], message=err)
    if payload.color not in HABIT_COLORS:
        return ApiResponse(code=BIZ_CODE["HABIT_COLOR_INVALID"], message="颜色标记不合法")

    habit = create_habit(db, current_user.id, payload.name.strip(), payload.color)
    return ApiResponse(code=0, message="新增成功", data=_habit_summary(db, habit))


@router.put("/{habit_id}", response_model=ApiResponse)
def edit_habit(
    habit_id: int,
    payload: HabitUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.name is not None:
        err = validate_habit_name(payload.name)
        if err:
            return ApiResponse(code=BIZ_CODE["HABIT_NAME_INVALID"], message=err)
    if payload.color is not None and payload.color not in HABIT_COLORS:
        return ApiResponse(code=BIZ_CODE["HABIT_COLOR_INVALID"], message="颜色标记不合法")

    habit = get_habit_by_id(db, current_user.id, habit_id)
    if not habit:
        return ApiResponse(code=BIZ_CODE["HABIT_NOT_FOUND"], message="习惯不存在")

    fields = {}
    if payload.name is not None:
        fields["name"] = payload.name.strip()
    if payload.color is not None:
        fields["color"] = payload.color

    habit = update_habit(db, habit, **fields)
    return ApiResponse(code=0, message="更新成功", data=_habit_summary(db, habit))


@router.delete("/{habit_id}", response_model=ApiResponse)
def remove_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = get_habit_by_id(db, current_user.id, habit_id)
    if not habit:
        return ApiResponse(code=BIZ_CODE["HABIT_NOT_FOUND"], message="习惯不存在")

    delete_habit(db, habit)
    return ApiResponse(code=0, message="删除成功", data=None)


@router.post("/{habit_id}/checkin", response_model=ApiResponse)
def checkin(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = get_habit_by_id(db, current_user.id, habit_id)
    if not habit:
        return ApiResponse(code=BIZ_CODE["HABIT_NOT_FOUND"], message="习惯不存在")

    # 幂等：当天已打卡直接返回当前摘要
    created = add_checkin(db, habit.id, current_user.id, _today_str())
    data = _habit_summary(db, habit)
    return ApiResponse(code=0, message="打卡成功" if created else "今日已打卡", data=data)


@router.delete("/{habit_id}/checkin", response_model=ApiResponse)
def uncheckin(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = get_habit_by_id(db, current_user.id, habit_id)
    if not habit:
        return ApiResponse(code=BIZ_CODE["HABIT_NOT_FOUND"], message="习惯不存在")

    removed = remove_checkin(db, habit.id, _today_str())
    data = _habit_summary(db, habit)
    return ApiResponse(code=0, message="已取消打卡" if removed else "今日未打卡", data=data)
