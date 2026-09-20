<template>
  <div class="mobile-booking">
    <div class="date-bar">
      <el-icon class="nav-btn" :class="{ 'is-disabled': isEarliest }" @click="!isEarliest && changeDate(-1)"><ArrowLeft /></el-icon>
      <div class="date-info">
        <span class="date-text">{{ selectedDate }}</span>
        <span class="weekday">{{ weekdayText }}</span>
      </div>
      <el-icon class="nav-btn" @click="changeDate(1)"><ArrowRight /></el-icon>
      <el-button size="small" :disabled="isEarliest" @click="goToday" class="today-btn">今天</el-button>
    </div>

    <div v-if="selectedRoomId" class="selection-bar">
      <span>已选: {{ selectedRoomName }} {{ selectedStartTime }}-{{ selectedEndTime }}</span>
      <el-button type="primary" size="small" @click="openBookingDialog">预订</el-button>
      <el-button size="small" @click="clearSelection">取消</el-button>
    </div>

    <div v-loading="loading" class="room-list">
      <div v-for="room in rooms" :key="room.id" class="room-card">
        <div class="room-header" @click="showRoomDetail(room)">
          <div class="room-name">{{ room.name }}</div>
          <div class="room-code">{{ room.room_code }}</div>
        </div>
        <div class="time-slots">
          <div
            v-for="slot in timeSlots"
            :key="slot"
            class="time-slot"
            :class="getSlotClass(room, slot)"
            @click="handleSlotClick(room, slot)"
          >
            <span class="slot-time">{{ slot }}</span>
          </div>
        </div>
      </div>
      <el-empty v-if="!rooms.length && !loading" description="暂无会议室" />
    </div>

    <el-dialog
      v-model="bookingDialogVisible"
      title="确认预订"
      width="90%"
      :close-on-click-modal="false"
    >
      <div class="booking-info">
        <div class="info-row">
          <span class="label">会议室:</span>
          <span>{{ selectedRoomName }}</span>
        </div>
        <div class="info-row">
          <span class="label">日期:</span>
          <span>{{ selectedDate }}</span>
        </div>
        <div class="info-row">
          <span class="label">时间:</span>
          <span>{{ selectedStartTime }} - {{ selectedEndTime }}</span>
        </div>
        <el-input
          v-model="meetingContent"
          type="textarea"
          :rows="3"
          placeholder="会议内容（选填）"
          style="margin-top: 12px"
        />
      </div>
      <template #footer>
        <el-button @click="bookingDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleBooking">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import { getRooms } from '../../api/rooms'
import { getBookings, createBooking } from '../../api/bookings'
import { useRefreshOnShow } from '../../composables/useRefreshOnShow'

const loading = ref(false)
const submitting = ref(false)
const rooms = ref([])
const bookings = ref([])
const selectedDate = ref(dayjs().format('YYYY-MM-DD'))
const bookingDialogVisible = ref(false)
const meetingContent = ref('')

const selectedRoomId = ref(null)
const selectedRoomName = ref('')
const selectedSlots = ref([])

const weekdayMap = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

const weekdayText = computed(() => {
  const d = dayjs(selectedDate.value)
  return weekdayMap[d.day()]
})

const isEarliest = computed(() => {
  return selectedDate.value <= dayjs().format('YYYY-MM-DD')
})

const timeSlots = computed(() => {
  const slots = []
  for (let h = 9; h < 20; h++) {
    slots.push(`${String(h).padStart(2, '0')}:00`)
  }
  return slots
})

const selectedStartTime = computed(() => {
  if (!selectedSlots.value.length) return ''
  return selectedSlots.value[0]
})

const selectedEndTime = computed(() => {
  if (!selectedSlots.value.length) return ''
  const last = selectedSlots.value[selectedSlots.value.length - 1]
  const [h] = last.split(':')
  return `${String(Number(h) + 1).padStart(2, '0')}:00`
})

function changeDate(delta) {
  selectedDate.value = dayjs(selectedDate.value).add(delta, 'day').format('YYYY-MM-DD')
  clearSelection()
  loadData()
}

function goToday() {
  selectedDate.value = dayjs().format('YYYY-MM-DD')
  clearSelection()
  loadData()
}

function getSlotClass(room, slot) {
  const booking = bookings.value.find(
    (b) => b.room_id === room.id && b.start_time <= slot && b.end_time > slot
  )
  if (booking) {
    return booking.is_system ? 'system-booked' : 'booked'
  }
  const slotIndex = timeSlots.value.indexOf(slot)
  const selectedIndex = selectedSlots.value.map((s) => timeSlots.value.indexOf(s))
  if (selectedIndex.includes(slotIndex) && room.id === selectedRoomId.value) {
    return 'selected'
  }
  return 'available'
}

function handleSlotClick(room, slot) {
  const booking = bookings.value.find(
    (b) => b.room_id === room.id && b.start_time <= slot && b.end_time > slot
  )
  if (booking) return

  if (selectedRoomId.value && selectedRoomId.value !== room.id) {
    selectedSlots.value = [slot]
    selectedRoomId.value = room.id
    selectedRoomName.value = room.name
    return
  }

  selectedRoomId.value = room.id
  selectedRoomName.value = room.name

  const idx = timeSlots.value.indexOf(slot)
  if (selectedSlots.value.includes(slot)) {
    const firstIdx = timeSlots.value.indexOf(selectedSlots.value[0])
    const lastIdx = timeSlots.value.indexOf(selectedSlots.value[selectedSlots.value.length - 1])
    if (idx !== firstIdx && idx !== lastIdx) {
      ElMessage.warning('只能从两端取消时间段，保持连续预订')
      return
    }
    selectedSlots.value = selectedSlots.value.filter((s) => s !== slot)
    if (!selectedSlots.value.length) {
      selectedRoomId.value = null
      selectedRoomName.value = ''
    }
  } else {
    if (selectedSlots.value.length) {
      const lastIdx = timeSlots.value.indexOf(selectedSlots.value[selectedSlots.value.length - 1])
      if (idx === lastIdx + 1) {
        selectedSlots.value.push(slot)
      } else {
        selectedSlots.value = [slot]
      }
    } else {
      selectedSlots.value = [slot]
    }
  }
}

function clearSelection() {
  selectedSlots.value = []
  selectedRoomId.value = null
  selectedRoomName.value = ''
}

function openBookingDialog() {
  if (!selectedSlots.value.length) return
  meetingContent.value = ''
  bookingDialogVisible.value = true
}

async function handleBooking() {
  submitting.value = true
  try {
    await createBooking({
      room_id: selectedRoomId.value,
      booking_date: selectedDate.value,
      start_time: selectedSlots.value[0],
      end_time: (() => {
        const last = selectedSlots.value[selectedSlots.value.length - 1]
        const [h] = last.split(':')
        return `${String(Number(h) + 1).padStart(2, '0')}:00`
      })(),
      meeting_content: meetingContent.value,
    })
    ElMessage.success('预订成功')
    bookingDialogVisible.value = false
    clearSelection()
    loadData()
  } catch (e) {
    // error handled by interceptor
  } finally {
    submitting.value = false
  }
}

function showRoomDetail(room) {
  ElMessage.info(`${room.name} - 容量: ${room.capacity || '-'}人`)
}

async function loadData() {
  loading.value = true
  try {
    const [roomData, bookingData] = await Promise.all([
      getRooms(),
      getBookings({ date: selectedDate.value }),
    ])
    rooms.value = roomData
    bookings.value = bookingData
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
.mobile-booking {
  padding: 0;
}
.date-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  border-radius: 10px;
  padding: 10px 12px;
  margin-bottom: 12px;
}
.nav-btn {
  font-size: 20px;
  cursor: pointer;
  color: #1a73e8;
  flex-shrink: 0;
}
.nav-btn.is-disabled {
  color: #ccc;
  cursor: not-allowed;
}
.date-info {
  flex: 1;
  text-align: center;
  cursor: pointer;
}
.date-text {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}
.weekday {
  font-size: 12px;
  color: #999;
  margin-left: 6px;
}
.today-btn {
  flex-shrink: 0;
}
.selection-bar {
  background: #e6f7ff;
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #1a73e8;
}
.room-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.room-card {
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
}
.room-header {
  padding: 12px 14px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
}
.room-name {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}
.room-code {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}
.time-slots {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
  gap: 6px;
  padding: 10px 12px;
}
.time-slot {
  padding: 8px 4px;
  text-align: center;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.time-slot.available {
  background: #f0f7ff;
  color: #1a73e8;
  border: 1px solid #d6e8fb;
}
.time-slot.available:active {
  background: #d6e8fb;
}
.time-slot.selected {
  background: #1a73e8;
  color: #fff;
}
.time-slot.booked {
  background: #f5f5f5;
  color: #ccc;
  cursor: not-allowed;
  text-decoration: line-through;
}
.time-slot.system-booked {
  background: #fff7e6;
  color: #fa8c16;
  cursor: not-allowed;
}
.slot-time {
  font-size: 12px;
}
.booking-info .info-row {
  display: flex;
  padding: 6px 0;
  font-size: 14px;
}
.booking-info .label {
  color: #999;
  width: 70px;
  flex-shrink: 0;
}
</style>
