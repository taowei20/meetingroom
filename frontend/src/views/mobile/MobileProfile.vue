<template>
  <div class="mobile-profile">
    <div class="profile-header">
      <div class="avatar">
        <el-icon :size="36" color="#fff"><UserFilled /></el-icon>
      </div>
      <div class="user-name">{{ userStore.userName }}</div>
      <div class="user-role">{{ userStore.isAdmin ? '管理员' : '普通用户' }}</div>
    </div>

    <div class="menu-section">
      <div class="menu-item" @click="showEditName = true">
        <el-icon><User /></el-icon>
        <span>修改昵称</span>
        <span class="menu-value">{{ userStore.userName }}</span>
        <el-icon class="menu-arrow"><ArrowRight /></el-icon>
      </div>
      <div class="menu-item" @click="showChangePassword = true">
        <el-icon><Lock /></el-icon>
        <span>修改密码</span>
        <el-icon class="menu-arrow"><ArrowRight /></el-icon>
      </div>
    </div>

    <div class="menu-section">
      <div class="menu-item logout" @click="handleLogout">
        <el-icon><SwitchButton /></el-icon>
        <span>退出登录</span>
      </div>
    </div>

    <div class="version-info">v1.0.0</div>

    <el-dialog v-model="showEditName" title="修改昵称" width="90%">
      <el-input v-model="editName" placeholder="请输入昵称" />
      <template #footer>
        <el-button @click="showEditName = false">取消</el-button>
        <el-button type="primary" :loading="savingName" @click="saveName">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showChangePassword" title="修改密码" width="90%">
      <el-form :model="pwdForm" label-width="80px">
        <el-form-item label="旧密码">
          <el-input v-model="pwdForm.old_password" type="password" show-password placeholder="请输入旧密码" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="pwdForm.new_password" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showChangePassword = false">取消</el-button>
        <el-button type="primary" :loading="savingPwd" @click="savePassword">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { UserFilled, User, Lock, ArrowRight, SwitchButton } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '../../store/user'
import { updateCurrentUser, changePassword } from '../../api/auth'

const router = useRouter()
const userStore = useUserStore()

const showEditName = ref(false)
const showChangePassword = ref(false)
const savingName = ref(false)
const savingPwd = ref(false)
const editName = ref(userStore.userName)
const pwdForm = ref({ old_password: '', new_password: '' })

async function saveName() {
  if (!editName.value.trim()) {
    ElMessage.warning('请输入昵称')
    return
  }
  savingName.value = true
  try {
    await updateCurrentUser({ name: editName.value.trim() })
    userStore.updateUser({ name: editName.value.trim() })
    ElMessage.success('保存成功')
    showEditName.value = false
  } catch (e) {
    // ignore
  } finally {
    savingName.value = false
  }
}

async function savePassword() {
  if (!pwdForm.value.old_password || !pwdForm.value.new_password) {
    ElMessage.warning('请填写完整')
    return
  }
  savingPwd.value = true
  try {
    await changePassword(pwdForm.value)
    ElMessage.success('密码修改成功，请重新登录')
    showChangePassword.value = false
    userStore.logout()
    router.push('/m/login')
  } catch (e) {
    // ignore
  } finally {
    savingPwd.value = false
  }
}

function handleLogout() {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    userStore.logout()
    router.push('/m/login')
  })
}
</script>

<style scoped>
.mobile-profile {
  padding: 0;
}
.profile-header {
  background: linear-gradient(135deg, #1a73e8, #1557b0);
  border-radius: 10px;
  padding: 28px 20px;
  text-align: center;
  margin-bottom: 16px;
}
.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
}
.user-name {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}
.user-role {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 4px;
}
.menu-section {
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 12px;
}
.menu-item {
  display: flex;
  align-items: center;
  padding: 15px 14px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
  font-size: 15px;
  color: #333;
  gap: 10px;
}
.menu-item:last-child {
  border-bottom: none;
}
.menu-item:active {
  background: #f9f9f9;
}
.menu-value {
  flex: 1;
  text-align: right;
  color: #999;
  font-size: 14px;
}
.menu-arrow {
  color: #ccc;
}
.menu-item.logout {
  color: #ff4d4f;
  justify-content: center;
}
.version-info {
  text-align: center;
  color: #ccc;
  font-size: 12px;
  margin-top: 24px;
}
</style>
