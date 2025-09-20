import request from '../utils/request'

export interface BeautyImage {
  directory: string
  id: string
  name: string
  type: string
  url: string
  views: number
}

export interface BeautyListResponse {
  current_directory: string
  list: BeautyImage[]
  pagination: {
    page: number
    page_size: number
    total: number
    total_pages: number
  }
}

export const getBeautyList = (refer_id: string, page: number = 1, page_size: number = 10) => {
  return request<BeautyListResponse>({
    url: '/api/beauty/beaulist',
    method: 'GET',
    params: {
      refer_id,
      page,
      page_size
    }
  })
}