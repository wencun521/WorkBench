<template>
  <aside class="sidebar" :class="{ collapsed }">
    <!-- 顶部 logo 区 -->
    <div class="logo-area" @click="emit('toggle')">
      <el-icon class="logo-icon" :size="24"><Platform /></el-icon>
      <transition name="fade">
        <span v-if="!collapsed" class="logo-title">Admin Pro</span>
      </transition>
    </div>

    <!-- 导航菜单 -->
    <el-menu
      class="menu"
      :default-active="route.path"
      :collapse="collapsed"
      :collapse-transition="false"
      :router="true"
    >
      <el-menu-item index="/">
        <el-icon><HomeFilled /></el-icon>
        <template #title>首页</template>
      </el-menu-item>
      <el-menu-item index="/todo">
        <el-icon><Tickets /></el-icon>
        <template #title>待办事项</template>
      </el-menu-item>
    </el-menu>

    <!-- 底部：折叠按钮 + 用户区 -->
    <div class="sidebar-footer">
      <el-button
        class="collapse-btn"
        text
        @click="emit('toggle')"
      >
        <el-icon :size="18">
          <Expand v-if="collapsed" />
          <Fold v-else />
        </el-icon>
      </el-button>
      <div class="user-area">
        <el-avatar :size="30" class="user-avatar">A</el-avatar>
        <el-tooltip content="退出登录" placement="top">
          <el-icon class="logout-btn" :size="17" @click="logout">
            <SwitchButton />
          </el-icon>
        </el-tooltip>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { HomeFilled, Tickets, Platform, Expand, Fold, SwitchButton } from '@element-plus/icons-vue'
import { useLogout } from '@/composables/useAuth'

defineProps({
  collapsed: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['toggle'])

const route = useRoute()
const logout = useLogout()
</script>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  width: 210px;
  height: 100%;
  background: #fff;
  border-right: 1px solid #e8e9eb;
  transition: width 0.25s;
  overflow: hidden;
}
.sidebar.collapsed {
  width: 64px;
}
.logo-area {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 56px;
  padding: 0 20px;
  cursor: pointer;
  flex-shrink: 0;
  white-space: nowrap;
}
.sidebar.collapsed .logo-area {
  padding: 0;
  justify-content: center;
}
.logo-icon {
  color: #409eff;
  flex-shrink: 0;
}
.logo-title {
  font-size: 17px;
  font-weight: 600;
  color: #1f2329;
}
.menu {
  flex: 1;
  border-right: none;
}
.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px 12px;
  border-top: 1px solid #f0f0f0;
  flex-shrink: 0;
}
.sidebar.collapsed .sidebar-footer {
  padding: 10px 0;
  align-items: center;
}
.collapse-btn {
  align-self: flex-end;
  color: #909399;
}
.sidebar.collapsed .collapse-btn {
  align-self: center;
}
.user-area {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 4px;
}
.sidebar.collapsed .user-area {
  flex-direction: column;
  gap: 8px;
  padding: 0;
}
.user-avatar {
  background: #409eff;
  color: #fff;
  font-size: 14px;
}
.logout-btn {
  color: #909399;
  cursor: pointer;
}
.logout-btn:hover {
  color: #f56c6c;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
