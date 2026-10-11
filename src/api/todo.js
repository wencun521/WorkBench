/**
 * 待办事项 API（真实后端实现）
 *
 * 响应格式与后端保持一致：
 *   成功：{ code: 0, message: string, data: T }
 *   失败：抛出 Error，error.code 为业务错误码、error.message 为提示文案
 */
import request from './request'

/* ---------- 业务错误码（与后端 app/validators.py 中的 BIZ_CODE 对齐） ---------- */
export const BIZ_CODE = {
  UNAUTHORIZED: 40100,
  TODO_TITLE_INVALID: 40005,
  TODO_NOT_FOUND: 40402,
  TODO_STATUS_INVALID: 40007
}

/* ---------- 看板三态（与后端 TODO_STATUSES 一致） ---------- */
export const TODO_STATUSES = [
  { value: 'todo', title: '待办' },
  { value: 'doing', title: '进行中' },
  { value: 'done', title: '已完成' }
]

/**
 * 待办列表
 * @returns {Promise<{ code: 0, message: string, data: { list: Array } }>}
 */
export async function listTodoApi() {
  return request.get('/todo/list')
}

/**
 * 新增待办
 * @param {{ title: string, note?: string, status?: string }} payload
 * @returns {Promise<{ code: 0, message: string, data: object }>}
 */
export async function createTodoApi({ title, note = '', status = 'todo' }) {
  return request.post('/todo', { title, note, status })
}

/**
 * 更新待办（标题 / 备注 / 状态，均可选传）
 * @param {number} id
 * @param {{ title?: string, note?: string, status?: string }} payload
 * @returns {Promise<{ code: 0, message: string, data: object }>}
 */
export async function updateTodoApi(id, payload) {
  return request.put(`/todo/${id}`, payload)
}

/**
 * 删除待办
 * @param {number} id
 * @returns {Promise<{ code: 0, message: string, data: null }>}
 */
export async function deleteTodoApi(id) {
  return request.delete(`/todo/${id}`)
}
