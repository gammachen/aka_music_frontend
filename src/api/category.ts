import request from '../utils/request'

export interface Track {
  id: number
  title: string
  artist: string
  coverUrl: string
  duration: number
  playCount: number
}

export interface Category {
  id: number
  name: string
  background_style?: string
  desc_image?: string
  prefix?: string
  children?: Category[]
}

export interface GetCategoryTreeResponse {
  code: number
  data: Category[]
}

// 获取分类树
export const getCategoryTree = () => {
  return request<GetCategoryTreeResponse>({
    url: '/api/category/tree',
    method: 'GET'
  })
}