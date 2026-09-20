<template>
  <div class="login-container">
    <div class="login-wrapper">
      <div class="login-left">
        <div class="left-content">
          <div class="left-text">
            <h2>会议室预订系统</h2>
          </div>
          <img :src="meetroomImg" alt="meeting room" class="login-image" />
        </div>
      </div>
      <div class="login-right">
        <div class="login-card">
          <div class="card-header">
            <h3 class="card-title">欢迎登录</h3>
            <p class="card-subtitle">请使用账号密码登录系统</p>
          </div>
          <el-form ref="formRef" :model="form" :rules="rules" label-width="0" size="large">
            <el-form-item prop="username">
              <el-input v-model="form.username" placeholder="请输入用户名" :prefix-icon="User" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="form.password" type="password" placeholder="请输入密码" :prefix-icon="Lock" show-password @keyup.enter="handleLogin" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" style="width: 100%" @click="handleLogin">登 录</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { login } from '../api/auth'
import { setToken, setLoginTime } from '../utils/auth'
import { useUserStore } from '../store/user'
import meetroomImg from '../asserts/meetingRoom.webp'

const link = document.createElement('link')
link.rel = 'preload'
link.as = 'image'
link.href = meetroomImg
document.head.appendChild(link)

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)
const form = ref({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await login(form.value)
    setToken(res.token)
    setLoginTime()
    userStore.setUser(res.user)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (e) {
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  background: #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-wrapper {
  display: flex;
  width: 1000px;
  height: 600px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}
.login-left {
  flex: 1;
  background: linear-gradient(135deg, #1a73e8 0%, #1557b0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.left-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.login-image {
  width: 640px;
  height: auto;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.15));
  background: rgba(255,255,255,0.06);
  animation: imgFadeIn 0.1s ease-in;
}
@keyframes imgFadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
.left-text {
  text-align: center;
  color: #fff;
  margin-top: 10px
}
.left-text h2 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
  letter-spacing: 2px;
}
.left-text p {
  font-size: 14px;
  opacity: 0.85;
  letter-spacing: 1px;
}
.login-right {
  width: 440px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}
.login-card {
  width: 100%;
  max-width: 360px;
}
.card-header {
  margin-bottom: 32px;
}
.card-title {
  font-size: 26px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8px;
}
.card-subtitle {
  font-size: 14px;
  color: #999;
}
@media (max-width: 768px) {
  .login-wrapper {
    flex-direction: column;
    width: 90%;
    height: auto;
    min-height: 500px;
  }
  .login-left {
    padding: 32px 20px;
    min-height: 200px;
  }
  .login-image {
    width: 160px;
  }
  .login-right {
    width: 100%;
    padding: 32px 24px;
  }
  .left-text h2 {
    font-size: 20px;
  }
}
</style>
