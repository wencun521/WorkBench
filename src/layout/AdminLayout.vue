<template>
  <el-container class="admin-layout">
    <el-aside :width="collapsed ? '64px' : '210px'" class="layout-aside">
      <AppSidebar :collapsed="collapsed" @toggle="collapsed = !collapsed" />
    </el-aside>
    <el-main class="layout-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import AppSidebar from './AppSidebar.vue'

const collapsed = ref(false)
</script>

<style scoped>
.admin-layout {
  height: 100%;
}
.layout-aside {
  transition: width 0.25s;
  overflow: hidden;
}
.layout-main {
  padding: 20px;
  overflow: auto;
  background: #f5f6f8;
}
</style>
