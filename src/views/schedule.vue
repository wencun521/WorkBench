<template>
  <div class="schedule-page">
    <el-card class="schedule-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>日程日历</span>
          <el-button type="primary" @click="openCreate">新增日程</el-button>
        </div>
      </template>

      <div class="schedule-layout">
        <!-- 左：月历 -->
        <el-calendar v-model="calendarDate">
          <template #date-cell="{ data }">
            <div class="day-cell" :class="{ 'is-selected': data.isSelected }">
              <span class="day-num" :class="{ dim: data.type !== 'current-month' }">
                {{ Number(data.day.slice(8)) }}
              </span>
              <div v-if="dotsByDate[data.day]" class="day-dots">
                <span
                  v-for="s in dotsByDate[data.day].slice(0, 3)"
                  :key="s.id"
                  class="schedule-dot"
                  :class="{ 'all-day': s.allDay }"
                  :title="s.title"
                />
                <span v-if="dotsByDate[data.day].length > 3" class="dots-more">
                  +{{ dotsByDate[data.day].length - 3 }}
                </span>
              </div>
            </div>
          </template>
        </el-calendar>

        <!-- 參：当日列表 -->
        <el-card class="day-list-card" shadow="never">
          <template #header>
            <div class="day-list-header">
              <span class="day-list-title">{{ selectedDateLabel }}</span>
              <el-button size="small" type="primary" plain @click="openCreate">新增</el-button>
            </div>
          </template>
          <div v-loading="loading" class="day-list">
            <el-empty
              v-if="!loading && daySchedules.length === 0"
              description="当天暂无日程"
              :image-size="72"
            />
            <div v-for="s in daySchedules" :key="s.id" class="day-item">
              <span class="item-time" :class="{ 'all-day': s.allDay }">
                {{ s.allDay ? '全天' : `${s.start || ''}${s.end ? ' - ' + s.end : ''}` }}
              </span>
              <div class="item-main">
                <p class="item-title">{{ s.title }}</p>
                <p v-if="s.note" class="item-note">{{ s.note }}</p>
              </div>
              <div class="item-actions">
                <el-tooltip content="编辑" placement="top">
                  <el-icon class="action-icon" :size="14" @click="openEdit(s)">
                    <EditPen />
                  </el-icon>
                </el-tooltip>
                <el-popconfirm title="确定删除该日程吗？" @confirm="handleDelete(s)">
                  <template #reference>
                    <el-icon class="action-icon danger" :size="14">
                      <Delete />
                    </el-icon>
                  </template>
                </el-popconfirm>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- 新增 / 编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑日程' : '新增日程'"
      width="480px"
      @opened="focusTitleInput"
    >
      <el-form label-position="top">
        <el-form-item label="标题" required>
          <el-input ref="titleInputRef" v-model="form.title" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="日期" required>
          <el-date-picker
            v-model="form.date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item>
          <div class="form-row">
            <el-switch v-model="form.allDay" active-text="全天" />
            <el-time-select
              v-model="form.start"
              :disabled="form.allDay"
              start="00:00"
              step="00:15"
              end="23:45"
              placeholder="开始"
              style="width: 120px"
            />
            <span class="time-sep" :class="{ disabled: form.allDay }">—</span>
            <el-time-select
              v-model="form.end"
              :disabled="form.allDay"
              :min-time="form.start || undefined"
              start="00:00"
              step="00:15"
              end="23:45"
              placeholder="结束"
              style="width: 120px"
            />
          </div>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="form.note"
            type="textarea"
            :rows="2"
            maxlength="500"
            show-word-limit
            placeholder="选填"
          />
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
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { EditPen, Delete } from '@element-plus/icons-vue'
import {
  BIZ_CODE,
  listSchedulesApi,
  createScheduleApi,
  updateScheduleApi,
  deleteScheduleApi
} from '@/api/schedule'
import { useUnauthorizedHandler } from '@/composables/useAuth'

const onUnauthorized = useUnauthorizedHandler()

const loading = ref(false)
const saving = ref(false)

/* 日历状态：calendarDate 由 el-calendar 维护（点击日期/切换月份都会更新） */
const calendarDate = ref(new Date())
const selectedDate = ref(formatDay(new Date()))
const monthSchedules = ref([])

function formatDay(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

/* 月份变化（含首次）时拉取当月日程 */
const monthKey = computed(() => formatDay(calendarDate.value).slice(0, 7))
watch(monthKey, fetchMonth, { immediate: true })

async function fetchMonth() {
  const ym = monthKey.value
  const [y, m] = ym.split('-').map(Number)
  const lastDay = new Date(y, m, 0).getDate()
  loading.value = true
  try {
    const res = await listSchedulesApi({ start: `${ym}-01`, end: `${ym}-${lastDay}` })
    monthSchedules.value = res.data.list
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    ElMessage.error(err.message || '加载日程失败')
  } finally {
    loading.value = false
  }
}

/* 点选日期同步选中日 */
watch(calendarDate, (d) => {
  selectedDate.value = formatDay(d)
})

const selectedDateLabel = computed(() => {
  const [y, m, d] = selectedDate.value.split('-')
  return `${Number(m)} 月 ${Number(d)} 日`
})

/* 当月日程按日期分桶，供月历圆点与当日列表使用 */
const dotsByDate = computed(() => {
  const map = {}
  for (const s of monthSchedules.value) {
    ;(map[s.date] = map[s.date] || []).push(s)
  }
  return map
})

const daySchedules = computed(() => dotsByDate.value[selectedDate.value] || [])

/* 新增 / 编辑 */
const dialogVisible = ref(false)
const editingId = ref(null)
const titleInputRef = ref(null)
const form = reactive({ title: '', date: '', start: '', end: '', allDay: false, note: '' })

const focusTitleInput = () => {
  titleInputRef.value?.focus?.()
}

const openCreate = () => {
  editingId.value = null
  Object.assign(form, {
    title: '',
    date: selectedDate.value,
    start: '',
    end: '',
    allDay: false,
    note: ''
  })
  dialogVisible.value = true
}

const openEdit = (s) => {
  editingId.value = s.id
  Object.assign(form, {
    title: s.title,
    date: s.date,
    start: s.start || '',
    end: s.end || '',
    allDay: s.allDay,
    note: s.note
  })
  dialogVisible.value = true
}

const handleSave = async () => {
  const title = form.title.trim()
  if (!title) {
    ElMessage.warning('请输入日程标题')
    return
  }
  if (!form.date) {
    ElMessage.warning('请选择日期')
    return
  }
  saving.value = true
  try {
    if (editingId.value) {
      const res = await updateScheduleApi(editingId.value, {
        title,
        date: form.date,
        start: form.allDay ? null : form.start || null,
        end: form.allDay ? null : form.end || null,
        allDay: form.allDay,
        note: form.note.trim()
      })
      // 更新当月缓存
      const index = monthSchedules.value.findIndex((x) => x.id === editingId.value)
      if (index !== -1) {
        if (res.data.date.slice(0, 7) === monthKey.value) {
          monthSchedules.value.splice(index, 1, res.data)
        } else {
          monthSchedules.value.splice(index, 1)
        }
      }
      ElMessage.success('保存成功')
    } else {
      const res = await createScheduleApi({
        title,
        date: form.date,
        start: form.allDay ? null : form.start || null,
        end: form.allDay ? null : form.end || null,
        allDay: form.allDay,
        note: form.note.trim()
      })
      if (res.data.date.slice(0, 7) === monthKey.value) {
        monthSchedules.value.push(res.data)
      }
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

const handleDelete = async (s) => {
  try {
    await deleteScheduleApi(s.id)
    monthSchedules.value = monthSchedules.value.filter((x) => x.id !== s.id)
    ElMessage.success('删除成功')
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    ElMessage.error(err.message || '删除失败')
  }
}

onMounted(() => {
  // monthKey 的 immediate watch 已处理首月加载
})
</script>

<style scoped>
.schedule-page {
  max-width: 1000px;
  margin: 0 auto;
}
.schedule-card {
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
.schedule-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(260px, 1fr);
  gap: 20px;
  align-items: start;
}
@media (max-width: 900px) {
  .schedule-layout {
    grid-template-columns: 1fr;
  }
}
/* 月历单元格 */
.day-cell {
  height: 100%;
  min-height: 56px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 2px;
}
.day-num {
  font-size: 13px;
  color: #1f2329;
}
.day-num.dim {
  color: #c0c4cc;
}
.day-dots {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 3px;
}
.schedule-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #409eff;
}
.schedule-dot.all-day {
  background: #67c23a;
}
.dots-more {
  font-size: 10px;
  color: #909399;
}
/* 当日列表 */
.day-list-card {
  border-radius: 12px;
  border: 1px solid #e8e9eb;
}
.day-list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.day-list-title {
  font-size: 15px;
  font-weight: 600;
  color: #1f2329;
}
.day-list {
  min-height: 120px;
}
.day-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 4px;
  border-bottom: 1px solid #f0f0f0;
}
.day-item:last-child {
  border-bottom: none;
}
.item-time {
  flex-shrink: 0;
  font-size: 12px;
  color: #409eff;
  min-width: 70px;
  padding-top: 2px;
}
.item-time.all-day {
  color: #67c23a;
}
.item-main {
  flex: 1;
  min-width: 0;
}
.item-title {
  margin: 0;
  font-size: 14px;
  color: #1f2329;
  word-break: break-word;
}
.item-note {
  margin: 4px 0 0;
  font-size: 12px;
  color: #909399;
  white-space: pre-wrap;
  word-break: break-word;
}
.item-actions {
  display: flex;
  gap: 10px;
  opacity: 0;
  transition: opacity 0.2s;
}
.day-item:hover .item-actions {
  opacity: 1;
}
@media (hover: none) {
  .item-actions {
    opacity: 1;
  }
}
.action-icon {
  color: #a0a2a8;
  cursor: pointer;
  transition: color 0.2s;
  margin-top: 2px;
}
.action-icon:hover {
  color: #409eff;
}
.action-icon.danger:hover {
  color: #f56c6c;
}
/* 弹窗表单 */
.form-row {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}
.time-sep {
  color: #909399;
}
.time-sep.disabled {
  color: #c0c4cc;
}
</style>
