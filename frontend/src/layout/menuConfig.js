/**
 * 侧边栏菜单注册配置
 *
 * 新增模块：在对应分组的 children 加一项，或新增分组，即可上线。
 * children 为 null 的项渲染为无分组的独立菜单项。
 */
import { HomeFilled, Tickets, Grid, Calendar, Memo, Timer, Finished, Collection } from '@element-plus/icons-vue'

export const MENU_GROUPS = [
  {
    key: 'home',
    title: '',
    children: [{ path: '/', title: '首页', icon: HomeFilled }]
  },
  {
    key: 'task',
    title: '任务',
    children: [
      { path: '/todo', title: '待办事项', icon: Tickets },
      { path: '/kanban', title: '任务看板', icon: Grid },
      { path: '/schedule', title: '日程日历', icon: Calendar },
      { path: '/pomodoro', title: '番茄钟', icon: Timer }
    ]
  },
  {
    key: 'record',
    title: '记录',
    children: [
      { path: '/notes', title: '便签', icon: Memo },
      { path: '/habits', title: '习惯打卡', icon: Finished },
      { path: '/bookmarks', title: '书签收藏', icon: Collection }
    ]
  }
]
