<template>
  <div class="auth-container">
    <!-- 背景装饰光斑 -->
    <div class="bg-circle circle-1"></div>
    <div class="bg-circle circle-2"></div>

    <AuthCard
      desc="加入我们，开启高效协作之旅"
      :features="['免费注册，即开即用', '多重安全保障机制', '专属顾问 1 对 1 服务']"
      item-gap="16px"
    >
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

        <el-form-item prop="email">
          <el-input
            v-model.trim="registerForm.email"
            placeholder="请输入邮箱"
            :prefix-icon="Message"
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
          class="auth-btn"
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
    </AuthCard>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { registerApi } from '@/api/user'
import AuthCard from '@/components/AuthCard.vue'

const router = useRouter()

const formRef = ref(null)
const loading = ref(false)

const registerForm = reactive({
  username: '',
  email: '',
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
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
      message: '邮箱格式不正确',
      trigger: 'blur'
    }
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
    await registerApi({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
      confirmPassword: registerForm.confirmPassword
    })

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
</style>
