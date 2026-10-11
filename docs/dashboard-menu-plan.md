# 工作台地基：菜单分组 + 聚合仪表盘 规格文档

> 上线时间：2026-10-11
> 关联：[HANDBOOK.md](./HANDBOOK.md)、[schedule-feature-plan.md](./schedule-feature-plan.md)（本轮同期上线，仪表盘的"今日日程"依赖其数据）

## 一、背景

项目定位升级为「个人工作台 all-in-one」（本机/内网自用）。模块将持续增加，需要先打地基：侧边栏菜单可扩展、首页能一屏总览所有模块。

## 二、菜单分组（数据驱动）

- 新增 `src/layout/menuConfig.js`：`MENU_GROUPS` 数组，每项 `{ key, title, children: [{path, title, icon}] }`；`title` 为空串表示无分组的独立项（首页）。**新模块加一行即上线**
- `AppSidebar.vue`：v-for 渲染配置。**决策：不用 el-menu-item-group**——EP 折叠态下组标题容器仍渲染会出现空白条；改为自定义 `<div class="group-title">`（`v-if="!collapsed"`），children 平铺为 el-menu-item 直接挂 el-menu 下。折叠态组标题消失、图标照常导航（EP 自带 tooltip）、default-active 跨组高亮正常
- 分组现状：首页（无组）｜任务：待办事项/任务看板/日程日历｜记录：便签

## 三、聚合仪表盘

- 后端新增 `GET /api/dashboard`（`routers/dashboard.py`，Depends(get_current_user)），一次返回：
  - `today`（YYYY-MM-DD）
  - `todo: {total, doing, done}`
  - `todayTodos: [{id,title,status}] ≤5`（未完成在前，**只读摘要**）
  - `noteCount`、`recentNotes ≤3`
  - `scheduleCount`、`todaySchedules: [{id,title,start,allDay}] ≤5`
- 决策：仪表盘**只读**——条目点击跳转对应模块页操作，保持"概览页轻、操作页重"的分工
- 旧模块 list 接口保留（各模块页仍用）

### home.vue 布局
欢迎卡（预留全局搜索 Ctrl+K 与提醒机制的挂载点注释）→ 4 张模块入口卡（彩色图标 + 数字摘要，hover 上浮）→ 今日概览卡（左今日待办带状态徽章 / 右今日日程）→ 最近便签卡。单请求渲染；失败静默降级。

## 四、验证记录

- 浏览器走查 8 步：菜单分组展示/折叠态无空白条、图标可导航、高亮正确；仪表盘四卡摘要与今日概览正确（修复了一处 `{{ today }}` → `{{ dash.today }}` 的模板笔误后全通过）
- 实施顺序：Schedule 后端 → Dashboard → 菜单分组 → Schedule 前端（dashboard 依赖日程数据）
