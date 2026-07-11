<template>
  <div class="login-logs">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>登录日志</span>
        </div>
      </template>
      <div class="search-bar">
        <el-input v-model="keyword" placeholder="搜索登录账号" clearable style="width: 220px" @clear="loadData" @keyup.enter="loadData">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" @click="loadData">搜索</el-button>
      </div>
      <el-table :data="tableData" v-loading="loading" stripe border>
        <el-table-column prop="username" label="登录账号" width="130" />
        <el-table-column prop="ip_address" label="登录IP" width="150" />
        <el-table-column prop="user_agent" label="浏览器/设备" min-width="300" show-overflow-tooltip />
        <el-table-column prop="login_time" label="登录时间" width="220" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getLoginLogs } from '../api/users'

const loading = ref(false)
const tableData = ref([])
const keyword = ref('')

async function loadData() {
  loading.value = true
  try {
    tableData.value = await getLoginLogs({ keyword: keyword.value })
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}
</style>
