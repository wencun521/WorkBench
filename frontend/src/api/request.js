/**
 * axios 请求封装
 *
 * 统一职责：
 *  1. baseURL 指向 /api，配合 vite 代理转发到后端 8000 端口
 *  2. 自动携带 Authorization: Bearer <token>
 *  3. 响应拦截：后端统一返回 { code, message, data }
 *     - code === 0：业务成功，返回完整响应对象
 *     - code !== 0：抛出 Error，error.code 为业务错误码，error.message 为提示文案
 *  4. 网络异常统一抛出带 message 的 Error
 */
import axios from 'axios'
import { getToken } from '@/utils/auth'

const service = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截：自动注入 token
service.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截：统一处理业务错误码
service.interceptors.response.use(
  (response) => {
    const res = response.data
    // 后端约定：code === 0 表示业务成功
    if (res.code !== 0) {
      const err = new Error(res.message || '请求失败')
      err.code = res.code
      err.bizCode = res.code
      return Promise.reject(err)
    }
    return res
  },
  (error) => {
    // 网络异常 / 超时等
    const message = error.response?.data?.message || error.message || '网络异常，请稍后重试'
    const err = new Error(message)
    if (error.response?.data?.code) {
      err.code = error.response.data.code
      err.bizCode = error.response.data.code
    }
    return Promise.reject(err)
  }
)

export default service
