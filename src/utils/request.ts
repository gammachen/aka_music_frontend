import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
// import {Message} from '@arco-design/web-vue';

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  },
  // 添加以下配置，在非HTTPS环境中也能处理某些需要HTTPS的功能
  withCredentials: true,  // 允许跨域请求携带凭证
  httpsAgent: {
    rejectUnauthorized: false // 忽略自签名证书的验证错误
  }
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    console.info('token:', token)
    
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    // 打印详细的请求信息
    console.log('Request Config:', {
      method: config.method,
      url: config.url,
      headers: config.headers,
      data: config.data,
      params: config.params
    })
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    // 打印详细的响应信息
    console.log('Response Data interceptior by requests.ts:', {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
      data: response.data
    })

    // 判断是否为mock请求
    const isMockRequest = response.config.url?.startsWith('/mockapi')
    
    // 对mock请求保持原始响应结构
    if (isMockRequest) {
      return response // 返回完整响应对象
    }

    const res = response.data
    return res
  },
  (error) => {
    // 打印详细的错误信息，包括CORS相关的错误
    console.error('Response error:', {
      message: error.message,
      code: error.code,
      config: error.config ? {
        method: error.config.method,
        url: error.config.url,
        headers: error.config.headers
      } : null,
      response: error.response ? {
        status: error.response.status,
        statusText: error.response.statusText,
        headers: error.response.headers,
        data: error.response.data
      } : null
    })

    // 处理CORS预检请求的错误
    if (error.code === 'ERR_NETWORK' && 
        error.config?.method?.toUpperCase() === 'OPTIONS') {
      console.warn('CORS预检请求失败，可能需要检查后端CORS配置')
      return Promise.reject(new Error('CORS预检请求失败，请检查后端配置'))
    }

    // 只有在收到服务器的响应时才进行状态码处理
    if (error.response) {
      const { status } = error.response
      // 处理401未授权的情况
      if (status === 401 && window.location.pathname !== '/login') {
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// 导出请求方法
const request = async <T = any>(config: AxiosRequestConfig): Promise<T> => {
  try {
    console.log('Request Interceptor Config:', config)
    const response = await service(config)
    return response as T
  } catch (error) {
    return Promise.reject(error)
  }
}

export default request

// 直接使用axios的异步请求的拦截器（针对的是editor的api） TODO 是否会对原来项目的请求有影响还待确认03.27（干）
import {useRoute, useRouter, RouteRecordRaw} from 'vue-router';

const router = useRouter();

// request interceptors
axios.interceptors.request.use(
  // @ts-ignore
  (config: AxiosRequestConfig) => {
      // 使用Token

      // const token = getToken();
      // if (token) {
      //     if (!config.headers) {
      //         config.headers = {};
      //     }
      //     config.headers.Authorization = `Bearer ${token}`;
      // }

      return config;
  },
  (error) => {
      console.log(error);
      return Promise.reject(error);
  }
);

export interface HttpResponse<T = unknown> {
  success: boolean; // 是否成功
  code: number; // 状态码
  msg: string; // 状态信息
  data: T; // 返回数据
  timestamp: string; // 时间戳
}

// response interceptors
axios.interceptors.response.use(
  // @ts-ignore
  (response: AxiosResponse<HttpResponse>) => {
      // 二进制数据则直接返回
      if (
          response.request.responseType === 'blob' ||
          response.request.responseType === 'arraybuffer'
      ) {
          return response;
      }

      // 操作成功则直接返回
      const res = response.data;
      if (res.success) {
          return res;
      }
      // 操作失败，弹出错误提示
      // Message.error({
      //     content: res.msg,
      //     duration: 3000,
      // });
      //
      if (res.code === 401) {
          // 重定向路由到登录页面
          router.replace('/login')
      }
      return Promise.reject(new Error(res.msg));
  },
  (error) => {
      console.error(`err: ${error}`);
      const res = error.response.data;
      // Message.error({
      //     content: res.msg || '网络错误',
      //     duration: 3000,
      // });
      return Promise.reject(error);
  }
);