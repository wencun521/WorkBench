/**
 * 用户相关 API（mock 实现）
 *
 * 响应格式与真实后端保持一致：
 *   成功：{ code: 0, message: string, data: T }
 *   失败：抛出 Error，error.code 为业务错误码、error.message 为提示文案
 *
 * 接入真实后端时，把函数体内的 mock 逻辑替换为 fetch / axios 即可，
 * 上层调用方式（async/await + try/catch）无需改动。
 */
import {
  findUserByName,
  findUserByEmail,
  addUser,
  validateUsername,
  validatePassword,
  validateEmail
} from '@/mock/user'

// 模拟网络延迟，便于看到 loading 状态
function delay(ms = 600) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function success(data, message = 'OK') {
  return { code: 0, message, data }
}

function fail(code, message) {
  const err = new Error(message)
  err.code = code
  err.bizCode = code // 业务错误码别名，便于上层判断
  return err
}

/* ---------- 业务错误码 ---------- */
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
  await delay()

  // 服务端二次校验入参格式
  const usernameErr = validateUsername(username)
  if (usernameErr) throw fail(BIZ_CODE.USERNAME_INVALID, usernameErr)

  const passwordErr = validatePassword(password)
  if (passwordErr) throw fail(BIZ_CODE.PASSWORD_INVALID, passwordErr)

  // 用户是否存在
  const user = findUserByName(username)
  if (!user) {
    // 出于安全考虑，真实后端通常不会区分「用户不存在」与「密码错误」
    // 这里为了便于联调区分两种场景，分别返回明确文案
    throw fail(BIZ_CODE.USER_NOT_FOUND, '用户名不存在')
  }

  // 校验密码
  if (user.password !== password) {
    throw fail(BIZ_CODE.PASSWORD_INCORRECT, '用户名或密码错误')
  }

  // 签发 token（真实项目由后端签发 JWT）
  const token = `mock-token-${user.id}-${Date.now()}`
  return success(
    {
      token,
      userInfo: {
        id: user.id,
        username: user.username,
        email: user.email,
        role: user.role
      }
    },
    '登录成功'
  )
}

/**
 * 注册
 * @param {{ username: string, password: string, confirmPassword: string, email: string }} payload
 * @returns {Promise<{ code: 0, message: string, data: { id: number, username: string } }>}
 */
export async function registerApi({ username, password, confirmPassword, email }) {
  await delay()

  // 入参格式校验
  const usernameErr = validateUsername(username)
  if (usernameErr) throw fail(BIZ_CODE.USERNAME_INVALID, usernameErr)

  const emailErr = validateEmail(email)
  if (emailErr) throw fail(BIZ_CODE.EMAIL_INVALID, emailErr)

  const passwordErr = validatePassword(password)
  if (passwordErr) throw fail(BIZ_CODE.PASSWORD_INVALID, passwordErr)

  if (password !== confirmPassword) {
    throw fail(BIZ_CODE.PASSWORD_NOT_MATCH, '两次输入的密码不一致')
  }

  // 用户名 / 邮箱查重
  if (findUserByName(username)) {
    throw fail(BIZ_CODE.USERNAME_EXISTS, '用户名已存在')
  }
  if (findUserByEmail(email)) {
    throw fail(BIZ_CODE.EMAIL_EXISTS, '邮箱已被注册')
  }

  // 写入「用户表」
  const newUser = addUser({ username, password, email })
  return success({ id: newUser.id, username: newUser.username }, '注册成功')
}
