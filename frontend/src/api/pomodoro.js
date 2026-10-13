/**
 * 番茄钟 API（真实后端实现）
 *
 * 专注时长后端写死 25 分钟；休息会话不入库。
 */
import request from './request'

/* ---------- 业务错误码（与后端 app/validators.py 中的 BIZ_CODE 对齐） ---------- */
export const BIZ_CODE = {
  UNAUTHORIZED: 40100,
  TODO_NOT_FOUND: 40402
}

/**
 * 保存一个完成的专注会话
 * @param {{ todoId?: number|null }} payload
 * @returns {Promise<{ code: 0, message: string, data: object }>}
 */
export async function savePomodoroApi(payload = {}) {
  return request.post('/pomodoro/sessions', payload)
}

/**
 * 番茄钟摘要（今日数量 + 最近记录 ≤10）
 * @returns {Promise<{ code: 0, message: string, data: { todayCount: number, recent: Array } }>}
 */
export async function pomodoroSummaryApi() {
  return request.get('/pomodoro/summary')
}
