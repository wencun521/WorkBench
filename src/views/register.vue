<template>
  <div class="register-container">
    <el-card class="register-card" shadow="never">
      <h2>注册账号</h2>
      <p class="subtitle">该页面为占位页，按需补充注册表单逻辑。</p>
      <el-button type="primary" @click="$router.push('/login')">返回登录</el-button>
    </el-card>
  </div>
</template>

<script setup></script>

<style scoped>
.register-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.register-card {
  width: 100%;
  max-width: 420px;
  text-align: center;
  border-radius: 12px;
}
.register-card h2 {
  margin: 0 0 8px;
}
.subtitle {
  margin: 0 0 20px;
  color: #909399;
}
</style>
