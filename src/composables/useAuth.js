/**
 * 认证相关组合式函数
 *
 * 供布局/视图层复用：
 *  - useLogout：主动退出登录
 *  - useUnauthorizedHandler：接口返回 40100（未登录/过期）时统一处理
 */
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { removeToken } from '@/utils/auth'

export function useLogout() {
  const router = useRouter()

  return () => {
    removeToken()
    ElMessage.success('已退出登录')
    router.replace('/login')
  }
}

export function useUnauthorizedHandler() {
  const router = useRouter()

  return () => {
    removeToken()
    ElMessage.warning('登录已过期，请重新登录')
    router.replace('/login')
  }
}
