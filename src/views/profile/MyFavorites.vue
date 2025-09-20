<template>
  <div class="my-favorites">
    <a-table
      :columns="columns"
      :data-source="favorites"
      :pagination="pagination"
      :loading="loading"
      @change="handleTableChange"
    >
      <template #title>我的收藏</template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { Table, Space, Divider, message } from 'ant-design-vue'
import type { TablePaginationConfig } from 'ant-design-vue'

const columns = [
  {
    title: '标题',
    dataIndex: 'title',
    key: 'title',
    width: '40%',
  },
  {
    title: '作者',
    dataIndex: 'author',
    key: 'author',
    width: '15%',
  },
  {
    title: '收藏时间',
    dataIndex: 'createTime',
    key: 'createTime',
    width: '20%',
  },
  {
    title: '操作',
    key: 'action',
    width: '15%',
    customRender: ({ record }) => {
      return h(Space, {}, {
        default: () => [
          h('a', { href: `/topic/${record.id}` }, '查看'),
          h(Divider, { type: 'vertical' }),
          h('a', { onClick: () => handleCancelFavorite(record.id) }, '取消收藏')
        ]
      })
    }
  },
]

const favorites = ref([])
const loading = ref(false)
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
})

const fetchFavorites = async (page = 1, pageSize = 10) => {
  loading.value = true
  try {
    // TODO: 替换为实际的API调用
    const response = await fetch(`/api/favorites?page=${page}&pageSize=${pageSize}`)
    const data = await response.json()
    favorites.value = data.items
    pagination.value.total = data.total
  } catch (error) {
    console.error('获取收藏列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag: TablePaginationConfig) => {
  pagination.value.current = pag.current
  fetchFavorites(pag.current, pag.pageSize)
}

const handleCancelFavorite = async (id: string) => {
  try {
    // TODO: 替换为实际的API调用
    await fetch(`/api/favorites/${id}`, { method: 'DELETE' })
    message.success('取消收藏成功')
    fetchFavorites(pagination.value.current, pagination.value.pageSize)
  } catch (error) {
    console.error('取消收藏失败:', error)
    message.error('取消收藏失败')
  }
}

onMounted(() => {
  fetchFavorites()
})
</script>

<style scoped>
.my-favorites {
  background: #fff;
}
</style>