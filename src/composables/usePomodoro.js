/**
 * 番茄钟计时器组合式函数（模块级单例）
 *
 * 状态提升到模块作用域：
 *  - 切换页面（组件卸载）后倒计时继续，返回页面不重置
 *  - 专注 / 休息两种模式各自保留剩余时间，来回切换不丢进度
 *  - 一个倒计时走完：蜂鸣 → 专注会话入库 → 自动开始下一阶段
 *  - localStorage 持久化：页面刷新后按墙钟时间恢复剩余秒数（恢复为暂停态）
 */
import { computed, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { savePomodoroApi, pomodoroSummaryApi } from '@/api/pomodoro'
import { useUnauthorizedHandler } from '@/composables/useAuth'

export const FOCUS_SECONDS = 25 * 60
export const BREAK_SECONDS = 5 * 60
const RING_RADIUS = 96
const RING_LENGTH = 2 * Math.PI * RING_RADIUS
const STORAGE_KEY = 'pomodoro-timer-state'

/* ---------- 模块级单例状态（跨组件卸载存活） ---------- */
const mode = ref('focus') // 'focus' | 'break'
const remaining = reactive({ focus: FOCUS_SECONDS, break: BREAK_SECONDS })
const isRunning = ref(false)
const todayCount = ref(0)
const recent = ref([])
const linkedTodoId = ref(null)
const todoOptions = ref([])
const loading = ref(false)

let timer = null
let inited = false
let onUnauthorized = null

const timeText = computed(() => {
  const total = remaining[mode.value]
  const m = Math.floor(total / 60)
  const s = total % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

const ringOffset = computed(() => {
  const full = mode.value === 'focus' ? FOCUS_SECONDS : BREAK_SECONDS
  return String(RING_LENGTH * (1 - remaining[mode.value] / full))
})

/* ---------- 持久化 ---------- */
function persist() {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        mode: mode.value,
        focus: remaining.focus,
        break: remaining.break,
        running: isRunning.value,
        ts: Date.now()
      })
    )
  } catch {
    // 存储不可用时静默跳过
  }
}

function restore() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return
    const s = JSON.parse(raw)
    mode.value = s.mode === 'break' ? 'break' : 'focus'
    let focus = Number.isFinite(s.focus) ? s.focus : FOCUS_SECONDS
    let brk = Number.isFinite(s.break) ? s.break : BREAK_SECONDS
    // 运行中按墙钟折算流逝时间；离开期间走完的会话不补录，恢复为满时长暂停态
    if (s.running && typeof s.ts === 'number') {
      const elapsed = Math.floor((Date.now() - s.ts) / 1000)
      if (mode.value === 'focus') {
        focus = Math.max(0, focus - elapsed)
      } else {
        brk = Math.max(0, brk - elapsed)
      }
    }
    remaining.focus = focus > 0 ? focus : FOCUS_SECONDS
    remaining.break = brk > 0 ? brk : BREAK_SECONDS
  } catch {
    // 数据损坏则忽略，保持默认
  }
}

/* ---------- 计时控制 ---------- */
function stop() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  isRunning.value = false
}

function start() {
  if (timer) return
  isRunning.value = true
  persist()
  timer = setInterval(() => {
    remaining[mode.value] -= 1
    persist()
    if (remaining[mode.value] <= 0) {
      completeSession()
    }
  }, 1000)
}

function toggleRun() {
  isRunning.value ? stop() : start()
}

function resetTimer() {
  stop()
  remaining[mode.value] = mode.value === 'focus' ? FOCUS_SECONDS : BREAK_SECONDS
  persist()
}

function switchMode(m) {
  if (mode.value === m) return
  // 切模式即停表：恢复为暂停态（各模式剩余时间保留），需手动点开始
  stop()
  mode.value = m
  persist()
}

/* ---------- 完成一个倒计时 ---------- */
function beep() {
  try {
    const ctx = new AudioContext()
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    osc.connect(gain)
    gain.connect(ctx.destination)
    osc.type = 'sine'
    osc.frequency.value = 880
    gain.gain.setValueAtTime(0.2, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.6)
    osc.start()
    osc.stop(ctx.currentTime + 0.6)
  } catch {
    // 音频不可用时静默跳过
  }
}

async function completeSession() {
  stop()
  beep()

  if (mode.value === 'focus') {
    try {
      const res = await savePomodoroApi({ todoId: linkedTodoId.value || null })
      todayCount.value += 1
      recent.value.unshift(res.data)
      if (recent.value.length > 10) {
        recent.value.pop()
      }
      ElMessage.success('专注完成，已记录')
    } catch (err) {
      if (err.code === 40100) {
        onUnauthorized()
        return
      }
      ElMessage.error(err.message || '专注记录保存失败')
    }
    remaining.focus = FOCUS_SECONDS
    mode.value = 'break'
  } else {
    ElMessage.success('休息结束，开始下一个番茄吧')
    remaining.break = BREAK_SECONDS
    mode.value = 'focus'
  }
  persist()
  start() // 自动开始下一阶段
}

/* ---------- 数据加载 ---------- */
async function fetchSummary() {
  loading.value = true
  try {
    const res = await pomodoroSummaryApi()
    todayCount.value = res.data.todayCount
    recent.value = res.data.recent
  } catch (err) {
    if (err.code === 40100) {
      onUnauthorized()
      return
    }
    ElMessage.error(err.message || '加载专注记录失败')
  } finally {
    loading.value = false
  }
}

async function fetchTodoOptions() {
  try {
    const res = await (await import('@/api/todo')).listTodoApi()
    // 只推荐未完成的待办作为专注目标
    todoOptions.value = res.data.list.filter((t) => t.status !== 'done')
  } catch {
    // 选项加载失败不阻塞计时器
  }
}

/* ---------- 对外入口（在组件 setup 中调用一次） ---------- */
export function usePomodoro() {
  if (!onUnauthorized) {
    onUnauthorized = useUnauthorizedHandler()
  }
  if (!inited) {
    inited = true
    restore()
    fetchSummary()
    fetchTodoOptions()
  }
  return {
    mode,
    remainingSeconds: computed(() => remaining[mode.value]),
    timeText,
    ringOffset,
    isRunning,
    todayCount,
    recent,
    linkedTodoId,
    todoOptions,
    loading,
    toggleRun,
    resetTimer,
    switchMode
  }
}
