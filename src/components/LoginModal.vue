<template>
  <div v-if="visible" class="login-modal-overlay" @click="closeModal">
    <div class="login-modal" @click.stop>
      <div class="login-header">
        <h2>登录</h2>
        <button class="close-btn" @click="closeModal">×</button>
      </div>
      <div class="login-container">
        <div class="login-tabs">
          <button 
            v-for="tab in tabs" 
            :key="tab.key" 
            :class="['tab-btn', { active: activeKey === tab.key }]"
            @click="activeKey = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>
        
        <div v-if="activeKey === 'qrcode'" class="qrcode-container">
          <div class="qrcode-box">
            <div class="qrcode-placeholder"></div>
          </div>
          <p class="qrcode-tip">请使用AKA Music App扫码登录</p>
        </div>
        
        <form v-if="activeKey === 'account'" @submit.prevent="handleAccountLogin">
          <div class="form-group">
            <input 
              v-model="accountForm.username" 
              type="text" 
              placeholder="请输入账号" 
              required
            />
          </div>
          <div class="form-group">
            <input 
              v-model="accountForm.password" 
              type="password" 
              placeholder="请输入密码" 
              required
            />
          </div>
          <button type="submit" class="login-btn">登录</button>
        </form>
        
        <form v-if="activeKey === 'sms'" @submit.prevent="handleSmsLogin">
          <div class="form-group">
            <input 
              v-model="smsForm.phone" 
              type="tel" 
              placeholder="请输入手机号" 
              required
            />
          </div>
          <div class="form-group code-input">
            <input 
              v-model="smsForm.code" 
              type="text" 
              placeholder="请输入验证码" 
              required
            />
            <button 
              type="button" 
              :disabled="!!countdown"
              @click="handleSendCode"
            >
              {{ countdown ? `${countdown}s后重试` : '获取验证码' }}
            </button>
          </div>
          <button type="submit" class="login-btn">登录</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, defineEmits } from 'vue'
import { message } from 'ant-design-vue'
import { useUserStore } from '../store'
import axios from 'axios'

const emit = defineEmits(['update:visible'])
const userStore = useUserStore()

const visible = ref(false)
const activeKey = ref('qrcode')

const tabs = [
  { key: 'qrcode', label: '扫码登录' },
  { key: 'account', label: '账号登录' },
  { key: 'sms', label: '短信登录' }
]

const accountForm = ref({
  username: '',
  password: ''
})

const smsForm = ref({
  phone: '',
  code: ''
})

const countdown = ref(0)
let timer: number | null = null

const closeModal = () => {
  visible.value = false
}

const handleSendCode = async () => {
  if (!smsForm.value.phone) {
    message.error('请输入手机号')
    return
  }
  try {
    const response = await axios.post('/api/auth/v1/phone-code', {
      phone: smsForm.value.phone
    })
    if (response.data.code === 0) {
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
    } else {
      message.error(response.data.message || '发送验证码失败')
    }
  } catch (error) {
    message.error('发送验证码失败')
  }
}

const handleAccountLogin = async () => {
  try {
    const response = await axios.post('/api/auth/v1/login', {
      username: accountForm.value.username,
      password: accountForm.value.password
    })
    if (response.data.code === 0) {
      const { token, user } = response.data.data
      userStore.setToken(token)
      userStore.setUserInfo(user)
      visible.value = false
      message.success('登录成功')
    } else {
      message.error(response.data.message || '登录失败')
    }
  } catch (error) {
    message.error('登录失败')
  }
}

const handleSmsLogin = async () => {
  try {
    const response = await axios.post('/api/auth/v1/login/sms', {
      phone: smsForm.value.phone,
      code: smsForm.value.code
    })
    if (response.data.code === 0) {
      const { token, user } = response.data.data
      userStore.setToken(token)
      userStore.setUserInfo(user)
      visible.value = false
      message.success('登录成功')
    } else {
      message.error(response.data.message || '登录失败')
    }
  } catch (error) {
    message.error('登录失败')
  }
}

// 暴露方法给父组件
const show = () => {
  visible.value = true
}

const hide = () => {
  visible.value = false
}

defineExpose({
  show,
  hide
})
</script>

<style scoped>
.login-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.login-modal {
  background: white;
  border-radius: 8px;
  width: 400px;
  max-width: 90vw;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.login-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.login-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #666;
}

.login-container {
  padding: 24px;
}

.login-tabs {
  display: flex;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 24px;
}

.tab-btn {
  flex: 1;
  background: none;
  border: none;
  padding: 12px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  border-bottom: 2px solid transparent;
}

.tab-btn.active {
  color: #1890ff;
  border-bottom-color: #1890ff;
}

.tab-btn:hover {
  color: #1890ff;
}

.qrcode-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.qrcode-box {
  width: 200px;
  height: 200px;
  border: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.qrcode-placeholder {
  width: 180px;
  height: 180px;
  background-color: #f5f5f5;
}

.qrcode-tip {
  color: #666;
  margin: 0;
  font-size: 14px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #1890ff;
}

.code-input {
  display: flex;
  gap: 8px;
}

.code-input input {
  flex: 1;
}

.code-input button {
  width: 120px;
  padding: 12px;
  border: 1px solid #d9d9d9;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.code-input button:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
  color: #999;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

.login-btn:hover {
  background: #40a9ff;
}
</style>