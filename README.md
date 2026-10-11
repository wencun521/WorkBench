# Admin Pro

轻量级全栈后台管理系统 —— Vue 3 + FastAPI + SQLite。

![version](https://img.shields.io/badge/version-0.1.0-blue) ![vue](https://img.shields.io/badge/Vue-3.5-42b883) ![fastapi](https://img.shields.io/badge/FastAPI-latest-009688) ![license](https://img.shields.io/badge/license-private-lightgrey)

## 功能一览

- **工作台首页**：聚合仪表盘，模块入口卡 + 今日待办/日程概览
- **用户认证**：注册 / 登录，JWT 认证，bcrypt 密码哈希
- **待办事项**：增删改查 + 三态状态（待办/进行中/已完成），数据按用户隔离
- **任务看板**：三列拖拽看板（原生 HTML5 DnD），与待办列表共用一份数据
- **日程日历**：月历视图 + 当日列表，支持全天/时段日程
- **便签**：彩色便签 + 置顶，随手记录文字
- **后台布局**：可折叠分组侧边栏（配置驱动），新模块加一行菜单即上线

## 技术栈

| 端 | 技术 |
|----|------|
| 前端 | Vue 3 · Vite 5 · Element Plus · vue-router 4 · axios |
| 后端 | FastAPI · SQLAlchemy · SQLite · JWT (python-jose) · bcrypt |

## 快速开始

```bash
# 后端（端口 8000）
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python run.py

# 前端（端口 5173，/api 自动代理到 8000）
npm install
npm run dev
```

访问 `http://localhost:5173`，注册账号即可体验。

## 文档

完整的架构说明、目录索引、接口清单（含错误码表）、部署与维护规范，请查阅 **[项目主文档 HANDBOOK](./docs/HANDBOOK.md)**；各功能规格与优化计划见 [docs/](./docs/) 目录。

## 项目结构

```
├─ docs/       # 项目文档（HANDBOOK.md 为主文档入口）
├─ backend/    # FastAPI 后端（routers / models / crud / auth ...）
├─ src/        # Vue 3 前端（views / layout / api / composables ...）
└─ public/     # 静态资源
```
