import request from '../utils/request'

export interface ContentNode {
  id: string
  name: string
  type: string
  children?: ContentNode[]
}

// 获取内容分类树
export const getContentTree = () => {
  return request<{ data: ContentNode[] }>({ 
    url: '/api/backend/content/tree',
    method: 'GET'
  })
}

// 添加内容节点
export interface AddContentNodeParams {
  name: string
  type: string
  parentId?: string
}

export const addContentNode = (data: AddContentNodeParams) => {
  return request<{ data: ContentNode }>({ 
    url: '/api/backend/content/node',
    method: 'POST',
    data
  })
}

// 上传章节文件
export const uploadChapters = (data: FormData) => {
  return request<{ data: { files: { filename: string, path: string }[] } }>({ 
    url: '/api/backend/content/upload_chapters',
    method: 'POST',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const uploadAdvideo = (data: FormData) => {
  return request<{ data: { files: { filename: string, path: string }[] } }>({ 
    url: '/api/backend/rtmp/upload_video',
    method: 'POST',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}