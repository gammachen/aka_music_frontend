<template>
  <div class="register-container">
    <div class="register-left">
      <img src="../assets/login-banner-2.jpg" alt="背景图片" />
    </div>
    <div class="register-right">
      <div class="register-form">
        <h2 class="login-title">注册账号</h2>
        <a-tabs v-model:activeKey="activeKey" button-style="solid">
          <a-tab-pane key="phone" tab="手机号注册">
            <a-form :model="phoneForm" @finish="onPhoneFinish">
              <a-form-item
                name="phone"
                :rules="[{ required: true, message: '请输入手机号' }]"
              >
                <a-input v-model:value="phoneForm.phone" placeholder="请输入手机号" size="large">
                  <template #prefix>
                    <phone-outlined />
                  </template>
                </a-input>
              </a-form-item>
              <a-form-item
                name="code"
                :rules="[{ required: true, message: '请输入验证码' }]"
              >
                <div class="code-input">
                  <a-input v-model:value="phoneForm.code" placeholder="请输入验证码" size="large">
                    <template #prefix>
                      <safety-outlined />
                    </template>
                  </a-input>
                  <a-button
                    :disabled="isGettingCode"
                    @click="fetchPhoneCode"
                  >
                    {{ codeButtonText }}
                  </a-button>
                </div>
              </a-form-item>
              <a-form-item
                name="password"
                :rules="[{ required: true, message: '请输入密码' }]"
              >
                <a-input-password v-model:value="phoneForm.password" placeholder="请输入密码" size="large">
                  <template #prefix>
                    <lock-outlined />
                  </template>
                </a-input-password>
              </a-form-item>
              <a-form-item
                name="confirmPassword"
                :rules="[
                  { required: true, message: '请确认密码' },
                  { validator: validateConfirmPassword }
                ]"
              >
                <a-input-password v-model:value="phoneForm.confirmPassword" placeholder="请确认密码" size="large">
                  <template #prefix>
                    <lock-outlined />
                  </template>
                </a-input-password>
              </a-form-item>
              <a-form-item>
                <a-button type="primary" html-type="submit" block size="large">注册</a-button>
              </a-form-item>
            </a-form>
          </a-tab-pane>
          <a-tab-pane key="email" tab="邮箱注册">
            <a-form :model="emailForm" @finish="onEmailFinish">
              <a-form-item
                name="email"
                :rules="[{ required: true, message: '请输入邮箱' }]"
              >
                <a-input v-model:value="emailForm.email" placeholder="请输入邮箱" size="large">
                  <template #prefix>
                    <mail-outlined />
                  </template>
                </a-input>
              </a-form-item>
              <a-form-item
                name="code"
                :rules="[{ required: true, message: '请输入验证码' }]"
              >
                <div class="code-input">
                  <a-input v-model:value="emailForm.code" placeholder="请输入验证码" size="large">
                    <template #prefix>
                      <safety-outlined />
                    </template>
                  </a-input>
                  <a-button
                    :disabled="isGettingCode"
                    @click="fetchEmailCode"
                  >
                    {{ codeButtonText }}
                  </a-button>
                </div>
              </a-form-item>
              <a-form-item
                name="password"
                :rules="[{ required: true, message: '请输入密码' }]"
              >
                <a-input-password v-model:value="emailForm.password" placeholder="请输入密码" size="large">
                  <template #prefix>
                    <lock-outlined />
                  </template>
                </a-input-password>
              </a-form-item>
              <a-form-item
                name="confirmPassword"
                :rules="[
                  { required: true, message: '请确认密码' },
                  { validator: validateConfirmPassword }
                ]"
              >
                <a-input-password v-model:value="emailForm.confirmPassword" placeholder="请确认密码" size="large">
                  <template #prefix>
                    <lock-outlined />
                  </template>
                </a-input-password>
              </a-form-item>
              <a-form-item>
                <a-button type="primary" html-type="submit" block size="large">注册</a-button>
              </a-form-item>
            </a-form>
          </a-tab-pane>
        </a-tabs>
        <div class="form-footer">
          <router-link to="/login">返回登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onUnmounted } from 'vue'
import { PhoneOutlined, LockOutlined, SafetyOutlined, MailOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { useRouter } from 'vue-router'
import { getPhoneCode, getEmailCode, registerByPhone, registerByEmail } from '../api/auth'

const router = useRouter()
const activeKey = ref('phone')

// 手机号注册表单数据
const phoneForm = ref({
  phone: '',
  code: '',
  password: '',
  confirmPassword: ''
})

// 邮箱注册表单数据
const emailForm = ref({
  email: '',
  code: '',
  password: '',
  confirmPassword: ''
})

// 验证码按钮状态
const isGettingCode = ref(false)
const countdown = ref(60)
const codeButtonText = ref('获取验证码')
let timer: NodeJS.Timeout | null = null

// 确认密码验证
const validateConfirmPassword = async (_rule: any, value: string) => {
  const form = activeKey.value === 'phone' ? phoneForm.value : emailForm.value
  if (value && value !== form.password) {
    return Promise.reject('两次输入的密码不一致')
  }
  return Promise.resolve()
}

// 获取手机验证码
const fetchPhoneCode = async () => {
  if (!phoneForm.value.phone) {
    message.error('请先输入手机号')
    return
  }
  if (isGettingCode.value) {
    return
  }
  try {
    isGettingCode.value = true
    await getPhoneCode(phoneForm.value.phone)
    message.success('验证码已发送')
    startCountdown()
  } catch (error: any) {
    message.error(error.response?.data?.message || '获取验证码失败')
    isGettingCode.value = false
  }
}

// 获取邮箱验证码
const fetchEmailCode = async () => {
  if (!emailForm.value.email) {
    message.error('请先输入邮箱')
    return
  }
  if (isGettingCode.value) {
    return
  }
  try {
    isGettingCode.value = true
    await getEmailCode(emailForm.value.email)
    message.success('验证码已发送')
    startCountdown()
  } catch (error: any) {
    message.error(error.response?.data?.message || '获取验证码失败')
    isGettingCode.value = false
  }
}

// 倒计时
const startCountdown = () => {
  if (timer) {
    clearInterval(timer)
  }
  countdown.value = 60
  timer = setInterval(() => {
    countdown.value--
    codeButtonText.value = `${countdown.value}秒后重试`
    if (countdown.value <= 0) {
      if (timer) {
        clearInterval(timer)
        timer = null
      }
      isGettingCode.value = false
      codeButtonText.value = '获取验证码'
    }
  }, 1000)
}

// 手机号注册提交
const onPhoneFinish = async (values: any) => {
  try {
    const { confirmPassword, ...params } = values
    const res = await registerByPhone(params)
    message.success('注册成功')
    router.push('/login')
  } catch (error: any) {
    message.error(error.response?.data?.message || '注册失败')
  }
}

// 邮箱注册提交
const onEmailFinish = async (values: any) => {
  try {
    const { confirmPassword, ...params } = values
    const res = await registerByEmail(params)
    message.success('注册成功')
    router.push('/login')
  } catch (error: any) {
    message.error(error.response?.data?.message || '注册失败')
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  height: 100vh;
}

.register-left {
  flex: 1;
  max-width: 50%;
  overflow: hidden;
}

.register-left img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.register-right {
  flex: 1;
  max-width: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.register-form {
  width: 100%;
  max-width: 400px;
}

.register-form h2 {
  text-align: center;
  margin-bottom: 24px;
  font-size: 28px;
  font-weight: 500;
}

.register-form .ant-tabs {
  margin-bottom: 24px;
}

.register-form .ant-form-item {
  margin-bottom: 24px;
}

.register-form .ant-input-affix-wrapper {
  height: 40px;
}

.register-form .ant-btn {
  height: 40px;
}

.code-input {
  display: flex;
  gap: 8px;
}

.code-input .ant-input-affix-wrapper {
  flex: 1;
}

.form-footer {
  text-align: center;
  margin-top: 16px;
}

@media (max-width: 768px) {
  .register-container {
    flex-direction: column;
  }

  .register-left,
  .register-right {
    max-width: 100%;
  }

  .register-left {
    height: 200px;
  }

  .register-right {
    padding: 20px;
  }
}
</style>