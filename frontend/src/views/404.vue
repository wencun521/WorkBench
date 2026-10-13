<template>
  <div class="not-found">
    <h1>404</h1>
    <p>抱歉，您访问的页面不存在</p>
    <el-button type="primary" @click="$router.replace('/')">返回首页</el-button>
  </div>
</template>

<script setup></script>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  gap: 12px;
  color: #909399;
}
.not-found h1 {
  font-size: 72px;
  color: #4e6ef2;
  margin: 0;
}
</style>
