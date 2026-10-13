/**
 * 习惯打卡 API（真实后端实现）
 *
 * 响应格式与后端保持一致：
 *   成功：{ code: 0, message: string, data: T }
 *   失败：抛出 Error，error.code 为业务错误码、error.message 为提示文案
 */
import request from './request'

/* ---------- 业务错误码（与后端 app/validators.py 中的 BIZ_CODE 对齐） ---------- */
export const BIZ_CODE = {
  UNAUTHORIZED: 40100,
  HABIT_NAME_INVALID: 40010,
  HABIT_COLOR_INVALID: 40011,
  HABIT_NOT_FOUND: 40405
}

/* ---------- 习惯色板（与后端 HABIT_COLORS 一致） ---------- */
export const HABIT_COLORS = [
  { value: 'yellow', hex: '#e6a23c' },
  { value: 'blue', hex: '#409eff' },
  { value: 'green', hex: '#67c23a' },
  { value: 'pink', hex: '#f56c6c' }
]

/**
 * 习惯列表（含 todayChecked / streak / last7）
 * @returns {Promise<{ code: 0, message: string, data: { list: Array } }>}
 */
export async function listHabitsApi() {
  return request.get('/habit/list')
}

/**
 * 新增习惯
 * @param {{ name: string, color?: string }} payload
 * @returns {Promise<{ code: 0, message: string, data: object }>}
 */
export async function createHabitApi(payload) {
  return request.post('/habit', payload)
}

/**
 * 更新习惯
 * @param {number} id
 * @param {{ name?: string, color?: string }} payload
 * @returns {Promise<{ code: 0, message: string, data: object }>}
 */
export async function updateHabitApi(id, payload) {
  return request.put(`/habit/${id}`, payload)
}

/**
 * 删除习惯（连带其打卡记录）
 * @param {number} id
 * @returns {Promise<{ code: 0, message: string, data: null }>}
 */
export async function deleteHabitApi(id) {
  return request.delete(`/habit/${id}`)
}

/**
 * 今日打卡（幂等）
 * @param {number} id
 * @returns {Promise<{ code: 0, message: string, data: object }>}
 */
export async function checkinHabitApi(id) {
  return request.post(`/habit/${id}/checkin`)
}

/**
 * 取消今日打卡
 * @param {number} id
 * @returns {Promise<{ code: 0, message: string, data: object }>}
 */
export async function uncheckinHabitApi(id) {
  return request.delete(`/habit/${id}/checkin`)
}
