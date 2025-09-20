import request from '../utils/request'

export interface TopicData {
  title: string
  category: string
  content: string
  hidden_content?: string
}

export interface TopicResponse {
  id: number
  title: string
  content: string
  category: string
  views: number
  likes: number
  favorites: number
  comments_count: number
  created_at: string
}

// 创建主题
export const createTopic = (data: TopicData) => {
  return request({
    url: '/api/topics/create',
    method: 'post',
    data
  })
}

// 获取主题列表
export const getTopics = (params: {
  page: number
  per_page: number
  category?: string
}) => {
  return request({
    url: '/api/topics',
    method: 'get',
    params
  })
}

// 获取主题详情
export const getTopic = (id: number) => {
  return request({
    url: `/api/topics/${id}`,
    method: 'get'
  })
}

// 更新主题
export const updateTopic = (id: number, data: TopicData) => {
  return request({
    url: `/api/topics/${id}`,
    method: 'put',
    data
  })
}

// 删除主题
export const deleteTopic = (id: number) => {
  return request({
    url: `/api/topics/${id}`,
    method: 'delete'
  })
}