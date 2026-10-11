# 习惯打卡 + 番茄钟 实现计划

## Context（背景）

工作台第二批模块（延续既有节奏：spec → 实现 → 走查 → 文档）。两个模块均复刻现有全链路模式（router→crud→validators→schemas→前端 api→view→菜单注册→dashboard 扩展）。

已确认决策：
- **习惯打卡**：今日列表 + streak + 近 7 天圆点网格（不做月历热图）；色板复用便签 4 色
- **番茄钟**：专注 25 分钟 / 休息 5 分钟固定时长；专注可关联待办；会话存库；仪表盘展示今日专注数
- 新错误码顺延：`HABIT_NAME_INVALID: 40010`、`HABIT_COLOR_INVALID: 40011`、`HABIT_NOT_FOUND: 40405`

## 一、习惯打卡后端（/api/habit）

### models.py — 两个新模型
- `Habit`：id、user_id(FK)、name String(50)、color String(10) 默认 'blue'（值域=便签 4 色板，后端 `HABIT_COLORS` 常量）、created_at
- `HabitCheckin`：id、habit_id(FK habits.id)、user_id(FK)、date String(10) 'YYYY-MM-DD'、created_at
  - `UniqueConstraint('habit_id','date')` 命名 `uq_habit_checkin_habit_date`；索引 `ix_habit_checkins_user_date(user_id,date)`

### validators.py
- 新码 40010/40011/40405；`HABIT_COLORS = NOTE_COLORS`
- `validate_habit_name`（非空 ≤50）

### crud.py / routers/habit.py
- 习惯 CRUD + `toggle_checkin`（POST 打卡幂等：已存在直接返回成功；DELETE 取消）
- **streak 后端计算**（与 dashboard 口径统一）：今日已打从今日回数，未打从昨日回数；同请求生成 `last7: [{date, checked}]`（含今日）
- `GET /list` 返回 `[{...habit, todayChecked, streak, last7}]`；DELETE 习惯时显式先删其 checkins（不依赖 DB 级联）

## 二、番茄钟后端（/api/pomodoro）

### models.py — PomodoroSession
- id、user_id(FK)、todo_id(FK todos.id, **nullable**)、**todo_title String(100) 快照列**、duration_minutes Integer、date String(10)、created_at；索引 `ix_pomodoro_sessions_user_date`
- todo 删除处理：crud.delete_todo 中显式 `UPDATE ... SET todo_id=NULL`；快照列保证历史可读

### routers/pomodoro.py
- `POST /sessions {todoId?}`：todoId 传了校验本人（失败复用 `TODO_NOT_FOUND: 40402`，不新增码）；duration 后端写死 25（休息不入库）
- `GET /summary` → `{todayCount, recent ≤10 条}`（页面初始化单请求）

### 页面（src/views/pomodoro.vue）
- SVG 圆环倒计时（stroke-dashoffset 绑比例）+ 开始/暂停/重置 + 模式切换（focus/break）
- `remainingSeconds` ref + setInterval 1s，onUnmounted 清理
- 完成流程：停表 → WebAudio 短 beep 提示（零依赖，不用 Notification）→ 保存会话；保存失败 ElMessage.error 且本地计数不增
- 专注完成自动切休息、休息完成切回；关联待办 el-select（clearable，选项来自 listTodoApi）

## 三、习惯打卡前端（src/views/habits.vue）

- 每行：色点 + 习惯名 + 今日打卡按钮（已打卡变实心勾）+ streak 徽章（🔥 n 天样式用文案"连续 n 天"）+ 近 7 天圆点网格
- 习惯增删改：新增/编辑 el-dialog（名称 + 4 色选择），删除 el-popconfirm
- api/habit.js BIZ_CODE 对齐 40010/40011/40405/40100

## 四、dashboard 扩展（两模块后端完成后一次改）

- routers/dashboard.py：`data.habit = {total, doneToday}`、`data.pomodoro = {todayCount}`
- home.vue：加"习惯打卡"（今日 x/y）与"番茄钟"（今日 n 个）两张入口卡

## 五、菜单/路由

- menuConfig.js：task 组加 `{path:'/pomodoro', title:'番茄钟', icon:Timer}`；record 组加 `{path:'/habits', title:'习惯打卡', icon:Finished}`
- router/index.js children 加 `habits`、`pomodoro`

## 六、文档
- docs/habit-feature-plan.md、docs/pomodoro-feature-plan.md；HANDBOOK §1/§5/§6 + README 同步

## 七、文件清单

| 操作 | 文件 |
|---|---|
| 新增 | backend/app/routers/habit.py、pomodoro.py、src/api/habit.js、pomodoro.js、src/views/habits.vue、pomodoro.vue、docs 两份 spec |
| 修改 | models.py、validators.py、schemas.py、crud.py、routers/dashboard.py、routers/__init__.py、main.py、menuConfig.js、router/index.js、home.vue |

## 八、实施顺序

1. 习惯打卡后端全链路（模型→校验→schemas→crud→路由→注册）
2. 番茄钟后端全链路（含 delete_todo 补 SET NULL）
3. dashboard 扩展 + home.vue 加两张入口卡
4. 习惯打卡前端（api/页面/路由/菜单）
5. 番茄钟前端（api/页面/路由/菜单）
6. 文档拆分同步

## 九、验证步骤

1. 重启 uvicorn 确认 habits/habit_checkins/pomodoro_sessions 三表创建；未登录均 40100
2. 习惯：增删改、打卡幂等/取消、streak（造昨日+前日数据验 2→打卡后 3）、非本人 40405、超长名 40010、非法色 40011
3. 番茄：带/不带 todoId 保存、假 todoId 40402、todayCount 递增、删关联 todo 后快照保留且 todo_id 置空
4. dashboard 含 habit/pomodoro 字段
5. `npm run build` + 浏览器走查（圆环倒计时、暂停/重置、响铃入库、7 天圆点、菜单分组渲染新两项）+ 第二账号隔离
