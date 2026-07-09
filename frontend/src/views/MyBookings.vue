<template>
  <div class="my-bookings">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>我的预订</span>
          <el-radio-group v-model="statusFilter" @change="loadData">
            <el-radio-button value="">全部</el-radio-button>
            <el-radio-button value="active">进行中</el-radio-button>
            <el-radio-button value="cancelled">已取消</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" stripe border>
        <el-table-column prop="room_name" label="会议室" width="130" />
        <el-table-column prop="room_code" label="编号" width="110" />
        <el-table-column prop="booking_date" label="日期" width="110" />
        <el-table-column label="星期" width="80">
          <template #default="{ row }">
            {{ getWeekday(row.booking_date) }}
          </template>
        </el-table-column>
        <el-table-column label="时间段" width="130">
          <template #default="{ row }">
            {{ row.start_time }} - {{ row.end_time }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'active'" :type="isFuture(row) ? 'success' : 'info'" size="small">
              {{ isFuture(row) ? '未开始' : isOngoing(row) ? '进行中' : '已结束' }}
            </el-tag>
            <el-tag v-else type="danger" size="small">已取消</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="meeting_content" label="会议内容" min-width="120" show-overflow-tooltip />
        <el-table-column label="会议记录" min-width="140">
          <template #default="{ row }">
            <div v-if="row.attachment_name" class="attachment-info">
              <el-icon><Document /></el-icon>
              <a :href="`/api/uploads/${row.attachment}`" target="_blank" class="attachment-link">
                {{ row.attachment_name }}
              </a>
              <el-button v-if="canUpload(row)" size="small" type="warning" link @click="openUploadDialog(row)">
                重新上传
              </el-button>
            </div>
            <el-button v-else-if="canUpload(row)" size="small" type="primary" link @click="openUploadDialog(row)">
              <el-icon><Upload /></el-icon> 上传
            </el-button>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-popconfirm
              v-if="row.status === 'active' && isFuture(row)"
              title="确定要取消预订吗？"
              @confirm="handleCancel(row.id)"
            >
              <template #reference>
                <el-button size="small" type="danger">取消</el-button>
              </template>
            </el-popconfirm>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="uploadDialogVisible" title="上传会议记录" width="420px" destroy-on-close>
      <div class="upload-info">
        <p>会议室: {{ currentBooking.room_name }}</p>
        <p>日期: {{ currentBooking.booking_date }} {{ currentBooking.start_time }} - {{ currentBooking.end_time }}</p>
      </div>
      <el-upload
        ref="uploadRef"
        :action="`/api/bookings/${currentBooking.id}/attachment`"
        :headers="uploadHeaders"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :before-upload="beforeUpload"
        :limit="1"
        :auto-upload="false"
        drag
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">支持所有文件类型</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="submitUpload">确认上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, Upload, UploadFilled } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { getMyBookingsHistory, cancelBooking, uploadAttachment } from '../api/bookings'
import { getToken } from '../utils/auth'

const loading = ref(false)
const uploading = ref(false)
const tableData = ref([])
const statusFilter = ref('')

const uploadDialogVisible = ref(false)
const currentBooking = ref({})
const uploadRef = ref(null)

const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']

function getWeekday(dateStr) {
  if (!dateStr) return ''
  return weekdays[dayjs(dateStr).day()]
}
const uploadHeaders = ref({ Authorization: `Bearer ${getToken()}` })

function isFuture(row) {
  return dayjs(row.booking_date).isAfter(dayjs(), 'day') ||
    (dayjs(row.booking_date).isSame(dayjs(), 'day') && row.start_time > dayjs().format('HH:mm'))
}

function isOngoing(row) {
  return dayjs(row.booking_date).isSame(dayjs(), 'day') &&
    row.start_time <= dayjs().format('HH:mm') &&
    row.end_time > dayjs().format('HH:mm')
}

function canUpload(row) {
  if (row.status !== 'active') return false
  if (isFuture(row)) return false
  return true
}

async function loadData() {
  loading.value = true
  try {
    tableData.value = await getMyBookingsHistory({ status: statusFilter.value })
  } finally {
    loading.value = false
  }
}

async function handleCancel(id) {
  await cancelBooking(id)
  ElMessage.success('取消成功')
  loadData()
}

function openUploadDialog(row) {
  currentBooking.value = row
  uploadDialogVisible.value = true
}

function beforeUpload(file) {
  return true
}

function submitUpload() {
  uploading.value = true
  uploadRef.value.submit()
}

async function handleUploadSuccess(response) {
  uploading.value = false
  uploadDialogVisible.value = false
  ElMessage.success('上传成功')
  loadData()
}

function handleUploadError() {
  uploading.value = false
  ElMessage.error('上传失败')
}

onMounted(loadData)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}
.attachment-info {
  display: flex;
  align-items: center;
  gap: 4px;
}
.attachment-link {
  color: #1890ff;
  text-decoration: none;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}
.attachment-link:hover {
  text-decoration: underline;
}
.no-attachment {
  color: #ccc;
}
.text-muted {
  color: #ccc;
}
.upload-info {
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
}
.upload-info p {
  margin: 4px 0;
  font-size: 14px;
  color: #333;
}
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
  :deep(.el-table) {
    font-size: 12px;
  }
  :deep(.el-table__header th) {
    padding: 8px 4px;
  }
  :deep(.el-table__body td) {
    padding: 8px 4px;
  }
  :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }
  :deep(.el-dialog__body) {
    padding: 12px;
  }
  :deep(.el-upload-dragger) {
    padding: 16px;
  }
}
</style>
