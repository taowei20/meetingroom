<template>
  <div class="mobile-layout">
    <div class="mobile-header">
      <span class="header-title">{{ currentTitle }}</span>
    </div>
    <div class="mobile-content">
      <router-view />
    </div>
    <div class="mobile-tabbar">
      <div
        v-for="tab in tabs"
        :key="tab.path"
        class="tab-item"
        :class="{ active: activeTab === tab.path }"
        @click="goTo(tab.path)"
      >
        <el-icon :size="22"><component :is="tab.icon" /></el-icon>
        <span class="tab-label">{{ tab.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Odometer, Calendar, List, User } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const tabs = [
  { path: '/m/dashboard', label: '首页', icon: Odometer },
  { path: '/m/booking', label: '预订', icon: Calendar },
  { path: '/m/my-bookings', label: '我的预订', icon: List },
  { path: '/m/profile', label: '我的', icon: User },
]

const activeTab = computed(() => {
  const path = route.path
  const match = tabs.find((t) => path.startsWith(t.path))
  return match ? match.path : '/m/dashboard'
})

const currentTitle = computed(() => {
  const match = tabs.find((t) => t.path === activeTab.value)
  return match ? match.label : '会议室预订'
})

function goTo(path) {
  router.push(path)
}
</script>

<style scoped>
.mobile-layout {
  display: flex;
  flex-direction: column;
  height: 100dvh;
  background: #f5f5f5;
  overflow: hidden;
  /* 避开 PWA 独立窗口/刘海屏顶部的状态栏 */
  padding-top: env(safe-area-inset-top, 0px);
  box-sizing: border-box;
}
.mobile-header {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a73e8;
  color: #fff;
  font-size: 17px;
  font-weight: 600;
  flex-shrink: 0;
  z-index: 10;
}
.mobile-content {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  padding: 12px;
  padding-bottom: calc(56px + env(safe-area-inset-bottom, 0px));
  box-sizing: border-box;
}
.mobile-tabbar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 56px;
  display: flex;
  background: #fff;
  border-top: 1px solid #e8e8e8;
  z-index: 10;
  padding-bottom: env(safe-area-inset-bottom, 0px);
  box-sizing: content-box;
  -webkit-transform: translate3d(0, 0, 0);
  transform: translate3d(0, 0, 0);
}
.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  cursor: pointer;
  color: #999;
  transition: color 0.2s;
  -webkit-tap-highlight-color: transparent;
}
.tab-item.active {
  color: #1a73e8;
}
.tab-label {
  font-size: 10px;
}
</style>
