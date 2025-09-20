<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Layout, Card, Tag, Statistic } from 'ant-design-vue'

const hotTags = [
  'HiRes经典老歌',
  '80后回忆',
  '刘德华',
  '陈奕迅',
  '周杰伦',
  '周杰伦',
  '洋葱',
  '张学友',
  'Taylor Swift',
  '林俊杰',
  '汪苏泷',
  '半阳兄弟'
]

const defaultPosts = [
  {
    id: 1,
    title: '韩宝仪《月圆花好》[FLAC/MP3-320K]',
    author: 'tudou',
    date: '2022-7-18',
    views: 243
  },
  {
    id: 2,
    title: '田园《先说爱的人为什么先离开》[FLAC/MP3-320K]',
    author: '黑星王子',
    date: '2022-3-1',
    views: 1846
  },
  {
    id: 3,
    title: '告五人《给你一个咒语好吗》[FLAC/MP3-320K]',
    author: '黑星王子',
    date: '2022-4-30',
    views: 22582
  }
]

const posts = ref([])
const loading = ref(false)
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0
})

const fetchPosts = async (page = 1, pageSize = 10) => {
  loading.value = true
  try {
    const response = await fetch(`/api/topics?page=${page}&pageSize=${pageSize}`)
    const result = await response.json()
    if (result.success) {
      const data = result.data

      posts.value = data.topics.map(item => ({
        id: item.id,
        title: item.title,
        author: item.author || 'Unknown',
        date: item.created_at,
        views: item.views
      }))
      pagination.value.total = data.total
    } else {
      console.error('获取主题列表失败:', result.message)
      // 使用默认数据作为兜底
      posts.value = defaultPosts
      pagination.value.total = defaultPosts.length
    }
  } catch (error) {
    console.error('获取主题列表失败:', error)
    // 使用默认数据作为兜底
    posts.value = defaultPosts
    pagination.value.total = defaultPosts.length
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPosts()
})

</script>

<template>
  <Layout class="layout">
    <Layout.Content class="main-content">
      <div class="main-layout">
        <div class="content">
          <div class="content-list">
            <div v-if="loading" class="loading-container">
              <div class="loading-spinner"></div>
            </div>
            <template v-else>
              <Card v-for="post in posts" :key="post.id" class="content-item" hoverable>
                <div class="post-content">
                  <div class="post-title">
                    <router-link :to="`/topic/${post.id}`" class="title-link">{{ post.title }}</router-link>
                  </div>
                  <div class="post-meta">
                    <span class="author">{{ post.author }}</span>
                    <span class="date">{{ post.date }}</span>
                    <span class="views">{{ post.views }}</span>
                  </div>
                </div>
              </Card>
            </template>
          </div>
          <div class="pagination-container">
            <div class="pagination">
              <button 
                v-for="page in Math.ceil(pagination.total / pagination.pageSize)" 
                :key="page"
                :class="['page-btn', { active: page === pagination.current }]"
                @click="() => fetchPosts(page)"
              >
                {{ page }}
              </button>
            </div>
          </div>
        </div>
        
        <div class="sider">
          <Card title="站点数据" class="stats-card">
            <div class="stats-content">
              <Statistic title="主题数" :value="80055" />
              <Statistic title="今日帖子" :value="9052" />
              <Statistic title="今日主题" :value="40" />
            </div>
          </Card>
          
          <Card title="关键词" class="tags-card">
            <div class="tags-container">
              <Tag v-for="tag in hotTags" :key="tag" class="tag">
                {{ tag }}
              </Tag>
            </div>
          </Card>
        </div>
      </div>
    </Layout.Content>
  </Layout>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  background: #f5f5f5;
}

.main-content {
  padding-top: 24px;
  background: #f5f5f5;
}

.main-layout {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 16px;
  display: flex;
  gap: 24px;
}

@media screen and (max-width: 768px) {
  .main-layout {
    flex-direction: column;
  }

  .header-content {
    padding: 0 8px;
  }

  .menu {
    flex: 1;
    overflow-x: auto;
    white-space: nowrap;
  }

  .content-item {
    margin-bottom: 8px;
  }

  .post-meta {
    flex-wrap: wrap;
    gap: 8px;
  }

  .sider {
    width: 100%;
  }

  .tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
}
.content {
  flex: 1;
  min-width: 0;
}

.content-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.content-item {
  margin-bottom: 12px;
  background: #fff;
}

.post-content {
  padding: 16px;
}

.post-title {
  font-size: 16px;
  color: #1a1a1a;
  font-weight: 500;
  line-height: 1.4;
  margin-bottom: 8px;
}

.post-meta {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #999;
}

.post-meta > span {
  position: relative;
  margin-right: 24px;
}

.post-meta > span:not(:last-child)::after {
  content: '';
  position: absolute;
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
  width: 1px;
  height: 12px;
  background-color: #e8e8e8;
}

.sider {
  width: 300px;
  flex-shrink: 0;
}

.stats-card,
.tags-card {
  margin-bottom: 24px;
  background: #fff;
}

.stats-content {
  display: grid;
  gap: 16px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  cursor: pointer;
  margin: 0;
}

.tag:hover {
  color: #1890ff;
}

.title-link {
  color: inherit;
  text-decoration: none;
}

.title-link:hover {
  color: #1890ff;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 20px auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.pagination {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
}

.page-btn {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  background: white;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.page-btn.active {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
}

.page-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
</style>