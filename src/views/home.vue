<template>
  <div class="home">
    <el-card class="welcome-card" shadow="never">
      <h1>欢迎来到 Admin Pro</h1>
      <p>登录成功！这是后台首页占位页，可以在此处接入看板 / 列表等业务模块。</p>
      <div class="actions">
        <el-button type="primary" @click="router.push('/todo')">待办事项</el-button>
        <el-button @click="handleLogout">退出登录</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { removeToken } from '@/utils/auth'

const router = useRouter()

const handleLogout = () => {
  removeToken()
  ElMessage.success('已退出登录')
  router.replace('/login')
}
</script>

<style scoped>
.home {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
}
.welcome-card {
  width: 100%;
  max-width: 600px;
  text-align: center;
  border-radius: 12px;
}
.welcome-card h1 {
  margin: 0 0 12px;
  font-size: 22px;
  color: #1f2329;
}
.welcome-card p {
  margin: 0 0 24px;
  color: #909399;
}
.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style>
