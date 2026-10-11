# 日程日历功能规格文档

> 上线时间：2026-10-11
> 关联：[dashboard-menu-plan.md](./dashboard-menu-plan.md)（仪表盘"今日日程"数据源）

## 一、背景

工作台首个业务模块：与待办形成"今天要干什么"的完整视图。日程提醒机制后置（仅预留）。

## 二、数据模型（models.py Schedule）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer PK | |
| user_id | FK users.id | 数据隔离 |
| title | String(100) | 必填 |
| date | String(10) | 'YYYY-MM-DD'；**决策：字符串存储**，字典序即时间序支持范围过滤，且与 el-calendar 的 `data.day` 格式天然对齐 |
| start / end | String(5) | 'HH:MM'，全天日程为空 |
| all_day | Boolean | 默认 false |
| note | String(500) | |
| created_at | DateTime | |

索引：`ix_schedules_user_date(user_id, date)`。全新表由 create_all 自动创建，**无需迁移脚本**。

## 三、API（prefix /api/schedule，HTTP 恒 200）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /list?start=&end= | 可选月范围过滤（YYYY-MM-DD），日期升序 + start 升序 |
| POST | | `{title, date, start?, end?, allDay?, note?}` |
| PUT | /{id} | 可选字段部分更新；allDay=true 时置空 start/end |
| DELETE | /{id} | |

错误码：`SCHEDULE_TITLE_INVALID: 40008`、`SCHEDULE_DATE_INVALID: 40009`（格式/日期不存在/end<start）、`SCHEDULE_NOT_FOUND: 40404`（含非本人防泄露）。

## 四、前端（/schedule 页）

- 左 `el-calendar` 月视图 + 右当日列表卡（窄屏纵向堆叠）
- 月历 `#date-cell` 插槽：按 `data.day` 分桶显示日程圆点（时段=蓝、全天=绿），>3 条显示 "+n"
- 月份切换（watch monthKey）按范围拉取当月日程；当月缓存支撑增删改的即时更新（跨月变更直接移除/不插入）
- 新增/编辑共用 el-dialog：标题（聚焦）、日期选择器、全天开关（开启禁用时间选择）、el-time-select 起止（end 限 min-time）、备注；删除走 el-popconfirm

## 五、验证记录

- 接口：非法日期 40009、end<start 40009、全天创建 start/end 置空、范围过滤、未登录 40100 全通过
- 浏览器走查：日历圆点、当日列表联动、新增/编辑/删除、跨月与刷新持久化全通过
