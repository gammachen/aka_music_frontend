import request from '../utils/request'

export interface Track {
  id: number
  title: string
  artist: string
  coverUrl: string
  duration: number
  playCount: number
}

export interface GetMusicResponse {
  data: Track[]
}

// 获取推荐音乐列表
export const getMusicList = (params: { category_id: string, page: number; pageSize: number }) => {
  return request<GetMusicResponse>({
    url: '/api/music/mulist',
    method: 'GET',
    params
  })
}

export interface GetTrendingTracksResponse {
  data: Track[]
}

// 获取推荐音乐列表
export const getTrendingTracks = () => {
  return request<GetTrendingTracksResponse>({
    url: '/api/recommend/online_musics',
    method: 'GET'
  })
}