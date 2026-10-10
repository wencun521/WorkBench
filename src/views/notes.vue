<template>
  <div class="notes-page">
    <el-card class="notes-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>便签</span>
          <el-button type="primary" @click="openCreate">新建便签</el-button>
        </div>
      </template>

      <div v-loading="loading" class="notes-list">
        <el-empty v-if="!loading && noteList.length === 0" description="暂无便签，记录点文字吧" />
        <div v-else class="notes-grid">
          <div
            v-for="note in noteList"
            :key="note.id"
            class="note-item"
            :style="{ background: colorHex(note.color) }"
          >
            <el-icon
              v-if="note.pinned"
              class="pin-icon"
              :size="16"
              title="已置顶"
            >
              <Top />
            </el-icon>
            <p class="note-content">{{ note.content }}</p>
            <div class="note-footer">
              <span class="note-time">{{ formatTime(note.createdAt) }}</span>
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
                <el-popconfirm title="确定删除该便签吗？" @confirm="handleDelete(note)">
                  <template #reference>
                    <el-icon class="action-icon danger" :size="15">
                      <Delete />
                    </el-icon>
                  </template>
                </el-popconfirm>
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
    >
      <el-input
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
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Top, EditPen, Delete } from '@element-plus/icons-vue'
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

const dialogVisible = ref(false)
const editingId = ref(null)
const form = reactive({ content: '', color: 'yellow' })

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
      noteList.value.unshift(res.data)
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

const handleDelete = async (note) => {
  try {
    await deleteNoteApi(note.id)
    noteList.value = noteList.value.filter((n) => n.id !== note.id)
    ElMessage.success('删除成功')
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    ElMessage.error(err.message || '删除失败')
  }
}

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
.notes-list {
  min-height: 160px;
}
.notes-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
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
  margin: 0 0 12px;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-word;
  padding-right: 20px;
}
.note-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.note-time {
  font-size: 12px;
  color: #a0a2a8;
}
.note-actions {
  display: flex;
  gap: 12px;
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
