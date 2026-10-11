# 书签收藏功能规格文档

> 上线时间：2026-10-11
> 关联：[dashboard-menu-plan.md](./dashboard-menu-plan.md)（仪表盘集成模式）

## 一、背景

工作台第三批模块。定位：链接 + 自由分类 + 搜索的快速找回工具。边界决策：**不做**网页抓取/快照、favicon 真实抓取、打开次数统计。

## 二、数据模型（models.py Bookmark）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer PK | |
| user_id | FK users.id | 数据隔离 |
| title | String(100) **nullable** | 可空，展示层用 URL 域名兜底 |
| url | String(500) 必填 | 仅 http/https |
| category | String(50) 默认"未分类" | 自由文本字段，前端 datalist 联想 |
| note | String(200) nullable | |
| created_at | DateTime | |

索引：`ix_bookmarks_user_created(user_id, created_at)`。全新表 create_all 自动创建，无需迁移。

## 三、API（prefix /api/bookmark，HTTP 恒 200）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /list | 一次拉全（created_at desc），**搜索/分类筛选由前端过滤**（量小） |
| POST | | `{url, title?, category?, note?}` |
| PUT | /{id} | 可选字段更新；title/note 空串落库为 null |
| DELETE | /{id} | |

错误码：`BOOKMARK_TITLE_INVALID: 40012`（标题 ≤100、备注 ≤200、分类 ≤50）、`BOOKMARK_URL_INVALID: 40013`、`BOOKMARK_NOT_FOUND: 40406`（含非本人防泄露）。

**关键决策：URL 校验用 urllib.parse.urlparse 而非纯正则**——scheme 白名单仅 http/https（拒绝 `javascript:` 注入）、netloc 非空且不含空格；urlparse 同时提供 netloc 供标题域名兜底。

## 四、前端（/bookmarks 页）

- 工具条：搜索框（title/url/note toLowerCase includes 前端过滤）+ 分类筛选 el-select（选项从数据去重 derive）+ 新增按钮
- 按分类分节渲染（组头 = 分类名 + 数量）；书签行是 `<a target="_blank" rel="noopener noreferrer">`：色块图标（**分类名首字符 + 分类名 charCodeAt 求和取模映射 4 色板**，零请求零依赖）+ 标题（hover 变蓝）+ 备注摘要 + 域名；悬停显编辑/删除
- 新增/编辑 el-dialog：url（聚焦）、title（placeholder"留空则显示域名"）、category 原生 `<input list>` + `<datalist>` 联想、note textarea
- 域名提取 `new URL(url).hostname` try/catch 兜底

## 五、验证记录

- 接口：无 title 创建（域名兜底）、`javascript:alert(1)` → 40013、超长 title → 40012、编辑/删除、dashboard bookmark.total、40100 全通过
- 浏览器走查：菜单/入口卡、分节渲染、新增（datalist 联想 + 域名兜底）、搜索/分类筛选、编辑备注、删除、新标签打开（noopener）——步骤 1-7 自动验证通过，步骤 8-9 由用户手动复核确认

---

## 六、增强：自动获取网站标题与 Favicon（已实现）

> 方案确认于 2026-10-11，已实现并验证通过（见 6.6 验证记录）。本文档即实现依据。

### 6.1 目标

1. 书签列表展示目标网站的真实 favicon，替代纯色块
2. 新增书签时可自动抓取网页 `<title>` 预填标题输入框（不直接落库，用户可改）

### 6.2 Favicon —— 纯前端，零后端改动

不做真实抓取与存储，按域名拼公共 favicon 服务地址，`<img>` 直接加载：

- 采用：`https://a.favicon.im/{域名}?throw-error-on-404=true`（favicon.im，国内可访问；`throw-error-on-404` 使未收录站点返回 HTTP 404，直接触发 `@error` 回退，避免加载默认占位图标）
- 初版曾用 `https://icons.duckduckgo.com/ip3/{域名}.ico`，因当前网络环境不可达（超时）于 2026-10-11 切换为 favicon.im
- `@error` 回退到现有「分类首字符色块」，视觉无缝降级（用一个 `faviconFailed` Set 记录加载失败的域名，避免重复请求）
- 优点：浏览器自动缓存、无存储成本、无后端请求；缺点：极少数未收录新站走回退

### 6.3 标题抓取 —— 后端代理接口

浏览器 CORS 限制导致前端无法直接请求任意网站，故新增后端接口：

- `GET /api/bookmark/fetch-meta?url=...`（登录态必需，40100）
- 复用 `validate_bookmark_url` 校验，仅 http/https
- httpx 请求目标页面：`follow_redirects=True`、超时 5 秒、限制读取响应体大小（如 ≤512KB 即够解析 head）
- 解析优先级：`<title>` 文本 → `<meta property="og:title">` → 全部为空时返回空 title（前端保持域名兜底，不报错中断）
- 编码处理：httpx 自动按响应头/charset 解码；乱码可接受（个人使用，不做 chardet 级探测）
- 响应：`{code: 0, data: {title: "..." | null}}`，沿用 HTTP 恒 200 约定；抓取失败一律 code=0 + title=null（抓取失败不是业务错误）
- 无需新增错误码；依赖 httpx（若未安装则 `pip install httpx`）

### 6.4 前端交互（bookmarks.vue + api/bookmark.js）

- 新增 el-dialog 中：**URL 输入框 blur 时，若 title 为空且 url 合法 → 调 fetch-meta → 成功则填入 title 输入框**（用户可见可改）
- title 输入框旁加「获取标题」按钮（重复触发补充手段）；获取中按钮 loading
- **编辑弹窗不自动触发** blur 抓取，仅保留手动按钮，避免覆盖用户已起的标题
- api/bookmark.js 新增 `fetchMetaApi(url)`

### 6.5 改动清单

| 文件 | 改动 |
|---|---|
| backend/app/routers/bookmark.py | 新增 fetch-meta 接口 |
| backend/app/validators.py | 复用 validate_bookmark_url（无需改） |
| src/api/bookmark.js | 新增 fetchMetaApi |
| src/views/bookmarks.vue | favicon 渲染 + 回退逻辑；弹窗 blur 自动抓取 + 手动按钮 |
| requirements.txt（如有） | 补 httpx |

### 6.6 验证记录

- 接口（2026-10-11）：合法 url（example.com）返回 title；`javascript:alert(1)` → 40013；不可达域名 → code=0 且 title=null；未登录 → 40100；github.com 返回真实标题 —— 全通过
- 页面：手动「获取标题」按钮（含 loading）成功抓取并填入（baidu → "百度一下，你就知道"）；保存后列表标题正确；编辑弹窗不自动抓取、手动可用 —— 通过
- 自动 blur 触发：模板编译产物确认 `onBlur: $setup.handleUrlBlur` 绑定存在，直接调用处理函数后请求立即发出且标题回填，链路完整；自动化环境的合成焦点事件无法送达 Vue 监听器（真实键盘 Tab 触发 focusout 但监听器未执行），属测试环境限制，需真实浏览器手动复核 blur 自动抓取
- favicon：favicon.im 服务可达性实测 github.com → 200 (SVG)、baidu.com → 200 (ICO)、未收录域名 → 404 触发 `@error` 回退；浏览器走查 github 书签显示真实猫标，未收录站点（example.com）无缝回退色块 —— 通过（2026-10-11 切换 favicon.im 后实测）
