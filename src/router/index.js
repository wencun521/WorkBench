import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/utils/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/register.vue'),
    meta: { title: '注册', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layout/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/home.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'todo',
        name: 'Todo',
        component: () => import('@/views/todo.vue'),
        meta: { title: '待办事项' }
      },
      {
        path: 'kanban',
        name: 'Kanban',
        component: () => import('@/views/kanban.vue'),
        meta: { title: '任务看板' }
      },
      {
        path: 'schedule',
        name: 'Schedule',
        component: () => import('@/views/schedule.vue'),
        meta: { title: '日程日历' }
      },
      {
        path: 'pomodoro',
        name: 'Pomodoro',
        component: () => import('@/views/pomodoro.vue'),
        meta: { title: '番茄钟' }
      },
      {
        path: 'habits',
        name: 'Habits',
        component: () => import('@/views/habits.vue'),
        meta: { title: '习惯打卡' }
      },
      {
        path: 'notes',
        name: 'Notes',
        component: () => import('@/views/notes.vue'),
        meta: { title: '便签' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/404.vue'),
    meta: { title: '404', requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// 全局前置守卫：未登录跳转登录页
router.beforeEach((to, from, next) => {
  const hasToken = !!getToken()
  if (to.meta.title) {
    document.title = `${to.meta.title} - Admin Pro`
  }
  if (to.meta.requiresAuth === false) {
    // 已登录用户访问登录页，直接回首页
    if (to.path === '/login' && hasToken) {
      return next({ path: '/' })
    }
    return next()
  }
  if (!hasToken) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }
  next()
})

export default router
