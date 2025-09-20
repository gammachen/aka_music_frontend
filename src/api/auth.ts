import request from '../utils/request'

export interface RegisterParams {
  phone?: string
  email?: string
  code: string
  password: string
}

export interface PhoneLoginParams {
  phone: string
  code: string
}

export interface EmailLoginParams {
  email: string
  password: string
}

export interface AuthResponse {
  token: string
  user: {
    id: number
    username: string
    phone?: string
    email?: string
  }
}

// 获取手机验证码
export const getPhoneCode = (phone: string) => {
  return request<AuthResponse>({
    url: '/api/auth/v1/phone-code',
    method: 'POST',
    data: { phone }
  })
}

// 获取邮箱验证码
export const getEmailCode = (email: string) => {
  return request<AuthResponse>({
    url: '/api/auth/v1/email-code',
    method: 'POST',
    data: { email }
  })
}

// 手机号注册
export const registerByPhone = (params: RegisterParams) => {
  return request<AuthResponse>({
    url: '/api/auth/v1/register/phone',
    method: 'POST',
    data: params
  })
}

// 邮箱注册
export const registerByEmail = (params: RegisterParams) => {
  return request<AuthResponse>({
    url: '/api/auth/v1/register/email',
    method: 'POST',
    data: params
  })
}

// 手机验证码登录
export const loginByPhone = (params: PhoneLoginParams) => {
  return request<AuthResponse>({
    url: '/api/auth/v1/login/phone',
    method: 'POST',
    data: params
  })
}

// 邮箱密码登录
export const loginByEmail = (params: EmailLoginParams) => {
  return request<AuthResponse>({
    url: '/api/auth/v1/login/email',
    method: 'POST',
    data: params
  })
}