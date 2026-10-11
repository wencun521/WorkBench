# 番茄钟功能规格文档

> 上线时间：2026-10-11
> 关联：[habit-feature-plan.md](./habit-feature-plan.md)（同期上线，仪表盘同批扩展）

## 一、背景

工作台第二批模块。专注倒计时 + 会话留痕，专注时长统计反哺工作概览。决策：
- 时长**固定 25/5 分钟**（后端写死，不开放配置——配置化需存储+UI，收益低后置）
- 休息会话不入库；只有专注会话落库
- 完成提示用 **WebAudio 蜂鸣**（零依赖、无音频文件、无需系统授权）

## 二、数据模型（models.py PomodoroSession）

id、user_id(FK)、todo_id(FK todos.id, **nullable**)、**todo_title String(100) 快照列**、duration_minutes、date String(10) 'YYYY-MM-DD'、created_at。索引 `ix_pomodoro_sessions_user_date`。

**关键决策：todo_title 快照 + 删除时解关联**——`crud.delete_todo` 显式 `UPDATE pomodoro_sessions SET todo_id=NULL`（不依赖 DB 级联），历史记录保留标题可读、列表免 join。

## 三、API（prefix /api/pomodoro，HTTP 恒 200）

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /sessions | `{todoId?}`；duration 后端写死 25；todoId 传了校验本人（失败复用 TODO_NOT_FOUND: 40402，不新增码） |
| GET | /summary | `{todayCount, recent ≤10}`（页面初始化单请求） |

## 四、前端（/pomodoro 页）

- 左：模式切换（专注蓝/休息绿胶囊）+ SVG 圆环倒计时（stroke-dashoffset 绑剩余比例，`remainingSeconds` ref + setInterval 1s，onUnmounted 清理）+ 开始/暂停/重置
- 完成流程：停表 → beep → 专注模式调保存（失败 ElMessage.error 且本地计数不增）→ 自动切另一模式
- 关联待办：el-select（clearable），选项来自 listTodoApi 且过滤掉 done；仅专注模式显示
- 右：专注记录卡（今日计数 + 最近 ≤10 条：todo_title 或"自由专注" + 时长）

## 五、验证记录

- 接口：带/不带 todoId 保存、假 todoId 40402、todayCount 递增、删关联待办后快照保留且 todo_id 置空、dashboard pomodoro.todayCount 全通过
- 浏览器走查：圆环倒数/暂停定格/重置、模式切换配色、今日计数与记录列表全通过（25 分钟完整会话未等待，保存链路由接口测试覆盖）

## 六、决策记录

- 2026-10-11：上线。
- 2026-10-11：**修复计时状态丢失缺陷**——原实现状态在组件内，切换页面（组件卸载）或切换模式即重置。重构为模块级单例组合式函数 [usePomodoro.js](../src/composables/usePomodoro.js)：
  - 状态提升到模块作用域：切页后倒计时继续，返回页面不重置
  - **专注/休息各自保留剩余时间**，来回切换不丢进度（不重置）
  - 完成一个阶段自动开始下一阶段（蜂鸣 + 入库后自动衔接）
  - localStorage 持久化（每次 tick 写入 mode/双模式剩余/running/时间戳）：刷新后按墙钟折算恢复；**恢复为暂停态**，离开期间走完的会话不补录（已知取舍）
  - 浏览器回归 6/6 通过（切页续走、暂停保持、双模式进度独立、F5 折算恢复、无控制台报错）
- 2026-10-11：**交互修正——切模式即停表**。原行为：运行中点休息/专注标签会无缝起跑新模式（"查看"被当成"开始"，时间无感流逝）。修正为 switchMode 时停止计时、恢复为暂停态（各模式剩余时间仍保留，需手动点开始）。浏览器回归 5/5 通过（运行中切换→暂停态且数字不流逝、双模式进度保留、切页不停表未受影响）。
