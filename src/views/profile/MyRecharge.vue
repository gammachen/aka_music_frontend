<template>
  <div class="my-recharge">
    <a-table
      :columns="columns"
      :data-source="records"
      :pagination="pagination"
      :loading="loading"
      @change="handleTableChange"
      :scroll="{ x: 1500 }"
    >
      <template #title>我的充值</template>
      <template #headerCell="{ column }">
        <template v-if="column.key === 'balance'">
          <span>当前余额：{{ totalBalance }}</span>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { TablePaginationConfig } from 'ant-design-vue'
import { getRechargeRecords } from '../../api/recharge'
import { ElMessage } from 'element-plus'

const columns = [
  {
    title: '充值时间',
    dataIndex: 'createTime',
    key: 'createTime',
    width: 180,
  },
  {
    title: '充值金额',
    dataIndex: 'amount',
    key: 'amount',
    width: 120,
    customRender: ({ text }) => `￥${text.toFixed(2)}`
  },
  {
    title: '支付方式',
    dataIndex: 'paymentMethod',
    key: 'paymentMethod',
    width: 120,
    customRender: ({ text }) => {
      const methodMap = {
        alipay: '支付宝',
        wechat: '微信支付',
        bank: '银行卡'
      }
      return methodMap[text] || text
    }
  },
  {
    title: '交易订单号',
    dataIndex: 'pay_order_no',
    key: 'pay_order_no',
    width: 280,
  },
  {
    title: '充值订单号',
    dataIndex: 'outer_order_no',
    key: 'outer_order_no',
    width: 280,
  },
  {
    title: '支付订单号',
    dataIndex: 'channel_order_no',
    key: 'channel_order_no',
    width: 280,
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100,
    fixed: 'right',
    customRender: ({ text }) => {
      const statusMap = {
        '已支付': '已支付',
        '待支付': '待支付',
        '支付失败': '支付失败'
      }
      return statusMap[text] || text
    }
  },
]

const records = ref([])
const loading = ref(false)
const totalBalance = ref(0)
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
})

const fetchRechargeRecords = async (page = 1, pageSize = 10) => {
  console.log('开始获取充值记录，参数：', { page, pageSize })
  loading.value = true
  try {
    const response = await getRechargeRecords({ page, pageSize })
    if (response.code === 200) {
      const { data } = response
      console.log('获取充值记录成功，数据：', data)
      records.value = data.items
      pagination.value.total = data.total
      totalBalance.value = data.totalBalance
    } else {
      ElMessage.error(response.message || '获取充值记录失败')
    }
  } catch (error: any) {
    console.error('获取充值记录失败:', error)
    ElMessage.error(error.message || '网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag: TablePaginationConfig) => {
  console.log('表格分页变化：', pag)
  pagination.value.current = pag.current
  fetchRechargeRecords(pag.current, pag.pageSize)
}

onMounted(() => {
  console.log('组件已挂载，准备获取充值记录')
  fetchRechargeRecords()
})
</script>

<style scoped>
.my-recharge {
  background: #fff;
}
</style>