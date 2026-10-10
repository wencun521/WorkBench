/**
 * 便签 API（真实后端实现）
 *
 * 响应格式与后端保持一致：
 *   成功：{ code: 0, message: string, data: T }
 *   失败：抛出 Error，error.code 为业务错误码、error.message 为提示文案
 */
import request from './request'

/* ---------- 业务错误码（与后端 app/validators.py 中的 BIZ_CODE 对齐） ---------- */
export const BIZ_CODE = {
  UNAUTHORIZED: 40100,
  NOTE_CONTENT_INVALID: 40006,
  NOTE_NOT_FOUND: 40403
}

/* ---------- 便签色板（与后端 NOTE_COLORS 一致，value 传后端，hex 用于渲染） ---------- */
export const NOTE_COLORS = [
  { value: 'yellow', hex: '#fff8d6' },
  { value: 'blue', hex: '#d6e8ff' },
  { value: 'green', hex: '#d9f2e3' },
  { value: 'pink', hex: '#ffe3ec' }
]

/**
 * 便签列表（置顶在前，其余按创建时间倒序）
 * @returns {Promise<{ code: 0, message: string, data: { list: Array } }>}
 */
export async function listNotesApi() {
  return request.get('/note/list')
}

/**
 * 新增便签
 * @param {{ content: string, color?: string }} payload
 * @returns {Promise<{ code: 0, message: string, data: object }>}
 */
export async function createNoteApi({ content, color = 'yellow' }) {
  return request.post('/note', { content, color })
}

/**
 * 更新便签（内容 / 颜色 / 置顶，均可选传）
 * @param {number} id
 * @param {{ content?: string, color?: string, pinned?: boolean }} payload
 * @returns {Promise<{ code: 0, message: string, data: object }>}
 */
export async function updateNoteApi(id, payload) {
  return request.put(`/note/${id}`, payload)
}

/**
 * 删除便签
 * @param {number} id
 * @returns {Promise<{ code: 0, message: string, data: null }>}
 */
export async function deleteNoteApi(id) {
  return request.delete(`/note/${id}`)
}
