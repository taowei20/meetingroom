<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '180px'" class="layout-aside">
      <div class="logo-area">
        <span v-if="!isCollapse">紫软会议室预订系统</span>
        <span v-else>会</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        background-color="#001529"
        text-color="#ffffffa6"
        active-text-color="#1890ff"
        router
        :collapse-transition="false"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>首页</template>
        </el-menu-item>
        <el-menu-item v-if="userStore.isAdmin" index="/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
        <el-menu-item v-if="userStore.isAdmin" index="/rooms">
          <el-icon><OfficeBuilding /></el-icon>
          <template #title>会议室管理</template>
        </el-menu-item>
        <el-menu-item index="/booking">
          <el-icon><Calendar /></el-icon>
          <template #title>会议室预订</template>
        </el-menu-item>
        <el-menu-item index="/my-bookings">
          <el-icon><List /></el-icon>
          <template #title>我的预订</template>
        </el-menu-item>
        <el-menu-item v-if="userStore.isAdmin" index="/admin-bookings">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>预订管理</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <span class="page-title">{{ currentTitle }}</span>
        </div>
        <div class="header-right">
          <el-dropdown trigger="click">
            <span class="user-info">
              <el-icon><UserFilled /></el-icon>
              {{ userStore.userName }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="goTo('/user-info')">修改信息</el-dropdown-item>
                <el-dropdown-item @click="goTo('/change-password')">修改密码</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { ElMessageBox } from 'element-plus'
import {
  Odometer, User, OfficeBuilding, Calendar, List, DataAnalysis,
  Fold, Expand, UserFilled, ArrowDown,
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const isCollapse = ref(false)

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta.title || '首页')

function goTo(path) {
  router.push(path)
}

function handleLogout() {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    userStore.logout()
    router.push('/login')
  })
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}
.layout-aside {
  background: #001529;
  transition: width 0.3s;
  overflow: hidden;
}
.logo-area {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  border-bottom: 1px solid #ffffff1a;
}
.el-menu {
  border-right: none;
}
.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  padding: 0 20px;
  z-index: 1;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #333;
}
.page-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}
.header-right {
  display: flex;
  align-items: center;
}
.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  gap: 4px;
}
.layout-main {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
@media (max-width: 768px) {
  .layout-aside {
    position: fixed;
    z-index: 100;
    height: 100vh;
  }
  .layout-aside:not(.el-menu--collapse) {
    width: 220px !important;
  }
  .layout-aside.el-menu--collapse {
    width: 64px !important;
  }
  .layout-main {
    padding: 12px;
  }
  .page-title {
    font-size: 14px;
  }
  .user-info {
    font-size: 12px;
  }
  .logo-area {
    font-size: 14px;
  }
}
</style>
