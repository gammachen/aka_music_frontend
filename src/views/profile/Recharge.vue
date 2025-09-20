<template>
  <div class="recharge">
    <a-card class="recharge-card">
      <template #title>
        <div class="card-title">
          <span>充值中心</span>
          <span class="balance">当前余额：￥{{ totalBalance }}</span>
        </div>
      </template>
      
      <div class="amount-section">
        <h3>选择充值金额</h3>
        <a-row :gutter="[16, 16]">
          <a-col :span="8" v-for="item in quickAmounts" :key="item.coin_id">
            <a-card
              :class="['amount-card', selectedAmount === item.amount ? 'selected' : '']"
              @click="selectAmount(item)"
            >
              <div class="amount-value">￥{{ item.amount }}</div>
              <div class="bonus" v-if="bonusMap[item.amount]">
                送{{ bonusMap[item.amount] }}币
              </div>
            </a-card>
          </a-col>
          <a-col :span="8">
            <a-card class="amount-card custom">
              <a-input-number
                v-model:value="customAmount"
                :min="1"
                :max="99999"
                placeholder="其他金额"
                @change="selectCustomAmount"
              />
            </a-card>
          </a-col>
        </a-row>
      </div>

      <div class="payment-section">
        <h3>选择支付方式</h3>
        <a-radio-group v-model:value="selectedPayment">
          <a-radio value="alipay">
            <img src="../../assets/icons/alipay.png" alt="支付宝" class="payment-icon" />
            支付宝
          </a-radio>
          <a-radio value="wechat">
            <img src="../../assets/icons/wechat.png" alt="微信支付" class="payment-icon" />
            微信支付
          </a-radio>
        </a-radio-group>
      </div>

      <div class="action-section">
        <a-button type="primary" size="large" block @click="handleRecharge" :loading="loading">
          立即充值
        </a-button>
      </div>

      <div class="vip-section">
        <a-card class="vip-card" @click="handleVipClick">
          <div class="vip-content">
            <div class="vip-title">
              <crown-outlined />
              开通VIP会员
            </div>
            <div class="vip-desc">享受专属特权和优惠</div>
          </div>
          <right-outlined />
        </a-card>
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { CrownOutlined, RightOutlined } from '@ant-design/icons-vue'

const loading = ref(false)
const totalBalance = ref(0)
const selectedAmount = ref(0)
const customAmount = ref<number | null>(null)
const selectedPayment = ref('alipay')
const selectedCoinId = ref<number | null>(null)

// 充值套餐选项
const quickAmounts = [
  { coin_id: 1, amount: 50 },
  { coin_id: 2, amount: 100 },
  { coin_id: 3, amount: 200 },
  { coin_id: 4, amount: 500 },
  { coin_id: 5, amount: 1000 }
]

// 充值赠送配置
const bonusMap = {
  100: 10,
  200: 25,
  500: 70,
  1000: 150
}

// 选择预设金额
const selectAmount = (item: { coin_id: number, amount: number }) => {
  selectedAmount.value = item.amount
  selectedCoinId.value = item.coin_id
  customAmount.value = null
}

// 选择自定义金额
const selectCustomAmount = (value: number | null) => {
  if (value) {
    selectedAmount.value = value
    selectedCoinId.value = null
  } else {
    selectedAmount.value = 0
    selectedCoinId.value = null
  }
}

// 处理充值请求
const handleRecharge = async () => {
  if (!selectedAmount.value && !customAmount.value) {
    message.warning('请选择或输入充值金额')
    return
  }

  const amount = selectedAmount.value || customAmount.value
  loading.value = true

  try {
    const response = await createRechargeOrder({
      amount,
      reference_id: selectedCoinId.value,
      reference_type: 'coin', // coin表明是金币类型的商品
      paymentMethod: selectedPayment.value
    })
    
    console.log('创建充值订单响应数据:', response)

    if (response.code === 200 && response.success) {
      // 创建一个临时div元素来放置支付宝返回的表单
      const div = document.createElement('div')
      div.innerHTML = response.data.pay_url
      document.body.appendChild(div)
      
      // 自动提交表单
      const form = div.getElementsByTagName('form')[0]
      if (form) {
        form.submit()
      } else {
        message.error('支付表单创建失败')
      }
    } else {
      message.error(response.message || '创建充值订单失败')
    }
  } catch (error) {
    console.error('充值请求失败:', error)
    message.error('充值请求失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

import { createRechargeOrder, getUserBalance } from '../../api/payment'

// 获取用户余额
const fetchBalance = async () => {
  try {
    const response = await getUserBalance()
    
    if (response.code == 200 && response.success) {
      totalBalance.value = response.data.balance
    } else {
      message.error(response.message || '获取余额失败')
    }
  } catch (error) {
    console.error('获取余额失败:', error)
    message.error('获取余额失败，请稍后重试')
  }
}

// 处理VIP点击
const handleVipClick = () => {
  // TODO: 实现VIP购买逻辑
  message.info('VIP功能即将上线')
}

onMounted(() => {
  fetchBalance()
})
</script>

<style scoped>
.recharge {
  padding: 24px;
}

.recharge-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.balance {
  color: #666;
  font-size: 14px;
}

.amount-section,
.payment-section,
.action-section,
.vip-section {
  margin-top: 24px;
}

.amount-card {
  cursor: pointer;
  text-align: center;
  transition: all 0.3s;
}

.amount-card:hover {
  border-color: #1890ff;
}

.amount-card.selected {
  border-color: #1890ff;
  background: #e6f7ff;
}

.amount-value {
  font-size: 20px;
  font-weight: bold;
  color: #1890ff;
}

.bonus {
  font-size: 12px;
  color: #ff4d4f;
  margin-top: 4px;
}

.amount-card.custom {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 86px;
}

.payment-section .ant-radio-group {
  display: flex;
  gap: 24px;
}

.payment-icon {
  width: 24px;
  height: 24px;
  margin-right: 8px;
  vertical-align: middle;
}

.vip-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  background: #fffbe6;
  border-color: #ffe58f;
}

.vip-card:hover {
  background: #fff7cc;
}

.vip-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.vip-title {
  font-size: 16px;
  font-weight: bold;
  color: #faad14;
}

.vip-desc {
  font-size: 12px;
  color: #666;
}
</style>