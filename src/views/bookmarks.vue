<template>
  <div class="bookmarks-page">
    <el-card class="bookmarks-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>书签收藏</span>
          <el-button type="primary" @click="openCreate">新增书签</el-button>
        </div>
      </template>

      <!-- 工具条：搜索 + 分类筛选 -->
      <div class="toolbar">
        <el-input
          v-model="keyword"
          placeholder="搜索标题 / URL / 备注"
          clearable
          :prefix-icon="Search"
          class="search-input"
        />
        <el-select
          v-model="filterCategory"
          clearable
          placeholder="全部分类"
          class="category-filter"
        >
          <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
        </el-select>
      </div>

      <!-- 分节展示 -->
      <div v-loading="loading" class="bookmark-groups">
        <el-empty
          v-if="!loading && filteredBookmarks.length === 0"
          :description="bookmarkList.length === 0 ? '暂无书签，收藏第一个链接吧' : '没有匹配的书签'"
        />
        <section
          v-for="sec in sections"
          :key="sec.category"
          class="bookmark-section"
        >
          <div class="section-title">
            {{ sec.category }}
            <span class="section-count">{{ sec.items.length }}</span>
          </div>
          <a
            v-for="b in sec.items"
            :key="b.id"
            class="bookmark-row"
            :href="b.url"
            target="_blank"
            rel="noopener noreferrer"
          >
            <span class="row-icon" :style="iconStyle(b.category, b.url)">
              <img
                v-if="!faviconFailed.has(hostname(b.url))"
                class="favicon-img"
                :src="faviconUrl(b.url)"
                alt=""
                loading="lazy"
                @error="markFaviconFailed(hostname(b.url))"
              />
              <template v-else>{{ iconChar(b.category) }}</template>
            </span>
            <div class="row-main">
              <span class="row-title">{{ b.title || hostname(b.url) }}</span>
              <span v-if="b.note" class="row-note">{{ b.note }}</span>
            </div>
            <span class="row-host">{{ hostname(b.url) }}</span>
            <div class="row-actions" @click.prevent>
              <el-tooltip content="编辑" placement="top">
                <el-icon class="action-icon" :size="14" @click="openEdit(b)">
                  <EditPen />
                </el-icon>
              </el-tooltip>
              <el-popconfirm title="确定删除该书签吗？" @confirm="handleDelete(b)">
                <template #reference>
                  <el-icon class="action-icon danger" :size="14">
                    <Delete />
                  </el-icon>
                </template>
              </el-popconfirm>
            </div>
          </a>
        </section>
      </div>
    </el-card>

    <!-- 新增 / 编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑书签' : '新增书签'"
      width="480px"
      @opened="focusUrlInput"
    >
      <el-form label-position="top">
        <el-form-item label="URL" required>
          <el-input ref="urlInputRef" v-model="form.url" placeholder="https://..." @blur="handleUrlBlur" />
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="form.title" maxlength="100" placeholder="留空则显示域名">
            <template #append>
              <el-button :loading="fetchingTitle" @click="fetchTitle">获取标题</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="分类">
          <input v-model="form.category" class="category-input" list="category-list" maxlength="50" placeholder="未分类" />
          <datalist id="category-list">
            <option v-for="c in categories" :key="c" :value="c" />
          </datalist>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="form.note"
            type="textarea"
            :rows="2"
            maxlength="200"
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
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, EditPen, Delete } from '@element-plus/icons-vue'
import {
  BIZ_CODE,
  listBookmarksApi,
  createBookmarkApi,
  updateBookmarkApi,
  deleteBookmarkApi,
  fetchMetaApi
} from '@/api/bookmark'
import { useUnauthorizedHandler } from '@/composables/useAuth'

const onUnauthorized = useUnauthorizedHandler()

const loading = ref(false)
const saving = ref(false)
const bookmarkList = ref([])

/* 搜索 + 分类筛选（前端过滤） */
const keyword = ref('')
const filterCategory = ref('')

const filteredBookmarks = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  return bookmarkList.value.filter((b) => {
    if (filterCategory.value && b.category !== filterCategory.value) return false
    if (kw) {
      const hit =
        (b.title || '').toLowerCase().includes(kw) ||
        (b.url || '').toLowerCase().includes(kw) ||
        (b.note || '').toLowerCase().includes(kw)
      if (!hit) return false
    }
    return true
  })
})

/* 按分类分节（保持创建时间倒序） */
const sections = computed(() => {
  const map = new Map()
  for (const b of filteredBookmarks.value) {
    if (!map.has(b.category)) map.set(b.category, [])
    map.get(b.category).push(b)
  }
  return Array.from(map, ([category, items]) => ({ category, items }))
})

/* 已有分类去重，供筛选与联想 */
const categories = computed(() =>
  Array.from(new Set(bookmarkList.value.map((b) => b.category)))
)

/* 分类名哈希映射 4 色板（无请求无依赖） */
const ICON_PALETTE = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c']
const iconColor = (category) => {
  const sum = String(category)
    .split('')
    .reduce((acc, ch) => acc + ch.charCodeAt(0), 0)
  return ICON_PALETTE[sum % ICON_PALETTE.length]
}
const iconChar = (category) => (category || '未')[0].toUpperCase()

/* Favicon：按域名拼 favicon.im 公共服务地址（throw-error-on-404 使未收录站点走 404），加载失败回退分类色块 */
const faviconFailed = reactive(new Set())
const markFaviconFailed = (host) => faviconFailed.add(host)
const faviconUrl = (url) => `https://a.favicon.im/${hostname(url)}?throw-error-on-404=true`
const iconStyle = (category, url) => {
  if (faviconFailed.has(hostname(url))) {
    return { background: iconColor(category), color: '#fff' }
  }
  return {}
}

const hostname = (url) => {
  try {
    return new URL(url).hostname
  } catch {
    return url
  }
}

const dialogVisible = ref(false)
const editingId = ref(null)
const urlInputRef = ref(null)
const form = reactive({ url: '', title: '', category: '', note: '' })

const focusUrlInput = () => {
  urlInputRef.value?.focus?.()
}

const openCreate = () => {
  editingId.value = null
  Object.assign(form, { url: '', title: '', category: filterCategory.value || '', note: '' })
  dialogVisible.value = true
}

const openEdit = (b) => {
  editingId.value = b.id
  Object.assign(form, { url: b.url, title: b.title || '', category: b.category, note: b.note })
  dialogVisible.value = true
}

/* 抓取网页标题预填（手动按钮 + 新增弹窗 URL blur 自动触发） */
const fetchingTitle = ref(false)
const fetchTitle = async () => {
  const url = form.url.trim()
  if (!url) {
    ElMessage.warning('请先输入书签 URL')
    return
  }
  fetchingTitle.value = true
  try {
    const res = await fetchMetaApi(url)
    if (res.data && res.data.title) {
      form.title = res.data.title
      ElMessage.success('标题获取成功')
    } else {
      ElMessage.info('未能获取到标题，请手动填写')
    }
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    ElMessage.info('未能获取到标题，请手动填写')
  } finally {
    fetchingTitle.value = false
  }
}

const handleUrlBlur = () => {
  /* 编辑弹窗不自动抓取，避免覆盖用户已起的标题 */
  if (editingId.value) return
  if (form.title.trim() || !form.url.trim()) return
  try {
    const parsed = new URL(form.url.trim())
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') return
  } catch {
    return
  }
  fetchTitle()
}

const handleSave = async () => {
  const url = form.url.trim()
  if (!url) {
    ElMessage.warning('请输入书签 URL')
    return
  }
  saving.value = true
  try {
    const payload = {
      url,
      title: form.title.trim(),
      category: form.category.trim() || '未分类',
      note: form.note.trim()
    }
    if (editingId.value) {
      const res = await updateBookmarkApi(editingId.value, payload)
      const index = bookmarkList.value.findIndex((b) => b.id === editingId.value)
      if (index !== -1) {
        bookmarkList.value[index] = res.data
      }
      ElMessage.success('保存成功')
    } else {
      const res = await createBookmarkApi(payload)
      bookmarkList.value.unshift(res.data)
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

const handleDelete = async (b) => {
  try {
    await deleteBookmarkApi(b.id)
    bookmarkList.value = bookmarkList.value.filter((x) => x.id !== b.id)
    ElMessage.success('删除成功')
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    ElMessage.error(err.message || '删除失败')
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await listBookmarksApi()
    bookmarkList.value = res.data.list
  } catch (err) {
    if (err.code === BIZ_CODE.UNAUTHORIZED) {
      onUnauthorized()
      return
    }
    ElMessage.error(err.message || '加载书签失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.bookmarks-page {
  max-width: 900px;
  margin: 0 auto;
}
.bookmarks-card {
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
/* 工具条 */
.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}
.search-input {
  flex: 1;
}
.category-filter {
  width: 160px;
}
.bookmark-groups {
  min-height: 120px;
}
.bookmark-section {
  margin-top: 8px;
}
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #909399;
  padding: 8px 4px 6px;
}
.section-count {
  font-size: 11px;
  font-weight: 400;
  color: #c0c4cc;
  background: #f5f6f8;
  border-radius: 8px;
  padding: 1px 8px;
}
/* 书签行 */
.bookmark-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 8px;
  border-radius: 8px;
  color: inherit;
  cursor: pointer;
  transition: background 0.15s;
}
.bookmark-row:hover {
  background: #f5f6f8;
}
.row-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}
.favicon-img {
  width: 18px;
  height: 18px;
  border-radius: 4px;
}
.row-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.row-title {
  font-size: 14px;
  color: #1f2329;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.bookmark-row:hover .row-title {
  color: #409eff;
}
.row-note {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.row-host {
  font-size: 12px;
  color: #c0c4cc;
  flex-shrink: 0;
  max-width: 180px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.row-actions {
  display: flex;
  gap: 10px;
  opacity: 0;
  transition: opacity 0.2s;
}
.bookmark-row:hover .row-actions {
  opacity: 1;
}
@media (hover: none) {
  .row-actions {
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
/* 弹窗分类输入（datalist 联想） */
.category-input {
  width: 100%;
  height: 32px;
  padding: 0 11px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  color: #1f2329;
  outline: none;
  background: #fff;
}
.category-input:focus {
  border-color: #409eff;
}
</style>
