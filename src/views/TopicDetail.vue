<template>
  <Layout class="layout">
    <!-- <NavBar /> -->

    <Layout.Content class="main-content">
      <div class="main-layout">
        <div class="topic-container">
          <Card class="topic-card">
            <div class="topic-header">
              <h1 class="topic-title">{{ topic.title }}</h1>
              <div class="topic-meta">
                <Avatar :size="24" :src="topic.authorAvatar" />
                <span class="author-name">{{ topic.author }}</span>
                <span class="publish-time">{{ topic.createTime }}</span>
                <span class="view-count">浏览 {{ topic.views }}</span>
              </div>
            </div>

            <Divider />

            <div class="topic-content">
              <div class="content-text" v-html="topic.content"></div>
              
              <div class="audio-player" v-if="topic.audioUrl">
                <h3>试听</h3>
                <audio controls>
                  <source :src="topic.audioUrl" type="audio/mpeg">
                  您的浏览器不支持音频播放
                </audio>
              </div>

              <div class="download-section">
                <h3>下载地址</h3>
                <div class="download-item">
                  <div class="download-info">
                    <span class="download-label">链接：</span>
                    <a :href="topic.downloadUrl" target="_blank">{{ topic.downloadUrl }}</a>
                  </div>
                  <div class="download-info" v-if="topic.extractCode">
                    <span class="download-label">提取码：</span>
                    <span class="extract-code">{{ topic.extractCode }}</span>
                  </div>
                </div>

                <div class="backup-links" v-if="topic.backupLinks && topic.backupLinks.length">
                  <h4>备用链接</h4>
                  <div v-for="(link, index) in topic.backupLinks" :key="index" class="backup-item">
                    <a :href="link.url" target="_blank">备用链接 {{ index + 1 }}</a>
                    <span v-if="link.extractCode" class="extract-code">提取码：{{ link.extractCode }}</span>
                  </div>
                </div>
              </div>
            </div>

            <Divider />

            <div class="topic-actions">
              <Space>
                <a-button type="primary" @click="handleLike">
                  <template #icon><LikeOutlined /></template>
                  点赞 {{ topic.likes }}
                </a-button>
                <a-button @click="handleFavorite">
                  <template #icon><StarOutlined /></template>
                  收藏
                </a-button>
                <a-button @click="handleReward">
                  <template #icon><GiftOutlined /></template>
                  打赏
                </a-button>
              </Space>
            </div>
          </Card>

          <Card class="comments-card">
            <template #title>
              <Space>
                <span>评论区</span>
                <Tag>{{ total }}条评论</Tag>
              </Space>
            </template>
            <template #extra>
              <Space>
                <Select v-model:value="sortBy" style="width: 120px">
                  <Select.Option value="time">按时间</Select.Option>
                  <Select.Option value="like">按点赞</Select.Option>
                </Select>
              </Space>
            </template>

            <div class="comment-editor">
              <Input.TextArea v-model:value="commentContent" :rows="4" placeholder="说点什么..." />
              <div class="editor-footer">
                <a-button type="primary" @click="handleComment" :loading="submitting">发表评论</a-button>
              </div>
            </div>

            <List
              class="comments-list"
              :data-source="comments"
              :loading="loading"
              item-layout="horizontal"
            >
              <template #renderItem="{ item, index }">
                <List.Item>
                  <Comment>
                    <template #avatar>
                      <Avatar :src="item.author.avatar" :alt="item.author.name" />
                    </template>
                    <template #author>
                      <Space>
                        <a>{{ item.author.name }}</a>
                        <Tag color="blue">#{{ (currentPage - 1) * pageSize + index + 1 }}楼</Tag>
                      </Space>
                    </template>
                    <template #content>
                      <div v-html="item.content"></div>
                    </template>
                    <template #datetime>
                      <Space>
                        <span>{{ item.createTime }}</span>
                        <Button type="link" size="small" @click="handleCommentLike(item)">
                          <template #icon><LikeOutlined /></template>
                          {{ item.likeCount }}
                        </Button>
                        <Button type="link" size="small" @click="showReplyModal(item)">
                          <template #icon><MessageOutlined /></template>
                          回复
                        </Button>
                      </Space>
                    </template>
                    <!-- <pre>{{ JSON.stringify(item.replies, null, 2) }}</pre>
                    <pre>{{item.replies.length}}</pre> -->
                    <!-- 评论的回复列表 -->
                    <template v-if="item.replies && item.replies.length > 0">
                      <div>
                        <List
                          class="reply-list"
                          :data-source="item.replies"
                          item-layout="horizontal"
                        >
                          <template #renderItem="{ item: reply }">
                            <List.Item>
                              <Comment>
                                <template #avatar>
                                  <Avatar :src="reply.author.avatar" :alt="reply.author.name" />
                                </template>
                                <template #author>
                                  <a>{{ reply.author.name }}</a>
                                </template>
                                <template #content>
                                  <div v-html="reply.content"></div>
                                </template>
                                <template #datetime>
                                  <Space>
                                    <span>{{ reply.createTime }}</span>
                                    <Button type="link" size="small" @click="handleCommentLike(reply)">
                                      <template #icon><LikeOutlined /></template>
                                      {{ reply.likeCount }}
                                    </Button>
                                  </Space>
                                </template>
                              </Comment>
                            </List.Item>
                          </template>
                        </List>
                      </div>
                    </template>
                  </Comment>
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

            <Modal
              v-model:visible="replyModalVisible"
              title="回复评论"
              @ok="handleReplySubmit"
              :confirmLoading="submitting"
            >
              <Form :model="replyForm">
                <Form.Item label="回复内容">
                  <Input.TextArea
                    v-model:value="replyForm.content"
                    :rows="4"
                    placeholder="请输入回复内容"
                  />
                </Form.Item>
              </Form>
            </Modal>
          </Card>
        </div>
      </div>
    </Layout.Content>
  <RewardModal
    v-model:visible="rewardModalVisible"
    @confirm="handleRewardConfirm"
  />
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Layout, Menu, Card, Avatar, Space, Divider, List, Tag, Select, Button, Modal, Form, Pagination, Comment, Input } from 'ant-design-vue'
import { ElMessage } from 'element-plus'
import {
  LikeOutlined,
  StarOutlined,
  GiftOutlined,
  MessageOutlined
} from '@ant-design/icons-vue'
import RewardModal from '../components/RewardModal.vue'
import { createReward } from '../api/reward'

const router = useRouter()
const commentContent = ref('')

// 默认主题数据作为兜底
const defaultTopic = {
  title: '分享一首超好听的音乐',
  author: '音乐达人',
  authorAvatar: '',
  createTime: '2024-02-15 14:30',
  views: 1234,
  likes: 88,
  content: '这是一首非常棒的音乐，希望大家喜欢！',
  audioUrl: 'https://bailian-bmp-prod.oss-cn-beijing.aliyuncs.com/public/audio/timbreList/%E9%BE%99%E5%A9%892.mp3',
  downloadUrl: 'https://bailian-bmp-prod.oss-cn-beijing.aliyuncs.com/public/audio/timbreList/%E9%BE%99%E5%A9%892.mp3',
  extractCode: 'abc1',
  backupLinks: [
    { url: 'https://pan.baidu.com/s/yyyyy', extractCode: 'xyz1' },
    { url: 'https://pan.baidu.com/s/zzzzz', extractCode: 'def1' }
  ]
}

// 主题数据
const topic = ref(defaultTopic)

// 获取主题详情数据
const fetchTopicDetail = async () => {
  const topicId = route.params.id
  try {
    const response = await fetch(`/api/topics/${topicId}`)
    const result = await response.json()
    if (result.success) {
      const data = result.data
      topic.value = {
            title: data.title,
            author: data.author || '匿名用户',
            authorAvatar: data.authorAvatar,
            createTime: data.created_at,
            views: data.views,
            likes: data.likes,
            content: data.content,
            audioUrl: data.audioUrl,
            downloadUrl: data.downloadUrl,
            extractCode: data.extractCode,
            backupLinks: data.backupLinks || []
        } 
    } else {
      console.error('获取主题详情失败:', result.message)
      topic.value = defaultTopic
    }
  } catch (error) {
    console.error('获取主题详情失败:', error)
    topic.value = defaultTopic
  }
}

onMounted(() => {
  fetchTopicDetail()
  fetchComments(currentPage.value, sortBy.value)
})

// 默认评论数据作为兜底
const defaultComments = [
  {
    id: 1,
    content: '这首歌真的很好听，旋律优美，歌词打动人心！',
    createTime: '2024-02-15 15:30',
    likeCount: 25,
    author: {
      name: '音乐爱好者',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix'
    }
  },
  {
    id: 2,
    content: '感谢分享，已经下载收藏了！',
    createTime: '2024-02-15 16:45',
    likeCount: 18,
    author: {
      name: '旋律达人',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Aneka'
    }
  },
  {
    id: 3,
    content: '这个版本编曲很棒，推荐大家都来听听',
    createTime: '2024-02-15 17:20',
    likeCount: 12,
    author: {
      name: '音乐制作人',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Melody'
    }
  }
]

// 评论列表相关状态
const comments = ref([])

// 获取评论列表(TODO 1. 限制只有登录用户才能够使用的 )
const fetchComments = async (page = 1, sort = 'time') => {
  loading.value = true
  const topicId = route.params.id
  try {
    const response = await fetch(`/api/comments?topic_id=${topicId}&page=${page}&page_size=${pageSize.value}&sort=${sort}`)
    const result = await response.json()
    if (result.success) {
      comments.value = result.data.comments.map(item => ({
        id: item.id,
        content: item.content,
        createTime: item.created_at,
        likeCount: item.like_count || 0,
        author: {
          name: item.author_name || '匿名用户',
          avatar: item.author_avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${item.author_id || 'anonymous'}`
        },
        replies: (item.replies || []).map(reply => ({
          id: reply.id,
          content: reply.content,
          createTime: reply.created_at,
          likeCount: reply.like_count || 0,
          author: {
            name: reply.author_name || '匿名用户',
            avatar: reply.author_avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${reply.author_id || 'anonymous'}`
          }
        }))
      }))
      total.value = result.data.total
    } else {
      console.error('获取评论列表失败:', result.message)
      // 使用默认评论数据作为兜底
      comments.value = defaultComments
      total.value = defaultComments.length
    }
  } catch (error) {
    console.error('获取评论列表失败:', error)
    // 使用默认评论数据作为兜底
    comments.value = defaultComments
    total.value = defaultComments.length
  } finally {
    loading.value = false
  }
}
const loading = ref(false)
const submitting = ref(false)
const total = ref(15)
const currentPage = ref(1)
const pageSize = ref(10)
const sortBy = ref('time')

watch(sortBy, (newSort) => {
  fetchComments(currentPage.value, newSort)
})

// 回复模态框相关状态
const replyModalVisible = ref(false)
const replyForm = ref({
  content: '',
  parentId: null
})

// 评论相关处理函数
const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchComments(page, sortBy.value)
}

const handleCommentLike = (comment: any) => {
  // TODO: 实现评论点赞功能
}

const showReplyModal = (comment?: any) => {
  if (comment) {
    replyForm.value.parentId = comment.id
  } else {
    replyForm.value.parentId = null
  }
  replyModalVisible.value = true
}

const handleReplySubmit = async () => {
  if (!replyForm.value.content.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }

  submitting.value = true
  try {
    const response = await fetch('/api/comments/reply', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}` // 添加token
      },
      body: JSON.stringify({
        topic_id: route.params.id,
        content: replyForm.value.content.trim(),
        parent_id: replyForm.value.parentId
      })
    })

    const result = await response.json()
    if (result.success) {
      ElMessage.success('回复发布成功')
      replyModalVisible.value = false
      replyForm.value.content = ''
      // 重新加载评论列表
      await fetchComments(currentPage.value, sortBy.value)
    } else {
      ElMessage.error(result.message || '回复发布失败')
    }
  } catch (error) {
    console.error('发布回复失败:', error)
    ElMessage.error('回复发布失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

const handleLike = () => {
  // TODO: 实现点赞功能
}

const handleFavorite = () => {
  // TODO: 实现收藏功能
}

const rewardModalVisible = ref(false)

const handleReward = () => {
  rewardModalVisible.value = true
}

const route = useRoute()

// 打赏确认处理函数
const handleRewardConfirm = async (amount: number) => {
  try {
    const result = await createReward({
      target_type: 'topic',
      target_id: Number(route.params.id),
      amount: amount
    })
    
    if (result.success) {
      ElMessage.success('打赏成功')
      // 更新主题信息
      await fetchTopicDetail()
    } else {
      ElMessage.error(result.message || '打赏失败')
    }
  } catch (error) {
    console.error('打赏失败:', error)
    ElMessage.error('打赏失败，请稍后重试')
  }
}

const handleComment = async () => {
  if (!commentContent.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }

  submitting.value = true
  try {
    const response = await fetch('/api/comments/reply', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}` // 添加token
      },
      body: JSON.stringify({
        topic_id: route.params.id,
        content: commentContent.value.trim()
      })
    })

    const result = await response.json()
    if (result.success) {
      ElMessage.success('评论发布成功')
      commentContent.value = ''
      // 重新加载评论列表
      await fetchComments(currentPage.value, sortBy.value)
    } else {
      ElMessage.error(result.message || '评论发布失败')
    }
  } catch (error) {
    console.error('发布评论失败:', error)
    ElMessage.error('评论发布失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

const handleLogout = () => {
  // TODO: 实现退出登录功能
  router.push('/login')
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

.logout-btn {
  padding: 4px 0;
  color: #999;
}

.logout-btn:hover {
  color: #1890ff;
}

.main-content {
  padding-top: 24px;
  background: #f5f5f5;
}

.main-layout {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 16px;
}

.topic-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.topic-card {
  background: #fff;
}

.topic-header {
  margin-bottom: 24px;
}

.topic-title {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 16px;
}

.topic-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #8c8c8c;
  font-size: 14px;
}

.author-name {
  color: #1a1a1a;
  font-weight: 500;
}

.topic-content {
  font-size: 16px;
  line-height: 1.8;
  color: #1a1a1a;
}

.audio-player {
  margin: 24px 0;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 4px;
}

.audio-player h3 {
  margin-bottom: 16px;
  font-size: 16px;
  color: #1a1a1a;
}

.download-section {
  margin: 24px 0;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 4px;
}

.download-section h3 {
  margin-bottom: 16px;
  font-size: 16px;
  color: #1a1a1a;
}

.download-item {
  margin-bottom: 16px;
}

.download-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.download-label {
  color: #8c8c8c;
}

.extract-code {
  color: #1890ff;
  background: #e6f7ff;
  padding: 2px 8px;
  border-radius: 2px;
}

.backup-links {
  margin-top: 16px;
}

.backup-links h4 {
  font-size: 14px;
  color: #1a1a1a;
  margin-bottom: 12px;
}

.backup-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.topic-actions {
  display: flex;
  justify-content: center;
  padding: 16px 0;
}

.comments-card {
  background: #fff;
}

.comment-editor {
  margin-bottom: 24px;
}

.editor-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.comments-list {
  margin-top: 24px;
}

.comment-item {
  width: 100%;
}

.reply-list {
  margin-left: 44px;
  margin-top: 16px;
  padding-left: 20px;
  border-left: 2px solid #f0f0f0;
}

.reply-to {
  color: #1890ff;
  margin-left: 8px;
}

:deep(.ant-comment-nested) {
  margin-top: 16px;
}

:deep(.ant-list-item) {
  padding: 16px 0;
}

:deep(.ant-comment-content-detail) {
  margin-bottom: 8px;
}

@media screen and (max-width: 768px) {
  .main-layout {
    padding: 16px 8px;
  }

  .topic-title {
    font-size: 20px;
  }

  .topic-meta {
    flex-wrap: wrap;
  }

  .download-info {
    flex-direction: column;
    align-items: flex-start;
  }
}

</style>