import request from '../utils/request'

export interface RewardParams {
  target_type: 'topic' | 'comment'
  target_id: number
  amount: number
  message?: string
}

export interface RewardConfigResponse {
  daily_free_count: number
  remaining_free_count: number
  min_amount: number
  max_amount: number
  suggested_amounts: number[]
}

export interface RewardResponse {
  success: boolean
  reward_id: number
  remaining_free_count: number
  cost_coins: number
}

// 获取打赏配置 TODO: 这个接口还没写
export const getRewardConfig = () => {
  return request<RewardConfigResponse>({
    url: '/api/rewards/config',
    method: 'get'
  })
}

// 创建打赏(就创建这个功能的先 0219)
export const createReward = (data: RewardParams) => {
  return request<RewardResponse>({
    url: '/api/rewards/create',
    method: 'post',
    data
  })
}

// 获取主题的打赏记录 TODO: 这个接口还没写
export const getTopicRewards = (topicId: number) => {
  return request({
    url: `/api/rewards/topic/${topicId}`,
    method: 'get'
  })
}

// 获取用户的打赏记录 TODO: 这个接口还没写
export const getUserRewards = (userId: number) => {
  return request({
    url: `/api/rewards/user/${userId}`,
    method: 'get'
  })
}