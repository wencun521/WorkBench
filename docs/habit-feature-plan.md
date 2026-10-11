# 习惯打卡功能规格文档

> 上线时间：2026-10-11
> 关联：[pomodoro-feature-plan.md](./pomodoro-feature-plan.md)（同期上线，仪表盘同批扩展）

## 一、背景

工作台第二批模块。目标：轻量习惯追踪——今日打卡 + 连续天数激励 + 近 7 天回顾。月历热图未采纳（页面过重，留待后续评估）。

## 二、数据模型（models.py）

| 表 | 字段 |
|---|---|
| habits | id、user_id(FK)、name String(50)、color String(10) 默认 'blue'、created_at |
| habit_checkins | id、habit_id(FK)、user_id(FK)、date String(10) 'YYYY-MM-DD'、created_at |

约束：`uq_habit_checkin_habit_date`（habit_id+date 唯一，防重复打卡）；索引 `ix_habit_checkins_user_date`。全新表 create_all 自动创建。

## 三、API（prefix /api/habit，HTTP 恒 200）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /list | 返回 `[{...habit, todayChecked, streak, last7: [{date,checked}] ≤7}]` |
| POST | | `{name, color?}` |
| PUT | /{id} | `{name?, color?}` |
| DELETE | /{id} | 显式先删该习惯全部打卡记录 |
| POST | /{id}/checkin | 今日打卡，**幂等**（已打卡返回"今日已打卡"） |
| DELETE | /{id}/checkin | 取消今日打卡 |

错误码：`HABIT_NAME_INVALID: 40010`（非空 ≤50）、`HABIT_COLOR_INVALID: 40011`（色板复用便签 4 色）、`HABIT_NOT_FOUND: 40405`（含非本人防泄露）。

**关键决策：streak 后端计算**（前端只展示）。规则：今日已打卡从今日回数，未打卡从昨日回数（一日未打不清零历史连续）。好处：与仪表盘"今日 x/y"单一口径，避免双端口径漂移。

## 四、前端（/habits 页）

- 每行：色点 + 名称 + streak 徽章（"连续 n 天"，0 天不显示）+ 近 7 天圆点网格（打卡=习惯色，未打=灰）+ 今日打卡按钮（打卡后变绿色"已打卡"）+ 悬停显编辑/删除
- 新增/编辑 el-dialog：名称（≤50 聚焦）+ 4 色圆点选择
- 交互约定：打卡/取消直接用后端返回的摘要替换本行（单数据源）

## 五、验证记录

- 接口：打卡/取消/幂等、非法名 40010、非法色 40011、非本人 40405、last7 结构全通过
- 浏览器走查：打卡按钮态切换、streak 徽章、7 天圆点变绿、增改、首页入口卡"今日 x/y"全通过
