<template>
  <div class="mobile-dashboard">
    <div class="stat-cards">
      <div class="stat-card blue">
        <div class="stat-value">{{ stats.today_count }}</div>
        <div class="stat-label">今日预订</div>
      </div>
      <div class="stat-card green">
        <div class="stat-value">{{ stats.total_rooms }}</div>
        <div class="stat-label">会议室</div>
      </div>
      <div class="stat-card orange">
        <div class="stat-value">{{ stats.total_bookings }}</div>
        <div class="stat-label">总预订</div>
      </div>
    </div>

    <div class="section">
      <div class="section-title">本周预订趋势</div>
      <div ref="weekChartRef" class="chart-area"></div>
    </div>

    <div class="section">
      <div class="section-title">最近预订</div>
      <div v-if="!stats.recent_bookings?.length" class="empty-text">暂无预订</div>
      <div v-for="item in stats.recent_bookings" :key="item.id" class="recent-item">
        <div class="item-left">
          <div class="item-room">{{ item.room_name }}</div>
          <div class="item-time">{{ item.start_time }} - {{ item.end_time }}</div>
        </div>
        <div class="item-right">
          <div class="item-date">{{ item.booking_date }}</div>
          <div class="item-user">{{ item.user_name }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getStatsOverview } from '../../api/bookings'
import { useRefreshOnShow } from '../../composables/useRefreshOnShow'

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
      axisLabel: { formatter: (v) => v.slice(5), fontSize: 11 },
    },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        data: data.map((d) => d.count),
        type: 'bar',
        color: '#1a73e8',
        barWidth: '40%',
        itemStyle: { borderRadius: [4, 4, 0, 0] },
      },
    ],
  })
}

onMounted(loadStats)
useRefreshOnShow(loadStats)
</script>

<style scoped>
.mobile-dashboard {
  padding: 0;
}
.stat-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 16px;
}
.stat-card {
  border-radius: 10px;
  padding: 14px 10px;
  text-align: center;
  color: #fff;
}
.stat-card.blue { background: linear-gradient(135deg, #1a73e8, #4da3ff); }
.stat-card.green { background: linear-gradient(135deg, #52c41a, #95de64); }
.stat-card.orange { background: linear-gradient(135deg, #fa8c16, #ffc53d); }
.stat-value {
  font-size: 24px;
  font-weight: 700;
}
.stat-label {
  font-size: 12px;
  opacity: 0.9;
  margin-top: 4px;
}
.section {
  background: #fff;
  border-radius: 10px;
  padding: 14px;
  margin-bottom: 12px;
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
}
.chart-area {
  height: 200px;
}
.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;
}
.recent-item:last-child {
  border-bottom: none;
}
.item-room {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}
.item-time {
  font-size: 12px;
  color: #1a73e8;
  margin-top: 2px;
}
.item-date {
  font-size: 12px;
  color: #999;
  text-align: right;
}
.item-user {
  font-size: 12px;
  color: #666;
  text-align: right;
  margin-top: 2px;
}
.empty-text {
  text-align: center;
  color: #ccc;
  padding: 32px 0;
}
</style>
