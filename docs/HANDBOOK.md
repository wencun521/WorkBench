# Admin Pro 项目主文档

> **版本**：0.1.0 ｜ **更新时间**：2026-10-11 ｜ **状态**：活跃开发中
>
> 本文档是整个项目的**核心导航入口**，汇总项目概述、架构说明、目录索引、开发/接口/部署/维护规范，并关联所有子文档。新成员请从本文档开始阅读；新增功能文档时请同步更新 [§5 文档导航](#五文档导航)。入口页为根目录 [README.md](../README.md)。

## 目录

- [一、项目概述与定位](#一项目概述与定位)
- [二、整体架构说明](#二整体架构说明)
- [三、目录结构索引](#三目录结构索引)
- [四、快速开始（开发指南）](#四快速开始开发指南)
- [五、文档导航](#五文档导航)
- [六、接口说明](#六接口说明)
- [七、版本管理规范](#七版本管理规范)
- [八、部署流程](#八部署流程)
- [九、维护手册](#九维护手册)
- [十、问题反馈渠道](#十问题反馈渠道)
- [十一、扩展指南](#十一扩展指南)

---

## 一、项目概述与定位

**Admin Pro** 是一个轻量级全栈后台管理系统，采用「Vue 3 前后端分离 + FastAPI 后端 + SQLite 存储」的技术组合。

**定位**：

- 个人全栈实践项目：完整走通「需求梳理 → 方案设计（spec）→ 编码 → 联调验证 → 文档沉淀」流程
- 可扩展的后台模板：登录认证、布局骨架、业务模块（待办/便签）均已就位，新模块可按既有模式快速复制

**已实现功能**：

| 模块 | 说明 | 上线日期 |
|------|------|----------|
| 用户认证 | 注册 / 登录，JWT（HS256，1 天有效期），bcrypt 密码哈希 | 2026-10-09 前 |
| 待办事项 `/todo` | 增删改查 + 三态状态（todo/doing/done），本人数据隔离 | 2026-10-09 |
| 任务看板 `/kanban` | 三列拖拽看板（原生 HTML5 DnD），与待办共用数据，列内新增/编辑/删除 | 2026-10-11 |
| 日程日历 `/schedule` | 月历 + 当日列表，日程增删改查（全天/时段），本人数据隔离 | 2026-10-11 |
| 习惯打卡 `/habits` | 习惯增删改 + 今日打卡（幂等）+ streak + 近 7 天网格 | 2026-10-11 |
| 番茄钟 `/pomodoro` | 专注/休息双模式倒计时，会话关联待办并留档，今日统计 | 2026-10-11 |
| 聚合仪表盘 `/` | 菜单分组 + 模块入口卡 + 今日概览（`/api/dashboard` 单请求聚合） | 2026-10-11 |
| 侧边栏布局 | 可折叠侧边栏（配置驱动分组菜单）+ 主内容区 | 2026-10-09 |
| 首页统计 | 欢迎卡 + 待办统计（总数/已完成/未完成）+ 最近便签速览 | 2026-10-09 |
| 便签 `/notes` | 增删改查 + 4 色标记 + 置顶，本人数据隔离 | 2026-10-09 |
| 书签收藏 `/bookmarks` | 链接 + 自由分类 + 前端搜索，http/https 协议白名单，本人数据隔离；favicon.im 图标展示（失败回退色块）、fetch-meta 自动抓取网页标题预填 | 2026-10-11 |

## 二、整体架构说明

### 2.1 技术栈

| 层 | 技术 | 版本 | 说明 |
|----|------|------|------|
| 前端框架 | Vue 3（Composition API + `<script setup>`） | ^3.5.10 | 无 pinia，状态局部化 |
| 构建工具 | Vite | ^5.4.8 | dev 端口 5173，`/api` 代理到后端 |
| UI 组件 | Element Plus + icons-vue | ^2.8.4 / ^2.3.1 | 全量引入 |
| 路由 | vue-router 4 | ^4.4.5 | 嵌套路由 + `meta.requiresAuth` 守卫 |
| HTTP | axios | ^1.7.7 | 统一封装 `src/api/request.js` |
| 后端框架 | FastAPI | 最新 | 统一响应 `{code, message, data}` |
| ORM | SQLAlchemy 2.x | 最新 | declarative_base，无 Alembic 迁移 |
| 数据库 | SQLite | 内置 | 文件 `backend/app/app.db` |
| 认证 | python-jose (JWT HS256) + bcrypt | 最新 | token 1 天过期 |
| HTTP 客户端 | httpx | 最新 | 书签 fetch-meta 抓取网页标题（5s 超时 + 512KB 截断） |

### 2.2 架构与请求链路

```
浏览器
  │  http://localhost:5173
  ▼
Vite Dev Server ─── /api 代理 ───► FastAPI (http://127.0.0.1:8000)
  │                                   │
  │  Vue 3 SPA                        ├─ routers/   路由层（校验 + 统一响应）
  │  ├─ views/      页面组件          ├─ crud.py    数据操作层
  │  ├─ api/        接口封装          ├─ models.py  ORM 模型
  │  ├─ layout/     侧边栏布局        ├─ deps.py    get_current_user 认证依赖
  │  ├─ composables/ 组合式函数       ├─ auth.py    JWT 签发/校验、密码哈希
  │  └─ router/     嵌套路由+守卫     ├─ validators.py 业务校验 + 错误码
  │                                   └─ database.py 连接 + get_db 依赖
  ▼                                   ▼
 localStorage(token)            SQLite (backend/app/app.db)
```

### 2.3 核心约定（全项目强制）

1. **统一响应**：HTTP 恒为 200，业务结果由 `code` 表达——`0` 成功，非 0 失败（含未登录 `40100`）
2. **数据隔离**：所有业务查询强制携带 `user_id` 条件，"不存在"与"非本人"返回同一错误码（防泄露）
3. **命名风格**：后端 `to_dict()` 输出 camelCase（`createdAt`），前端直接消费
4. **错误码单一来源**：后端 `validators.py` 的 `BIZ_CODE` ↔ 前端各 api 模块的 `BIZ_CODE`，保持对齐

## 三、目录结构索引

```
f:\code\vu1\
├─ docs/                        # 项目文档（详细导航见本目录 HANDBOOK.md）
│  ├─ HANDBOOK.md               # ★ 项目主文档（核心导航入口）
│  ├─ todo-basic-feature-plan.md       # 待办功能规格
│  ├─ home-sidebar-layout-plan.md      # 侧边栏布局改造规格
│  ├─ note-feature-plan.md             # 便签功能规格
│  └─ notes-optimization.md            # 便签优化建议（待排期）
├─ backend/                     # FastAPI 后端（虚拟环境 backend/.venv 也在此目录）
│  ├─ run.py                    # 启动脚本（uvicorn + reload，端口 8000）
│  ├─ requirements.txt          # Python 依赖
│  └─ app/
│     ├─ main.py                # 应用入口：建表、注册路由、40100 异常处理
│     ├─ database.py            # SQLite 连接 + get_db 依赖
│     ├─ models.py              # ORM 模型（User / Todo / Note）
│     ├─ schemas.py             # Pydantic 请求模型 + ApiResponse
│     ├─ crud.py                # 数据操作层（首参 db: Session）
│     ├─ validators.py          # BIZ_CODE 错误码 + 校验函数
│     ├─ auth.py                # 密码哈希 + JWT 签发/校验
│     ├─ deps.py                # get_current_user 认证依赖
│     ├─ app.db                 # SQLite 数据文件（不入库则 gitignore）
│     └─ routers/               # 路由层
│        ├─ user.py             # /api/user  登录、注册
│        ├─ todo.py             # /api/todo  待办 CRUD
│        └─ note.py             # /api/note  便签 CRUD
├─ frontend/                    # Vue 3 前端
│  ├─ main.js                   # 入口：挂载 App、router、Element Plus
│  ├─ App.vue                   # 根组件（仅 router-view）
│  ├─ router/index.js           # 路由表 + 登录守卫
│  ├─ layout/
│  │  ├─ AdminLayout.vue        # 布局骨架（可折叠侧边栏 + 主区）
│  │  └─ AppSidebar.vue         # 侧边栏（logo/菜单/用户区/折叠）
│  ├─ views/                    # 页面组件
│  │  ├─ login.vue / register.vue / 404.vue
│  │  ├─ home.vue               # 首页（欢迎 + 待办统计）
│  │  ├─ todo.vue               # 待办事项页
│  │  └─ notes.vue              # 便签页
│  ├─ api/                      # 接口封装（每个后端模块一个文件）
│  │  ├─ request.js             # axios 实例：token 注入 + code!==0 拦截
│  │  ├─ user.js / todo.js / note.js
│  ├─ composables/
│  │  └─ useAuth.js             # useLogout / useUnauthorizedHandler
│  ├─ utils/auth.js             # token 存取（localStorage）
│  └─ styles/global.css         # 全局样式（reset + 灰底基调）
├─ frontend/                    # （续）静态资源与构建配置
│  ├─ public/                   # 静态资源（favicon）
│  ├─ index.html                # SPA 入口
│  ├─ vite.config.js            # Vite 配置（/api 代理 → 127.0.0.1:8000）
│  └─ package.json              # 前端依赖与脚本
```

## 四、快速开始（开发指南）

### 4.1 环境要求

- Node.js ≥ 18（含 npm）
- Python ≥ 3.12（项目使用 3.14 + `.venv` 虚拟环境）

### 4.2 启动后端（端口 8000）

```bash
cd backend
# 首次：创建虚拟环境并安装依赖
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
# 启动（自动 create_all 建表；开发模式带热重载）
.venv\Scripts\python run.py
```

验证：访问 `http://127.0.0.1:8000/health` 返回 `{"status":"ok"}`。

### 4.3 启动前端（端口 5173）

```bash
cd frontend
npm install   # 首次
npm run dev   # 开发服务器，/api 自动代理到 8000
```

### 4.4 其他常用命令

| 命令 | 说明 |
|------|------|
| `npm run build` | 产出生产构建到 `frontend/dist/` |
| `npm run preview` | 本地预览构建产物 |

## 五、文档导航

| 文档 | 类型 | 内容概要 |
|------|------|----------|
| [HANDBOOK.md](./HANDBOOK.md) | **主文档** | 本文档：概述/架构/规范/导航 |
| [todo-basic-feature-plan.md](./todo-basic-feature-plan.md) | 功能规格 | 待办事项：数据模型、API 设计、认证依赖方案、验证清单 |
| [home-sidebar-layout-plan.md](./home-sidebar-layout-plan.md) | 功能规格 | 侧边栏布局：Layout 组件拆分、嵌套路由、组合式函数 |
| [dashboard-menu-plan.md](./dashboard-menu-plan.md) | 功能规格 | 工作台地基：菜单分组（menuConfig 配置驱动）、/api/dashboard 聚合仪表盘 |
| [schedule-feature-plan.md](./schedule-feature-plan.md) | 功能规格 | 日程日历：Schedule 模型、el-calendar 月视图、当日列表 |
| [habit-feature-plan.md](./habit-feature-plan.md) | 功能规格 | 习惯打卡：双表模型、streak 后端口径、幂等打卡 |
| [pomodoro-feature-plan.md](./pomodoro-feature-plan.md) | 功能规格 | 番茄钟：会话快照模型、WebAudio 提示、仪表盘集成 |
| [bookmark-feature-plan.md](./bookmark-feature-plan.md) | 功能规格 | 书签收藏：URL 协议白名单校验、自由分类、前端过滤；第六章增强（favicon.im 图标、fetch-meta 标题抓取）已实现 |
| [kanban-feature-plan.md](./kanban-feature-plan.md) | 功能规格 | 任务看板：status 三态改造、迁移脚本、原生拖拽方案 |
| [note-feature-plan.md](./note-feature-plan.md) | 功能规格 | 便签：Note 模型、色板约定、置顶排序方案 |
| [notes-optimization.md](./notes-optimization.md) | 优化清单 | 便签体验优化建议（已全部落地，含决策记录） |

> **维护约定**：新增功能时在 `docs/` 新建 `<feature>-plan.md` 规格文档；上线后在本文档 §1 功能表和 §5 导航表各加一行。

## 六、接口说明

### 6.1 通用约定

- **Base URL**：`/api`（前端 axios baseURL；vite 代理转发）
- **响应格式**：`{ "code": 0, "message": "OK", "data": object | null }`，HTTP 状态码恒为 200
- **认证方式**：请求头 `Authorization: Bearer <token>`；token 由登录接口签发，有效期 1 天
- **未登录/过期**：返回 `code=40100`，前端拦截后清除 token 并跳转登录页

### 6.2 业务错误码表

| 错误码 | 常量名 | 含义 |
|--------|--------|------|
| 0 | - | 成功 |
| 40001 | USERNAME_INVALID | 用户名格式错误（3~20 位，字母/数字/下划线） |
| 40002 | PASSWORD_INVALID | 密码格式错误（6~20 位） |
| 40003 | EMAIL_INVALID | 邮箱格式错误 |
| 40004 | PASSWORD_NOT_MATCH | 两次密码不一致 |
| 40005 | TODO_TITLE_INVALID | 待办标题非法（非空，≤100 字） |
| 40007 | TODO_STATUS_INVALID | 待办状态非法（须为 todo/doing/done） |
| 40008 | SCHEDULE_TITLE_INVALID | 日程标题非法（非空，≤100 字） |
| 40009 | SCHEDULE_DATE_INVALID | 日程日期/时间非法（格式错误、日期不存在、结束早于开始） |
| 40010 | HABIT_NAME_INVALID | 习惯名称非法（非空，≤50 字） |
| 40011 | HABIT_COLOR_INVALID | 习惯颜色非法（须在 4 色白名单内） |
| 40012 | BOOKMARK_TITLE_INVALID | 书签标题/备注/分类非法（超长） |
| 40013 | BOOKMARK_URL_INVALID | 书签 URL 非法（仅 http/https，≤500 字符） |
| 40006 | NOTE_CONTENT_INVALID | 便签内容/颜色非法（内容非空 ≤500 字；颜色需在白名单内） |
| 40100 | UNAUTHORIZED | 未登录或 token 已过期 |
| 40101 | PASSWORD_INCORRECT | 用户名或密码错误 |
| 40401 | USER_NOT_FOUND | 用户不存在 |
| 40402 | TODO_NOT_FOUND | 待办不存在（含非本人，防泄露） |
| 40403 | NOTE_NOT_FOUND | 便签不存在（含非本人，防泄露） |
| 40404 | SCHEDULE_NOT_FOUND | 日程不存在（含非本人，防泄露） |
| 40405 | HABIT_NOT_FOUND | 习惯不存在（含非本人，防泄露） |
| 40406 | BOOKMARK_NOT_FOUND | 书签不存在（含非本人，防泄露） |
| 40901 | USERNAME_EXISTS | 用户名已存在 |
| 40902 | EMAIL_EXISTS | 邮箱已被注册 |

> 单一来源：后端 `backend/app/validators.py` 的 `BIZ_CODE`；前端在 `src/api/*.js` 中按模块对齐维护。

### 6.3 接口清单

**系统**

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/health` | 否 | 健康检查 |

**用户 `/api/user`**

| 方法 | 路径 | 认证 | 请求体 | 说明 |
|------|------|------|--------|------|
| POST | `/api/user/register` | 否 | `{username, email, password, confirmPassword}` | 注册 |
| POST | `/api/user/login` | 否 | `{username, password}` | 登录，data 含 `token` 与 `userInfo` |

**待办 `/api/todo`**（均需认证）

| 方法 | 路径 | 请求体 | 说明 |
|------|------|--------|------|
| GET | `/api/todo/list` | - | 本人待办，按 `createdAt` 倒序，data 为 `{list}`；条目含 `status`（todo/doing/done） |
| POST | `/api/todo` | `{title, note?, status?}` | 新增，status 默认 todo |
| PUT | `/api/todo/{id}` | `{title?, note?, status?}` | 更新（可选字段） |
| DELETE | `/api/todo/{id}` | - | 删除 |

**便签 `/api/note`**（均需认证）

| 方法 | 路径 | 请求体 | 说明 |
|------|------|--------|------|
| GET | `/api/note/list` | - | 本人便签，置顶在前 + 时间倒序 |
| POST | `/api/note` | `{content, color?}` | 新增，color ∈ yellow/blue/green/pink |
| PUT | `/api/note/{id}` | `{content?, color?, pinned?}` | 更新（可选字段） |
| DELETE | `/api/note/{id}` | - | 删除 |

**日程 `/api/schedule`**（均需认证）

| 方法 | 路径 | 请求体 | 说明 |
|------|------|--------|------|
| GET | `/api/schedule/list?start=&end=` | - | 可选月范围过滤（YYYY-MM-DD），日期升序 |
| POST | `/api/schedule` | `{title, date, start?, end?, allDay?, note?}` | 新增，allDay=true 时忽略时间 |
| PUT | `/api/schedule/{id}` | `{title?, date?, start?, end?, allDay?, note?}` | 可选字段更新 |
| DELETE | `/api/schedule/{id}` | - | 删除 |

**仪表盘 `/api/dashboard`**（需认证）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/dashboard` | 聚合返回：todo 统计、今日待办 ≤5、最近便签 ≤3、今日日程 ≤5、habit/pomodoro 摘要、today 日期 |

**习惯 `/api/habit`**（均需认证）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/habit/list` | `[{...habit, todayChecked, streak, last7}]` |
| POST | `/api/habit` | `{name, color?}` |
| PUT | `/api/habit/{id}` | `{name?, color?}` |
| DELETE | `/api/habit/{id}` | 删除习惯及其打卡记录 |
| POST | `/api/habit/{id}/checkin` | 今日打卡（幂等） |
| DELETE | `/api/habit/{id}/checkin` | 取消今日打卡 |

**番茄钟 `/api/pomodoro`**（均需认证）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/pomodoro/sessions` | `{todoId?}`，记录一个 25 分钟专注会话 |
| GET | `/api/pomodoro/summary` | `{todayCount, recent ≤10}` |

**书签 `/api/bookmark`**（均需认证）

| 方法 | 路径 | 请求体/参数 | 说明 |
|------|------|-------------|------|
| GET | `/api/bookmark/list` | - | 本人书签，按 `createdAt` 倒序，data 为 `{list}`；搜索/分类筛选由前端过滤 |
| POST | `/api/bookmark` | `{url, title?, category?, note?}` | 新增，title 留空落库 null（前端域名兜底），category 默认"未分类" |
| PUT | `/api/bookmark/{id}` | `{url?, title?, category?, note?}` | 可选字段更新，title/note 空串落库为 null |
| DELETE | `/api/bookmark/{id}` | - | 删除 |
| GET | `/api/bookmark/fetch-meta?url=` | - | 抓取目标网页 `<title>`/`og:title` 供新增书签预填；抓取失败恒 `code=0 + title=null`（非业务错误） |

## 七、版本管理规范

- **版本号**：遵循语义化版本 `主版本.次版本.修订号`（当前 `0.1.0`），前后端在 `package.json` / `main.py` 各自维护
- **分支模型**：`main` 为主干保持可运行；功能开发建议使用 `feat/<模块>` 短命分支，合入后删除
- **提交信息**：约定式提交（Conventional Commits）格式：
  - `feat: 新增便签功能` / `fix: 修复侧边栏折叠对齐` / `docs: 补充接口文档` / `refactor:` / `chore:`
- **提交纪律**：一次提交聚焦一件事；`app.db`、`.venv/`、`node_modules/`、`dist/` 不入库（见 `.gitignore`）

## 八、部署流程

### 8.1 当前阶段（开发环境）

前后端分别启动即可：后端 `python run.py`（8000），前端 `npm run dev`（5173，代理 `/api`）。

### 8.2 生产部署步骤

**方式一：后端单进程托管（推荐，最简单）**

1. **前端构建**：`npm run build` → 产出 `dist/` 静态文件
2. **启动后端**：`uvicorn app.main:app --host 127.0.0.1 --port 8000`（不带 `--reload`）
   - `main.py` 末尾会自动检测 `frontend/dist/` 并以 catch-all 路由托管：dist 中真实存在的文件（js/css/图标）直接返回，其余路径统一回退 `index.html`，由前端路由处理（SPA history 回退已内置，**无需 Nginx 配置 try_files**）
   - `/api` 与 `/health` 路由注册在前，不会被 catch-all 拦截
3. **公网部署**：前置 Nginx 处理 HTTPS/域名，将请求反代到 `127.0.0.1:8000`；后端只绑定本机回环地址，不对公网开放

**方式二：前后端分离部署（Nginx 托管静态资源）**

1. `dist/` 交给 Nginx / Caddy 静态托管，需自行配置 history 回退（所有路径回退到 `index.html`）
2. Nginx 将 `/api` 反向代理到 uvicorn（`uvicorn app.main:app --host 127.0.0.1 --port 8000`，去掉 `--reload`）

**安全加固（上线前必做）**：

- 通过环境变量注入强随机 `JWT_SECRET_KEY`（`auth.py` 已支持，未设置时启动会输出警告）
- 公网若走同域反代，CORS 中间件可保留；若前后端分开域名，需将 `main.py` 中 `allow_origins=["*"]` 收紧为具体域名
- SQLite 适合单机轻量场景；多实例/高并发需换 PostgreSQL/MySQL
- 注意：修改前端代码后需重新 `npm run build` 才会生效（后端托管的是 dist 产物，不是源码）

## 九、维护手册

### 9.1 常见问题

| 现象 | 原因 | 处理 |
|------|------|------|
| 接口 404 但登录正常 | **8000 端口被旧实例占用**（多实例重复绑定，Windows 下不报错），旧代码无新路由 | `netstat -ano | findstr :8000` 找到 PID，`taskkill /PID <pid> /T /F` 全树终止后重启 |
| 前端提示"登录已过期" | JWT 1 天有效期已到 | 重新登录即可 |
| 新加的表没建出来 | 无迁移机制，靠启动时 `create_all` | 确认模型已导入 `main.py`（noqa 注释处）并**重启**后端；给已有表加列不会自动迁移，需手动 ALTER 或删库重建 |
| 构建报 "X is not exported" | 图标名不存在于 `@element-plus/icons-vue` | 在 `node_modules/@element-plus/icons-vue/dist/index.js` 中搜索确认真实图标名 |
| 修改后端代码未生效 | 启动方式未带 `--reload` | 重启进程，或用 `python run.py`（自带 reload） |

### 9.2 数据库说明

- 数据文件：`backend/app/app.db`（SQLite 单文件，含 `users` / `todos` / `notes` 表）
- 备份：直接复制该文件即可
- 重置：停止后端后删除文件，重启会重建全部表（**数据不可恢复**）

### 9.3 测试约定

- 手动验证路径：注册 → 登录 → 各页面 CRUD → 刷新持久化 → 第二账号隔离验证
- 测试产生的账号/数据验证后清理，避免污染 `app.db`

## 十、问题反馈渠道

本项目为个人项目，暂未开放外部反馈渠道：

- **开发者**：项目所有者本人
- **问题记录方式**：开发中发现的问题记录在本文档 §9.1 常见问题表；体验类改进建议沉淀到 `docs/` 对应 `<feature>-optimization.md`
- 若后续开源，在此处补充 GitHub Issues 链接

## 十一、扩展指南

新增一个业务模块（以"便签"为参照模板）的标准步骤：

**后端**（参照 `note.py` 全链路）：

1. `models.py`：新增模型（外键 `users.id` + `user_id` 索引 + `to_dict()` camelCase）
2. `validators.py`：`BIZ_CODE` 加错误码（用未占用的号段）+ 校验函数
3. `schemas.py`：`XxxCreateRequest` / `XxxUpdateRequest`
4. `crud.py`：CRUD 五件套，查询强制 `user_id` 隔离
5. `routers/xxx.py`：复刻 `note.py` 结构（`Depends(get_current_user)` + 统一响应）
6. `main.py` + `routers/__init__.py`：注册模型与路由 → 重启验证

**前端**：

1. `src/api/xxx.js`：BIZ_CODE 对齐 + API 函数（模式同 `todo.js`）
2. `src/views/xxx.vue`：页面（40100 处理用 `useUnauthorizedHandler`）
3. `src/router/index.js`：`/` children 加路由（`meta.requiresAuth` 继承自父级）
4. `src/layout/AppSidebar.vue`：侧边栏加菜单项
5. `npm run build` 验证编译 → 浏览器走查

---

*本文档由项目维护者维护，最后更新于 2026-10-10。*
