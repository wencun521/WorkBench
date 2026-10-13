/**
 * 用户相关 API（真实后端实现）
 *
 * 响应格式与后端保持一致：
 *   成功：{ code: 0, message: string, data: T }
 *   失败：抛出 Error，error.code 为业务错误码、error.message 为提示文案
 *
 * 上层调用方式（async/await + try/catch）无需改动。
 */
import request from './request'

/* ---------- 业务错误码（与后端 app/validators.py 中的 BIZ_CODE 对齐） ---------- */
export const BIZ_CODE = {
  USERNAME_INVALID: 40001,
  PASSWORD_INVALID: 40002,
  EMAIL_INVALID: 40003,
  PASSWORD_NOT_MATCH: 40004,
  USER_NOT_FOUND: 40401,
  PASSWORD_INCORRECT: 40101,
  USERNAME_EXISTS: 40901,
  EMAIL_EXISTS: 40902
}

/**
 * 登录
 * @param {{ username: string, password: string }} payload
 * @returns {Promise<{ code: 0, message: string, data: { token: string, userInfo: object } }>}
 */
export async function loginApi({ username, password }) {
  return request.post('/user/login', { username, password })
}

/**
 * 注册
 * @param {{ username: string, password: string, confirmPassword: string, email: string }} payload
 * @returns {Promise<{ code: 0, message: string, data: { id: number, username: string } }>}
 */
export async function registerApi({ username, password, confirmPassword, email }) {
  return request.post('/user/register', { username, password, confirmPassword, email })
}
