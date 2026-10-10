# 最基础版 Todo 功能实现计划

## Context（背景）

项目（Vue 3 + Element Plus / FastAPI + SQLite）已完成登录注册。本计划开发最基础版 Todo 功能：**独立 /todo 页面，条目字段为标题（必填）+ 备注（可选）+ 完成状态 + 创建时间**，仅本人可见可操作。不做分类/标签/优先级/截止日期/分页。

关键现状（已探明）：
- 后端无 `get_current_user` 依赖（auth.py 仅提供 token 编解码），需新建
- 无迁移机制，`main.py` 启动时 `create_all` 自动建新表
- 统一响应约定：HTTP 恒 200，业务失败 `code != 0`；前端 request.js 拦截器在 `code!==0` 时 reject 并附 `err.code`
- 现有错误码：BIZ_CODE 中 40001~40004、40401、40101、40901、40902 已占用

## 一、后端改动

### 1. models.py — 新增 Todo 模型
- 字段：`id`、`user_id`(Integer, ForeignKey("users.id"), nullable=False)、`title`(String(100), nullable=False)、`note`(String(500), nullable=True, default="")、`completed`(Boolean, default=False)、`created_at`(DateTime, default=datetime.utcnow)
- 复合索引 `Index("ix_todos_user_created", "user_id", "created_at")`
- `to_dict()` 输出 camelCase（`{id, title, note, completed, createdAt: isoformat()}`），与 User.to_dict 风格一致

### 2. validators.py — 新增错误码与校验
- `BIZ_CODE` 新增：`UNAUTHORIZED: 40100`、`TODO_TITLE_INVALID: 40005`、`TODO_NOT_FOUND: 40402`
- 新增 `validate_todo_title(title)`：返回错误文案或空串，规则同 validate_username 风格（非空、长度 ≤ 100）

### 3. 新建 backend/app/deps.py — get_current_user 依赖
- `OAuth2PasswordBearer(tokenUrl="/api/user/login")` 取 Bearer token + `Depends(get_db)` 查 User
- 失败时 raise 自定义 `UnauthorizedError`，在 main.py 注册 `app.exception_handler` 返回 `{code: 40100, message: "未登录或登录已过期", data: null}`（HTTP 200，沿用项目约定，前端拦截器零改动）
- token 的 `sub` 即 user.id

### 4. schemas.py — 新增请求模型
- `TodoCreateRequest{title, note?}`、`TodoUpdateRequest{title?, note?, completed?}`（title 可选字段单独校验）

### 5. crud.py — 新增 CRUD 函数
- `create_todo / list_todos / get_todo_by_id / update_todo / delete_todo`，首参 `db: Session`，风格同现有
- 列表固定 `created_at DESC`

### 6. 新建 backend/app/routers/todo.py — prefix="/api/todo"
- `GET /list` → data: `{list: [...]}`
- `POST /`（TodoCreateRequest）→ data: todo
- `PUT /{todo_id}`（TodoUpdateRequest）→ data: todo
- `DELETE /{todo_id}` → data: null
- 所有路由 `Depends(get_current_user)`，查询强制 `filter(Todo.user_id == 当前用户.id)`；不存在/非本人统一返回 `TODO_NOT_FOUND`（防泄露）
- 错误处理沿用 user.py 模式：`validate_todo_title()` 返回非空即 `ApiResponse(code=..., message=err)`

### 7. main.py / routers/__init__.py
- main.py：import Todo（noqa 注册）、include todo_router、注册 40100 exception handler
- routers/__init__.py：导出 todo_router

## 二、前端改动

### 8. 新建 src/api/todo.js
- 顶部 BIZ_CODE（与后端对齐：40100/40005/40402）
- `listTodoApi / createTodoApi / updateTodoApi / deleteTodoApi`，模式同 user.js

### 9. 新建 src/views/todo.vue
- el-card 容器；顶部 el-input（回车新增）+ el-button primary 新增；空标题 ElMessage.warning
- 列表 v-for：el-checkbox 切换 completed（勾选后标题删除线置灰）；行内 el-button link 编辑/删除
- 编辑用 el-dialog（标题必填、备注 textarea）；删除前 el-popconfirm 二次确认
- 空状态 el-empty
- 页面加载时请求列表；catch `err.code === 40100` 时 removeToken() + 跳 /login

### 10. src/router/index.js / src/views/home.vue
- 新增 `/todo` 路由（lazy import，meta.requiresAuth）
- home.vue 欢迎卡片内加"待办事项"入口按钮/链接

## 三、验证步骤

1. 重启 uvicorn（自动建 todos 表）→ 登录 → home 点入口跳 /todo
2. 新增：空标题提示错误；正常创建显示 createdAt
3. 勾选完成 → 刷新页面状态持久；编辑标题/备注；删除（有二次确认）
4. 注册第二个账号登录，确认看不到第一个账号的 todo
5. `curl localhost:8000/api/todo/list`（无 token）→ 返回 `{code: 40100}`；前端收到 40100 自动跳登录页

## 文件清单

| 操作 | 文件 |
|---|---|
| 新增 | backend/app/deps.py、backend/app/routers/todo.py、src/api/todo.js、src/views/todo.vue |
| 修改 | backend/app/models.py、schemas.py、crud.py、validators.py、main.py、routers/__init__.py、src/router/index.js、src/views/home.vue |
