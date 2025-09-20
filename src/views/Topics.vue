<template>
  <Layout class="layout">
    
    <Layout.Content class="main-content">
      <div class="main-layout">
        <div class="topics-container">
          <Card class="topics-card">
            <template #title>
              <Space>
                <span>主题列表</span>
                <Tag>{{ total }}个主题</Tag>
              </Space>
            </template>
            <template #extra>
              <Space>
                <Select v-model:value="sortBy" style="width: 120px">
                  <Select.Option value="time">最新发布</Select.Option>
                  <Select.Option value="hot">最热门</Select.Option>
                </Select>
              </Space>
            </template>

            <List
              class="topics-list"
              :data-source="topics"
              :loading="loading"
              item-layout="vertical"
            >
              <template #renderItem="{ item }">
                <List.Item>
                  <List.Item.Meta>
                    <template #title>
                      <router-link :to="`/topic/${item.id}`" class="topic-title">
                        {{ item.title }}
                      </router-link>
                    </template>
                    <template #description>
                      <Space>
                        <Avatar :size="24" :src="item.authorAvatar" />
                        <span class="author-name">{{ item.author }}</span>
                        <span class="publish-time">{{ item.createTime }}</span>
                      </Space>
                    </template>
                  </List.Item.Meta>
                  <div class="topic-brief">
                    <p>{{ item.brief }}</p>
                  </div>
                  <div class="topic-footer">
                    <Space>
                      <span>
                        <EyeOutlined /> {{ item.views }} 浏览
                      </span>
                      <span>
                        <LikeOutlined /> {{ item.likes }} 点赞
                      </span>
                      <span>
                        <MessageOutlined /> {{ item.comments }} 评论
                      </span>
                    </Space>
                  </div>
                </List.Item>
              </template>
            </List>

            <div class="pagination">
              <Pagination
                v-model:current="currentPage"
                :total="total"
                :page-size="pageSize"
                show-quick-jumper
                @change="handlePageChange"
              />
            </div>
          </Card>
        </div>
      </div>
    </Layout.Content>
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Layout, Menu, Card, Avatar, Space, List, Tag, Select, Pagination } from 'ant-design-vue'
import UserInfo from '../components/UserInfo.vue'
import {
  EyeOutlined,
  LikeOutlined,
  MessageOutlined
} from '@ant-design/icons-vue'

const props = defineProps<{
  cid?: string
}>()

const selectedKeys = ref(['discover'])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const sortBy = ref('time')

// 默认主题列表数据
const defaultTopics = [
  {
    id: 1,
    title: '分享一首超好听的音乐',
    author: '音乐达人',
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix',
    createTime: '2024-02-15 14:30',
    brief: '这是一首非常棒的音乐，希望大家喜欢！',
    views: 1234,
    likes: 88,
    comments: 45
  },
  {
    id: 2,
    title: '推荐一个新发现的音乐人',
    author: '乐评人',
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Aneka',
    createTime: '2024-02-15 16:45',
    brief: '最近发现了一个很有才华的音乐人，来分享给大家。',
    views: 856,
    likes: 67,
    comments: 32
  }
]

const topics = ref(defaultTopics)

// 获取主题列表
const fetchTopics = async (page = 1, sort = 'time') => {
  const categoryParam = props.cid ? `&category=${props.cid}` : ''
  loading.value = true
  try {
    const response = await fetch(`/api/topics?page=${page}&page_size=${pageSize.value}&sort=${sort}${categoryParam}`)
    const result = await response.json()
    if (result.success) {
      topics.value = result.data.topics.map(item => ({
        id: item.id,
        title: item.title,
        author: item.author || '匿名用户',
        authorAvatar: item.authorAvatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${item.author_id || 'anonymous'}`,
        createTime: item.created_at,
        brief: item.brief || item.content.substring(0, 100) + '...',
        views: item.views,
        likes: item.likes,
        comments: item.comment_count
      }))
      total.value = result.data.total
    } else {
      console.error('获取主题列表失败:', result.message)
      topics.value = defaultTopics
      total.value = defaultTopics.length
    }
  } catch (error) {
    console.error('获取主题列表失败:', error)
    topics.value = defaultTopics
    total.value = defaultTopics.length
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchTopics(currentPage.value, sortBy.value)
})

watch(sortBy, (newSort) => {
  fetchTopics(currentPage.value, newSort)
})

watch(() => props.cid, (newCid) => {
  currentPage.value = 1
  fetchTopics(currentPage.value, sortBy.value)
})

const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchTopics(page, sortBy.value)
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: #fff;
  padding: 0;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}

.menu {
  line-height: 64px;
  border: none;
}

.user-area {
  margin-left: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.main-content {
  padding-top: 84px;
  background: #f5f5f5;
}

.main-layout {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 16px;
}

.topics-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.topics-card {
  background: #fff;
}

.topics-list {
  margin-top: 16px;
}

.topic-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  text-decoration: none;
}

.topic-title:hover {
  color: #1890ff;
}

.author-name {
  color: #1a1a1a;
  font-weight: 500;
}

.publish-time {
  color: #8c8c8c;
}

.topic-brief {
  margin: 12px 0;
  color: #595959;
  line-height: 1.6;
}

.topic-footer {
  color: #8c8c8c;
}

.pagination {
  margin-top: 24px;
  text-align: center;
}

@media screen and (max-width: 768px) {
  .main-layout {
    padding: 16px 8px;
  }

  .topic-title {
    font-size: 16px;
  }
}
</style>