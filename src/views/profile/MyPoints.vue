<template>
  <div class="my-points">
    <a-table
      :columns="columns"
      :data-source="points"
      :pagination="pagination"
      :loading="loading"
      @change="handleTableChange"
    >
      <template #title>我的积分</template>
      <template #headerCell="{ column }">
        <template v-if="column.key === 'balance'">
          <span>当前积分：{{ totalPoints }}</span>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Table } from 'ant-design-vue'
import type { TablePaginationConfig } from 'ant-design-vue'

const columns = [
  {
    title: '变动时间',
    dataIndex: 'createTime',
    key: 'createTime',
    width: '20%',
  },
  {
    title: '变动类型',
    dataIndex: 'type',
    key: 'type',
    width: '15%',
    customRender: ({ text }) => {
      const typeMap = {
        post: '发帖奖励',
        reply: '回复奖励',
        like: '获赞奖励',
        consume: '积分消费'
      }
      return typeMap[text] || text
    }
  },
  {
    title: '变动数量',
    dataIndex: 'amount',
    key: 'amount',
    width: '15%',
    customRender: ({ text }) => (text > 0 ? `+${text}` : text)
  },
  {
    title: '变动说明',
    dataIndex: 'description',
    key: 'description',
    width: '35%',
  },
  {
    title: '余额',
    dataIndex: 'balance',
    key: 'balance',
    width: '15%',
  },
]

const points = ref([])
const loading = ref(false)
const totalPoints = ref(0)
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
})

const fetchPoints = async (page = 1, pageSize = 10) => {
  loading.value = true
  try {
    // TODO: 替换为实际的API调用
    const response = await fetch(`/api/points?page=${page}&pageSize=${pageSize}`)
    const data = await response.json()
    points.value = data.items
    pagination.value.total = data.total
    totalPoints.value = data.totalPoints
  } catch (error) {
    console.error('获取积分记录失败:', error)
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag: TablePaginationConfig) => {
  pagination.value.current = pag.current
  fetchPoints(pag.current, pag.pageSize)
}

onMounted(() => {
  fetchPoints()
})
</script>

<style scoped>
.my-points {
  background: #fff;
}
</style>