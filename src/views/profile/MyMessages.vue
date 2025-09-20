<template>
  <div class="my-messages">
    <a-table
      :columns="columns"
      :data-source="messages"
      :pagination="pagination"
      :loading="loading"
      @change="handleTableChange"
    >
      <template #title>我的消息</template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Table } from 'ant-design-vue'
import type { TablePaginationConfig } from 'ant-design-vue'

const columns = [
  {
    title: '消息内容',
    dataIndex: 'content',
    key: 'content',
    width: '50%',
  },
  {
    title: '发送者',
    dataIndex: 'sender',
    key: 'sender',
    width: '15%',
  },
  {
    title: '发送时间',
    dataIndex: 'createTime',
    key: 'createTime',
    width: '20%',
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: '15%',
    customRender: ({ text }) => text === 'unread' ? '未读' : '已读'
  },
]

const messages = ref([])
const loading = ref(false)
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
})

const fetchMessages = async (page = 1, pageSize = 10) => {
  loading.value = true
  try {
    // TODO: 替换为实际的API调用
    const response = await fetch(`/api/messages?page=${page}&pageSize=${pageSize}`)
    const data = await response.json()
    messages.value = data.items
    pagination.value.total = data.total
  } catch (error) {
    console.error('获取消息列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag: TablePaginationConfig) => {
  pagination.value.current = pag.current
  fetchMessages(pag.current, pag.pageSize)
}

onMounted(() => {
  fetchMessages()
})
</script>

<style scoped>
.my-messages {
  background: #fff;
}
</style>