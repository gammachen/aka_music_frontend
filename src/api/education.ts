
import request from '../utils/request'

export interface Track {
  id: string
  title: string
  name: string
  author_id: string
  cover_url: string | null
  description: string
  status: string
  type: string
  price_strategy: string
  publish_date: string
  created_at: string
  updated_at: string
}

interface ChapterImage {
  order: number
  url: string
}

interface ChapterPages {
  images: ChapterImage[]
}

export interface ChapterDetail {
  id: string
  title: string
  chapter_no: number
  content_id: string
  is_free: boolean
  price: number
  unlock_type: string
  pages: ChapterPages
  created_at: string
  updated_at: string
}

export interface GetContentResponse {
  data: Track[]
}

export interface Educations {
  name: string
  author: string | null
  is_completed: string
  country: string
  tags: string[]
  publish_date: string
  cover_url: string
}

export interface EducationGenre {
  category: string
  educations: Educations[]
}
export interface EducationGenreResponse {
  data: EducationGenre[]
}

export const getAllEducationGenre = () => {
  return request<EducationGenreResponse>({
    url: '/api/education/all_education_genre',
    method: 'GET'
  })
}

// 获取教育详情
export const getContentDetail = (params: { id: string}) => {
  return request<GetContentResponse>({
    url: '/api/education/contentDetail',
    method: 'GET',
    params
  })
}

// 获取推荐教育列表(TODO 这个改成getChapterList更好一点)
export const getContentList = (params: { id: string, page: number; pageSize: number }) => {
  return request<GetContentResponse>({
    url: '/api/education/chapterList',
    method: 'GET',
    params
  })
}

export interface GetChapterResponse {
  code: number
  data: ChapterDetail
}

// http://127.0.0.1:5000/api/education/chapterDetail?id=290018ac-7e2f-4d19-b8cf-fd0c1d4c992d
export const getChapterDetail = (params: { id: string}) => {
  return request<GetChapterResponse>({
    url: '/api/education/chapterDetail',
    method: 'GET',
    params
  })
}

export const getChapterDetailForLogin = (params: { id: string}) => {
  return request<GetChapterResponse>({
    url: '/api/education/chapterDetailForLogin',
    method: 'GET',
    params
  })
}

export const orderChapter = (params: { id: string}) => {
  return request<GetChapterResponse>({
    url: '/api/education/orderChapter',
    method: 'POST',
    data: { chapter_id: params.id }
  })
}

export interface GetTrendingTracksResponse {
  data: Track[]
}

// 获取推荐教育列表
export const getTrendingTracks = () => {
  return request<GetTrendingTracksResponse>({
    url: '/api/recommend/online_educations',
    method: 'GET'
  })
}

