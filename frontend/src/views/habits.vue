<template>
  <div class="habits-page">
    <el-card class="habits-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>习惯打卡</span>
          <el-button type="primary" @click="openCreate">新建习惯</el-button>
        </div>
      </template>

      <div v-loading="loading" class="habits-list">
        <el-empty v-if="!loading && habitList.length === 0" description="还没有习惯，建一个开始打卡吧" />
        <div v-for="habit in habitList" :key="habit.id" class="habit-row">
          <!-- 色点 + 名称 + streak -->
          <span class="habit-dot" :style="{ background: colorHex(habit.color) }" />
          <div class="habit-main">
            <span class="habit-name">{{ habit.name }}</span>
            <span v-if="habit.streak > 0" class="streak-badge">连续 {{ habit.streak }} 天</span>
          </div>

          <!-- 近 7 天圆点网格 -->
          <div class="last7">
            <div v-for="d in habit.last7" :key="d.date" class="last7-cell" :title="d.date">
              <span
                class="day-dot"
                :class="{ checked: d.checked }"
                :style="d.checked ? { background: colorHex(habit.color) } : null"
              />
            </div>
          </div>

          <!-- 今日打卡 -->
          <el-button
            :type="habit.todayChecked ? 'success' : 'primary'"
            :plain="!habit.todayChecked"
            size="small"
            round
            @click="handleToggleCheckin(habit)"
          >
            {{ habit.todayChecked ? '已打卡' : '打卡' }}
          </el-button>

          <!-- 操作 -->
          <div class="habit-actions">
            <el-tooltip content="编辑" placement="top">
              <el-icon class="action-icon" :size="15" @click="openEdit(habit)">
                <EditPen />
              </el-icon>
            </el-tooltip>
            <el-popconfirm title="删除习惯将同时清除其打卡记录，确定吗？" width="240" @confirm="handleDelete(habit)">
              <template #reference>
                <el-icon class="action-icon danger" :size="15">
                  <Delete />
                </el-icon>
              </template>
            </el-popconfirm>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 新增 / 编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑习惯' : '新建习惯'"
      width="420px"
      @opened="focusNameInput"
    >
      <el-form label-position="top">
        <el-form-item label="名称" required>
          <el-input ref="nameInputRef" v-model="form.name" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="颜色标记">
          <div class="color-picker">
            <span
              v-for="c in HABIT_COLORS"
              :key="c.value"
              class="color-swatch"
              :class="{ selected: form.color === c.value }"
              :style="{ background: c.hex }"
              @click="form.color = c.value"
            />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { EditPen, Delete } from '@element-plus/icons-vue'
import {
  BIZ_CODE,
  HABIT_COLORS,
  listHabitsApi,
  createHabitApi,
  updateHabitApi,
  deleteHabitApi,
  checkinHabitApi,
  uncheckinHabitApi
} from '@/api/habit'
import { useUnauthorizedHandler } from '@/composables/useAuth'

const onUnauthorized = useUnauthorizedHandler()

const loading = ref(false)
const saving = ref(false)
const habitList = ref([])

const dialogVisible = ref(false)
const editingId = ref(null)
const nameInputRef = ref(null)
const form = reactive({ name: '', color: 'blue' })

const colorHex = (value) => {
  return HABIT_COLORS.find((c) => c.value === value)?.hex || HABIT_COLORS[1].hex
}

const fetchList = async () => {
  loading.value = true
  try {
    const res = await listHabitsApi()
    habitList.value = res.data.list
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    ElMessage.error(err.message || '加载习惯失败')
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  editingId.value = null
  form.name = ''
  form.color = 'blue'
  dialogVisible.value = true
}

const openEdit = (habit) => {
  editingId.value = habit.id
  form.name = habit.name
  form.color = habit.color
  dialogVisible.value = true
}

const focusNameInput = () => {
  nameInputRef.value?.focus?.()
}

const handleSave = async () => {
  const name = form.name.trim()
  if (!name) {
    ElMessage.warning('请输入习惯名称')
    return
  }
  saving.value = true
  try {
    if (editingId.value) {
      const res = await updateHabitApi(editingId.value, { name, color: form.color })
      const index = habitList.value.findIndex((h) => h.id === editingId.value)
      if (index !== -1) {
        Object.assign(habitList.value[index], res.data)
      }
      ElMessage.success('保存成功')
    } else {
      const res = await createHabitApi({ name, color: form.color })
      habitList.value.push(res.data)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    ElMessage.error(err.message || '保存失败')
  } finally {
    saving.value = false
  }
}

/* 今日打卡 / 取消打卡（后端幂等，直接用返回摘要替换本行） */
const handleToggleCheckin = async (habit) => {
  try {
    const res = habit.todayChecked
      ? await uncheckinHabitApi(habit.id)
      : await checkinHabitApi(habit.id)
    const index = habitList.value.findIndex((h) => h.id === habit.id)
    if (index !== -1) {
      habitList.value[index] = res.data
    }
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    ElMessage.error(err.message || '打卡失败')
  }
}

const handleDelete = async (habit) => {
  try {
    await deleteHabitApi(habit.id)
    habitList.value = habitList.value.filter((h) => h.id !== habit.id)
    ElMessage.success('删除成功')
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    ElMessage.error(err.message || '删除失败')
  }
}

onMounted(fetchList)
</script>

<style scoped>
.habits-page {
  max-width: 900px;
  margin: 0 auto;
}
.habits-card {
  border-radius: 12px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.card-header span {
  font-size: 18px;
  font-weight: 600;
  color: #1f2329;
}
.habits-list {
  min-height: 120px;
}
.habit-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 4px;
  border-bottom: 1px solid #f0f0f0;
}
.habit-row:last-child {
  border-bottom: none;
}
.habit-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.habit-main {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.habit-name {
  font-size: 14px;
  color: #1f2329;
}
.streak-badge {
  font-size: 11px;
  line-height: 1;
  padding: 3px 6px;
  border-radius: 4px;
  color: #e6a23c;
  background: #fbf0dc;
}
/* 近 7 天网格 */
.last7 {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
.last7-cell {
  width: 14px;
  height: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.day-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #e8e9eb;
}
.day-dot.checked {
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.04) inset;
}
.habit-actions {
  display: flex;
  gap: 10px;
  opacity: 0;
  transition: opacity 0.2s;
}
.habit-row:hover .habit-actions {
  opacity: 1;
}
@media (hover: none) {
  .habit-actions {
    opacity: 1;
  }
}
.action-icon {
  color: #a0a2a8;
  cursor: pointer;
  transition: color 0.2s;
}
.action-icon:hover {
  color: #409eff;
}
.action-icon.danger:hover {
  color: #f56c6c;
}
.color-picker {
  display: flex;
  gap: 12px;
}
.color-swatch {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  box-sizing: content-box;
  transition: transform 0.15s;
}
.color-swatch:hover {
  transform: scale(1.1);
}
.color-swatch.selected {
  border-color: #409eff;
}
</style>
