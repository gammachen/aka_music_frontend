import request from '../utils/request'

// 图片搜索相关接口
export interface SearchImageParams {
  query: string
  ratios: string[] // 图片比例数组，如 ["1:1", "16:9"]
}

export interface SearchImageResponse {
  code: number
  data: {
    results: {
      image_paths: string[]
      keyword: string
      ratio: string
      recommended_pixel: string
      layout: string        // 布局方式，如 'horizontal'
      animation_class: string  // 动画效果类名
      card_style: string    // 卡片样式，如 'square'
    }[]
  }
  message: string
  success: boolean
}

// 搜索图片
export const searchImages = (params: SearchImageParams) => {
  return request<SearchImageResponse>({
    url: '/api/image-search/search',
    method: 'POST',
    data: params,
    timeout: 300000  // 设置为30秒
  })
}

// 图片生成相关接口
export interface GenerateImageParams {
  prompt: string
  negative_prompt?: string
  width?: number
  height?: number
  num_images?: number
  style?: string
}

export interface GenerateImageResult {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  images: string[]
  created_at: string
  updated_at: string
}

export interface GenerateImageResponse {
  code: number
  data: GenerateImageResult
}

// 生成图片
export const generateImage = (params: GenerateImageParams) => {
  return request<GenerateImageResponse>({
    url: '/api/draw/generate',
    method: 'POST',
    data: params
  })
}

// 查询图片生成任务状态
export const getGenerateTaskStatus = (taskId: string) => {
  return request<GenerateImageResponse>({
    url: `/api/draw/tasks/${taskId}`,
    method: 'GET'
  })
}