<template>
  <div class="admin-bookings">
    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="card-header">
          <span>预订管理</span>
          <div class="header-filters">
            <el-input v-model="keyword" placeholder="搜索用户/会议室" clearable style="width: 180px" @clear="loadData" @keyup.enter="loadData">
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
            <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期"
              value-format="YYYY-MM-DD" style="width: 260px" @change="loadData" />
            <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 120px" @change="loadData">
              <el-option label="进行中" value="active" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
            <el-button type="primary" @click="loadData">搜索</el-button>
            <el-button type="success" @click="openBatchDialog">
              <el-icon><Calendar /></el-icon> 批量预订
            </el-button>
          </div>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="普通预订" name="normal">
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
            <el-table-column prop="user_name" label="预订人" width="100" />
            <el-table-column prop="user_department" label="部门" width="120" />
            <el-table-column prop="user_phone" label="电话" width="130" />
            <el-table-column prop="meeting_content" label="会议内容" min-width="130" show-overflow-tooltip />
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
                  {{ row.status === 'active' ? '有效' : '已取消' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <template v-if="row.status === 'active' && !isBookingEnded(row)">
                  <el-button size="small" type="warning" link @click="openTransferDialog(row)">转让</el-button>
                  <el-popconfirm title="确定要强制取消此预订吗？" @confirm="handleCancel(row.id)">
                    <template #reference>
                      <el-button size="small" type="danger" link>取消</el-button>
                    </template>
                  </el-popconfirm>
                </template>
                <span v-else class="text-muted">-</span>
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-wrap">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[15, 20, 50, 100]"
              :total="total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="loadData"
              @current-change="loadData"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="系统预订" name="system">
          <div class="system-header">
            <el-button type="primary" @click="openSystemDialog()">
              <el-icon><Plus /></el-icon> 新增系统预订
            </el-button>
          </div>
          <el-table :data="systemTableData" v-loading="systemLoading" stripe border>
            <el-table-column prop="room_name" label="会议室" width="150" />
            <el-table-column prop="room_code" label="编号" width="120" />
            <el-table-column label="星期" width="100">
              <template #default="{ row }">
                {{ weekdayMap[row.weekday] }}
              </template>
            </el-table-column>
            <el-table-column label="时间段" width="140">
              <template #default="{ row }">
                {{ row.start_time }} - {{ row.end_time }}
              </template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" min-width="120" />
            <el-table-column label="忽略日期" min-width="180">
              <template #default="{ row }">
                <template v-if="row.ignore_dates && row.ignore_dates.length">
                  <el-tooltip :content="row.ignore_dates.join('、')">
                    <span class="ignore-dates-text">{{ row.ignore_dates.length }} 天</span>
                  </el-tooltip>
                </template>
                <span v-else class="text-muted">-</span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'">
                  {{ row.is_active ? '启用' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160" fixed="right">
              <template #default="{ row }">
                <el-button size="small" link @click="openSystemDialog(row)">编辑</el-button>
                <el-popconfirm title="确定要删除吗？" @confirm="handleDeleteSystem(row.id)">
                  <template #reference>
                    <el-button size="small" type="danger" link>删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="transferDialogVisible" title="转让预订" width="420px" destroy-on-close>
      <div class="transfer-info">
        <p>会议室: {{ currentBooking.room_name }}</p>
        <p>日期: {{ currentBooking.booking_date }} {{ currentBooking.start_time }} - {{ currentBooking.end_time }}</p>
        <p>当前预订人: {{ currentBooking.user_name }}</p>
      </div>
      <el-form label-width="80px">
        <el-form-item label="新预订人">
          <el-select
            v-model="transferUserId"
            filterable
            remote
            :remote-method="searchUsers"
            :loading="userLoading"
            placeholder="搜索用户"
            style="width: 100%"
          >
            <el-option
              v-for="u in userOptions"
              :key="u.id"
              :label="`${u.name} (${u.username})`"
              :value="u.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="transferDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="transferLoading" @click="confirmTransfer">确认转让</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="batchDialogVisible" title="批量预订会议室" width="520px" destroy-on-close>
      <el-form ref="batchFormRef" :model="batchForm" :rules="batchRules" label-width="90px">
        <el-form-item label="会议室" prop="room_id">
          <el-select v-model="batchForm.room_id" placeholder="请选择会议室" style="width: 100%">
            <el-option v-for="r in rooms" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="预订人" prop="user_id">
          <el-select
            v-model="batchForm.user_id"
            filterable
            remote
            :remote-method="searchUsers"
            :loading="userLoading"
            placeholder="搜索用户"
            style="width: 100%"
          >
            <el-option
              v-for="u in userOptions"
              :key="u.id"
              :label="`${u.name} (${u.username})`"
              :value="u.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围" prop="date_range">
          <el-date-picker
            v-model="batchForm.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-time-select v-model="batchForm.start_time" :start="'09:00'" :step="'01:00'" :end="'20:00'" placeholder="请选择" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-time-select v-model="batchForm.end_time" :start="'09:00'" :step="'01:00'" :end="'20:00'" placeholder="请选择" style="width: 100%" />
        </el-form-item>
        <el-form-item label="会议内容">
          <el-input v-model="batchForm.meeting_content" placeholder="请输入会议内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="batchSubmitting" @click="handleBatchSubmit">开始批量预订</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="systemDialogVisible" :title="isSystemEdit ? '编辑系统预订' : '新增系统预订'" width="460px" destroy-on-close>
      <el-form ref="systemFormRef" :model="systemForm" :rules="systemRules" label-width="90px">
        <el-form-item label="会议室" prop="room_id">
          <el-select v-model="systemForm.room_id" placeholder="请选择会议室" style="width: 100%">
            <el-option v-for="r in rooms" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="星期" prop="weekday">
          <el-select v-model="systemForm.weekday" placeholder="请选择星期" style="width: 100%">
            <el-option v-for="item in weekdayOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-time-select v-model="systemForm.start_time" :start="'08:00'" :step="'00:30'" :end="'22:00'" placeholder="请选择" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-time-select v-model="systemForm.end_time" :start="'08:00'" :step="'00:30'" :end="'22:00'" placeholder="请选择" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="systemForm.remark" placeholder="请输入备注" />
        </el-form-item>
        <el-form-item label="忽略日期">
          <el-date-picker
            v-model="systemForm.ignore_dates"
            type="dates"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            placeholder="选择需要忽略的日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item v-if="isSystemEdit" label="状态">
          <el-switch v-model="systemForm.is_active" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="systemDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="systemSubmitting" @click="handleSystemSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Plus, Calendar } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { getAllBookings, cancelBooking, transferBooking, getUserOptions, getSystemBookings, createSystemBooking, updateSystemBooking, deleteSystemBooking, createBatchBookings } from '../api/bookings'
import { getRooms } from '../api/rooms'
import { useUserStore } from '../store/user'

const userStore = useUserStore()

const loading = ref(false)
const tableData = ref([])
const keyword = ref('')
const dateRange = ref(null)
const statusFilter = ref('')
const activeTab = ref('normal')
const currentPage = ref(1)
const pageSize = ref(15)
const total = ref(0)

const transferDialogVisible = ref(false)
const transferLoading = ref(false)
const currentBooking = ref({})
const transferUserId = ref(null)
const userOptions = ref([])
const userLoading = ref(false)

const systemLoading = ref(false)
const systemTableData = ref([])
const systemDialogVisible = ref(false)
const systemSubmitting = ref(false)
const isSystemEdit = ref(false)
const systemEditId = ref(null)
const systemFormRef = ref(null)
const rooms = ref([])

const batchDialogVisible = ref(false)
const batchSubmitting = ref(false)
const batchFormRef = ref(null)

const batchForm = ref({
  room_id: null,
  user_id: null,
  date_range: null,
  start_time: '',
  end_time: '',
  meeting_content: '',
})

const batchRules = {
  room_id: [{ required: true, message: '请选择会议室', trigger: 'change' }],
  user_id: [{ required: true, message: '请选择预订人', trigger: 'change' }],
  date_range: [{ required: true, message: '请选择日期范围', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
}

const weekdayOptions = [
  { value: 1, label: '星期一' },
  { value: 2, label: '星期二' },
  { value: 3, label: '星期三' },
  { value: 4, label: '星期四' },
  { value: 5, label: '星期五' },
  { value: 6, label: '星期六' },
  { value: 0, label: '星期日' },
]

const weekdayMap = {
  0: '星期日', 1: '星期一', 2: '星期二', 3: '星期三', 4: '星期四', 5: '星期五', 6: '星期六'
}

const systemForm = ref({
  room_id: null,
  weekday: null,
  start_time: '',
  end_time: '',
  remark: '系统预订',
  ignore_dates: [],
  is_active: true,
})

const systemRules = {
  room_id: [{ required: true, message: '请选择会议室', trigger: 'change' }],
  weekday: [{ required: true, message: '请选择星期', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
}

function getWeekday(dateStr) {
  if (!dateStr) return ''
  return weekdayMap[dayjs(dateStr).day()]
}

function isBookingEnded(row) {
  if (row.status !== 'active') return true
  const now = dayjs()
  const bookingDate = dayjs(row.booking_date)
  if (bookingDate.isBefore(now, 'day')) return true
  if (bookingDate.isSame(now, 'day') && row.end_time <= now.format('HH:mm')) return true
  return false
}

async function loadData() {
  loading.value = true
  try {
    const params = { keyword: keyword.value, status: statusFilter.value, page: currentPage.value, page_size: pageSize.value }
    if (dateRange.value) {
      params.date_from = dateRange.value[0]
      params.date_to = dateRange.value[1]
    }
    const res = await getAllBookings(params)
    tableData.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

async function loadSystemData() {
  systemLoading.value = true
  try {
    systemTableData.value = await getSystemBookings()
  } finally {
    systemLoading.value = false
  }
}

async function loadRooms() {
  rooms.value = await getRooms()
}

async function handleCancel(id) {
  await cancelBooking(id)
  ElMessage.success('取消成功')
  loadData()
}

function openTransferDialog(row) {
  currentBooking.value = row
  transferUserId.value = null
  userOptions.value = []
  transferDialogVisible.value = true
  searchUsers('')
}

async function searchUsers(query) {
  userLoading.value = true
  try {
    userOptions.value = await getUserOptions({ keyword: query })
  } finally {
    userLoading.value = false
  }
}

async function confirmTransfer() {
  if (!transferUserId.value) {
    ElMessage.warning('请选择新预订人')
    return
  }
  transferLoading.value = true
  try {
    await transferBooking(currentBooking.value.id, { user_id: transferUserId.value })
    ElMessage.success('转让成功')
    transferDialogVisible.value = false
    loadData()
  } finally {
    transferLoading.value = false
  }
}

function openSystemDialog(row) {
  if (row) {
    isSystemEdit.value = true
    systemEditId.value = row.id
    systemForm.value = { ...row, ignore_dates: row.ignore_dates ? [...row.ignore_dates] : [] }
  } else {
    isSystemEdit.value = false
    systemEditId.value = null
    systemForm.value = { room_id: null, weekday: null, start_time: '', end_time: '', remark: '系统预订', ignore_dates: [], is_active: true }
  }
  systemDialogVisible.value = true
}

async function handleSystemSubmit() {
  const valid = await systemFormRef.value.validate().catch(() => false)
  if (!valid) return

  if (systemForm.value.start_time >= systemForm.value.end_time) {
    ElMessage.error('结束时间必须大于开始时间')
    return
  }

  systemSubmitting.value = true
  try {
    if (isSystemEdit.value) {
      await updateSystemBooking(systemEditId.value, systemForm.value)
      ElMessage.success('修改成功')
    } else {
      await createSystemBooking(systemForm.value)
      ElMessage.success('新增成功')
    }
    systemDialogVisible.value = false
    loadSystemData()
  } finally {
    systemSubmitting.value = false
  }
}

async function handleDeleteSystem(id) {
  await deleteSystemBooking(id)
  ElMessage.success('删除成功')
  loadSystemData()
}

function openBatchDialog() {
  batchForm.value = {
    room_id: null,
    user_id: userStore?.userId || null,
    date_range: null,
    start_time: '',
    end_time: '',
    meeting_content: '',
  }
  batchDialogVisible.value = true
  searchUsers('')
}

async function handleBatchSubmit() {
  const valid = await batchFormRef.value.validate().catch(() => false)
  if (!valid) return

  if (batchForm.value.start_time >= batchForm.value.end_time) {
    ElMessage.error('结束时间必须大于开始时间')
    return
  }

  batchSubmitting.value = true
  try {
    const res = await createBatchBookings({
      room_id: batchForm.value.room_id,
      user_id: batchForm.value.user_id,
      start_date: batchForm.value.date_range[0],
      end_date: batchForm.value.date_range[1],
      start_time: batchForm.value.start_time,
      end_time: batchForm.value.end_time,
      meeting_content: batchForm.value.meeting_content,
    })
    if (res.conflicts && res.conflicts.length > 0) {
      const detail = res.conflicts.map(c => `${c.date}(${c.reason})`).join('，')
      ElMessage.warning(`${res.message}。冲突日期: ${detail}`)
    } else {
      ElMessage.success(res.message)
    }
    batchDialogVisible.value = false
    loadData()
  } catch (e) {
    const msg = e.response?.data?.error || '批量预订失败'
    ElMessage.error(msg)
  } finally {
    batchSubmitting.value = false
  }
}

onMounted(() => {
  loadData()
  loadSystemData()
  loadRooms()
})
</script>

<style scoped>
.main-card :deep(.el-card__body) {
  padding: 0 16px 16px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}
.header-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.system-header {
  margin-bottom: 12px;
}
.transfer-info {
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
}
.transfer-info p {
  margin: 4px 0;
  font-size: 14px;
  color: #333;
}
.text-muted {
  color: #ccc;
}
.ignore-dates-text {
  color: #e6a23c;
  cursor: pointer;
}
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
