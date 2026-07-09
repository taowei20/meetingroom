<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #e6f7ff">
            <el-icon style="color: #1890ff; font-size: 32px"><Calendar /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.today_count }}</div>
            <div class="stat-label">今日预订数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #f6ffed">
            <el-icon style="color: #52c41a; font-size: 32px"><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_rooms }}</div>
            <div class="stat-label">会议室总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #fff7e6">
            <el-icon style="color: #fa8c16; font-size: 32px"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_bookings }}</div>
            <div class="stat-label">总预订数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :xs="24" :sm="14">
        <el-card shadow="hover">
          <template #header>本周预订趋势</template>
          <div ref="weekChartRef" style="height: 320px"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="10">
        <el-card shadow="hover">
          <template #header>最近预订</template>
          <div class="recent-list">
            <div v-if="!stats.recent_bookings?.length" class="empty-text">暂无预订</div>
            <div v-for="item in stats.recent_bookings" :key="item.id" class="recent-item">
              <div class="recent-room">{{ item.room_name }}</div>
              <div class="recent-info">
                <span>{{ item.booking_date }}</span>
                <span class="time-range">{{ item.start_time }} - {{ item.end_time }}</span>
              </div>
              <div class="recent-user">{{ item.user_name }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Calendar, OfficeBuilding, Document } from '@element-plus/icons-vue'
import { getStatsOverview } from '../api/bookings'

const stats = ref({
  today_count: 0,
  total_rooms: 0,
  total_bookings: 0,
  recent_bookings: [],
  week_data: [],
})

const weekChartRef = ref(null)

async function loadStats() {
  try {
    stats.value = await getStatsOverview()
    await nextTick()
    renderChart()
  } catch (e) {
    // ignore
  }
}

function renderChart() {
  if (!weekChartRef.value) return
  const chart = echarts.init(weekChartRef.value)
  const data = stats.value.week_data || []
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: data.map((d) => d.date),
      axisLabel: { formatter: (v) => v.slice(5) },
    },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        data: data.map((d) => d.count),
        type: 'bar',
        color: '#1890ff',
        barWidth: '40%',
        itemStyle: { borderRadius: [4, 4, 0, 0] },
      },
    ],
  })
}

onMounted(loadStats)
</script>

<style scoped>
.dashboard {
  padding: 0;
}
.stat-row {
  margin-bottom: 20px;
}
.stat-card {
  display: flex;
  align-items: center;
}
.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 20px;
}
.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
}
.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #333;
}
.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 4px;
}
.recent-list {
  max-height: 320px;
  overflow-y: auto;
}
.recent-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}
.recent-item:last-child {
  border-bottom: none;
}
.recent-room {
  font-weight: 500;
  color: #333;
  width: 100px;
}
.recent-info {
  flex: 1;
  text-align: center;
  font-size: 13px;
  color: #666;
}
.time-range {
  margin-left: 8px;
  color: #1890ff;
}
.recent-user {
  width: 80px;
  text-align: right;
  color: #666;
}
.empty-text {
  text-align: center;
  color: #ccc;
  padding: 40px 0;
}
@media (max-width: 768px) {
  .stat-card :deep(.el-card__body) {
    padding: 12px;
  }
  .stat-icon {
    width: 48px;
    height: 48px;
  }
  .stat-icon :deep(.el-icon) {
    font-size: 24px !important;
  }
  .stat-value {
    font-size: 20px;
  }
  .stat-label {
    font-size: 12px;
  }
  .recent-room {
    width: 80px;
    font-size: 13px;
  }
  .recent-info {
    font-size: 12px;
  }
  .recent-user {
    width: 60px;
    font-size: 12px;
  }
  .stat-row {
    margin-bottom: 12px;
  }
  :deep(.el-row) {
    margin-left: 0 !important;
    margin-right: 0 !important;
  }
  :deep(.el-col) {
    padding-left: 0 !important;
    padding-right: 0 !important;
    margin-bottom: 12px;
  }
}
</style>
