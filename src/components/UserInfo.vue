
<script setup lang="ts">
import { useUserStore } from '../store'
import { useRouter } from 'vue-router'

// 明确从ant-design-vue导入组件和API
// import { message, Dropdown, Menu, MenuItem, MenuDivider, Avatar, Button } from 'ant-design-vue'
import { 
  message, 
  Dropdown as ADropdown,
  Menu as AMenu,
  MenuItem as AMenuItem,
  MenuDivider as AMenuDivider,
  Avatar as AAvatar,
  Button as AButton 
} from 'ant-design-vue'
// 注意：本组件使用的所有a-前缀组件(a-dropdown, a-menu, a-button等)均来自ant-design-vue
// 不要混淆为@arco-design/web-vue的组件

const userStore = useUserStore()
const router = useRouter()

const handleLogout = async () => {
  try {
    userStore.clearUserInfo()
    message.success('退出登录成功')
    router.push('/login')
  } catch (error) {
    message.error('退出登录失败')
  }
}

const showLoginModal = () => {
  router.push('/login')
}
</script>


<template>
  <!-- 使用Ant Design Vue组件 -->
  <div class="user-info">
    <!-- a-dropdown是Ant Design Vue组件，不是Arco Design Vue组件 -->
    <a-dropdown v-if="userStore.userInfo">
      <a class="user-dropdown-link" @click.prevent>
        <a-avatar :size="32" class="user-avatar">
          {{ userStore.userInfo?.nickname?.[0] || userStore.userInfo?.username?.[0] || 'U' }}
        </a-avatar>
        <span class="username">{{ userStore.userInfo?.nickname || userStore.userInfo?.username }}</span>
      </a>
      <template #overlay>
        <a-menu>
          <a-menu-item key="profile">
            <router-link to="/profile">个人中心</router-link>
          </a-menu-item>
          <a-menu-item key="settings">
            <router-link to="/settings">设置</router-link>
          </a-menu-item>
          <a-menu-divider />
          <a-menu-item key="logout" @click="handleLogout">
            退出登录
          </a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
    <a-button v-else type="link" @click="showLoginModal">登录</a-button> 
   
  </div>
</template>


<style scoped>
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-dropdown-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: inherit;
  text-decoration: none;
}

.user-avatar {
  background-color: #1890ff;
  color: #fff;
}

.username {
  font-size: 14px;
}
</style>