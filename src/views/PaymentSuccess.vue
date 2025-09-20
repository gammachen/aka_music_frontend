<template>
  <div class="payment-success">
    <div class="result-container">
      <div class="icon-wrapper">
        <i class="el-icon-success success-icon"></i>
      </div>
      <h2 class="result-title">支付成功</h2>
      <div class="order-info" v-if="orderInfo">
        <p class="info-item">
          <span class="label">订单号：</span>
          <span class="value">{{ orderInfo.order_no }}</span>
        </p>
        <p class="info-item">
          <span class="label">支付宝订单号：</span>
          <span class="value">{{ orderInfo.out_trade_no }}</span>
        </p>
        <p class="info-item">
          <span class="label">支付金额：</span>
          <span class="value">¥{{ orderInfo.total_amount }}</span>
        </p>
      </div>
      <div class="action-buttons">
        <el-button type="primary" @click="goToRechargeRecord">查看充值记录</el-button>
        <el-button @click="goToHome">返回首页</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPaymentStatus } from '../api/payment'

const route = useRoute()
const router = useRouter()
const orderInfo = ref(null)

onMounted(async () => {
  //   charset=utf-8
  // out_trade_no=20250219161651424b1614
  // method=alipay.trade.page.pay.return
  // total_amount=100.00
  // sign=OIuGQLQM50ftCCo6gc%2FGnHOFnfHdbULMKmdUodAKhhim8LeUiVIyBRU1Uq3QUng2b9HbaZagxTuno%2Bv3DfAoz4K3LDMVlZTyQjb6ySlZYb6NqASDb89ruU9r%2FbuC151Ih9rQEbhsc%2Bw6xvgyiPEncYgIXwN8WiZmzVrx7J7p0XPXx%2BK1SiCV7Ml107aRgHb1%2BqDZ6FW%2B7f19hHFBreYcL7ATTnsZPLbQ8fI3znnFMBVWpj9HVUsKg84b0HTduW%2FH%2BffMOfvVJ0wbUXXedgPUWemuAI%2BmtE1WhzQYIy8YBaNWOCc2AmA0PMoJZykEtQIrLr2W6GmerGVmS5K2UaPWMA%3D%3D
  // trade_no=2025021922001441780506525151
  // auth_app_id=9021000144619580
  // version=1.0
  // app_id=9021000144619580
  // sign_type=RSA2
  // seller_id=2088721058496853
  // timestamp=2025-02-19+16%3A18%3A10

  console.log('[PaymentSuccess] 支付成功页面加载')
  const out_trade_no = route.query.out_trade_no
  const trade_no = route.query.trade_no
  const total_amount = route.query.total_amount

  console.log('[PaymentSuccess] 获取到订单号:', {out_trade_no, trade_no, total_amount})
  
  if (!out_trade_no) {
    console.warn('[PaymentSuccess] 订单号为空，无法查询订单状态')
    ElMessage.error('订单信息不完整')
    return
  }

  try {
    /* TODO 因为同步返回的数据并不是完全可靠，所以这里面先不调用查询接口，直接显示返回的链接中的相关信息
    // 将所有参数都传递过去
    const response = await getPaymentStatus({
      params: route.query
    })
    console.log('[PaymentSuccess] 订单状态查询响应:', response)
    
    if (response.code === 200) {
      orderInfo.value = response.data
      console.log('[PaymentSuccess] 订单状态查询成功:', orderInfo.value)
    } else {
      console.error('[PaymentSuccess] 订单状态查询失败:', response.message)
      ElMessage.error(response.message || '获取订单信息失败')
    }
    */

    orderInfo.value = {
      order_no: out_trade_no,
      out_trade_no: trade_no,
      total_amount: total_amount
    }
  } catch (error) {
    console.error('[PaymentSuccess] 订单状态查询异常:', error)
    ElMessage.error('获取订单信息失败')
  }
})

const goToRechargeRecord = () => {
  // 目前无法直接定位到我的充值记录，转到我的个人中心首页
  router.push('/profile')
}

const goToHome = () => {
  router.push('/')
}
</script>

<style scoped>
.payment-success {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 64px);
  background-color: #f5f7fa;
}

.result-container {
  background: #fff;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 100%;
  max-width: 480px;
}

.icon-wrapper {
  margin-bottom: 24px;
}

.success-icon {
  font-size: 72px;
  color: #67c23a;
}

.result-title {
  margin: 0 0 32px;
  color: #303133;
  font-weight: 500;
}

.order-info {
  margin-bottom: 32px;
  text-align: left;
}

.info-item {
  margin: 12px 0;
  font-size: 14px;
  color: #606266;
}

.label {
  display: inline-block;
  width: 80px;
  color: #909399;
}

.value {
  color: #303133;
}

.value.gold {
  color: #e6a23c;
  font-weight: 500;
}

.action-buttons {
  margin-top: 32px;
}

.action-buttons .el-button + .el-button {
  margin-left: 16px;
}
</style>