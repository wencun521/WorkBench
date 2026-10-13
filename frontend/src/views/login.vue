<template>
  <div class="auth-container">
    <!-- 背景装饰光斑 -->
    <div class="bg-circle circle-1"></div>
    <div class="bg-circle circle-2"></div>

    <AuthCard
      desc="高效 · 简洁 · 强大的后台管理系统"
      :features="['统一权限管理', '数据可视化看板', '开箱即用的组件库']"
    >
      <h2 class="form-title">欢迎登录</h2>
      <p class="form-subtitle">请输入您的账号信息</p>

      <el-form
        ref="formRef"
        :model="loginForm"
        :rules="rules"
        size="large"
        label-position="top"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model.trim="loginForm.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model.trim="loginForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <div class="form-options">
          <el-checkbox v-model="loginForm.remember">记住密码</el-checkbox>
          <el-link type="primary" :underline="false" @click="handleForgot">
            忘记密码？
          </el-link>
        </div>

        <el-button
          class="auth-btn"
          type="primary"
          :loading="loading"
          @click="handleLogin"
        >
          {{ loading ? '登录中' : '登 录' }}
        </el-button>

        <p class="tip">
          还没有账号？
          <el-link type="primary" :underline="false" @click="handleRegister">
            立即注册
          </el-link>
        </p>
      </el-form>
    </AuthCard>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { setToken } from '@/utils/auth'
import { loginApi } from '@/api/user'
import AuthCard from '@/components/AuthCard.vue'

const router = useRouter()

const formRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为 3 ~ 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为 6 ~ 20 个字符', trigger: 'blur' }
  ]
}

/* ---------- 回显「记住密码」 ---------- */
onMounted(() => {
  const saved = localStorage.getItem('login_info')
  if (!saved) return
  try {
    const { username, password } = JSON.parse(saved)
    loginForm.username = username || ''
    loginForm.password = password || ''
    loginForm.remember = true
  } catch (e) {
    localStorage.removeItem('login_info')
  }
})

/* ---------- 登录 ---------- */
const handleLogin = async () => {
  if (!formRef.value || loading.value) return

  // 校验失败会 reject，用 catch 兜住
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await loginApi({
      username: loginForm.username,
      password: loginForm.password
    })
    setToken(res.data.token)

    // 记住密码（生产环境建议只存用户名，token 由后端管理）
    if (loginForm.remember) {
      localStorage.setItem(
        'login_info',
        JSON.stringify({
          username: loginForm.username,
          password: loginForm.password
        })
      )
    } else {
      localStorage.removeItem('login_info')
    }

    ElMessage.success('登录成功')
    const redirect = router.currentRoute.value.query.redirect
    router.replace(redirect || '/') // 跳转到首页
  } catch (err) {
    ElMessage.error(err?.message || '登录失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleForgot = () => {
  ElMessage.info('请联系管理员重置密码')
}

const handleRegister = () => {
  router.push('/register')
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
  margin: 0 0 28px;
  font-size: 13px;
  color: #909399;
}

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
</style>
