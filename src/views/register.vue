<template>
  <div class="register-container">
    <!-- 背景装饰光斑 -->
    <div class="bg-circle circle-1"></div>
    <div class="bg-circle circle-2"></div>

    <div class="register-card">
      <!-- 左侧品牌区 -->
      <div class="register-brand">
        <div class="brand-logo">A</div>
        <h1 class="brand-title">Admin Pro</h1>
        <p class="brand-desc">加入我们，开启高效协作之旅</p>
        <ul class="brand-features">
          <li>免费注册，即开即用</li>
          <li>多重安全保障机制</li>
          <li>专属顾问 1 对 1 服务</li>
        </ul>
      </div>

      <!-- 右侧表单区 -->
      <div class="register-form-wrap">
        <h2 class="form-title">创建账号</h2>
        <p class="form-subtitle">请填写以下信息完成注册</p>

        <el-form
          ref="formRef"
          :model="registerForm"
          :rules="rules"
          size="large"
          label-position="top"
          @keyup.enter="handleRegister"
        >
          <el-form-item prop="username">
            <el-input
              v-model.trim="registerForm.username"
              placeholder="请输入用户名"
              :prefix-icon="User"
              clearable
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model.trim="registerForm.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              show-password
            />
            <!-- 密码强度指示器 -->
            <div v-if="registerForm.password" class="pwd-strength">
              <div class="pwd-strength-bars">
                <span
                  v-for="i in 3"
                  :key="i"
                  class="bar"
                  :class="{ active: i <= pwdStrength.level, [`level-${pwdStrength.level}`]: i <= pwdStrength.level }"
                ></span>
              </div>
              <span class="pwd-strength-text" :class="`level-${pwdStrength.level}`">
                {{ pwdStrength.label }}
              </span>
            </div>
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <el-input
              v-model.trim="registerForm.confirmPassword"
              type="password"
              placeholder="请再次输入密码"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <el-form-item prop="agree" class="agree-item">
            <el-checkbox v-model="registerForm.agree">
              我已阅读并同意
              <el-link type="primary" :underline="false" @click="showAgreement">《用户协议</el-link>
              与
              <el-link type="primary" :underline="false" @click="showPrivacy">《隐私政策》</el-link>
            </el-checkbox>
          </el-form-item>

          <el-button
            class="register-btn"
            type="primary"
            :loading="loading"
            @click="handleRegister"
          >
            {{ loading ? '注册中' : '注 册' }}
          </el-button>

          <p class="tip">
            已有账号？
            <el-link type="primary" :underline="false" @click="goLogin">立即登录</el-link>
          </p>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
// import { registerApi } from '@/api/user'   // 换成你自己的接口

const router = useRouter()

const formRef = ref(null)
const loading = ref(false)

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  agree: false
})

/* ---------- 密码强度 ---------- */
const pwdStrength = computed(() => {
  const pwd = registerForm.password
  if (!pwd) return { level: 0, label: '' }

  let score = 0
  if (pwd.length >= 6) score++
  if (pwd.length >= 10) score++
  if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) score++
  if (/\d/.test(pwd)) score++
  if (/[^a-zA-Z0-9]/.test(pwd)) score++

  if (score <= 1) return { level: 1, label: '弱' }
  if (score <= 3) return { level: 2, label: '中' }
  return { level: 3, label: '强' }
})

/* ---------- 校验规则 ---------- */
const validateConfirm = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateAgree = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请先同意用户协议与隐私政策'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为 3 ~ 20 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '仅支持字母、数字、下划线', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为 6 ~ 20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirm, trigger: 'blur' }
  ],
  agree: [
    { required: true, validator: validateAgree, trigger: 'change' }
  ]
}

/* ---------- 注册 ---------- */
const handleRegister = async () => {
  if (!formRef.value || loading.value) return

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    // ===== 替换为真实请求 =====
    // await registerApi({
    //   username: registerForm.username,
    //   password: registerForm.password
    // })
    await new Promise((resolve) => setTimeout(resolve, 800)) // 模拟请求
    // =========================

    ElMessage.success('注册成功，请登录')
    router.replace({
      path: '/login',
      query: { username: registerForm.username }
    })
  } catch (err) {
    ElMessage.error(err?.message || '注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const goLogin = () => {
  router.push('/login')
}

const showAgreement = () => {
  ElMessage.info('用户协议待补充')
}

const showPrivacy = () => {
  ElMessage.info('隐私政策待补充')
}
</script>

<style scoped>
.register-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 背景装饰 */
.bg-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  filter: blur(2px);
}
.circle-1 {
  width: 420px;
  height: 420px;
  top: -140px;
  left: -120px;
}
.circle-2 {
  width: 320px;
  height: 320px;
  right: -100px;
  bottom: -120px;
}

/* 卡片：与登录页保持一致的高度 */
.register-card {
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
.register-brand {
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
.register-form-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 40px 44px;
}

.form-title {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 600;
  color: #1f2329;
}

.form-subtitle {
  margin: 0 0 20px;
  font-size: 13px;
  color: #909399;
}

/* 密码强度 */
.pwd-strength {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
  font-size: 12px;
  line-height: 1;
}
.pwd-strength-bars {
  display: flex;
  gap: 4px;
}
.pwd-strength-bars .bar {
  width: 24px;
  height: 4px;
  background: #e4e7ed;
  border-radius: 2px;
  transition: background 0.2s;
}
.pwd-strength-bars .bar.level-1 { background: #f56c6c; }
.pwd-strength-bars .bar.level-2 { background: #e6a23c; }
.pwd-strength-bars .bar.level-3 { background: #67c23a; }
.pwd-strength-text.level-1 { color: #f56c6c; }
.pwd-strength-text.level-2 { color: #e6a23c; }
.pwd-strength-text.level-3 { color: #67c23a; }

/* 协议同意：留出错误提示的空间，避免盖住下方按钮 */
.agree-item {
  margin-bottom: 18px !important;
}
.agree-item :deep(.el-form-item__content) {
  line-height: 1.6;
}
.agree-item :deep(.el-checkbox__label) {
  font-size: 13px;
  color: #606266;
  white-space: normal;
}

/* 注册按钮 */
.register-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  letter-spacing: 4px;
  border: none;
  border-radius: 8px;
}
.register-btn.el-button--primary,
.register-btn.el-button--primary:hover,
.register-btn.el-button--primary:focus {
  background: linear-gradient(90deg, #4e6ef2, #8b5cf6);
  border: none;
}
.register-btn.el-button--primary:hover {
  opacity: 0.9;
}

.tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin: 20px 0 0;
  font-size: 14px;
  color: #909399;
  text-align: center;
}

/* Element Plus 样式微调 */
.register-form-wrap :deep(.el-input__wrapper) {
  border-radius: 8px;
}
.register-form-wrap :deep(.el-form-item) {
  margin-bottom: 16px;
}

/* 响应式 */
@media (max-width: 768px) {
  .register-card {
    width: 100%;
    min-height: auto;
  }
  .register-brand {
    display: none;
  }
  .register-form-wrap {
    padding: 36px 24px;
  }
}
</style>
