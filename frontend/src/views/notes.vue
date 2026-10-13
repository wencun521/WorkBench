<template>
  <div class="notes-page">
    <el-card class="notes-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>便签</span>
          <el-button type="primary" @click="openCreate">新建便签</el-button>
        </div>
      </template>

      <!-- 搜索 + 颜色筛选 -->
      <div class="notes-toolbar">
        <el-input
          v-model="keyword"
          class="search-input"
          placeholder="搜索便签内容"
          clearable
          :prefix-icon="Search"
        />
        <div class="color-filter">
          <span
            class="filter-all"
            :class="{ active: filterColor === '' }"
            @click="filterColor = ''"
          >全部</span>
          <span
            v-for="c in NOTE_COLORS"
            :key="c.value"
            class="filter-swatch"
            :class="{ active: filterColor === c.value }"
            :style="{ background: c.hex }"
            :title="c.value"
            @click="filterColor = filterColor === c.value ? '' : c.value"
          />
        </div>
      </div>

      <div v-loading="loading" class="notes-list">
        <el-empty
          v-if="!loading && filteredNotes.length === 0"
          :description="noteList.length === 0 ? '暂无便签，记录点文字吧' : '没有匹配的便签'"
        >
          <el-button v-if="noteList.length === 0" type="primary" @click="openCreate">新建便签</el-button>
        </el-empty>
        <div v-else class="notes-grid">
          <div
            v-for="note in filteredNotes"
            :key="note.id"
            class="note-item"
            :style="{ background: colorHex(note.color) }"
            :title="'双击编辑'"
            @dblclick="openEdit(note)"
          >
            <el-icon
              v-if="note.pinned"
              class="pin-icon"
              :size="16"
              title="已置顶"
            >
              <Top />
            </el-icon>
            <p class="note-content" :class="{ clamped: isClamped(note) }">{{ note.content }}</p>
            <span
              v-if="isLong(note)"
              class="expand-link"
              @click="toggleExpand(note)"
            >{{ expandedIds.has(note.id) ? '收起' : '展开' }}</span>
            <div class="note-footer">
              <div class="note-meta">
                <span class="note-time">{{ formatTime(note.createdAt) }}</span>
                <span v-if="isEdited(note)" class="edited-tag">已编辑</span>
              </div>
              <div class="note-actions">
                <el-tooltip :content="note.pinned ? '取消置顶' : '置顶'" placement="top">
                  <el-icon
                    class="action-icon"
                    :class="{ active: note.pinned }"
                    :size="15"
                    @click="handleTogglePin(note)"
                  >
                    <Top />
                  </el-icon>
                </el-tooltip>
                <el-icon class="action-icon" :size="15" @click="openEdit(note)">
                  <EditPen />
                </el-icon>
                <el-tooltip content="删除" placement="top">
                  <el-icon class="action-icon danger" :size="15" @click="handleDelete(note)">
                    <Delete />
                  </el-icon>
                </el-tooltip>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 新建 / 编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑便签' : '新建便签'"
      width="520px"
      @opened="focusContentInput"
    >
      <el-input
        ref="contentInputRef"
        v-model="form.content"
        type="textarea"
        :rows="5"
        maxlength="500"
        show-word-limit
        placeholder="记录点文字..."
      />
      <div class="color-picker">
        <span
          v-for="c in NOTE_COLORS"
          :key="c.value"
          class="color-swatch"
          :class="{ selected: form.color === c.value }"
          :style="{ background: c.hex }"
          @click="form.color = c.value"
        />
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, h, onMounted, onUnmounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Top, EditPen, Delete, Search } from '@element-plus/icons-vue'
import {
  BIZ_CODE,
  NOTE_COLORS,
  listNotesApi,
  createNoteApi,
  updateNoteApi,
  deleteNoteApi
} from '@/api/note'
import { useUnauthorizedHandler } from '@/composables/useAuth'

const onUnauthorized = useUnauthorizedHandler()

const loading = ref(false)
const saving = ref(false)
const noteList = ref([])

/* 搜索 + 颜色筛选 */
const keyword = ref('')
const filterColor = ref('')

const filteredNotes = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  return noteList.value.filter((n) => {
    if (kw && !n.content.toLowerCase().includes(kw)) return false
    if (filterColor.value && n.color !== filterColor.value) return false
    return true
  })
})

/* 长内容折叠：超阈值可展开，默认收起（CSS 限 6 行） */
const CLAMP_THRESHOLD = 120
const expandedIds = ref(new Set())

const isLong = (note) => note.content.length > CLAMP_THRESHOLD
const isClamped = (note) => isLong(note) && !expandedIds.value.has(note.id)

const toggleExpand = (note) => {
  const next = new Set(expandedIds.value)
  next.has(note.id) ? next.delete(note.id) : next.add(note.id)
  expandedIds.value = next
}

const dialogVisible = ref(false)
const editingId = ref(null)
const form = reactive({ content: '', color: 'yellow' })
const contentInputRef = ref(null)

/* 弹窗动画结束后聚焦输入框 */
const focusContentInput = () => {
  contentInputRef.value?.focus()
}

/* 是否编辑过：updatedAt 存在且与创建时间（秒级精度）不同；
   旧数据 ALTER 后 updatedAt 为 null，视为未编辑；
   新建时两值由两次 utcnow() 生成，仅微秒级差异，按秒比较视为未编辑 */
const isEdited = (note) => {
  return !!note.updatedAt && note.updatedAt.slice(0, 19) !== note.createdAt.slice(0, 19)
}

const colorHex = (value) => {
  return NOTE_COLORS.find((c) => c.value === value)?.hex || NOTE_COLORS[0].hex
}

const fetchList = async () => {
  loading.value = true
  try {
    const res = await listNotesApi()
    noteList.value = res.data.list
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    ElMessage.error(err.message || '加载便签失败')
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  editingId.value = null
  form.content = ''
  form.color = 'yellow'
  dialogVisible.value = true
}

const openEdit = (note) => {
  editingId.value = note.id
  form.content = note.content
  form.color = note.color
  dialogVisible.value = true
}

const handleSave = async () => {
  const content = form.content.trim()
  if (!content) {
    ElMessage.warning('请输入便签内容')
    return
  }
  saving.value = true
  try {
    if (editingId.value) {
      const res = await updateNoteApi(editingId.value, {
        content,
        color: form.color
      })
      const index = noteList.value.findIndex((n) => n.id === editingId.value)
      if (index !== -1) {
        Object.assign(noteList.value[index], res.data)
      }
      ElMessage.success('保存成功')
    } else {
      const res = await createNoteApi({ content, color: form.color })
      // 与后端排序规则一致（置顶在前 + 时间倒序），避免新便签插到置顶便签之前
      noteList.value = [res.data, ...noteList.value].sort(
        (a, b) => Number(b.pinned) - Number(a.pinned) || b.createdAt.localeCompare(a.createdAt)
      )
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

const handleTogglePin = async (note) => {
  try {
    const res = await updateNoteApi(note.id, { pinned: !note.pinned })
    // 置顶状态变化会影响排序，直接用后端返回刷新本条并重排
    Object.assign(note, res.data)
    noteList.value = [...noteList.value].sort(
      (a, b) => Number(b.pinned) - Number(a.pinned) || b.createdAt.localeCompare(a.createdAt)
    )
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    ElMessage.error(err.message || '操作失败')
  }
}

/* 删除撤销：先本地移除，5 秒后真正调删除接口；期间可撤销恢复 */
const pendingTimers = new Map()
const UNDO_WINDOW = 5000

const handleDelete = (note) => {
  const index = noteList.value.indexOf(note)
  if (index === -1) return
  noteList.value.splice(index, 1)

  // 若已有同 id 的待删除任务，先清理
  clearPending(note.id)

  const msg = ElMessage({
    type: 'success',
    duration: UNDO_WINDOW,
    message: h('span', null, [
      '已删除便签',
      h(
        'a',
        {
          style: { color: '#409eff', marginLeft: '8px', cursor: 'pointer' },
          onClick: () => undoDelete(note, index, msg)
        },
        '撤销'
      )
    ])
  })

  const timer = setTimeout(async () => {
    pendingTimers.delete(note.id)
    try {
      await deleteNoteApi(note.id)
    } catch (err) {
      if (err.code === BIZ_CODE.UNAUTHORIZED) {
        onUnauthorized()
        return
      }
      // 删除失败：恢复到原位置
      noteList.value.splice(Math.min(index, noteList.value.length), 0, note)
      ElMessage.error(err.message || '删除失败，已恢复该便签')
    }
  }, UNDO_WINDOW)
  pendingTimers.set(note.id, timer)
}

const undoDelete = (note, index, msg) => {
  clearPending(note.id)
  noteList.value.splice(Math.min(index, noteList.value.length), 0, note)
  msg.close()
}

const clearPending = (id) => {
  const timer = pendingTimers.get(id)
  if (timer) {
    clearTimeout(timer)
    pendingTimers.delete(id)
  }
}

// 离开页面前取消尚未落库的删除（接口未调，数据无变化，无需恢复）
onUnmounted(() => {
  pendingTimers.forEach((timer) => clearTimeout(timer))
  pendingTimers.clear()
})

const formatTime = (iso) => {
  if (!iso) return ''
  return iso.replace('T', ' ').slice(0, 16)
}

onMounted(fetchList)
</script>

<style scoped>
.notes-page {
  max-width: 900px;
  margin: 0 auto;
}
.notes-card {
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
/* 搜索 + 筛选工具条 */
.notes-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}
.search-input {
  width: 260px;
}
.color-filter {
  display: flex;
  align-items: center;
  gap: 10px;
}
.filter-all {
  font-size: 13px;
  color: #909399;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 4px;
}
.filter-all.active {
  color: #409eff;
  background: #ecf5ff;
}
.filter-swatch {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  box-sizing: content-box;
  transition: transform 0.15s;
}
.filter-swatch:hover {
  transform: scale(1.15);
}
.filter-swatch.active {
  border-color: #409eff;
}
.notes-list {
  min-height: 160px;
}
.notes-grid {
  display: grid;
  /* 响应式：宽屏多列，窄屏自动减列 */
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.note-item {
  position: relative;
  padding: 14px 16px 10px;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.2s;
}
.note-item:hover {
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}
.pin-icon {
  position: absolute;
  top: 10px;
  right: 12px;
  color: #606266;
}
.note-content {
  margin: 0 0 4px;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-word;
  padding-right: 20px;
}
/* 长内容折叠：最多显示 6 行 */
.note-content.clamped {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 6;
  line-clamp: 6;
  overflow: hidden;
}
.expand-link {
  display: inline-block;
  margin-bottom: 8px;
  font-size: 12px;
  color: #409eff;
  cursor: pointer;
}
.note-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 4px;
}
.note-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}
.note-time {
  font-size: 12px;
  color: #a0a2a8;
}
.edited-tag {
  font-size: 11px;
  line-height: 1;
  padding: 3px 6px;
  border-radius: 4px;
  color: #909399;
  background: rgba(255, 255, 255, 0.65);
}
.note-actions {
  display: flex;
  gap: 12px;
  /* 悬停显示，触屏设备无 hover 则常显 */
  opacity: 0;
  transition: opacity 0.2s;
}
.note-item:hover .note-actions {
  opacity: 1;
}
@media (hover: none) {
  .note-actions {
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
.action-icon.active {
  color: #e6a23c;
}
.action-icon.danger:hover {
  color: #f56c6c;
}
.color-picker {
  display: flex;
  gap: 12px;
  margin-top: 16px;
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
