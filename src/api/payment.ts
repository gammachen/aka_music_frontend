import request from '../utils/request'

// 创建充值订单
export const createRechargeOrder = (data: {
  amount: number,
  reference_id: number,
  reference_type: string,
  paymentMethod: string
}) => {
  return request({
    url: '/api/payment/create',
    method: 'POST',
    data
  })
}

// 获取用户余额
export const getUserBalance = () => {
  return request({
    url: '/api/user/balance',
    method: 'GET'
  })
}

// 获取支付订单状态
export const getPaymentStatus = (params?: any) => {
  return request({
    url: `/api/payment/return/alipay`,
    method: 'GET',
    params: params?.params
  })
}