# AGENTS.md

本文件为 AI 编码代理提供本仓库的工作指引。

## 项目概览

个人工作台应用（Vue3 + FastAPI 单仓全栈项目）：

- **前端**：Vue 3 + Element Plus + Vue Router + Vite + Axios，位于仓库根目录 `src/`
- **后端**：FastAPI + SQLAlchemy + SQLite，位于 `backend/`，入口 `backend/app/main.py`
- **业务模块**：首页仪表盘、待办、便签、日程日历、习惯打卡、番茄钟、看板、书签收藏

## 常用命令

```bash
# 前端开发（根目录执行）
npm run dev        # Vite 开发服务器
npm run build      # 构建产物输出到根目录 dist/

# 后端开发（backend/ 目录执行）
uvicorn app.main:app --reload --port 8000
# 或 python run.py
```

健康检查：`GET /health`

## 目录结构

```
src/
  api/            # 每模块一个 API 封装文件（axios 基于 api/request.js 拦截器）
  composables/    # 组合式函数（useAuth、usePomodoro 等）
  layout/         # AdminLayout、AppSidebar、menuConfig.js（侧边栏菜单统一配置）
  router/         # 路由（嵌套路由，主布局为父路由）
  views/          # 页面组件（home、todo、notes、schedule、habits、pomodoro、kanban、bookmarks）
backend/app/
  main.py         # FastAPI 入口，注册路由 + SPA 回退 catch-all
  routers/        # 每模块一个路由文件
  models.py / schemas.py / crud.py / deps.py / auth.py / validators.py
  database.py     # SQLite（backend/app/app.db）
docs/             # 各模块功能设计文档 + HANDBOOK.md（完整主手册）
```

## 核心约定

### 前后端响应协议

- 接口统一返回「HTTP 恒 200 + `code` 表达业务结果」：`code === 0` 成功，非 0 为业务错误
- 未授权也返回 HTTP 200（`code: 40100`），由前端 axios 拦截器统一处理并跳转登录，路由守卫需处理 401 场景
- 错误码定义在后端 `backend/app/validators.py` 的 `BIZ_CODE`，需与前端 `src/api/user.js` 的 `BIZ_CODE` 对齐；**每个模块使用独立错误码区间**（4xx01/4xx02… 按模块递增）

### 新增模块固定流程

1. 先在 `docs/` 编写功能设计文档（`xxx-feature-plan.md`）
2. 后端：`models.py` 建模 → `schemas.py` → `crud.py` → `routers/xxx.py` → `main.py` 注册路由 → `BIZ_CODE` 增加错误码
3. 前端：`src/api/xxx.js` 封装接口 → `src/views/xxx.vue` 页面 → `src/router/index.js` 嵌套路由 → `src/layout/menuConfig.js` 添加一行菜单配置即可上线
4. 更新 `docs/HANDBOOK.md` 与根目录 `README.md`

### 状态管理

- 跨组件/页面需保持的状态（如番茄钟计时）使用**模块级单例组合式函数**（`src/composables/`），避免组件卸载丢状态
- 持久化优先 `localStorage` 做本地缓存，配合后端接口落地
- 布局组件独立拆分文件，侧边栏展开/折叠需注意 flex 对齐一致性

### 安全

- 书签等用户输入的 URL 必须做协议白名单校验（见 `backend/app/validators.py`），禁止危险协议
- 公网部署硬性要求：
  - 后端仅绑定 `127.0.0.1`，禁止直接对外暴露 8000 端口，仅通过 Nginx 反向代理访问
  - 必须配置独立强随机 JWT 密钥，禁止使用开发默认密钥
  - 必须启用 HTTPS，避免 JWT 明文传输

### 部署

- 生产模式：`npm run build` 生成根目录 `dist/`，后端通过 **catch-all 路由**（`main.py` 末尾）托管前端静态文件并实现 SPA 回退（刷新 404 问题的修复方案）
- 注意：catch-all 路由必须在所有 API 路由注册之后；不要改用 `StaticFiles` 托管 dist（会导致 SPA 刷新 404）
- 服务器进程守护用 systemd，参考 `docs/HANDBOOK.md` 部署章节

## 已知坑（勿重蹈）

- 番茄钟计时状态放组件内会在切换页面/模式时丢失，必须用独立 composable
- 便签新建的排序要避免插入到置顶便签之前；`createdAt`/`updatedAt` 时间比较需注意精度，避免误判为已编辑
- 直接用 FastAPI `StaticFiles` 托管 dist 会导致 SPA 路由刷新 404

## 文档结构

- 根目录 `README.md`：仓库简版门面
- `docs/HANDBOOK.md`：完整详细的项目主手册
- `docs/*-feature-plan.md`：各模块功能设计与决策记录

## 提交规范

提交信息使用 conventional commits，如 `feat(kanban): 美化看板视觉，新增三列主题色与拖拽动效`。
