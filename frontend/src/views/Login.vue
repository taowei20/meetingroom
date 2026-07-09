<template>
  <div class="login-container">
    <div class="login-card">
      <h2 class="login-title">紫软会议室预订系统</h2>
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

<!--      <h3 class="login-title">会议室预订系统升级维护中<br><br><span style="color:red">请去三楼前台登记预订会议室</span> <br><br>具体恢复时间另行通知!</h3>-->
<!--   -->
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { login } from '../api/auth'
import { setToken } from '../utils/auth'
import { useUserStore } from '../store/user'

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
    userStore.setUser(res.user)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (e) {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}
.login-card {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}
.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 22px;
}
.login-hint {
  text-align: center;
  font-size: 12px;
  color: #999;
  margin-top: 10px;
}
@media (max-width: 480px) {
  .login-card {
    padding: 24px 20px;
  }
  .login-title {
    font-size: 18px;
    margin-bottom: 20px;
  }
}
</style>
