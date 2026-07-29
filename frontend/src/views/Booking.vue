<template>
  <div class="booking-page">
    <el-card shadow="never" class="booking-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span>会议室预订</span>
            <el-date-picker
              v-model="selectedDate"
              type="date"
              placeholder="选择日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              :disabled-date="disabledDate"
              style="margin-left: 16px"
              @change="loadBookings"
            />
            <span class="weekday-tag">{{ weekdayText }}</span>
            <div class="date-nav-btns">
              <el-button size="small" @click="changeDate(-1)" :disabled="isPrevDisabled">
                <el-icon><ArrowLeft /></el-icon> 前一天
              </el-button>
              <el-button size="small" @click="goToday" :disabled="isEarliest">今天</el-button>
              <el-button size="small" @click="changeDate(1)" :disabled="isNextDisabled">
                下一天 <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </div>
          <div class="header-right">
            <el-button v-if="hasSelection" type="primary" @click="openBookingDialog">
              <el-icon><Check /></el-icon> 确认预订 ({{ selectedSlots.length }}个时段)
            </el-button>
            <el-button v-if="hasSelection" @click="clearSelection">取消选择</el-button>
            <el-radio-group v-model="viewMode" @change="handleViewModeChange">
              <el-radio-button value="grid">网格视图</el-radio-button>
              <el-radio-button value="monthly">月度视图</el-radio-button>
              <el-radio-button value="list">列表视图</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>

      <div v-if="viewMode === 'grid'" class="grid-view" v-loading="loading">
        <div class="grid-hint" v-if="!hasSelection">
          <el-icon><InfoFilled /></el-icon> 点击选择一个时段，或按住拖拽选择多个连续时段
        </div>
        <div class="grid-hint selected-hint" v-else>
          已选中 <strong>{{ selectedRoom?.name }}</strong> 的
          <strong>{{ selectedSlots[0] }}</strong> 至
          <strong>{{ lastSelectedEnd }}</strong>，共 {{ selectedSlots.length }} 个时段
        </div>
        <div class="grid-container" v-if="rooms.length">
          <div class="grid-scroll">
            <table class="grid-table"
              @mouseup="handleMouseUp"
              @mouseleave="handleMouseLeave"
            >
              <thead>
                <tr>
                  <th class="room-header">会议室</th>
                  <th v-for="h in timeSlots" :key="h" class="time-header">{{ h }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="room in rooms" :key="room.id">
                  <td class="room-name-cell" @mouseenter="showRoomRemark(room, $event)" @mouseleave="hideRoomRemark">
                    <div class="room-title">{{ room.name }}</div>
                    <div class="room-code">{{ room.room_code }}</div>
                  </td>
                  <td
                    v-for="(slot, idx) in timeSlots"
                    :key="idx"
                    class="slot-cell"
                    :class="getSlotClass(room.id, slot)"
                    @mousedown.prevent="handleMouseDown(room, slot)"
                    @mouseenter="handleMouseEnter(room, slot)"
                    @mouseup.stop="handleMouseUp"
                    @touchstart.prevent="handleTouchStart(room, slot, $event)"
                    @touchmove.prevent="handleTouchMove($event)"
                    @touchend.prevent="handleTouchEnd"
                    @click.prevent
                  >
                    <span v-if="getBooking(room.id, slot)" class="slot-booked" :class="{ 'system-text': getBooking(room.id, slot).is_system }">
                      {{ getBooking(room.id, slot).is_system ? getBooking(room.id, slot).meeting_content : getBooking(room.id, slot).user_name }}
                    </span>
                    <span v-else-if="isSlotSelected(room.id, slot)" class="slot-selected-icon">
                      <el-icon><Check /></el-icon>
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <el-empty v-else description="暂无会议室" />
      </div>

      <div v-else-if="viewMode === 'monthly'" class="monthly-view" v-loading="loading">
        <div class="monthly-header">
          <div class="month-nav-btns">
            <el-button size="small" @click="changeMonth(-1)" :disabled="isPrevMonthDisabled">
              <el-icon><ArrowLeft /></el-icon> 上个月
            </el-button>
            <span class="month-title">{{ currentYear }}年{{ currentMonth }}月</span>
            <el-button size="small" @click="changeMonth(1)" :disabled="isNextMonthDisabled">
              下个月 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>
        <div class="monthly-grid-container" v-if="rooms.length">
          <div class="monthly-grid-scroll">
            <table class="monthly-table">
              <thead>
                <tr>
                  <th class="monthly-room-header">会议室</th>
                  <th v-for="day in monthDays" :key="day" class="monthly-day-header" :class="{ 'is-today': isToday(day), 'is-weekend': isWeekend(day) }">
                    <div class="day-num">{{ day }}</div>
                    <div class="day-label">{{ getDayLabel(day) }}</div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="room in rooms" :key="room.id">
                  <td class="monthly-room-cell" @mouseenter="showRoomRemark(room, $event)" @mouseleave="hideRoomRemark">
                    <div class="room-title">{{ room.name }}</div>
                    <div class="room-code">{{ room.room_code }}</div>
                  </td>
                  <td v-for="day in monthDays" :key="day" class="monthly-day-cell" :class="getMonthlyCellClass(room.id, day)" @click="handleMonthlyCellClick(room, day)">
                    <div class="cell-content">
                      <span v-if="getMonthlyBookingCount(room.id, day) > 0" class="booking-count">
                        {{ getMonthlyBookingCount(room.id, day) }}
                      </span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <el-empty v-else description="暂无会议室" />
      </div>

      <div v-else class="list-view" v-loading="loading">
        <el-table :data="bookingList" stripe border>
          <el-table-column prop="room_name" label="会议室" width="150" />
          <el-table-column prop="room_code" label="编号" width="120" />
          <el-table-column prop="booking_date" label="日期" width="120" />
          <el-table-column label="时间段" width="160">
            <template #default="{ row }">
              {{ row.start_time }} - {{ row.end_time }}
            </template>
          </el-table-column>
          <el-table-column prop="user_name" label="预订人" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.is_system" type="warning" size="small">系统</el-tag>
              {{ row.user_name }}
            </template>
          </el-table-column>
          <el-table-column prop="user_department" label="部门" width="120" />
          <el-table-column prop="user_phone" label="联系方式" width="140" />
        </el-table>
      </div>
    </el-card>

    <div class="booking-tooltip" v-show="tooltipVisible" :style="tooltipStyle">
      <div class="tooltip-title">{{ tooltipData.room_name }}</div>
      <template v-if="tooltipData.is_system">
        <div class="tooltip-info" style="color: #722ed1; font-weight: 500;">系统预订</div>
        <div class="tooltip-info">{{ tooltipData.meeting_content }}</div>
      </template>
      <template v-else>
        <div class="tooltip-info">预订人: {{ tooltipData.user_name }}</div>
        <div class="tooltip-info">部门: {{ tooltipData.user_department }}</div>
        <div class="tooltip-info">电话: {{ tooltipData.user_phone }}</div>
      </template>
      <div class="tooltip-info">时间: {{ tooltipData.start_time }} - {{ tooltipData.end_time }}</div>
    </div>

    <div class="room-remark-tooltip" v-show="roomRemarkVisible" :style="roomRemarkStyle">
      <div class="remark-title">会议室备注</div>
      <div class="remark-content" v-html="roomRemarkHtml"></div>
    </div>

    <el-dialog v-model="bookingDialogVisible" title="确认预订" width="460px" destroy-on-close>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="会议室">{{ bookingForm.room_name }}</el-descriptions-item>
        <el-descriptions-item label="日期">{{ bookingForm.date }} {{ bookingForm.weekday }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ bookingForm.start_time }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ bookingForm.end_time }}</el-descriptions-item>
        <el-descriptions-item label="预订时长">{{ bookingForm.duration }} 小时</el-descriptions-item>
      </el-descriptions>
      <el-form :model="bookingForm" label-width="80px" style="margin-top: 16px">
        <el-form-item label="会议内容">
          <el-input v-model="bookingForm.meeting_content" type="textarea" :rows="3" placeholder="请输入会议内容（选填）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bookingDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="confirmBooking">确认预订</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="monthlyDayDialogVisible" :title="monthlyDayDialogTitle" width="600px" destroy-on-close>
      <el-table :data="monthlyDayBookings" stripe border>
        <el-table-column label="类型" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.is_system" type="warning" size="small">系统</el-tag>
            <el-tag v-else type="info" size="small">预订</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间段" width="140">
          <template #default="{ row }">
            {{ row.start_time }} - {{ row.end_time }}
          </template>
        </el-table-column>
        <el-table-column prop="user_name" label="预订人" width="100" />
        <el-table-column prop="user_department" label="部门" />
      </el-table>
      <el-empty v-if="monthlyDayBookings.length === 0" description="当天暂无预订" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, InfoFilled, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { getRooms } from '../api/rooms'
import { getBookings, getMonthlyBookings, createBooking, cancelBooking } from '../api/bookings'
import { useUserStore } from '../store/user'

const userStore = useUserStore()
const loading = ref(false)
const submitting = ref(false)
const rooms = ref([])
const bookings = ref([])
const selectedDate = ref(dayjs().add(0, 'day').format('YYYY-MM-DD'))
const viewMode = ref('grid')
const bookingList = ref([])

// Monthly view state
const currentYear = ref(dayjs().year())
const currentMonth = ref(dayjs().month() + 1)
const monthlyBookings = ref([])

const monthDays = computed(() => {
  const daysInMonth = dayjs(`${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}`).daysInMonth()
  return Array.from({ length: daysInMonth }, (_, i) => i + 1)
})

function isToday(day) {
  const today = dayjs()
  return today.year() === currentYear.value && today.month() + 1 === currentMonth.value && today.date() === day
}

function isWeekend(day) {
  const d = dayjs(`${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(day).padStart(2, '0')}`)
  const weekday = d.day()
  return weekday === 0 || weekday === 6
}

function getDayLabel(day) {
  const d = dayjs(`${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(day).padStart(2, '0')}`)
  const labels = ['日', '一', '二', '三', '四', '五', '六']
  return labels[d.day()]
}

function changeMonth(delta) {
  const newMonth = currentMonth.value + delta
  if (newMonth < 1) {
    currentMonth.value = 12
    currentYear.value--
  } else if (newMonth > 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value = newMonth
  }
  loadMonthlyBookings()
}

const isPrevMonthDisabled = computed(() => {
  const now = dayjs()
  return currentYear.value === now.year() && currentMonth.value === now.month() + 1
})

const isNextMonthDisabled = computed(() => {
  const now = dayjs()
  const maxMonth = now.add(3, 'month')
  return currentYear.value === maxMonth.year() && currentMonth.value === maxMonth.month() + 1
})

const monthlyBookingMap = computed(() => {
  const map = {}
  monthlyBookings.value.forEach((b) => {
    const key = `${b.room_id}_${b.booking_date}`
    if (!map[key]) {
      map[key] = []
    }
    map[key].push(b)
  })
  return map
})

function getMonthlyBookingCount(roomId, day) {
  const dateStr = `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  const key = `${roomId}_${dateStr}`
  return monthlyBookingMap.value[key]?.length || 0
}

function getMonthlyCellClass(roomId, day) {
  const count = getMonthlyBookingCount(roomId, day)
  const dateStr = `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  const d = dayjs(dateStr)

  if (d.isBefore(dayjs().startOf('day'))) {
    return 'past-day'
  }

  if (count === 0) {
    return 'no-booking'
  }

  const dateStr2 = `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  const bookings = monthlyBookingMap.value[`${roomId}_${dateStr2}`] || []
  const timeSlotsCount = 11
  const bookedSlots = new Set()
  bookings.forEach(b => {
    let startIdx = timeSlots.indexOf(b.start_time)
    let endIdx = timeSlots.indexOf(b.end_time)
    if (endIdx === -1) endIdx = timeSlotsCount
    if (startIdx === -1) startIdx = 0
    for (let i = startIdx; i < endIdx; i++) {
      bookedSlots.add(timeSlots[i])
    }
  })

  if (bookedSlots.size >= timeSlotsCount) {
    return 'fully-booked'
  }

  if (bookedSlots.size >= timeSlotsCount / 2) {
    return 'partially-booked'
  }

  return 'has-booking'
}

async function loadMonthlyBookings() {
  loading.value = true
  try {
    const [roomList, bookingData] = await Promise.all([
      getRooms(),
      getMonthlyBookings({ year: currentYear.value, month: currentMonth.value }),
    ])
    rooms.value = roomList.filter((r) => r.is_active)
    monthlyBookings.value = bookingData
  } finally {
    loading.value = false
  }
}

// ====== Monthly Day Dialog ======
const monthlyDayDialogVisible = ref(false)
const monthlyDayDialogTitle = ref('')
const monthlyDayBookings = ref([])

function handleMonthlyCellClick(room, day) {
  const count = getMonthlyBookingCount(room.id, day)
  if (count === 0) return

  const dateStr = `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  const cellDate = dayjs(dateStr)
  if (cellDate.isBefore(dayjs().startOf('day'))) return

  const key = `${room.id}_${dateStr}`
  const bookings = monthlyBookingMap.value[key] || []

  monthlyDayDialogTitle.value = `${room.name} - ${dateStr} 预订情况`
  monthlyDayBookings.value = bookings
  monthlyDayDialogVisible.value = true
}

function handleViewModeChange() {
  if (viewMode.value === 'monthly') {
    loadMonthlyBookings()
  } else {
    loadBookings()
  }
}

const timeSlots = []
for (let h = 9; h < 20; h++) {
  timeSlots.push(`${String(h).padStart(2, '0')}:00`)
}

const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']

function getWeekday(dateStr) {
  if (!dateStr) return ''
  return weekdays[dayjs(dateStr).day()]
}

function disabledDate(date) {
  const today = dayjs().startOf('day')
  const maxDate = dayjs().add(15, 'day').endOf('day')
  return dayjs(date).isBefore(today) || dayjs(date).isAfter(maxDate)
}

const isEarliest = computed(() => {
  return dayjs(selectedDate.value).isSame(dayjs().add(0, 'day'), 'day')
})

const isPrevDisabled = computed(() => {
  return dayjs(selectedDate.value).isSameOrBefore(dayjs().add(0, 'day'))
})

const isNextDisabled = computed(() => {
  return dayjs(selectedDate.value).isSameOrAfter(dayjs().add(15, 'day'))
})

function changeDate(delta) {
  const newDate = dayjs(selectedDate.value).add(delta, 'day')
  if (disabledDate(newDate.toDate())) return
  selectedDate.value = newDate.format('YYYY-MM-DD')
  loadBookings()
}

function goToday() {
  const today = dayjs().add(0, 'day')
  selectedDate.value = today.format('YYYY-MM-DD')
  loadBookings()
}

const weekdayText = computed(() => getWeekday(selectedDate.value))

const bookingMap = computed(() => {
  const map = {}
  bookings.value.forEach((b) => {
    let startIdx = timeSlots.indexOf(b.start_time)
    let endIdx = timeSlots.indexOf(b.end_time)
    if (endIdx === -1) endIdx = timeSlots.length
    if (startIdx === -1) startIdx = 0
    for (let i = startIdx; i < endIdx; i++) {
      const key = `${b.room_id}_${timeSlots[i]}`
      map[key] = b
    }
  })
  return map
})

function getBooking(roomId, slot) {
  return bookingMap.value[`${roomId}_${slot}`]
}

// ====== 多时段选择逻辑 ======
const selectedRoom = ref(null)
const selectedSlots = ref([])
const isDragging = ref(false)
const dragStartSlot = ref(null)

const hasSelection = computed(() => selectedSlots.value.length > 0 && selectedRoom.value)

const lastSelectedEnd = computed(() => {
  if (!selectedSlots.value.length) return ''
  const lastIdx = timeSlots.indexOf(selectedSlots.value[selectedSlots.value.length - 1])
  const nextIdx = lastIdx + 1
  return nextIdx < timeSlots.length ? timeSlots[nextIdx] : '20:00'
})

function isSlotSelected(roomId, slot) {
  return selectedRoom.value?.id === roomId && selectedSlots.value.includes(slot)
}

function getSlotClass(roomId, slot) {
  if (isSlotSelected(roomId, slot)) {
    return 'selected'
  }
  const booking = getBooking(roomId, slot)
  if (booking) {
    if (booking.is_system) {
      return 'system-booked'
    }
    if (userStore.isAdmin || booking.user_id === userStore.userId) {
      return 'booked-self'
    }
    return 'booked'
  }
  return 'available'
}

function getAvailableRange(roomId, startSlot) {
  const startIdx = timeSlots.indexOf(startSlot)
  let endIdx = startIdx

  while (endIdx < timeSlots.length) {
    const nextSlot = timeSlots[endIdx]
    if (getBooking(roomId, nextSlot)) break
    endIdx++
  }

  return timeSlots.slice(startIdx, endIdx)
}

function clearSelection() {
  selectedRoom.value = null
  selectedSlots.value = []
  isDragging.value = false
  dragStartSlot.value = null
}

function handleMouseDown(room, slot) {
  if (getBooking(room.id, slot)) return

  if (selectedRoom.value?.id === room.id && selectedSlots.value.includes(slot)) {
    clearSelection()
    return
  }

  if (selectedRoom.value?.id !== room.id) {
    clearSelection()
  }

  isDragging.value = true
  dragStartSlot.value = slot
  selectedRoom.value = room
  selectedSlots.value = [slot]
}

function handleMouseEnter(room, slot) {
  if (!isDragging.value) return
  if (selectedRoom.value?.id !== room.id) return

  const available = getAvailableRange(room.id, dragStartSlot.value)
  const dragIdx = timeSlots.indexOf(dragStartSlot.value)
  const hoverIdx = timeSlots.indexOf(slot)

  const minIdx = Math.min(dragIdx, hoverIdx)
  const maxIdx = Math.max(dragIdx, hoverIdx)

  const selected = []
  for (let i = minIdx; i <= maxIdx; i++) {
    const s = timeSlots[i]
    if (!getBooking(room.id, s)) {
      selected.push(s)
    } else {
      break
    }
  }

  selectedSlots.value = selected
}

function handleMouseUp() {
  isDragging.value = false
}

function handleMouseLeave() {
  isDragging.value = false
}

function getSlotFromTouch(touch) {
  const element = document.elementFromPoint(touch.clientX, touch.clientY)
  if (!element) return null
  const td = element.closest('.slot-cell')
  if (!td) return null
  const room = rooms.value.find(r => {
    const tr = td.closest('tr')
    return tr && tr.querySelector('.room-title')?.textContent === r.name
  })
  if (!room) return null
  const slotIndex = Array.from(td.parentNode.children).indexOf(td) - 1
  if (slotIndex < 0 || slotIndex >= timeSlots.length) return null
  return { room, slot: timeSlots[slotIndex] }
}

function handleTouchStart(room, slot, event) {
  if (getBooking(room.id, slot)) return

  if (selectedRoom.value?.id === room.id && selectedSlots.value.includes(slot)) {
    clearSelection()
    return
  }

  if (selectedRoom.value?.id !== room.id) {
    clearSelection()
  }

  isDragging.value = true
  dragStartSlot.value = slot
  selectedRoom.value = room
  selectedSlots.value = [slot]
}

function handleTouchMove(event) {
  if (!isDragging.value) return

  const touch = event.touches[0]
  const result = getSlotFromTouch(touch)
  if (!result) return
  if (selectedRoom.value?.id !== result.room.id) return

  const dragIdx = timeSlots.indexOf(dragStartSlot.value)
  const hoverIdx = timeSlots.indexOf(result.slot)

  const minIdx = Math.min(dragIdx, hoverIdx)
  const maxIdx = Math.max(dragIdx, hoverIdx)

  const selected = []
  for (let i = minIdx; i <= maxIdx; i++) {
    const s = timeSlots[i]
    if (!getBooking(result.room.id, s)) {
      selected.push(s)
    } else {
      break
    }
  }

  selectedSlots.value = selected
}

function handleTouchEnd() {
  isDragging.value = false
}

function handleSlotClick(room, slot) {
  if (getBooking(room.id, slot)) return
}

// ====== 预订对话框 ======
const bookingDialogVisible = ref(false)
const bookingForm = ref({})

function openBookingDialog() {
  if (!hasSelection.value) return

  const sorted = [...selectedSlots.value].sort()
  const start = sorted[0]
  const endIdx = timeSlots.indexOf(sorted[sorted.length - 1]) + 1
  const end = endIdx < timeSlots.length ? timeSlots[endIdx] : '20:00'

  bookingForm.value = {
    room_id: selectedRoom.value.id,
    room_name: selectedRoom.value.name,
    date: selectedDate.value,
    weekday: getWeekday(selectedDate.value),
    start_time: start,
    end_time: end,
    duration: sorted.length,
    meeting_content: '',
  }
  bookingDialogVisible.value = true
}

async function confirmBooking() {
  submitting.value = true
  try {
    await createBooking({
      room_id: bookingForm.value.room_id,
      booking_date: bookingForm.value.date,
      start_time: bookingForm.value.start_time,
      end_time: bookingForm.value.end_time,
      meeting_content: bookingForm.value.meeting_content,
    })
    ElMessage.success('预订成功')
    bookingDialogVisible.value = false
    clearSelection()
    loadBookings()
  } finally {
    submitting.value = false
  }
}

async function handleCancel(bookingId) {
  await cancelBooking(bookingId)
  ElMessage.success('取消成功')
  loadBookings()
}

// ====== Tooltip ======
const tooltipVisible = ref(false)
const tooltipStyle = ref({})
const tooltipData = ref({})

function handleSlotHover(room, slot, event) {
  const booking = getBooking(room.id, slot)
  if (!booking) return
  tooltipData.value = booking
  tooltipVisible.value = true
  const rect = event.target.getBoundingClientRect()
  tooltipStyle.value = {
    left: rect.left + 'px',
    top: rect.bottom + 4 + 'px',
  }
}

function hideTooltip() {
  tooltipVisible.value = false
}

// ====== Room Remark Tooltip ======
const roomRemarkVisible = ref(false)
const roomRemarkStyle = ref({})
const roomRemarkText = ref('')

const roomRemarkHtml = computed(() => {
  if (!roomRemarkText.value) return ''
  return roomRemarkText.value.replace(/\n/g, '<br>')
})

function showRoomRemark(room, event) {
  if (!room.remark) return
  roomRemarkText.value = room.remark
  roomRemarkVisible.value = true
  const rect = event.target.getBoundingClientRect()
  roomRemarkStyle.value = {
    left: rect.left + 'px',
    top: rect.bottom + 4 + 'px',
  }
}

function hideRoomRemark() {
  roomRemarkVisible.value = false
}

// ====== 数据加载 ======
async function loadBookings() {
  loading.value = true
  try {
    const [roomList, bookingData] = await Promise.all([
      getRooms(),
      getBookings({ date: selectedDate.value }),
    ])
    rooms.value = roomList.filter((r) => r.is_active)
    bookings.value = bookingData
    bookingList.value = bookingData
  } finally {
    loading.value = false
  }
}

onMounted(loadBookings)
</script>

<style scoped>
.booking-card :deep(.el-card__body) {
  padding: 16px;
}
.grid-table {
  touch-action: none;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}
.header-left {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.grid-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  margin-bottom: 12px;
  background: #f0f5ff;
  border: 1px solid #adc6ff;
  border-radius: 4px;
  font-size: 13px;
  color: #1890ff;
}
.grid-hint.selected-hint {
  background: #f6ffed;
  border-color: #b7eb8f;
  color: #52c41a;
}
.grid-view {
  overflow: hidden;
}
.grid-scroll {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
.grid-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  user-select: none;
}
.grid-table th,
.grid-table td {
  border: 1px solid #e8e8e8;
  padding: 0;
  text-align: center;
  height: 48px;
  min-width: 72px;
}
.room-header {
  width: 140px;
  min-width: 140px;
  background: #fafafa;
  font-weight: 600;
  color: #333;
  position: sticky;
  left: 0;
  z-index: 1;
}
.time-header {
  background: #fafafa;
  font-weight: 500;
  color: #666;
  font-size: 13px;
}
.room-name-cell {
  background: #fafafa;
  position: sticky;
  left: 0;
  z-index: 1;
  padding: 8px;
  text-align: left !important;
  cursor: default;
}
.room-title {
  font-weight: 500;
  color: #333;
  font-size: 14px;
}
.room-code {
  font-size: 12px;
  color: #999;
}
.slot-cell {
  cursor: pointer;
  transition: background 0.15s;
  font-size: 12px;
  touch-action: none;
  user-select: none;
  -webkit-user-select: none;
}
.slot-cell.available {
  background: #f6ffed;
}
.slot-cell.available:hover {
  background: #d9f7be;
}
.slot-cell.selected {
  background: #1890ff !important;
  color: #fff;
}
.slot-cell.selected .slot-selected-icon {
  color: #fff;
  font-size: 16px;
  font-weight: bold;
}
.slot-cell.booked {
  background: #fff1f0;
  cursor: not-allowed;
}
.slot-cell.booked-self {
  background: #ffd8bf;
  cursor: pointer;
}
.slot-booked {
  font-size: 11px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
  padding: 0 4px;
}
.slot-cell.system-booked {
  background: #f9f0ff;
  cursor: not-allowed;
}
.slot-cell.system-booked:hover {
  background: #efdbff;
}
.slot-cell.system-booked .slot-booked {
  color: #722ed1;
  font-weight: 500;
}
.slot-cell.system-booked .system-text {
  font-size: 10px;
  letter-spacing: 0.5px;
}
.weekday-tag {
  display: inline-block;
  padding: 2px 10px;
  background: #e6f7ff;
  color: #1890ff;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
}
.date-nav-btns {
  display: inline-flex;
  gap: 4px;
  margin-left: 8px;
}
.date-nav-btns .el-button {
  padding: 5px 10px;
}
.booking-tooltip {
  position: fixed;
  z-index: 9999;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  pointer-events: none;
  min-width: 200px;
}
.tooltip-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 8px;
  color: #333;
}
.tooltip-info {
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
}
.room-remark-tooltip {
  position: fixed;
  z-index: 9999;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  pointer-events: none;
  min-width: 150px;
  max-width: 300px;
}
.remark-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 8px;
  color: #333;
}
.remark-content {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}
.monthly-view {
  overflow: hidden;
}
.monthly-header {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}
.month-nav-btns {
  display: inline-flex;
  align-items: center;
  gap: 12px;
}
.month-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  min-width: 120px;
  text-align: center;
}
.monthly-grid-container {
  overflow: hidden;
}
.monthly-grid-scroll {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
.monthly-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  user-select: none;
}
.monthly-table th,
.monthly-table td {
  border: 1px solid #e8e8e8;
  padding: 0;
  text-align: center;
  height: 48px;
  min-width: 56px;
}
.monthly-room-header {
  width: 140px;
  min-width: 140px;
  background: #fafafa;
  font-weight: 600;
  color: #333;
  position: sticky;
  left: 0;
  z-index: 1;
}
.monthly-day-header {
  background: #fafafa;
  font-weight: 500;
  color: #666;
  font-size: 12px;
  padding: 4px 2px;
}
.monthly-day-header.is-today {
  background: #e6f7ff;
  color: #1890ff;
}
.monthly-day-header.is-weekend {
  color: #ff4d4f;
}
.day-num {
  font-size: 14px;
  font-weight: 600;
}
.day-label {
  font-size: 11px;
  color: #999;
}
.monthly-day-header.is-weekend .day-label {
  color: #ff4d4f;
}
.monthly-room-cell {
  background: #fafafa;
  position: sticky;
  left: 0;
  z-index: 1;
  padding: 8px;
  text-align: left !important;
  cursor: default;
}
.monthly-day-cell {
  cursor: default;
  transition: background 0.15s;
}
.monthly-day-cell.has-booking,
.monthly-day-cell.partially-booked,
.monthly-day-cell.fully-booked {
  cursor: pointer;
}
.monthly-day-cell .cell-content {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}
.booking-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 500;
}
.monthly-day-cell.no-booking {
  background: #f6ffed;
}
.monthly-day-cell.has-booking {
  background: #fff7e6;
}
.monthly-day-cell.has-booking .booking-count {
  background: #ffd591;
  color: #d46b08;
}
.monthly-day-cell.partially-booked {
  background: #fff1f0;
}
.monthly-day-cell.partially-booked .booking-count {
  background: #ffa39e;
  color: #cf1322;
}
.monthly-day-cell.fully-booked {
  background: #ffccc7;
}
.monthly-day-cell.fully-booked .booking-count {
  background: #ff4d4f;
  color: #fff;
}
.monthly-day-cell.past-day {
  background: #f5f5f5;
  color: #bbb;
}
.monthly-day-cell.past-day .booking-count {
  background: #d9d9d9;
  color: #999;
}
@media (max-width: 768px) {
  .booking-card :deep(.el-card__body) {
    padding: 12px 8px;
  }
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .header-left {
    width: 100%;
  }
  .header-right {
    width: 100%;
    justify-content: space-between;
  }
  .grid-table th,
  .grid-table td {
    height: 40px;
    min-width: 60px;
  }
  .room-header {
    width: 100px;
    min-width: 100px;
  }
  .room-name-cell {
    padding: 4px;
  }
  .room-title {
    font-size: 12px;
  }
  .room-code {
    font-size: 10px;
  }
  .slot-booked {
    font-size: 10px;
  }
  .weekday-tag {
    font-size: 12px;
    padding: 2px 6px;
  }
  .date-nav-btns {
    margin-left: 4px;
  }
  .date-nav-btns .el-button {
    padding: 4px 6px;
    font-size: 12px;
  }
  .grid-hint {
    font-size: 12px;
    padding: 6px 8px;
  }
  :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }
  :deep(.el-dialog__body) {
    padding: 12px;
  }
  :deep(.el-descriptions) {
    font-size: 13px;
  }
  .monthly-table th,
  .monthly-table td {
    height: 40px;
    min-width: 44px;
  }
  .monthly-room-header {
    width: 100px;
    min-width: 100px;
  }
  .monthly-room-cell {
    padding: 4px;
  }
  .day-num {
    font-size: 12px;
  }
  .day-label {
    font-size: 10px;
  }
  .month-title {
    font-size: 14px;
    min-width: 100px;
  }
}
</style>
