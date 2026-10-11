/**
 * 书签收藏 API（真实后端实现）
 *
 * 列表一次拉全，搜索/分类筛选由前端过滤。
 */
import request from './request'

/* ---------- 业务错误码（与后端 app/validators.py 中的 BIZ_CODE 对齐） ---------- */
export const BIZ_CODE = {
  UNAUTHORIZED: 40100,
  BOOKMARK_TITLE_INVALID: 40012,
  BOOKMARK_URL_INVALID: 40013,
  BOOKMARK_NOT_FOUND: 40406
}

/**
 * 书签列表（按创建时间倒序）
 * @returns {Promise<{ code: 0, message: string, data: { list: Array } }>}
 */
export async function listBookmarksApi() {
  return request.get('/bookmark/list')
}

/**
 * 新增书签
 * @param {{ url: string, title?: string, category?: string, note?: string }} payload
 * @returns {Promise<{ code: 0, message: string, data: object }>}
 */
export async function createBookmarkApi(payload) {
  return request.post('/bookmark', payload)
}

/**
 * 更新书签（均可选传）
 * @param {number} id
 * @param {{ url?: string, title?: string|null, category?: string, note?: string|null }} payload
 * @returns {Promise<{ code: 0, message: string, data: object }>}
 */
export async function updateBookmarkApi(id, payload) {
  return request.put(`/bookmark/${id}`, payload)
}

/**
 * 删除书签
 * @param {number} id
 * @returns {Promise<{ code: 0, message: string, data: null }>}
 */
export async function deleteBookmarkApi(id) {
  return request.delete(`/bookmark/${id}`)
}
