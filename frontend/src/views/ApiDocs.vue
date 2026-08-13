<template>
  <div class="api-docs">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <el-icon><Document /></el-icon>
          <span>单点登录（SSO）接口说明</span>
        </div>
      </template>

      <el-alert
        type="info"
        :closable="false"
        show-icon
        title="通过以下两个接口即可实现免登录直接进入系统：先用账号密码换取 JWT Token，再用 Token 跳转进入首页。"
      />

      <div class="step-block">
        <div class="step-title">
          <el-icon><Key /></el-icon>
          <span>第一步：登录获取 JWT Token</span>
        </div>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="接口地址">POST /api/auth/login</el-descriptions-item>
          <el-descriptions-item label="Content-Type">application/json</el-descriptions-item>
        </el-descriptions>

        <div class="sub-title">请求参数</div>
        <el-table :data="loginParams" border stripe size="small">
          <el-table-column prop="field" label="字段" width="160" />
          <el-table-column prop="type" label="类型" width="100" />
          <el-table-column prop="required" label="必填" width="80" />
          <el-table-column prop="desc" label="说明" />
        </el-table>

        <div class="sub-title">请求示例</div>
        <pre class="code-block">{{ loginExample }}</pre>

        <div class="sub-title">成功响应</div>
        <el-table :data="loginResponse" border stripe size="small">
          <el-table-column prop="field" label="字段" width="160" />
          <el-table-column prop="desc" label="说明" />
        </el-table>
        <pre class="code-block">{{ loginResponseExample }}</pre>
      </div>

      <el-divider />

      <div class="step-block">
        <div class="step-title">
          <el-icon><Link /></el-icon>
          <span>第二步：携带 Token 直接跳转首页</span>
        </div>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="接口地址">GET /api/auth/verify?token=&lt;JWT Token&gt;</el-descriptions-item>
          <el-descriptions-item label="说明">
            校验 Token 合法后，浏览器将 302 跳转到系统首页并自动完成登录，无需再输入用户名密码。
          </el-descriptions-item>
        </el-descriptions>

        <div class="sub-title">请求参数</div>
        <el-table :data="verifyParams" border stripe size="small">
          <el-table-column prop="field" label="字段" width="160" />
          <el-table-column prop="type" label="类型" width="100" />
          <el-table-column prop="required" label="必填" width="80" />
          <el-table-column prop="desc" label="说明" />
        </el-table>

        <div class="sub-title">请求示例（浏览器地址栏直接访问）</div>
        <pre class="code-block">{{ verifyExample }}</pre>

        <div class="sub-title">响应说明</div>
        <el-table :data="verifyResponse" border stripe size="small">
          <el-table-column prop="code" label="HTTP 状态码" width="120" />
          <el-table-column prop="desc" label="说明" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { Document, Key, Link } from '@element-plus/icons-vue'

const loginParams = [
  { field: 'username', type: 'string', required: '是', desc: '登录用户名' },
  { field: 'password', type: 'string', required: '是', desc: '登录密码' },
]

const loginResponse = [
  { field: 'token', desc: 'JWT Token，后续接口调用时放入 Authorization 头：Bearer &lt;token&gt;' },
  { field: 'user', desc: '用户信息对象（id、name、username、department、phone、is_admin 等）' },
]

const loginExample = `curl -X POST http://10.19.1.168/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"username": "admin", "password": "123456"}'`

const loginResponseExample = `{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9....",
  "user": {
    "id": 1,
    "username": "admin",
    "name": "系统管理员",
    "department": "信息技术部",
    "phone": "13800000000",
    "is_admin": true
  }
}`

const verifyParams = [
  { field: 'token', type: 'string', required: '是', desc: '第一步获取的 JWT Token，可直接粘贴或带 Bearer 前缀' },
]

const verifyExample = `http://10.19.1.168/api/auth/verify?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9....`

const verifyResponse = [
  { code: '302', desc: 'Token 合法，浏览器自动跳转到系统首页，免登录进入' },
  { code: '401', desc: '缺少 Token 或 Token 无效/已过期，返回错误信息，不跳转' },
]
</script>

<style scoped>
.api-docs {
  max-width: 1000px;
  margin: 0 auto;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
.step-block {
  margin-top: 20px;
}
.step-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 12px;
}
.sub-title {
  font-size: 14px;
  font-weight: bold;
  color: #606266;
  margin: 16px 0 8px;
}
.code-block {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>