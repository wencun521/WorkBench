<template>
  <div class="kanban-page">
    <el-card class="kanban-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>任务看板</span>
          <span class="header-tip">拖拽卡片即可调整状态</span>
        </div>
      </template>

      <div v-loading="loading" class="kanban-board">
        <div
          v-for="col in columns"
          :key="col.key"
          class="kanban-column"
          :class="{ 'drop-target': dragOverCol === col.key }"
          @dragover.prevent="dragOverCol = col.key"
          @dragleave="dragOverCol = ''"
          @drop.prevent="handleDrop($event, col.key)"
        >
          <!-- 列头 -->
          <div class="column-header">
            <span class="column-title">{{ col.title }}</span>
            <span class="column-count">{{ col.list.length }}</span>
            <el-icon class="add-btn" :size="16" title="新增" @click="toggleAdd(col.key)">
              <Plus />
            </el-icon>
          </div>

          <!-- 列内新增输入框 -->
          <el-input
            v-if="addingCol === col.key"
            ref="addInputRefs"
            v-model="addTitle"
            size="small"
            placeholder="输入标题，回车添加"
            maxlength="100"
            @keyup.enter="handleCreate(col.key)"
            @blur="addingCol = ''"
          />

          <!-- 卡片列表 -->
          <div class="column-body">
            <p v-if="col.list.length === 0" class="column-empty">拖拽卡片到这里</p>
            <div
              v-for="todo in col.list"
              :key="todo.id"
              class="kanban-item"
              :class="{ dragging: draggingId === todo.id, done: todo.status === 'done' }"
              draggable="true"
              @dragstart="handleDragStart($event, todo)"
              @dragend="handleDragEnd"
            >
              <p class="item-title">{{ todo.title }}</p>
              <p v-if="todo.note" class="item-note">{{ todo.note }}</p>
              <div class="item-footer">
                <span class="item-time">{{ formatTime(todo.createdAt) }}</span>
                <div class="item-actions">
                  <el-tooltip content="编辑" placement="top">
                    <el-icon class="action-icon" :size="14" @click="openEdit(todo)">
                      <EditPen />
                    </el-icon>
                  </el-tooltip>
                  <el-popconfirm title="确定删除该待办吗？" @confirm="handleDelete(todo)">
                    <template #reference>
                      <el-icon class="action-icon danger" :size="14">
                        <Delete />
                      </el-icon>
                    </template>
                  </el-popconfirm>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="editVisible" title="编辑待办" width="480px">
      <el-form label-position="top">
        <el-form-item label="标题" required>
          <el-input v-model="editForm.title" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="editForm.note"
            type="textarea"
            :rows="3"
            maxlength="500"
            show-word-limit
            placeholder="选填"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, EditPen, Delete } from '@element-plus/icons-vue'
import {
  BIZ_CODE,
  TODO_STATUSES,
  listTodoApi,
  createTodoApi,
  updateTodoApi,
  deleteTodoApi
} from '@/api/todo'
import { useUnauthorizedHandler } from '@/composables/useAuth'

const onUnauthorized = useUnauthorizedHandler()

const loading = ref(false)
const saving = ref(false)
const todoList = ref([])

/* 三列定义 + 按状态分组 */
const columns = computed(() =>
  TODO_STATUSES.map((s) => ({
    key: s.value,
    title: s.title,
    list: todoList.value
      .filter((t) => t.status === s.value)
      .sort((a, b) => b.createdAt.localeCompare(a.createdAt))
  }))
)

/* 拖拽状态 */
const draggingId = ref(null)
const dragOverCol = ref('')

const handleDragStart = (e, todo) => {
  draggingId.value = todo.id
  e.dataTransfer.setData('text/plain', String(todo.id))
  e.dataTransfer.effectAllowed = 'move'
}

const handleDragEnd = () => {
  draggingId.value = null
  dragOverCol.value = ''
}

const handleDrop = async (e, colKey) => {
  dragOverCol.value = ''
  const id = Number(e.dataTransfer.getData('text/plain'))
  const todo = todoList.value.find((t) => t.id === id)
  if (!todo || todo.status === colKey) return

  // 乐观更新，失败回滚
  const prevStatus = todo.status
  todo.status = colKey
  try {
    const res = await updateTodoApi(id, { status: colKey })
    Object.assign(todo, res.data)
  } catch (err) {
    todo.status = prevStatus
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    ElMessage.error(err.message || '状态更新失败')
  }
}

/* 列内新增 */
const addingCol = ref('')
const addTitle = ref('')
const addInputRefs = ref([])

const toggleAdd = async (colKey) => {
  if (addingCol.value === colKey) {
    addingCol.value = ''
    return
  }
  addingCol.value = colKey
  addTitle.value = ''
  await nextTick()
  // v-for ref 为数组，取当前列的输入框实例聚焦
  const input = addInputRefs.value?.[0]
  input?.focus?.()
}

const handleCreate = async (colKey) => {
  const title = addTitle.value.trim()
  if (!title) {
    addingCol.value = ''
    return
  }
  try {
    const res = await createTodoApi({ title, status: colKey })
    todoList.value.unshift(res.data)
    addTitle.value = ''
    addingCol.value = ''
    ElMessage.success('新增成功')
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    ElMessage.error(err.message || '新增失败')
  }
}

/* 编辑 */
const editVisible = ref(false)
const editForm = reactive({ id: null, title: '', note: '' })

const openEdit = (todo) => {
  editForm.id = todo.id
  editForm.title = todo.title
  editForm.note = todo.note
  editVisible.value = true
}

const handleSaveEdit = async () => {
  const title = editForm.title.trim()
  if (!title) {
    ElMessage.warning('请输入待办标题')
    return
  }
  saving.value = true
  try {
    const res = await updateTodoApi(editForm.id, {
      title,
      note: editForm.note.trim()
    })
    const index = todoList.value.findIndex((t) => t.id === editForm.id)
    if (index !== -1) {
      Object.assign(todoList.value[index], res.data)
    }
    editVisible.value = false
    ElMessage.success('保存成功')
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

/* 删除 */
const handleDelete = async (todo) => {
  try {
    await deleteTodoApi(todo.id)
    todoList.value = todoList.value.filter((t) => t.id !== todo.id)
    ElMessage.success('删除成功')
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    ElMessage.error(err.message || '删除失败')
  }
}

const fetchList = async () => {
  loading.value = true
  try {
    const res = await listTodoApi()
    todoList.value = res.data.list
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    ElMessage.error(err.message || '加载看板失败')
  } finally {
    loading.value = false
  }
}

const formatTime = (iso) => {
  if (!iso) return ''
  return iso.slice(5, 10)
}

onMounted(fetchList)
</script>

<style scoped>
.kanban-page {
  max-width: 1100px;
  margin: 0 auto;
}
.kanban-card {
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
.header-tip {
  font-size: 12px;
  font-weight: 400;
  color: #c0c4cc;
}
/* 三列看板 */
.kanban-board {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
  min-height: 300px;
  align-items: start;
}
.kanban-column {
  background: #f5f6f8;
  border: 2px dashed transparent;
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: border-color 0.2s, background 0.2s;
}
.kanban-column.drop-target {
  border-color: #409eff;
  background: #ecf5ff;
}
.column-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
.column-title {
  font-size: 14px;
  font-weight: 600;
  color: #1f2329;
}
.column-count {
  font-size: 12px;
  color: #909399;
  background: #e8e9eb;
  border-radius: 8px;
  padding: 1px 8px;
}
.add-btn {
  margin-left: auto;
  color: #909399;
  cursor: pointer;
}
.add-btn:hover {
  color: #409eff;
}
.column-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 80px;
}
.column-empty {
  margin: 0;
  font-size: 12px;
  color: #c0c4cc;
  text-align: center;
  padding: 16px 0;
}
/* 卡片 */
.kanban-item {
  background: #fff;
  border-radius: 8px;
  padding: 10px 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  cursor: grab;
  transition: box-shadow 0.2s, opacity 0.2s;
}
.kanban-item:hover {
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
}
.kanban-item:active {
  cursor: grabbing;
}
.kanban-item.dragging {
  opacity: 0.4;
}
.kanban-item.done .item-title {
  text-decoration: line-through;
  color: #c0c4cc;
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
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
}
.item-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
}
.item-time {
  font-size: 11px;
  color: #c0c4cc;
}
.item-actions {
  display: flex;
  gap: 10px;
  /* 悬停显示，触屏设备无 hover 则常显 */
  opacity: 0;
  transition: opacity 0.2s;
}
.kanban-item:hover .item-actions {
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
}
.action-icon:hover {
  color: #409eff;
}
.action-icon.danger:hover {
  color: #f56c6c;
}
</style>
