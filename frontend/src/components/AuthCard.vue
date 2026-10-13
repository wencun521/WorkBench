<template>
  <div class="auth-card">
    <!-- 左侧品牌区 -->
    <div class="auth-brand">
      <div class="brand-logo">F</div>
      <h1 class="brand-title">FlowDesk</h1>
      <p class="brand-desc">{{ desc }}</p>
      <ul class="brand-features">
        <li v-for="item in features" :key="item">{{ item }}</li>
      </ul>
    </div>

    <!-- 右侧表单区 -->
    <div class="auth-form-wrap" :style="{ '--form-item-gap': itemGap }">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  desc: {
    type: String,
    required: true
  },
  features: {
    type: Array,
    default: () => []
  },
  /* 表单项间距，默认 20px */
  itemGap: {
    type: String,
    default: '20px'
  }
})
</script>

<style scoped>
.auth-card {
  position: relative;
  z-index: 1;
  display: flex;
  width: 900px;
  max-width: 100%;
  min-height: 540px;
  overflow: hidden;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.25);
}

/* 左侧品牌区 */
.auth-brand {
  flex: 0 0 420px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 48px 40px;
  color: #fff;
  background: linear-gradient(160deg, #4e6ef2 0%, #8b5cf6 100%);
}

.brand-logo {
  width: 52px;
  height: 52px;
  margin-bottom: 20px;
  font-size: 26px;
  font-weight: 700;
  line-height: 52px;
  text-align: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 14px;
  backdrop-filter: blur(6px);
}

.brand-title {
  margin: 0 0 12px;
  font-size: 28px;
  font-weight: 600;
  letter-spacing: 1px;
}

.brand-desc {
  margin: 0 0 28px;
  font-size: 14px;
  line-height: 1.6;
  opacity: 0.85;
}

.brand-features {
  margin: 0;
  padding: 0;
  list-style: none;
  font-size: 14px;
  opacity: 0.9;
}
.brand-features li {
  position: relative;
  padding-left: 18px;
  margin-bottom: 14px;
}
.brand-features li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 7px;
  width: 6px;
  height: 6px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
}

/* 右侧表单区 */
.auth-form-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 48px 44px;
}

/* 表单区通用样式微调 */
.auth-form-wrap :deep(.el-input__wrapper) {
  border-radius: 8px;
}
.auth-form-wrap :deep(.el-form-item) {
  margin-bottom: var(--form-item-gap);
}
.auth-form-wrap :deep(.tip) {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin: 20px 0 0;
  font-size: 14px;
  color: #909399;
  text-align: center;
}
.auth-form-wrap :deep(.auth-btn) {
  width: 100%;
  height: 44px;
  font-size: 16px;
  letter-spacing: 4px;
  border: none;
  border-radius: 8px;
}
.auth-form-wrap :deep(.auth-btn.el-button--primary),
.auth-form-wrap :deep(.auth-btn.el-button--primary:hover),
.auth-form-wrap :deep(.auth-btn.el-button--primary:focus) {
  background: linear-gradient(90deg, #4e6ef2, #8b5cf6);
  border: none;
}
.auth-form-wrap :deep(.auth-btn.el-button--primary:hover) {
  opacity: 0.9;
}

/* 响应式 */
@media (max-width: 768px) {
  .auth-card {
    min-height: auto;
  }
  .auth-brand {
    display: none;
  }
  .auth-form-wrap {
    padding: 36px 24px;
  }
}
</style>
