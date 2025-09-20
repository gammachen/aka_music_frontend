<template>
  <Layout class="layout">
    <!-- <NavBar /> -->
    <Layout.Content class="main-content">
      <div class="main-layout">
        <Layout class="inner-layout" hasSider>
          <Layout.Sider width="240" class="side-menu">
            <Menu
              mode="inline"
              v-model:selectedKeys="menuSelectedKeys"
              style="height: 100%"
            >
              <Menu.Item key="profile">
                <template #icon><UserOutlined /></template>
                个人信息
              </Menu.Item>
              <Menu.Item key="topics">
                <template #icon><FileTextOutlined /></template>
                我的主题
              </Menu.Item>
              <Menu.Item key="messages">
                <template #icon><MessageOutlined /></template>
                我的消息
              </Menu.Item>
              <Menu.Item key="points">
                <template #icon><TrophyOutlined /></template>
                我的积分
              </Menu.Item>
              <Menu.Item key="favorites">
                <template #icon><StarOutlined /></template>
                我的收藏
              </Menu.Item>
              <Menu.Item key="my_recharge">
                <template #icon><WalletOutlined /></template>
                我的充值
              </Menu.Item>
              <Menu.Item key="recharge">
                <template #icon><WalletOutlined /></template>
                充值
              </Menu.Item>
              <Menu.Item key="statistics">
                <template #icon><BarChartOutlined /></template>
                数据统计
              </Menu.Item>
            </Menu>
          </Layout.Sider>
          <Layout.Content class="inner-content">
            <component :is="currentComponent" v-if="currentComponent" />
            <a-card :bordered="false" class="profile-card" v-else>
              <a-descriptions title="个人资料" bordered>
                <a-descriptions-item label="用户名">{{ userStore.userInfo?.username || '-' }}</a-descriptions-item>
                <a-descriptions-item label="注册时间">{{ userStore.userInfo?.createTime || '-' }}</a-descriptions-item>
                <a-descriptions-item label="上次登录">{{ userStore.userInfo?.lastLoginTime || '-' }}</a-descriptions-item>
              </a-descriptions>
            </a-card>
          </Layout.Content>
        </Layout>
      </div>
    </Layout.Content>
  </Layout>
</template>

<script setup lang="ts">
import { ref, computed, defineAsyncComponent } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store'
import { message } from 'ant-design-vue'
import { Layout, Menu, Avatar } from 'ant-design-vue'
import {
  UserOutlined,
  FileTextOutlined,
  MessageOutlined,
  TrophyOutlined,
  StarOutlined,
  WalletOutlined,
  BarChartOutlined
} from '@ant-design/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const selectedKeys = ref(['profile'])
const menuSelectedKeys = ref(['profile'])

const currentComponent = computed(() => {
  switch (menuSelectedKeys.value[0]) {
    case 'topics':
      return defineAsyncComponent(() => import('./profile/MyTopics.vue'))
    case 'messages':
      return defineAsyncComponent(() => import('./profile/MyMessages.vue'))
    case 'points':
      return defineAsyncComponent(() => import('./profile/MyPoints.vue'))
    case 'favorites':
      return defineAsyncComponent(() => import('./profile/MyFavorites.vue'))
    case 'my_recharge':
      return defineAsyncComponent(() => import('./profile/MyRecharge.vue'))
    case 'recharge':
      return defineAsyncComponent(() => import('./profile/Recharge.vue'))
    case 'statistics':
      return defineAsyncComponent(() => import('./profile/MyStatistics.vue'))
    default:
      return null
  }
})

const handleLogout = () => {
  userStore.logout()
  message.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: #fff;
  padding: 0;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}

.menu {
  line-height: 64px;
  border: none;
}

.user-area {
  margin-left: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.logout-btn {
  padding: 4px 0;
  color: #999;
}

.logout-btn:hover {
  color: #1890ff;
}

.main-content {
  padding-top: 24px;
  background: #f5f5f5;
}

.main-layout {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 16px;
}

.inner-layout {
  background: #fff;
  border-radius: 2px;
}

.side-menu {
  background: #fff;
  border-right: 1px solid #f0f0f0;
}

.inner-content {
  padding: 24px;
  background: #fff;
}

.profile-card {
  background: #fff;
}
</style>