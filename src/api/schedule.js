/**
 * 日程 API（真实后端实现）
 *
 * 响应格式与后端保持一致：
 *   成功：{ code: 0, message: string, data: T }
 *   失败：抛出 Error，error.code 为业务错误码、error.message 为提示文案
 */
import request from './request'

/* ---------- 业务错误码（与后端 app/validators.py 中的 BIZ_CODE 对齐） ---------- */
export const BIZ_CODE = {
  UNAUTHORIZED: 40100,
  SCHEDULE_TITLE_INVALID: 40008,
  SCHEDULE_DATE_INVALID: 40009,
  SCHEDULE_NOT_FOUND: 40404
}

/**
 * 日程列表（可选月范围过滤）
 * @param {{ start?: string, end?: string }} params 'YYYY-MM-DD'
 * @returns {Promise<{ code: 0, message: string, data: { list: Array } }>}
 */
export async function listSchedulesApi({ start, end } = {}) {
  return request.get('/schedule/list', { params: { start, end } })
}

/**
 * 新增日程
 * @param {{ title: string, date: string, start?: string, end?: string, allDay?: boolean, note?: string }} payload
 * @returns {Promise<{ code: 0, message: string, data: object }>}
 */
export async function createScheduleApi(payload) {
  return request.post('/schedule', payload)
}

/**
 * 更新日程（均可选传）
 * @param {number} id
 * @param {{ title?: string, date?: string, start?: string|null, end?: string|null, allDay?: boolean, note?: string }} payload
 * @returns {Promise<{ code: 0, message: string, data: object }>}
 */
export async function updateScheduleApi(id, payload) {
  return request.put(`/schedule/${id}`, payload)
}

/**
 * 删除日程
 * @param {number} id
 * @returns {Promise<{ code: 0, message: string, data: null }>}
 */
export async function deleteScheduleApi(id) {
  return request.delete(`/schedule/${id}`)
}
