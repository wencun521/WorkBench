/**
 * 用户模拟数据模块
 *
 * 职责：
 *  1. 维护一份「用户表」，持久化到 localStorage，刷新后仍可用
 *  2. 提供与服务端一致的数据校验规则（用户名 / 密码 / 邮箱）
 *  3. 暴露数据查询、新增、重置等管理函数，方便开发测试环境维护
 *
 * 真实后端接入后，可保留本文件用于单测或联调前的占位。
 */

const STORAGE_KEY = 'mock_users'

/* ---------- 校验规则（与表单校验保持一致） ---------- */
export const RULES = {
  username: {
    min: 3,
    max: 20,
    pattern: /^[a-zA-Z0-9_]+$/,
    messages: {
      required: '请输入用户名',
      length: '用户名长度为 3 ~ 20 个字符',
      format: '仅支持字母、数字、下划线'
    }
  },
  password: {
    min: 6,
    max: 20,
    messages: {
      required: '请输入密码',
      length: '密码长度为 6 ~ 20 个字符'
    }
  },
  email: {
    pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
    messages: {
      required: '请输入邮箱',
      format: '邮箱格式不正确'
    }
  }
}

/* ---------- 种子用户（首次加载或重置时使用） ---------- */
const SEED_USERS = [
  {
    id: 1,
    username: 'admin',
    password: 'admin123',
    email: 'admin@example.com',
    role: 'admin',
    createdAt: '2024-01-01T00:00:00.000Z'
  },
  {
    id: 2,
    username: 'testuser',
    password: 'test123456',
    email: 'test@example.com',
    role: 'user',
    createdAt: '2024-02-15T00:00:00.000Z'
  },
  {
    id: 3,
    username: 'demo',
    password: 'demo123456',
    email: 'demo@example.com',
    role: 'user',
    createdAt: '2024-03-20T00:00:00.000Z'
  }
]

/* ---------- 数据读写（localStorage 持久化） ---------- */
function loadUsers() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) {
      // 首次加载：写入种子数据
      localStorage.setItem(STORAGE_KEY, JSON.stringify(SEED_USERS))
      return clone(SEED_USERS)
    }
    return JSON.parse(raw)
  } catch (e) {
    console.warn('[mock/user] 数据解析失败，已重置为种子数据', e)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(SEED_USERS))
    return clone(SEED_USERS)
  }
}

function saveUsers(users) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(users))
}

function clone(obj) {
  return JSON.parse(JSON.stringify(obj))
}

/* ---------- 数据查询 ---------- */

/** 获取全部用户（深拷贝，避免外部误改） */
export function getUsers() {
  return clone(loadUsers())
}

/** 按用户名查找 */
export function findUserByName(username) {
  const user = loadUsers().find((u) => u.username === username)
  return user ? clone(user) : null
}

/** 按邮箱查找 */
export function findUserByEmail(email) {
  const user = loadUsers().find((u) => u.email === email)
  return user ? clone(user) : null
}

/** 按 id 查找 */
export function findUserById(id) {
  const user = loadUsers().find((u) => u.id === id)
  return user ? clone(user) : null
}

/* ---------- 数据操作 ---------- */

/**
 * 新增用户（不会重复校验，调用方需自行查重）
 * @param {{ username: string, password: string, email: string, role?: string }} info
 */
export function addUser(info) {
  const users = loadUsers()
  const newUser = {
    id: users.length ? Math.max(...users.map((u) => u.id)) + 1 : 1,
    role: 'user',
    createdAt: new Date().toISOString(),
    ...info
  }
  users.push(newUser)
  saveUsers(users)
  return clone(newUser)
}

/** 按 id 删除用户 */
export function removeUserById(id) {
  const users = loadUsers()
  const next = users.filter((u) => u.id !== id)
  saveUsers(next)
  return users.length !== next.length
}

/** 重置为种子数据 */
export function resetMockUsers() {
  saveUsers(SEED_USERS)
  return clone(SEED_USERS)
}

/* ---------- 数据校验（与服务端规则保持一致） ---------- */

export function validateUsername(username) {
  if (!username) return RULES.username.messages.required
  if (username.length < RULES.username.min || username.length > RULES.username.max) {
    return RULES.username.messages.length
  }
  if (!RULES.username.pattern.test(username)) {
    return RULES.username.messages.format
  }
  return ''
}

export function validatePassword(password) {
  if (!password) return RULES.password.messages.required
  if (password.length < RULES.password.min || password.length > RULES.password.max) {
    return RULES.password.messages.length
  }
  return ''
}

export function validateEmail(email) {
  if (!email) return RULES.email.messages.required
  if (!RULES.email.pattern.test(email)) {
    return RULES.email.messages.format
  }
  return ''
}
