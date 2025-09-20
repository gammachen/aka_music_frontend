import request from '../utils/request'

export interface FaceExtractResponse {
  image_path: string
  face_path: string
  face_location: [number, number, number, number] // [top, right, bottom, left]
  metadata: Record<string, any>
}

export interface SimilarFaceResult {
  id: number
  image_path: string
  face_path: string
  face_location: [number, number, number, number] // [top, right, bottom, left]
  metadata: Record<string, any>
  cosine_similarity: number
  cosine_distance: number
}

export interface SearchSimilarFacesResponse {
  results: SimilarFaceResult[]
}

/**
 * 从图片中提取人脸特征
 * @param path 图片路径
 * @returns 人脸特征信息
 */
export const extractFace = (path: string) => {
  return request<FaceExtractResponse>({
    url: '/api/face/extract',
    method: 'GET',
    params: { path }
  })
}

/**
 * 搜索相似人脸
 * @param path 图片路径
 * @returns 相似人脸列表
 */
export const searchSimilarFaces = (path: string) => {
  return request<SearchSimilarFacesResponse>({
    url: '/api/face/search',
    method: 'GET',
    params: { path }
  })
}