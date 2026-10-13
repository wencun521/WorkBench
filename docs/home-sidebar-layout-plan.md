# home 页改造：侧边栏 + 主内容区布局计划

## Summary（摘要）

将 home 页从"全屏居中卡片"改造为后台管理式布局：**公共 Layout（可折叠侧边栏 + 主内容区）**，home 与 /todo 作为嵌套子路由共用；home 主区改为欢迎语 + 待办统计卡片；组件按 Vue 3 最佳实践拆分（`<script setup>`、组合式函数、router 模式菜单）。

## Current State（现状）

- [home.vue](file:///f:/code/flowdesk/src/views/home.vue)：全屏居中欢迎卡 + 待办事项按钮 + 退出按钮
- [todo.vue](file:///f:/code/flowdesk/src/views/todo.vue)：独立全屏卡片页，自带"返回首页"按钮和 40100 处理逻辑（handleUnauthorized 内联）
- [router/index.js](file:///f:/code/flowdesk/src/router/index.js)：扁平路由 `/`、`/todo`，meta.requiresAuth + beforeEach 守卫（vue-router 4 会合并父子 meta，嵌套后守卫无需改动）
- [App.vue](file:///f:/code/flowdesk/src/App.vue)：仅 router-view
- 依赖：Element Plus ^2.8.4 + @element-plus/icons-vue；无 pinia；用户信息未持久化（仅 token）
- 样式基调：全局灰底 `#f5f6f8`、卡片圆角 12px

## 已确认决策

1. home + /todo 共用公共 Layout（嵌套路由）
2. home 主区：欢迎语 + 待办统计卡片（数据来自已有 `GET /api/todo/list`）
3. 侧边栏：logo/标题 + 菜单（首页/待办事项）+ 底部用户区（头像+用户名+退出）+ 可折叠

## Proposed Changes（改动清单）

### 1. 新增 `src/layout/AdminLayout.vue` — 布局骨架
- `el-container` 满屏高：`el-aside`（宽度随折叠 64px/210px，transition 过渡）+ `el-main`（overflow auto，内边距 20px）
- 主区直接放 `<router-view />`
- 折叠状态由本组件持有（`ref`），传给 AppSidebar（props down）

### 2. 新增 `src/layout/AppSidebar.vue` — 侧边栏组件
- props：`collapsed`；emits：`toggle`
- 顶部：logo 图标 + "Admin Pro" 标题（折叠时只留图标）
- 中部：`el-menu`，`:router="true"`（index 即路径，激活态跟随 `$route.path`）、`:collapse="collapsed"`、`:collapse-transition="false"`
  - `/` 首页（HomeFilled 图标）、`/todo` 待办事项（Tickets 图标）
- 底部：折叠触发按钮（Fold/Expand 图标）+ 用户区（el-avatar 显示用户名首字符 + 用户名 + 退出图标按钮）
- 用户名来源：现有接口无"获取个人信息"端点，token 里只有 sub(user.id) —— **折衷方案：不展示用户名，仅展示头像（固定字符）+ 退出按钮**；如需用户名需后端加接口，超出本次范围
- 退出逻辑：调用共享的 `useUnauthorized` 同源写法 → `removeToken()` + `ElMessage.success` + `router.replace('/login')`

### 3. 新增 `src/composables/useAuth.js` — 共享组合式函数
- 导出 `useLogout()`（登出）与 `useUnauthorizedHandler()`（40100 清 token 跳登录，提示"登录已过期"）
- 内部用 `useRouter`，供 todo.vue / home.vue / AppSidebar 三处复用，消除 todo.vue 内联重复

### 4. 修改 `src/router/index.js` — 嵌套路由
```js
{
  path: '/',
  component: () => import('@/layout/AdminLayout.vue'),
  meta: { requiresAuth: true },   // 子路由自动继承（vue-router 4 合并 matched meta）
  children: [
    { path: '', name: 'Home', component: () => import('@/views/home.vue'), meta: { title: '首页' } },
    { path: 'todo', name: 'Todo', component: () => import('@/views/todo.vue'), meta: { title: '待办事项' } }
  ]
}
```
- 删除原独立的 `/` 与 `/todo` 两条路由；beforeEach 守卫逻辑不变

### 5. 重写 `src/views/home.vue` — 主内容区
- 去掉全屏居中外壳，改为普通文档流内容
- 顶部欢迎卡：欢迎语 + 一句说明
- 统计区：3 个统计卡片（待办总数 / 已完成 / 未完成），`onMounted` 调 `listTodoApi` 后 computed 计算；err.code === 40100 走 `useUnauthorizedHandler`
- 加载失败静默降级为 0（不阻塞页面）
- 删除原"退出登录"按钮（已移至侧边栏）

### 6. 修改 `src/views/todo.vue` — 套用布局
- 外壳 `.todo-page` 从"满屏 flex 居中"改为普通内边距容器（max-width 900px 居中即可）
- 卡片头部"返回首页"按钮可移除（侧边栏已有导航），保留"待办事项"标题
- 40100 处理改用 `useUnauthorizedHandler`，删除内联 handleUnauthorized

### 不改动
- `App.vue`、`global.css`、`utils/auth.js`、后端（统计由前端对 list 求和，无新接口）

## Assumptions & Decisions（假设与决策）

- 用户名展示需后端新增"当前用户信息"接口，本次不做（侧边栏用户区仅头像+退出）；后续可加 `GET /api/user/me`
- 统计数据前端计算而非后端聚合接口：最基础版条目量小，避免新增 API
- 不引入 pinia：折叠状态仅在 Layout 内部使用，无需全局状态

## Verification（验证）

1. `npm run dev` + 后端启动，登录后落在 `/`：出现侧边栏布局，主区显示欢迎卡与 3 个统计卡片
2. 点侧边栏"待办事项"→ URL 变为 `/todo`，列表页在主内容区内渲染，菜单高亮跟随路由
3. 点折叠按钮：侧边栏收窄为图标条，菜单正确折叠，再点恢复
4. 刷新 `/todo` 直达（守卫通过，布局正常）
5. 侧边栏退出登录 → 跳转 /login；手动清 token 后访问 /todo → 重定向登录页
6. `npm run build` 编译无错误
