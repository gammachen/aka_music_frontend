
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

export interface Comics {
  name: string
  author: string | null
  is_completed: string
  country: string
  tags: string[]
  publish_date: string
  cover_url: string
}

export interface ComicGenre {
  category: string
  comics: Comics[]
}
export interface ComicGenreResponse {
  data: ComicGenre[]
}

export const getAllComicGenre = () => {
  return request<ComicGenreResponse>({
    url: '/api/comic/all_comic_genre',
    method: 'GET'
  })
}

// 获取音乐详情
export const getContentDetail = (params: { id: string}) => {
  return request<GetContentResponse>({
    url: '/api/comic/contentDetail',
    method: 'GET',
    params
  })
}

// 获取推荐音乐列表(TODO 这个改成getChapterList更好一点)
export const getContentList = (params: { id: string, page: number; pageSize: number }) => {
  return request<GetContentResponse>({
    url: '/api/comic/chapterList',
    method: 'GET',
    params
  })
}

export interface GetChapterResponse {
  code: number
  data: ChapterDetail
}

// http://127.0.0.1:5000/api/comic/chapterDetail?id=290018ac-7e2f-4d19-b8cf-fd0c1d4c992d
export const getChapterDetail = (params: { id: string}) => {
  return request<GetChapterResponse>({
    url: '/api/comic/chapterDetail',
    method: 'GET',
    params
  })
}

export const getChapterDetailForLogin = (params: { id: string}) => {
  return request<GetChapterResponse>({
    url: '/api/comic/chapterDetailForLogin',
    method: 'GET',
    params
  })
}

export const orderChapter = (params: { id: string}) => {
  return request<GetChapterResponse>({
    url: '/api/comic/orderChapter',
    method: 'POST',
    data: { chapter_id: params.id }
  })
}

export interface GetTrendingTracksResponse {
  data: Track[]
}

// 获取推荐音乐列表
export const getTrendingTracks = () => {
  return request<GetTrendingTracksResponse>({
    url: '/api/recommend/online_comics',
    method: 'GET'
  })
}

