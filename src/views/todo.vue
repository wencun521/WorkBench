<template>
  <div class="todo-page">
    <el-card class="todo-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>待办事项</span>
          <el-button @click="router.replace('/')">返回首页</el-button>
        </div>
      </template>

      <!-- 新增 -->
      <div class="todo-add">
        <el-input
          v-model="newTitle"
          placeholder="新增待办，输入后回车或点击按钮"
          maxlength="100"
          clearable
          @keyup.enter="handleCreate"
        />
        <el-button type="primary" :loading="creating" @click="handleCreate">新增</el-button>
      </div>

      <!-- 列表 -->
      <div v-loading="loading" class="todo-list">
        <el-empty v-if="!loading && todoList.length === 0" description="暂无待办，快去添加一个吧" />
        <div v-for="todo in todoList" :key="todo.id" class="todo-item">
          <el-checkbox
            :model-value="todo.completed"
            @change="(val) => handleToggle(todo, val)"
          >
            <span class="todo-title" :class="{ done: todo.completed }">{{ todo.title }}</span>
          </el-checkbox>
          <p v-if="todo.note" class="todo-note" :class="{ done: todo.completed }">{{ todo.note }}</p>
          <p class="todo-time">{{ formatTime(todo.createdAt) }}</p>

          <div class="todo-actions">
            <el-button link type="primary" @click="openEdit(todo)">编辑</el-button>
            <el-popconfirm title="确定删除该待办吗？" @confirm="handleDelete(todo)">
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
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
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { removeToken } from '@/utils/auth'
import {
  BIZ_CODE,
  listTodoApi,
  createTodoApi,
  updateTodoApi,
  deleteTodoApi
} from '@/api/todo'

const router = useRouter()

const loading = ref(false)
const creating = ref(false)
const saving = ref(false)
const newTitle = ref('')
const todoList = ref([])

const editVisible = ref(false)
const editForm = reactive({ id: null, title: '', note: '' })

/* 认证过期统一处理：清 token 回登录页 */
const handleUnauthorized = () => {
  removeToken()
  ElMessage.warning('登录已过期，请重新登录')
  router.replace('/login')
}

const fetchList = async () => {
  loading.value = true
  try {
    const res = await listTodoApi()
    todoList.value = res.data.list
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      handleUnauthorized()
      return
    }
    ElMessage.error(err.message || '加载待办失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  const title = newTitle.value.trim()
  if (!title) {
    ElMessage.warning('请输入待办标题')
    return
  }
  creating.value = true
  try {
    const res = await createTodoApi({ title })
    todoList.value.unshift(res.data)
    newTitle.value = ''
    ElMessage.success('新增成功')
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      handleUnauthorized()
      return
    }
    ElMessage.error(err.message || '新增失败')
  } finally {
    creating.value = false
  }
}

const handleToggle = async (todo, completed) => {
  try {
    const res = await updateTodoApi(todo.id, { completed })
    Object.assign(todo, res.data)
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      handleUnauthorized()
      return
    }
    ElMessage.error(err.message || '更新失败')
  }
}

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
      handleUnauthorized()
      return
    }
    ElMessage.error(err.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (todo) => {
  try {
    await deleteTodoApi(todo.id)
    todoList.value = todoList.value.filter((t) => t.id !== todo.id)
    ElMessage.success('删除成功')
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      handleUnauthorized()
      return
    }
    ElMessage.error(err.message || '删除失败')
  }
}

const formatTime = (iso) => {
  if (!iso) return ''
  return iso.replace('T', ' ').slice(0, 19)
}

onMounted(fetchList)
</script>

<style scoped>
.todo-page {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  min-height: 100vh;
  padding: 40px 20px;
}
.todo-card {
  width: 100%;
  max-width: 640px;
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
.todo-add {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}
.todo-list {
  min-height: 120px;
}
.todo-item {
  position: relative;
  padding: 12px 4px;
  border-bottom: 1px solid #f0f0f0;
}
.todo-item:last-child {
  border-bottom: none;
}
.todo-title {
  font-size: 15px;
  color: #1f2329;
}
.todo-title.done {
  text-decoration: line-through;
  color: #c0c4cc;
}
.todo-note {
  margin: 4px 0 0 24px;
  font-size: 13px;
  color: #606266;
  white-space: pre-wrap;
}
.todo-note.done {
  color: #c0c4cc;
}
.todo-time {
  margin: 4px 0 0 24px;
  font-size: 12px;
  color: #c0c4cc;
}
.todo-actions {
  position: absolute;
  top: 12px;
  right: 0;
}
</style>
