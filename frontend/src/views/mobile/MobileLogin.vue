<template>
  <div class="mobile-login">
    <div class="login-header">
      <div class="logo-circle">
        <el-icon :size="40" color="#fff"><OfficeBuilding /></el-icon>
      </div>
      <h1 class="app-title">会议室预订</h1>
      <p class="app-subtitle">紫软会议室预订管理系统</p>
    </div>
    <div class="login-form">
      <el-input
        v-model="form.username"
        placeholder="请输入用户名"
        size="large"
        :prefix-icon="User"
      />
      <el-input
        v-model="form.password"
        type="password"
        placeholder="请输入密码"
        size="large"
        :prefix-icon="Lock"
        show-password
        @keyup.enter="handleLogin"
      />
      <el-button
        type="primary"
        size="large"
        :loading="loading"
        class="login-btn"
        @click="handleLogin"
      >登 录</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, OfficeBuilding } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { login } from '../../api/auth'
import { setToken, setLoginTime } from '../../utils/auth'
import { useUserStore } from '../../store/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const form = ref({ username: '', password: '' })

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await login(form.value)
    setToken(res.token)
    setLoginTime()
    userStore.setUser(res.user)
    ElMessage.success('登录成功')
    router.push('/m/dashboard')
  } catch (e) {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.mobile-login {
  min-height: 100vh;
  min-height: 100dvh;
  background: linear-gradient(135deg, #1a73e8 0%, #1557b0 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 24px;
}
.login-header {
  text-align: center;
  margin-bottom: 48px;
}
.logo-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}
.app-title {
  font-size: 24px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8px;
}
.app-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}
.login-form {
  width: 100%;
  max-width: 360px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.login-btn {
  height: 44px;
  font-size: 16px;
  border-radius: 8px;
}
</style>
