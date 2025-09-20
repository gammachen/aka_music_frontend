<template>
  <div class="my-topics">
    <a-table
      :columns="columns"
      :data-source="topics"
      :pagination="pagination"
      :loading="loading"
      @change="handleTableChange"
    >
      <template #title>我的主题</template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Table } from 'ant-design-vue'
import type { TablePaginationConfig } from 'ant-design-vue'

const columns = [
  {
    title: '标题',
    dataIndex: 'title',
    key: 'title',
    width: '40%',
  },
  {
    title: '回复/浏览',
    dataIndex: 'stats',
    key: 'stats',
    width: '15%',
    customRender: ({ record }) => `${record.replies}/${record.views}`
  },
  {
    title: '发布时间',
    dataIndex: 'createTime',
    key: 'createTime',
    width: '20%',
  },
  {
    title: '最后回复',
    dataIndex: 'lastReplyTime',
    key: 'lastReplyTime',
    width: '20%',
  },
]

const topics = ref([])
const loading = ref(false)
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
})

const fetchTopics = async (page = 1, pageSize = 10) => {
  loading.value = true
  try {
    // TODO: 替换为实际的API调用
    const response = await fetch(`/api/topics?page=${page}&pageSize=${pageSize}`)
    const data = await response.json()
    topics.value = data.items
    pagination.value.total = data.total
  } catch (error) {
    console.error('获取主题列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag: TablePaginationConfig) => {
  pagination.value.current = pag.current
  fetchTopics(pag.current, pag.pageSize)
}

onMounted(() => {
  fetchTopics()
})
</script>

<style scoped>
.my-topics {
  background: #fff;
}
</style>