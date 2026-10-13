# 任务看板（Kanban）功能实现计划

## Context（背景）

用户希望新增看板功能，经讨论确认为**拖拽式任务看板**：Todo 数据模型新增三态 `status`（`todo`/`doing`/`done`）**替代 `completed` 布尔列**（单一数据源）；新增 `/kanban` 独立页面（固定三列 + HTML5 原生拖拽，零依赖）；`/todo` 列表页保留并存，勾选逻辑适配 status；home 统计取值同步改造。

已确认决策：status 替代 completed ｜ 两页并存 ｜ 固定三列 ｜ 原生 HTML5 DnD。
存量数据已确认：todos 表 3 条记录全部 `completed=0`，迁移后均为 `todo`，无冲突。

## 一、后端改动

### 1. models.py — Todo 模型
- 新增 `status = Column(String(10), nullable=False, default="todo")`
- `completed` 列**保留声明**但全链路停止读写（模型删除该列会导致 INSERT 违反 NOT NULL——原表无 SQL DEFAULT，Python 侧 default 在补；SQLite 删列收益低风险高）
- `to_dict()`：移除 `completed`，新增 `status`

### 2. 迁移脚本 backend/scripts/migrate_todo_status.py（一次性，幂等）
- PRAGMA 判断是否已加列；执行：
  - `ALTER TABLE todos ADD COLUMN status VARCHAR(10) NOT NULL DEFAULT 'todo'`
  - `UPDATE todos SET status='done' WHERE completed=1`
- 无需新索引（沿用 ix_todos_user_created）

### 3. validators.py
- `BIZ_CODE` 新增 `TODO_STATUS_INVALID: 40007`
- `validate_todo_status(status)`：白名单 `todo/doing/done`，返回错误文案或空串

### 4. schemas.py
- `TodoUpdateRequest`：加 `status: str | None`，**删除 `completed` 字段**（前后端同步上线，无第三方调用方）
- `TodoCreateRequest`：加可选 `status`（默认 "todo"），支持看板列内新增直接落列

### 5. crud.py / routers/todo.py
- `crud.create_todo` 加 `status="todo"` 参数
- `crud.update_todo` 保持现状（None 检查逻辑对 status 适用）
- PUT 路由：`payload.status is not None` 时先 `validate_todo_status`（非法返回 40007），通过后并入 fields；`completed` 相关逻辑移除
- POST 路由：`payload.status` 传入时同样校验

## 二、前端改动

### 6. 新建 src/views/kanban.vue
- **数据**：单数组 `todoList` 一次拉取，computed 按 `todo/doing/done` 分组为三列（key/title/count/list），列内按 `createdAt` 排序（不做列内排序持久化）
- **布局**：`grid-template-columns: repeat(auto-fit, minmax(260px, 1fr))` 三列，列卡片容器 min-height + 空列占位文案
- **原生 DnD**：
  - 卡片 `draggable`；`@dragstart`：`dataTransfer.setData('text/plain', id)` + `effectAllowed='move'` + 记录拖拽 id + `.dragging` 半透明样式
  - 列容器 `@dragover.prevent`（必须，否则 drop 不触发）+ 悬停列高亮；`@drop`：取 id，同列 drop 直接 return
  - **乐观更新**：本地先改 status → `updateTodoApi(id, {status})` → 失败回滚原值 + ElMessage.error
- **列内新增**：列头"+"展开内联输入框，回车 `createTodoApi({title, status: colKey})`
- **卡片**：悬停显示操作按钮（复用 notes.vue 的 opacity + `@media (hover: none)` 模式）；编辑弹窗（title/note）复用 todo.vue 方案；删除复用 el-popconfirm
- 外壳样式与 todo.vue 一致（max-width 900px el-card）

### 7. src/views/todo.vue — 适配 status
- checkbox：`:model-value="todo.status === 'done'"`，`handleToggle` 改调 `{status: val ? 'done' : 'todo'}`（doing 取消勾选天然落回 todo）
- 划线/置灰 class 判断改用 `todo.status === 'done'`

### 8. src/views/home.vue — 统计适配
- `stats` 中 `t.completed` → `t.status === 'done'`，pending → `t.status !== 'done'`

### 9. src/api/todo.js
- BIZ_CODE 加 `TODO_STATUS_INVALID: 40007`；注释更新（`{title?, note?, status?}`）

### 10. src/router/index.js + src/layout/AppSidebar.vue
- `/` children 加 `{ path: 'kanban', name: 'Kanban', meta: { title: '任务看板' } }`
- 侧边栏菜单加"任务看板"项（Grid 图标，index="/kanban"）

### 11. 文档
- 本计划移入 `docs/kanban-feature-plan.md`；[README.md](file:///f:/code/flowdesk/README.md) 功能一览、[HANDBOOK.md](file:///f:/code/flowdesk/docs/HANDBOOK.md) §1 功能表 / §5 导航 / §6 接口清单（TodoUpdateRequest 变更）同步更新

## 三、文件清单

| 操作 | 文件 |
|---|---|
| 新增 | src/views/kanban.vue、backend/scripts/migrate_todo_status.py、docs/kanban-feature-plan.md |
| 修改 | backend：models.py、schemas.py、validators.py、crud.py、routers/todo.py；前端：api/todo.js、views/todo.vue、views/home.vue、router/index.js、layout/AppSidebar.vue、docs/HANDBOOK.md、README.md |

## 四、验证步骤

1. 停后端 → 跑迁移脚本（幂等）→ 重启；`PRAGMA table_info(todos)` 确认 status 列，3 条存量均为 'todo'，数据完好
2. 接口：PUT 合法 status 生效；PUT `status:"xxx"` → `code=40007`；POST 带 status 落对应列；未登录 → 40100
3. 看板页：跨列拖拽刷新后仍在目标列；同列 drop 无副作用；三列"新增"入口均可用；编辑/删除正常
4. /todo 勾选 → done（划线），取消 → todo；home 统计与状态一致
5. 第二账号隔离 + `npm run build` 编译通过 + 浏览器端到端走查

## 五、决策记录

- 2026-10-11：功能上线，验证 8/8 通过（含迁移、接口、拖拽、两页联动）。
- 2026-10-11：**看板视觉美化（方案二·标准美化）落地**，改动仅 `kanban.vue` 样式与列头结构：
  - 三列主题色头部：图标（Clock/Loading/CircleCheck）+ 主色 + 浅底，沿用 Element Plus 语义色系（info 灰 / warning 琥珀 / success 绿），计数徽章同色
  - 卡片左缘 3px 状态色条；完成列卡片整体灰化弱化
  - 动效：hover 上浮、拖拽倾斜 ghost（rotate 2° + 深阴影）、拖入列实线高亮 + 内阴影、卡片 150ms 进场淡入（遵循 prefers-reduced-motion）
  - 未采纳（方案三）：列内插入位置指示线、列筛选/收起——待列内排序持久化需求出现后再评估
