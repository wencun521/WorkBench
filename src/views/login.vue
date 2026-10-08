<template>
  <div class="login-container">
    <!-- 背景装饰光斑 -->
    <div class="bg-circle circle-1"></div>
    <div class="bg-circle circle-2"></div>

    <div class="login-card">
      <!-- 左侧品牌区 -->
      <div class="login-brand">
        <div class="brand-logo">A</div>
        <h1 class="brand-title">Admin Pro</h1>
        <p class="brand-desc">高效 · 简洁 · 强大的后台管理系统</p>
        <ul class="brand-features">
          <li>统一权限管理</li>
          <li>数据可视化看板</li>
          <li>开箱即用的组件库</li>
        </ul>
      </div>

      <!-- 右侧表单区 -->
      <div class="login-form-wrap">
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
            class="login-btn"
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { setToken } from '@/utils/auth'
// import { loginApi } from '@/api/user'   // 换成你自己的接口

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
    // ===== 替换为真实请求 =====
    // const res = await loginApi({
    //   username: loginForm.username,
    //   password: loginForm.password
    // })
    // localStorage.setItem('token', res.data.token)
    await new Promise((resolve) => setTimeout(resolve, 800)) // 模拟请求
    setToken('mock-token-' + Date.now()) // TODO: 用真实接口返回的 token 替换
    // =========================

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
.login-container {
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

/* 卡片 */
.login-card {
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
.login-brand {
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
.login-form-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 48px 44px;
}

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

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  letter-spacing: 4px;
  border: none;
  border-radius: 8px;
}

.login-btn.el-button--primary,
.login-btn.el-button--primary:hover,
.login-btn.el-button--primary:focus {
  background: linear-gradient(90deg, #4e6ef2, #8b5cf6);
  border: none;
}
.login-btn.el-button--primary:hover {
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
.login-form-wrap :deep(.el-input__wrapper) {
  border-radius: 8px;
}
.login-form-wrap :deep(.el-form-item) {
  margin-bottom: 20px;
}

/* 响应式 */
@media (max-width: 768px) {
  .login-card {
    width: 100%;
    min-height: auto;
  }
  .login-brand {
    display: none;
  }
  .login-form-wrap {
    padding: 36px 24px;
  }
}
</style>
