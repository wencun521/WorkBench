/**
 * 工作台仪表盘 API（真实后端实现）
 *
 * 单次聚合首页所需的各模块摘要数据。
 */
import request from './request'

/**
 * 获取仪表盘聚合数据
 * @returns {Promise<{ code: 0, message: string, data: {
 *   today: string,
 *   todo: { total: number, doing: number, done: number },
 *   todayTodos: Array<{ id: number, title: string, status: string }>,
 *   noteCount: number,
 *   recentNotes: Array<{ id: number, content: string, color: string, createdAt: string }>,
 *   scheduleCount: number,
 *   todaySchedules: Array<{ id: number, title: string, start: string|null, allDay: boolean }>
 * } }>}
 */
export async function getDashboardApi() {
  return request.get('/dashboard')
}
