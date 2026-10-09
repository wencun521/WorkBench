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
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { listTodoApi, BIZ_CODE } from '@/api/todo'
import { useUnauthorizedHandler } from '@/composables/useAuth'

const onUnauthorized = useUnauthorizedHandler()

const todoList = ref([])

const stats = computed(() => ({
  total: todoList.value.length,
  completed: todoList.value.filter((t) => t.completed).length,
  pending: todoList.value.filter((t) => !t.completed).length
}))

onMounted(async () => {
  try {
    const res = await listTodoApi()
    todoList.value = res.data.list
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    // 统计数据加载失败不阻塞页面，静默降级为 0
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
</style>
