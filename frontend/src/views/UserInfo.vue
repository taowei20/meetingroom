<template>
  <div class="user-info">
    <el-card shadow="never" style="max-width: 480px">
      <template #header>个人信息</template>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="登录账号">
          <el-input :value="form.username" disabled />
        </el-form-item>
        <el-form-item label="用户名" prop="name">
          <el-input v-model="form.name" placeholder="请输入用户名" disabled/>
        </el-form-item>
        <el-form-item label="所属部门">
          <el-input v-model="form.department" placeholder="请输入所属部门" />
        </el-form-item>
        <el-form-item label="联系方式">
          <el-input v-model="form.phone" placeholder="请输入联系方式" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">保存修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" style="max-width: 480px; margin-top: 16px;">
      <template #header>
        <div class="card-header">
          <span>MCP 授权码</span>
          <el-tag v-if="mcpCode" type="success" size="small">已启用</el-tag>
          <el-tag v-else type="info" size="small">未启用</el-tag>
        </div>
      </template>
      <div class="mcp-section">
        <p class="mcp-desc">
          MCP 授权码用于 Agent 客户端（如 Claude Desktop）连接本系统。
          生成授权码后，在 Agent 配置中使用该授权码即可访问会议室预订功能。
        </p>

        <div v-if="mcpCode" class="mcp-code-display">
          <el-input
            v-model="mcpCode"
            readonly
            :type="showCode ? 'text' : 'password'"
          >
            <template #append>
              <el-button @click="showCode = !showCode">
                <el-icon><View v-if="showCode" /><Hide v-else /></el-icon>
              </el-button>
            </template>
          </el-input>
          <div class="mcp-actions">
            <el-button type="primary" plain @click="copyCode" :loading="copying">
              <el-icon><DocumentCopy /></el-icon> 复制授权码
            </el-button>
            <el-button type="warning" plain @click="handleRefresh" :loading="refreshing">
              <el-icon><Refresh /></el-icon> 重新生成
            </el-button>
            <el-button type="danger" plain @click="handleDelete" :loading="deleting">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </div>
        </div>

        <div v-else class="mcp-empty">
          <el-empty description="尚未生成MCP授权码" :image-size="60">
            <el-button type="primary" @click="handleGenerate" :loading="generating">
              <el-icon><Key /></el-icon> 生成MCP授权码
            </el-button>
          </el-empty>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  View, Hide, DocumentCopy, Refresh, Delete, Key,
} from '@element-plus/icons-vue'
import {
  getCurrentUser, updateCurrentUser,
  getMcpCode, generateMcpCode, deleteMcpCode,
} from '../api/auth'
import { useUserStore } from '../store/user'

const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = ref({
  username: '',
  name: '',
  department: '',
  phone: '',
})

const rules = {
  name: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
}

const mcpCode = ref('')
const showCode = ref(false)
const generating = ref(false)
const refreshing = ref(false)
const deleting = ref(false)
const copying = ref(false)

async function loadUser() {
  const user = await getCurrentUser()
  form.value = { ...user }
}

async function loadMcpCode() {
  try {
    const res = await getMcpCode()
    mcpCode.value = res.mcp_auth_code || ''
  } catch (e) {
    // ignore
  }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const updated = await updateCurrentUser({
      name: form.value.name,
      department: form.value.department,
      phone: form.value.phone,
    })
    userStore.updateUser(updated)
    ElMessage.success('保存成功')
  } finally {
    loading.value = false
  }
}

async function handleGenerate() {
  generating.value = true
  try {
    const res = await generateMcpCode()
    mcpCode.value = res.mcp_auth_code
    ElMessage.success('授权码已生成，请妥善保管')
  } finally {
    generating.value = false
  }
}

async function handleRefresh() {
  try {
    await ElMessageBox.confirm(
      '重新生成授权码后，旧授权码将立即失效。确定要继续吗？',
      '确认重新生成',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }
  refreshing.value = true
  try {
    const res = await generateMcpCode()
    mcpCode.value = res.mcp_auth_code
    ElMessage.success('授权码已重新生成，旧授权码已失效')
  } finally {
    refreshing.value = false
  }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm(
      '删除授权码后，使用该授权码的 Agent 将无法访问系统。确定要删除吗？',
      '确认删除',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }
  deleting.value = true
  try {
    await deleteMcpCode()
    mcpCode.value = ''
    ElMessage.success('授权码已删除')
  } finally {
    deleting.value = false
  }
}

async function copyCode() {
  copying.value = true
  try {
    const text = mcpCode.value
    const ok = await copyText(text)
    if (ok) {
      ElMessage.success('授权码已复制到剪贴板')
    } else {
      ElMessage.error('复制失败，请手动复制')
    }
  } finally {
    copying.value = false
  }
}

function copyText(text) {
  return new Promise((resolve) => {
    // 优先使用 Clipboard API（仅 HTTPS/localhost 可用）
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(() => resolve(true)).catch(() => resolve(fallbackCopy(text)))
    } else {
      resolve(fallbackCopy(text))
    }
  })
}

function fallbackCopy(text) {
  try {
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.focus()
    textarea.select()
    const ok = document.execCommand('copy')
    document.body.removeChild(textarea)
    return ok
  } catch {
    return false
  }
}

onMounted(() => {
  loadUser()
  loadMcpCode()
})
</script>

<style scoped>
.user-info {
  padding: 0;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
.mcp-section {
  padding: 0;
}
.mcp-desc {
  font-size: 13px;
  color: #999;
  margin-bottom: 16px;
  line-height: 1.6;
}
.mcp-code-display {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.mcp-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.mcp-empty {
  padding: 10px 0;
}
@media (max-width: 768px) {
  :deep(.el-card) {
    max-width: 100% !important;
  }
  :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }
  :deep(.el-form-item__label) {
    font-size: 13px;
  }
  .mcp-actions {
    flex-direction: column;
  }
  .mcp-actions .el-button {
    width: 100%;
  }
}
</style>
