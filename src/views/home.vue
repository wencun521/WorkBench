<template>
  <div class="home">
    <!-- 欢迎卡片：预留全局搜索与提醒机制挂载点 -->
    <el-card class="welcome-card" shadow="never">
      <h1>欢迎回来</h1>
      <p>今天是 {{ dash.today }}，以下是你的工作台概览。</p>
      <!-- TODO: 全局搜索（Ctrl+K）挂载点 -->
      <div class="search-slot"></div>
      <!-- TODO: 提醒机制挂载点（到期任务/日程提醒） -->
    </el-card>

    <!-- 模块入口卡 -->
    <div class="entry-row">
      <el-card
        v-for="entry in entries"
        :key="entry.path"
        class="entry-card"
        shadow="never"
        @click="router.push(entry.path)"
      >
        <div class="entry-head">
          <span class="entry-icon" :style="{ background: entry.soft, color: entry.color }">
            <el-icon :size="16"><component :is="entry.icon" /></el-icon>
          </span>
          <span class="entry-arrow">›</span>
        </div>
        <div class="entry-name">{{ entry.title }}</div>
        <div class="entry-summary">{{ entry.summary }}</div>
      </el-card>
    </div>

    <!-- 今日概览 -->
    <el-card class="today-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>今日概览</span>
          <span class="header-tip">只读摘要，点击条目前往对应模块</span>
        </div>
      </template>
      <div class="today-grid">
        <!-- 左：今日待办 -->
        <div class="today-block">
          <div class="block-title">待办事项</div>
          <p v-if="dash.todayTodos.length === 0" class="block-empty">今天没有待办，去看看列表吧</p>
          <div
            v-for="todo in dash.todayTodos"
            :key="todo.id"
            class="today-item"
            @click="router.push('/todo')"
          >
            <span class="status-chip" :class="todo.status">{{ statusText(todo.status) }}</span>
            <span class="item-brief">{{ todo.title }}</span>
          </div>
        </div>
        <!-- 右：今日日程 -->
        <div class="today-block">
          <div class="block-title">今日日程</div>
          <p v-if="dash.todaySchedules.length === 0" class="block-empty">今天没有日程安排</p>
          <div
            v-for="s in dash.todaySchedules"
            :key="s.id"
            class="today-item"
            @click="router.push('/schedule')"
          >
            <span class="schedule-time">{{ s.allDay ? '全天' : s.start }}</span>
            <span class="item-brief">{{ s.title }}</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 最近便签 -->
    <el-card class="recent-notes-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>最近便签</span>
          <el-link type="primary" :underline="false" @click="router.push('/notes')">查看全部</el-link>
        </div>
      </template>
      <div v-loading="loading" class="recent-notes">
        <p v-if="!loading && dash.recentNotes.length === 0" class="notes-empty">暂无便签，去便签页记录点文字吧</p>
        <div
          v-for="note in dash.recentNotes"
          :key="note.id"
          class="recent-note-item"
          @click="router.push('/notes')"
        >
          <span class="color-dot" :style="{ background: noteColorHex(note.color) }" />
          <span class="note-brief">{{ note.content }}</span>
          <span class="note-date">{{ formatDate(note.createdAt) }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, markRaw, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Tickets, Grid, Memo, Calendar, Finished, Timer } from '@element-plus/icons-vue'
import { getDashboardApi } from '@/api/dashboard'
import { NOTE_COLORS } from '@/api/note'
import { useUnauthorizedHandler } from '@/composables/useAuth'

const router = useRouter()
const onUnauthorized = useUnauthorizedHandler()

const loading = ref(false)

const dash = reactive({
  today: '',
  todo: { total: 0, doing: 0, done: 0 },
  todayTodos: [],
  noteCount: 0,
  recentNotes: [],
  scheduleCount: 0,
  todaySchedules: [],
  habit: { total: 0, doneToday: 0 },
  pomodoro: { todayCount: 0 }
})

const statusText = (status) =>
  ({ todo: '待办', doing: '进行中', done: '已完成' })[status] || status

const noteColorHex = (value) => {
  return NOTE_COLORS.find((c) => c.value === value)?.hex || NOTE_COLORS[0].hex
}

const formatDate = (iso) => {
  if (!iso) return ''
  return iso.replace('T', ' ').slice(5, 10)
}

/* 模块入口卡：数字摘要来自聚合数据 */
const entries = computed(() => [
  {
    path: '/todo', title: '待办事项', icon: markRaw(Tickets),
    color: '#409eff', soft: '#ecf5ff',
    summary: `进行中 ${dash.todo.doing} · 已完成 ${dash.todo.done}`
  },
  {
    path: '/kanban', title: '任务看板', icon: markRaw(Grid),
    color: '#7367f0', soft: '#f0effd',
    summary: `共 ${dash.todo.total} 项任务`
  },
  {
    path: '/schedule', title: '日程日历', icon: markRaw(Calendar),
    color: '#67c23a', soft: '#eaf4e3',
    summary: `今日 ${dash.scheduleCount} 项安排`
  },
  {
    path: '/notes', title: '便签', icon: markRaw(Memo),
    color: '#e6a23c', soft: '#fbf0dc',
    summary: `共 ${dash.noteCount} 条便签`
  },
  {
    path: '/habits', title: '习惯打卡', icon: markRaw(Finished),
    color: '#f56c6c', soft: '#fde2e2',
    summary: `今日 ${dash.habit.doneToday}/${dash.habit.total} 已打卡`
  },
  {
    path: '/pomodoro', title: '番茄钟', icon: markRaw(Timer),
    color: '#1dc981', soft: '#e5fff2',
    summary: `今日 ${dash.pomodoro.todayCount} 个专注`
  }
])

onMounted(async () => {
  loading.value = true
  try {
    const res = await getDashboardApi()
    Object.assign(dash, res.data)
  } catch (err) {
    if (err.code === 40100) {
      onUnauthorized()
      return
    }
    // 仪表盘加载失败不阻塞页面，静默降级为 0/空列表
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.home {
  max-width: 900px;
  margin: 0 auto;
}
.welcome-card {
  border-radius: 12px;
  text-align: center;
  margin-bottom: 20px;
}
.welcome-card h1 {
  margin: 8px 0 12px;
  font-size: 22px;
  color: #1f2329;
}
.welcome-card p {
  margin: 0 0 12px;
  color: #909399;
}
.search-slot {
  min-height: 1px;
}
/* 模块入口卡 */
.entry-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}
.entry-card {
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.2s;
}
.entry-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.entry-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.entry-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 8px;
}
.entry-arrow {
  color: #c0c4cc;
  font-size: 18px;
}
.entry-name {
  margin-top: 10px;
  font-size: 15px;
  font-weight: 600;
  color: #1f2329;
}
.entry-summary {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}
/* 今日概览 */
.today-card {
  border-radius: 12px;
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.card-header span {
  font-size: 16px;
  font-weight: 600;
  color: #1f2329;
}
.header-tip {
  font-size: 12px;
  font-weight: 400;
  color: #c0c4cc;
}
.today-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}
.block-title {
  font-size: 13px;
  font-weight: 600;
  color: #909399;
  margin-bottom: 8px;
}
.block-empty {
  margin: 8px 0;
  font-size: 13px;
  color: #c0c4cc;
}
.today-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 4px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}
.today-item:last-child {
  border-bottom: none;
}
.today-item:hover .item-brief {
  color: #409eff;
}
.status-chip {
  flex-shrink: 0;
  font-size: 11px;
  line-height: 1;
  padding: 3px 6px;
  border-radius: 4px;
}
.status-chip.todo {
  color: #909399;
  background: #f0f1f4;
}
.status-chip.doing {
  color: #e6a23c;
  background: #fbf0dc;
}
.status-chip.done {
  color: #67c23a;
  background: #eaf4e3;
}
.schedule-time {
  flex-shrink: 0;
  font-size: 12px;
  color: #909399;
  min-width: 34px;
}
.item-brief {
  flex: 1;
  font-size: 14px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.2s;
}
/* 最近便签 */
.recent-notes-card {
  border-radius: 12px;
}
.recent-notes {
  min-height: 40px;
}
.notes-empty {
  margin: 8px 0;
  font-size: 13px;
  color: #909399;
  text-align: center;
}
.recent-note-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 4px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
}
.recent-note-item:last-child {
  border-bottom: none;
}
.recent-note-item:hover .note-brief {
  color: #409eff;
}
.color-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.note-date {
  font-size: 12px;
  color: #c0c4cc;
  flex-shrink: 0;
}
</style>
