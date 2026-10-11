<template>
  <div class="home">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card" shadow="never">
      <h1>欢迎来到 Admin Pro</h1>
      <p>这里可以接入看板 / 列表等业务模块，左侧菜单可快速切换页面。</p>
    </el-card>

    <!-- 待办统计 -->
    <div class="stat-row">
      <el-card class="stat-card" shadow="never">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">待办总数</div>
      </el-card>
      <el-card class="stat-card" shadow="never">
        <div class="stat-value done">{{ stats.completed }}</div>
        <div class="stat-label">已完成</div>
      </el-card>
      <el-card class="stat-card" shadow="never">
        <div class="stat-value pending">{{ stats.pending }}</div>
        <div class="stat-label">未完成</div>
      </el-card>
    </div>

    <!-- 最近便签速览 -->
    <el-card class="recent-notes-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>最近便签</span>
          <el-link type="primary" :underline="false" @click="router.push('/notes')">查看全部</el-link>
        </div>
      </template>
      <div v-loading="notesLoading" class="recent-notes">
        <p v-if="!notesLoading && recentNotes.length === 0" class="notes-empty">暂无便签，去便签页记录点文字吧</p>
        <div
          v-for="note in recentNotes"
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
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { listTodoApi, BIZ_CODE as TODO_CODE } from '@/api/todo'
import { listNotesApi, BIZ_CODE as NOTE_CODE, NOTE_COLORS } from '@/api/note'
import { useUnauthorizedHandler } from '@/composables/useAuth'

const router = useRouter()
const onUnauthorized = useUnauthorizedHandler()

const todoList = ref([])

const stats = computed(() => ({
  total: todoList.value.length,
  completed: todoList.value.filter((t) => t.completed).length,
  pending: todoList.value.filter((t) => !t.completed).length
}))

/* 最近便签（后端已按置顶+时间排序，取前 3 条） */
const notesLoading = ref(false)
const recentNotes = ref([])

const noteColorHex = (value) => {
  return NOTE_COLORS.find((c) => c.value === value)?.hex || NOTE_COLORS[0].hex
}

const formatDate = (iso) => {
  if (!iso) return ''
  return iso.replace('T', ' ').slice(5, 10)
}

onMounted(async () => {
  try {
    const res = await listTodoApi()
    todoList.value = res.data.list
  } catch (err) {
    if (err.code === TODO_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    // 统计数据加载失败不阻塞页面，静默降级为 0
  }

  notesLoading.value = true
  try {
    const res = await listNotesApi()
    recentNotes.value = res.data.list.slice(0, 3)
  } catch (err) {
    if (err.code === NOTE_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    // 便签速览加载失败不阻塞页面
  } finally {
    notesLoading.value = false
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
.stat-row {
  display: flex;
  gap: 16px;
}
.stat-card {
  flex: 1;
  border-radius: 12px;
  text-align: center;
}
.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #1f2329;
}
.stat-value.done {
  color: #67c23a;
}
.stat-value.pending {
  color: #e6a23c;
}
.stat-label {
  margin-top: 6px;
  font-size: 13px;
  color: #909399;
}
.recent-notes-card {
  border-radius: 12px;
  margin-top: 20px;
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
.note-brief {
  flex: 1;
  font-size: 14px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.2s;
}
.note-date {
  font-size: 12px;
  color: #c0c4cc;
  flex-shrink: 0;
}
</style>
