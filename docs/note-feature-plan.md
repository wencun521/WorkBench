# 便签（Note）功能实现计划

## Summary（摘要）

新增便签功能：独立 `/notes` 页面（侧边栏加菜单入口），便签字段为**内容 + 颜色（黄/蓝/绿/粉）+ 置顶标记**，支持基础 CRUD（创建/列表/编辑/删除/置顶切换）。完全复用 todo 的既有模式：后端"HTTP 200 + code 业务码"、get_current_user 认证、本人数据隔离；前端 api 模块 + 组合式函数 + Element Plus 卡片网格。

## Current State（现状）

- 后端已有完整可复制模板：[models.py](file:///f:/code/flowdesk/backend/app/models.py)（Todo 模型）、[crud.py](file:///f:/code/flowdesk/backend/app/crud.py)、[routers/todo.py](file:///f:/code/flowdesk/backend/app/routers/todo.py)、[deps.py](file:///f:/code/flowdesk/backend/app/deps.py)（get_current_user）、[validators.py](file:///f:/code/flowdesk/backend/app/validators.py)（BIZ_CODE）
- 前端已有：[api/todo.js](file:///f:/code/flowdesk/src/api/todo.js) 模式、[views/todo.vue](file:///f:/code/flowdesk/src/views/todo.vue) 页面模式、[composables/useAuth.js](file:///f:/code/flowdesk/src/composables/useAuth.js)（useUnauthorizedHandler）、嵌套路由 [router/index.js](file:///f:/code/flowdesk/src/router/index.js)、[AppSidebar.vue](file:///f:/code/flowdesk/src/layout/AppSidebar.vue)（el-menu 路由模式）
- 无迁移机制，create_all 自动建新表
- BIZ_CODE 已占用：40001~40005、40100、40101、40401、40402、40901、40902

## 已确认决策

1. 入口形态：独立页面 `/notes` + 侧边栏菜单项（不用抽屉）
2. 字段：内容（必填，≤500 字）+ 颜色 + 置顶标记
3. 操作：创建 / 列表 / 编辑（内容、颜色）/ 删除 / 置顶切换

## Proposed Changes（改动清单）

### 后端（6 个文件）

**1. models.py — 新增 Note 模型**
- 字段：`id`、`user_id`(FK users.id, not null)、`content`(String(500), not null)、`color`(String(10), default "yellow")、`pinned`(Boolean, default False)、`created_at`(DateTime, default utcnow)
- 索引：`Index("ix_notes_user_created", "user_id", "created_at")`
- `to_dict()` 输出 camelCase：`{id, content, color, pinned, createdAt}`

**2. validators.py — 错误码与校验**
- BIZ_CODE 新增：`NOTE_CONTENT_INVALID: 40006`、`NOTE_NOT_FOUND: 40403`
- `validate_note_content(content)`：非空、去空格后 ≤500 字
- `NOTE_COLORS = ("yellow", "blue", "green", "pink")` 常量供路由校验颜色合法性

**3. schemas.py** — `NoteCreateRequest{content, color?}`、`NoteUpdateRequest{content?, color?, pinned?}`

**4. crud.py** — `create_note / list_notes / get_note_by_id / update_note / delete_note`，风格同 todo
- `list_notes` 排序：`pinned DESC, created_at DESC`（置顶在前，其余按时间倒序）

**5. 新建 routers/note.py** — prefix="/api/note"，完全复刻 todo.py 结构
- `GET /list` → `{list: [...]}`；`POST ""`；`PUT /{note_id}`；`DELETE /{note_id}`
- 全部 `Depends(get_current_user)`，查询强制 user_id 隔离，不存在/非本人统一 `NOTE_NOT_FOUND`
- 创建/编辑时校验 content 与 color（color 不在 NOTE_COLORS 内按非法处理）

**6. main.py + routers/__init__.py** — 注册 Note 模型、include note_router

### 前端（5 个文件）

**7. 新建 src/api/note.js** — BIZ_CODE（40100/40006/40403 对齐）+ `listNotesApi / createNoteApi / updateNoteApi / deleteNoteApi`，模式同 todo.js

**8. 新建 src/views/notes.vue** — 页面主体
- 外壳同 todo.vue（max-width 900px 居中卡片）
- 卡片头部："便签"标题 + "新建便签"按钮
- 列表：`el-row/el-col` 两列网格（或 CSS grid），每张便签 `el-card`，背景色映射：yellow→#fff8d6 / blue→#d6e8ff / green→#d9f2e3 / pink→#ffe3ec，置顶便签右上角显示图钉图标（深色）
- 单卡操作：置顶/取消置顶（图钉 icon 按钮）、编辑、删除（el-popconfirm）
- 新建/编辑共用 el-dialog：textarea（≤500，show-word-limit）+ 4 个颜色色块单选（选中描边）
- 置顶的便签排前面（后端已排序，前端直接渲染）
- 40100 → `useUnauthorizedHandler`；空列表 `el-empty`

**9. router/index.js** — `/` children 加 `{ path: 'notes', name: 'Notes', meta: { title: '便签' } }`

**10. AppSidebar.vue** — el-menu 加"便签"项：index="/notes"，图标 `Memo`（@element-plus/icons-vue 自带）

**11. src/views/home.vue 不动**（不加便签统计，非本次需求）

### 不改动
- App.vue、global.css、utils/auth.js、deps.py、composables、request.js

## Assumptions & Decisions（假设与决策）

- 颜色用固定 4 色白名单（前后端一致），不做自由取色器
- 置顶排序由后端完成（pinned DESC + created_at DESC），前端不做排序逻辑
- 无 updated_at 字段（基础版不展示"最后编辑时间"）
- 便签无标题字段，仅正文（与"随手记录文字"的定位一致）

## Verification（验证）

1. 重启后端（自动建 notes 表），`npm run build` 编译通过
2. 登录 → 侧边栏出现"便签"菜单 → 点击进入 /notes
3. 新建：空内容报错（40006 文案）；选色创建 → 卡片颜色正确、显示创建时间
4. 编辑改内容/换色 → 生效；置顶 → 卡片移到最前且图钉显示；取消置顶恢复
5. 删除（有二次确认）→ 列表移除；刷新页面数据持久
6. 第二个账号登录看不到对方便签；无 token 请求 `/api/note/list` 返回 code=40100
7. 浏览器端到端走查（登录→新建→置顶→编辑→删除→退出）
