<template>
  <div class="mobile-my-bookings">
    <div class="filter-bar">
      <el-radio-group v-model="statusFilter" size="small" @change="loadData">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button value="active">进行中</el-radio-button>
        <el-radio-button value="cancelled">已取消</el-radio-button>
      </el-radio-group>
    </div>

    <div v-loading="loading" class="booking-list">
      <div v-if="!tableData.length && !loading" class="empty-text">暂无预订记录</div>
      <div v-for="item in tableData" :key="item.id" class="booking-card">
        <div class="card-top">
          <div class="room-info">
            <span class="room-name">{{ item.room_name }}</span>
            <span class="room-code">{{ item.room_code }}</span>
          </div>
          <el-tag
            v-if="item.status === 'active'"
            :type="isFuture(item) ? 'success' : isOngoing(item) ? '' : 'info'"
            size="small"
          >
            {{ isFuture(item) ? '未开始' : isOngoing(item) ? '进行中' : '已结束' }}
          </el-tag>
          <el-tag v-else type="danger" size="small">已取消</el-tag>
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">日期</span>
            <span>{{ item.booking_date }} {{ getWeekday(item.booking_date) }}</span>
          </div>
          <div class="info-row">
            <span class="label">时间</span>
            <span>{{ item.start_time }} - {{ item.end_time }}</span>
          </div>
          <div v-if="item.meeting_content" class="info-row">
            <span class="label">会议</span>
            <span>{{ item.meeting_content }}</span>
          </div>
          <div v-if="item.attachment_name" class="info-row">
            <span class="label">附件</span>
            <span class="attachment" @click="downloadFile(item)">
              <el-icon><Document /></el-icon> {{ item.attachment_name }}
            </span>
          </div>
        </div>
        <div v-if="item.status === 'active' && isFuture(item)" class="card-footer">
          <el-popconfirm title="确定要取消预订吗？" @confirm="handleCancel(item.id)">
            <template #reference>
              <el-button size="small" type="danger" plain>取消预订</el-button>
            </template>
          </el-popconfirm>
          <el-button v-if="canUpload(item)" size="small" type="primary" plain @click="openUploadDialog(item)">
            上传记录
          </el-button>
        </div>
      </div>
    </div>

    <div v-if="total > pageSize" class="pagination-bar">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadData"
      />
    </div>

    <el-dialog v-model="uploadDialogVisible" title="上传会议记录" width="90%">
      <el-upload
        ref="uploadRef"
        :action="uploadUrl"
        :headers="uploadHeaders"
        :data="{ booking_id: uploadBookingId }"
        :on-success="onUploadSuccess"
        :on-error="onUploadError"
        :limit="1"
        :auto-upload="false"
      >
        <template #trigger>
          <el-button type="primary" plain>选择文件</el-button>
        </template>
        <el-button type="success" style="margin-left: 12px" @click="submitUpload">上传</el-button>
      </el-upload>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import { getMyBookingsHistory, cancelBooking, uploadAttachment } from '../../api/bookings'
import { getToken } from '../../utils/auth'
import { useRefreshOnShow } from '../../composables/useRefreshOnShow'

const loading = ref(false)
const tableData = ref([])
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = 15
const total = ref(0)

const uploadDialogVisible = ref(false)
const uploadBookingId = ref(null)
const uploadUrl = computed(() => `/api/bookings/${uploadBookingId.value}/attachment`)
const uploadHeaders = computed(() => ({ Authorization: `Bearer ${getToken()}` }))

const weekdayMap = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

function getWeekday(date) {
  return weekdayMap[dayjs(date).day()]
}

function isFuture(item) {
  const now = dayjs()
  const bookingDate = dayjs(item.booking_date)
  if (bookingDate.isAfter(now, 'day')) return true
  if (bookingDate.isSame(now, 'day')) {
    return item.start_time > now.format('HH:mm')
  }
  return false
}

function isOngoing(item) {
  const now = dayjs()
  const bookingDate = dayjs(item.booking_date)
  if (bookingDate.isSame(now, 'day')) {
    return item.start_time <= now.format('HH:mm') && item.end_time > now.format('HH:mm')
  }
  return false
}

function canUpload(item) {
  return item.status === 'active' && !isFuture(item)
}

async function downloadFile(item) {
  if (!item.id) return
  window.open(`/api/bookings/${item.id}/attachment`, '_blank')
}

function openUploadDialog(item) {
  uploadBookingId.value = item.id
  uploadDialogVisible.value = true
}

function submitUpload() {
  const el = document.querySelector('.el-upload--input input')
  if (el) el.click()
}

function onUploadSuccess() {
  ElMessage.success('上传成功')
  uploadDialogVisible.value = false
  loadData()
}

function onUploadError() {
  ElMessage.error('上传失败')
}

async function handleCancel(id) {
  try {
    await cancelBooking(id)
    ElMessage.success('已取消')
    loadData()
  } catch (e) {
    // ignore
  }
}

async function loadData() {
  loading.value = true
  try {
    const res = await getMyBookingsHistory({
      page: currentPage.value,
      page_size: pageSize,
      status: statusFilter.value || undefined,
    })
    tableData.value = res.items || res
    total.value = res.total || 0
  } catch (e) {
    // ignore
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
useRefreshOnShow(loadData)
</script>

<style scoped>
.mobile-my-bookings {
  padding: 0;
}
.filter-bar {
  margin-bottom: 12px;
}
.booking-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.booking-card {
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
}
.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-bottom: 1px solid #f5f5f5;
}
.room-info {
  display: flex;
  align-items: center;
  gap: 8px;
}
.room-name {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}
.room-code {
  font-size: 12px;
  color: #999;
}
.card-body {
  padding: 10px 14px;
}
.info-row {
  display: flex;
  padding: 3px 0;
  font-size: 13px;
  color: #666;
}
.info-row .label {
  color: #999;
  width: 50px;
  flex-shrink: 0;
}
.attachment {
  color: #1a73e8;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.card-footer {
  padding: 10px 14px;
  border-top: 1px solid #f5f5f5;
  display: flex;
  gap: 8px;
}
.pagination-bar {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}
.empty-text {
  text-align: center;
  color: #ccc;
  padding: 40px 0;
}
</style>
