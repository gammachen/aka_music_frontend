import request from '../utils/request'

interface PaymentOrder {
  id: number
  userId: number
  amount: number
  status: string
  createdAt: string
  updatedAt: string
}

interface RechargeResponse {
  items: PaymentOrder[]
  total: number
  totalBalance: number
}

export const getRechargeRecords = (params: { page: number; pageSize: number }) => {
  return request({
    url: '/api/payment/records',
    method: 'GET',
    params
  })
}