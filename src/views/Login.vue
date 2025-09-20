<template>
  <div class="login-page">
    <!-- 左侧图片区域 -->
    <div class="login-banner">
      <img src="../assets/login-banner-2.jpg" alt="登录页面背景" />
    </div>
    
    <!-- 右侧登录区域 -->
    <div class="login-content">
      <div class="login-box">
        <h2 class="login-title">欢迎使用 AKA Music</h2>
        
        <!-- 登录方式切换 -->
        <div class="login-type-switch">
          <a-radio-group v-model:value="loginType" button-style="solid">
            <a-radio-button value="phone">手机号登录</a-radio-button>
            <a-radio-button value="email">邮箱登录</a-radio-button>
          </a-radio-group>
          <router-link to="/register" class="register-link">立即注册</router-link>
        </div>

        <!-- 手机号登录表单 -->
        <a-form v-if="loginType === 'phone'" :model="phoneForm" @finish="handlePhoneLogin" class="login-form">
          <a-form-item name="phone" :rules="[{ required: true, message: '请输入手机号' }]">
            <a-input v-model:value="phoneForm.phone" placeholder="请输入手机号" size="large">
              <template #prefix>
                <MobileOutlined />
              </template>
            </a-input>
          </a-form-item>
          <a-form-item name="code" :rules="[{ required: true, message: '请输入验证码' }]">
            <div class="code-input-group">
              <a-input v-model:value="phoneForm.code" placeholder="请输入验证码" size="large" />
              <a-button :disabled="!!countdown" @click="handleSendCode" size="large">
                {{ countdown ? `${countdown}s后重试` : '获取验证码' }}
              </a-button>
            </div>
          </a-form-item>
          <a-form-item>
            <a-button type="primary" html-type="submit" block size="large">登录</a-button>
          </a-form-item>
        </a-form>

        <!-- 邮箱登录表单 -->
        <a-form v-else :model="emailForm" @finish="handleEmailLogin" class="login-form">
          <a-form-item name="email" :rules="[{ required: true, message: '请输入邮箱' }]">
            <a-input v-model:value="emailForm.email" placeholder="请输入邮箱" size="large">
              <template #prefix>
                <MailOutlined />
              </template>
            </a-input>
          </a-form-item>
          <a-form-item name="password" :rules="[{ required: true, message: '请输入密码' }]">
            <a-input-password v-model:value="emailForm.password" placeholder="请输入密码" size="large">
              <template #prefix>
                <LockOutlined />
              </template>
            </a-input-password>
          </a-form-item>
          <a-form-item>
            <a-button type="primary" html-type="submit" block size="large">登录</a-button>
          </a-form-item>
        </a-form>

        <!-- 第三方登录 -->
        <div class="other-login">
          <div class="divider">
            <span>其他登录方式</span>
          </div>
          <div class="other-login-buttons">
            <a-button shape="circle" class="social-button">
              <template #icon><WechatOutlined /></template>
            </a-button>
            <a-button shape="circle" class="social-button">
              <template #icon><QqOutlined /></template>
            </a-button>
            <a-button shape="circle" class="social-button">
              <template #icon><WeiboOutlined /></template>
            </a-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { message } from 'ant-design-vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store'
import { getPhoneCode, loginByPhone, loginByEmail } from '../api/auth'
import {
  MobileOutlined,
  MailOutlined,
  LockOutlined,
  WechatOutlined,
  QqOutlined,
  WeiboOutlined
} from '@ant-design/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const loginType = ref('phone')

// 手机号登录表单
const phoneForm = ref({
  phone: '',
  code: ''
})

// 邮箱登录表单
const emailForm = ref({
  email: '',
  password: ''
})

// 倒计时
const countdown = ref(0)
let timer: number | null = null

// 发送验证码
const handleSendCode = async () => {
  if (!phoneForm.value.phone) {
    message.error('请输入手机号')
    return
  }
  try {
    await getPhoneCode(phoneForm.value.phone)
    message.success('验证码发送成功')
    countdown.value = 60
    timer = window.setInterval(() => {
      if (countdown.value > 0) {
        countdown.value--
      } else {
        if (timer) {
          clearInterval(timer)
          timer = null
        }
      }
    }, 1000)
  } catch (error: any) {
    message.error(error.response?.data?.message || '发送验证码失败')
  }
}

// 手机号登录
const handlePhoneLogin = async () => {
  try {
    const res = await loginByPhone(phoneForm.value)
    userStore.setToken(res.token)
    userStore.setUserInfo(res.user)
    message.success('登录成功')
    router.push('/')
  } catch (error: any) {
    message.error(error.response?.data?.message || '登录失败')
  }
}

// 邮箱登录
const handleEmailLogin = async () => {
  try {
    const res = await loginByEmail(emailForm.value)
    console.log('登录响应:', res)
    if (res.code === 0) {
      userStore.setToken(res.data.token)
      userStore.setUserInfo(res.data.user)
      message.success(res.message || '登录成功')
      router.push('/')
    } else {
      message.error(res.message || '登录失败')
    }
  } catch (error: any) {
    console.error('登录错误:', error)
    message.error(error.response?.data?.message || '登录失败')
  }
}

// 组件销毁时清除定时器
onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})
</script>

<style scoped>
.login-page {
  display: flex;
  height: 100vh;
}

.login-banner {
  flex: 1;
  max-width: 50%;
  overflow: hidden;
}

.login-banner img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.login-content {
  flex: 1;
  max-width: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.login-box {
  width: 100%;
  max-width: 400px;
}

.login-title {
  text-align: center;
  margin-bottom: 24px;
  font-size: 28px;
  font-weight: 500;
}

.login-type-switch {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.login-form .ant-form-item {
  margin-bottom: 24px;
}

.code-input-group {
  display: flex;
  gap: 8px;
}

.code-input-group .ant-input {
  flex: 1;
}

.other-login {
  margin-top: 24px;
}

.divider {
  display: flex;
  align-items: center;
  margin: 16px 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #e8e8e8;
}

.divider span {
  padding: 0 16px;
  color: #999;
}

.other-login-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 16px;
}

.social-button {
  color: #666;
}

@media (max-width: 768px) {
  .login-page {
    flex-direction: column;
  }

  .login-banner,
  .login-content {
    max-width: 100%;
  }

  .login-banner {
    height: 200px;
  }

  .login-content {
    padding: 20px;
  }
}
</style>