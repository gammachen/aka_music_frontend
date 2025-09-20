
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Layout, Button, Input, Card, Modal, message } from 'ant-design-vue'
import { EyeOutlined, DownloadOutlined, HeartOutlined, PlusOutlined, ShareAltOutlined, DownOutlined, DollarOutlined } from '@ant-design/icons-vue'
import HeroSearch from '../../components/HeroSearch.vue'
import AdCarousel from '../../components/AdCarousel.vue'
import { getContentDetail, getContentList, getChapterDetail, getChapterDetailForLogin, orderChapter} from '../../api/comic'

// 路由参数
const route = useRoute()
const router = useRouter()

// 添加一个函数来获取随机默认封面
const getRandomDefaultCover = () => {
  const randomNum = Math.floor(Math.random() * 8) + 1
  return `/static/def/a${randomNum}.png`
}

// 状态管理
const loading = ref(false)
const error = ref('')

// 漫画数据
const comic = ref({
  id: '',
  title: '',
  author: '',
  rating: 0,
  totalRatings: 0,
  popularity: 0,
  collections: 0,
  coverUrl: '',
  description: '',
  tags: [],
  status: 'DRAFT'
})

// 章节预览浮层
const previewVisible = ref(false)
const currentChapter = ref(null)
const chapterImages = ref([])
const imageLoadingStates = ref({})
const hasPermission = ref(false)

// 章节列表相关
const currentPage = ref(1)
const pageSize = ref(20)
const totalChapters = ref(0)
const sortOrder = ref('asc')
const chapters = ref([])

// 获取本地存储的用户登录状态
const isLoggedIn = () => {
  return !!localStorage.getItem('token')
}

// 获取章节列表
const fetchChapterList = async () => {
  try {
    loading.value = true
    error.value = ''
    const response = await getContentList({
      id: route.params.id,
      page: currentPage.value,
      page_size: pageSize.value
    })
    if (response.data) {
      chapters.value = response.data.list.map(chapter => ({
        id: chapter.id,
        title: chapter.title,
        updateTime: chapter.updated_at,
        isFree: chapter.is_free // 添加免费标识
      }))
      totalChapters.value = response.data.pagination.total
    }
  } catch (err) {
    error.value = '获取章节列表失败'
    message.error('获取章节列表失败')
  } finally {
    loading.value = false
  }
}

// 获取漫画详情
const fetchComicDetail = async () => {
  try {
    loading.value = true
    error.value = ''

    // console.log("xxxxx", route.params.id)

    const response = await getContentDetail({ id: route.params.id })

    if (response.data) {
      comic.value = {
        id: response.data.id,
        title: response.data.title,
        author: response.data.author_id,
        rating: response.data.rating || 0,
        totalRatings: response.data.total_ratings || 0,
        popularity: response.data.popularity || 0,
        collections: response.data.collections || 0,
        coverUrl: response.data.cover_url || getRandomDefaultCover(),
        description: response.data.description || '',
        tags: response.data.tags || [],
        status: response.data.status
      }
    } else {
      error.value = '漫画不存在'
      message.error('漫画不存在')
    }
  } catch (err) {
    error.value = '获取漫画详情失败'
    message.error('获取漫画详情失败')
  } finally {
    loading.value = false
  }
}

// 计算排序后的章节列表
const sortedChapters = computed(() => {
  const sorted = [...chapters.value]
  if (sortOrder.value === 'desc') {
    sorted.reverse()
  }
  return sorted
})


// 获取章节内容
const fetchChapterContent = async (chapterId) => {
  try {
    const response = await getChapterDetail({ id: chapterId })
    console.log('Chapter content:', response.data)
    if (response.data && response.data.pages) {
      const images = response.data.pages.images || []
      // 初始化每个图片的加载状态
      images.forEach(image => {
        imageLoadingStates.value[image.order] = true
      })
      return images
    }
    throw new Error('获取章节内容失败')
  } catch (err) {
    console.error('获取章节内容失败:', err)
    throw err
  }
}

// 处理章节预览
const previewChapter = async (chapter) => {
  currentChapter.value = chapter
  hasPermission.value = false

  if (chapter.isFree) {
    hasPermission.value = true
    try {
      chapterImages.value = await fetchChapterContent(chapter.id)
      previewVisible.value = true
    } catch (err) {
      message.error('获取章节内容失败')
    }
  } else {
    // 首先是客户端先判断是否登录（TODO 似乎不太准确，需要修改）
    if (!isLoggedIn()) {
      // 未登录，保存当前URL并跳转到登录页
      localStorage.setItem('redirect_url', route.fullPath)
      router.push('/login')
      return
    } else {
      // 已登录，请求后端验证用户是否已购买该章节
      const rep = await getChapterDetailForLogin({id:chapter.id})

      console.log("login validation:", rep)
      if (rep.code === 401){
        // 未登录，保存当前URL并跳转到登录页
        localStorage.setItem('redirect_url', route.fullPath)
        router.push('/login')
        return
      }

      if (rep.code === 1101) { // 用户未购买该章节，显示订购浮层
        hasPermission.value = false
        // 用户未购买该章节，显示订购浮层
        Modal.info({
          title: '购买提示',
          content: '该章节需要购买才能观看，是否立即购买？',
          okText: '立即购买',
          cancelText: '取消',
          onOk: async () => {
            try {
              await handlePurchase(chapter)
              // 购买成功后仅关闭浮层
              previewVisible.value = false
            } catch (err) {
              // 错误已在handlePurchase中处理
            }
          },
          onCancel: () => {
            // 用户取消购买，不做任何操作
          }
        })
      } else if (rep.code === 200) {
        // 用户已购买该章节，直接显示章节内容
        hasPermission.value = true
        try {
          const images = rep.data.pages.images || []
          // 初始化每个图片的加载状态
          images.forEach(image => {
            imageLoadingStates.value[image.order] = true
          })
          chapterImages.value = images
          previewVisible.value = true
        } catch (err) {
          message.error('获取章节内容失败')
        }
      }
    }
  }
}

// 事件处理函数
const startReading = () => {
  router.push(`/comic/${comic.value.id}/chapter/1`)
}

const addToCollection = () => {
  message.success('收藏成功')
}

const vote = () => {
  message.success('投票成功')
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchChapterList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchChapterList()
}

// 处理图片加载完成
const handleImageLoad = (imageOrder) => {
  imageLoadingStates.value[imageOrder] = false
}

// 用户余额
const userBalance = ref(0)

// 处理章节购买
const handlePurchase = async (chapter) => {
  try {
    const response = await orderChapter({ id: chapter.id })
    if (response.data) {
      message.success('购买成功')
      previewVisible.value = false
      // 购买成功后跳转到章节阅读页面，现在使用当前页面（列表页面）
      router.push(`/comic/${comic.value.id}`)
    }
  } catch (err) {
    message.error('购买失败：' + (err.message || '未知错误'))
  }
}

// 处理充值跳转
const handleRecharge = () => {
  router.push('/recharge')
}

// 组件挂载时加载数据
onMounted(() => {
  fetchComicDetail()
  fetchChapterList()
})

// 监听路由参数变化
watch(() => route.params.id, async (newId, oldId) => {
  if (newId && newId !== oldId) {
    console.log('漫画ID变化:', oldId, '->', newId)
    currentPage.value = 1
    await fetchComicDetail()
    await fetchChapterList()
  }
})
</script>

<template>
  <Layout class="landing-layout">
    <HeroSearch @search="handleSearch" />
    
  <div class="comic-detail">

    <section class="ad-section">
        <div class="ad-wrapper">
          <AdCarousel :ads="[
            {
              link: 'https://example.com/ad1',
              image: '/static/def/ad1.png',
              alt: '精选音乐'
            },
            {
              link: 'https://example.com/ad2',
              image: '/static/def/ad2.png',
              alt: '热门歌单'
            },{
              link: 'https://example.com/ad1',
              image: '/static/def/ad1.png',
              alt: '精选音乐'
            },
            {
              link: 'https://example.com/ad2',
              image: '/static/def/ad2.png',
              alt: '热门歌单'
            }
          ]" />
        </div>
      </section>

    <!-- 上部分：漫画基本信息 -->
    <div class="comic-info">
      <div class="comic-cover">
        <img :src="comic.coverUrl || getRandomDefaultCover()" alt="封面" class="cover-image">
        <div class="status-tag">{{ comic.status }}</div>
      </div>
      
      <div class="comic-meta">
        <h1 class="title">{{ comic.title }}</h1>
        
        <div class="rating-info">
          <div class="rating">
            <span class="label">评分：</span>
            <span class="score">{{ comic.rating }}</span>
            <div class="stars">
              <el-rate v-model="comic.rating" disabled show-score text-color="#ff9900" />
            </div>
            <span class="total-rating">({{ comic.totalRatings }}人评分)</span>
          </div>
        </div>
        
        <div class="author-info">
          <span class="label">作者：</span>
          <span class="author">{{ comic.author }}</span>
        </div>
        
        <div class="stats">
          <span class="popularity">人气：{{ comic.popularity }}亿</span>
          <span class="collection">收藏数：{{ comic.collections }}</span>
        </div>
        
        <div class="tags">
          <el-tag v-for="tag in comic.tags" :key="tag" size="small" class="tag">{{ tag }}</el-tag>
        </div>
        
        <div class="description">{{ comic.description }}</div>
        
        <div class="actions">
          <el-button type="primary" size="large" @click="startReading">开始阅读</el-button>
          <el-button size="large" @click="addToCollection">收藏</el-button>
          <el-button size="large" @click="vote">投月票</el-button>
        </div>
      </div>
    </div>

    <!-- 下部分：章节列表 -->
    <div class="chapter-list">
      <div class="list-header">
        <h2>章节列表</h2>
        <div class="sort-options">
          <el-radio-group v-model="sortOrder">
            <el-radio-button value="asc">正序</el-radio-button>
            <el-radio-button value="desc">倒序</el-radio-button>
          </el-radio-group>
        </div>
      </div>
      
      <div class="chapters">
        <div v-for="chapter in sortedChapters" :key="chapter.id" class="chapter-item" @click="previewChapter(chapter)">
          <span class="chapter-title">
            <span v-if="chapter.isFree" class="tag free-tag"><EyeOutlined /> 免费</span>
            <span v-else class="tag pay-tag"><DollarOutlined /> 付费</span>
            {{ chapter.title }}
          </span>
          <span class="update-time">{{ chapter.updateTime }}</span>
        </div>

        <!-- 章节预览浮层 -->
        <Modal
          v-model:visible="previewVisible"
          :title="currentChapter?.title"
          width="800px"
          @cancel="previewVisible = false"
        >
          <div v-if="currentChapter && !hasPermission" class="chapter-purchase">
            <div class="purchase-info">
              <h3>{{ currentChapter.title }}</h3>
              <div class="user-balance">
                <span class="label">当前余额：</span>
                <span class="amount">{{ userBalance }}</span>
                <span class="unit">金币</span>
              </div>
              <p class="price">
                <span class="label">购买价格：</span>
                <span class="amount">{{ currentChapter.price || 100 }}</span>
                <span class="unit">金币</span>
              </p>
              <div class="purchase-notice" v-if="userBalance < (currentChapter.price || 100)">
                <el-alert
                  title="余额不足"
                  type="warning"
                  description="您的金币余额不足，请先充值"
                  show-icon
                />
              </div>
              <div class="purchase-actions">
                <el-button 
                  type="primary" 
                  @click="handlePurchase(currentChapter)"
                  :disabled="userBalance < (currentChapter.price || 100)"
                >
                  立即购买
                </el-button>
                <el-button v-if="userBalance < (currentChapter.price || 100)" @click="handleRecharge">去充值</el-button>
              </div>
            </div>
          </div>
          <div v-else class="chapter-preview">
            <div v-for="image in chapterImages" :key="image.order" class="image-wrapper">
              <img
                :src="image.url"
                :alt="`第${image.order}页`"
                class="chapter-image"
                @load="handleImageLoad(image.order)"
              >
              <div class="image-loading" v-show="imageLoadingStates[image.order]">
                <a-spin />
              </div>
            </div>
          </div>
        </Modal>
      </div>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalChapters"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
  </Layout>
</template>


<style scoped>
.comic-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.comic-info {
  display: flex;
  gap: 30px;
  margin-bottom: 40px;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.comic-cover {
  position: relative;
  width: 240px;
  height: 320px;
  border-radius: 8px;
  overflow: hidden;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.status-tag {
  position: absolute;
  top: 10px;
  left: 10px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.comic-meta {
  flex: 1;
}

.title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
}

.rating-info {
  margin-bottom: 15px;
}

.rating {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score {
  color: #ff9900;
  font-size: 20px;
  font-weight: bold;
}

.total-rating {
  color: #666;
  font-size: 14px;
}

.author-info,
.stats {
  margin-bottom: 15px;
  color: #666;
}

.stats {
  display: flex;
  gap: 20px;
}

.tags {
  margin-bottom: 20px;
}

.tag {
  margin-right: 8px;
}

.description {
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
}

.actions {
  display: flex;
  gap: 15px;
}

.chapter-list {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chapters {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.chapter-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border: 1px solid #eee;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.chapter-title {
  color: #333;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chapter-title .tag {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
  line-height: 1;
  margin-right: 8px;
}

.chapter-title .free-tag {
  background-color: #52c41a;
  color: white;
}

.chapter-title .pay-tag {
  background-color: #f5222d;
  color: white;
}

.chapter-preview {
  max-height: 80vh;
  overflow-y: auto;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.chapter-purchase {
  padding: 30px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.purchase-info {
  text-align: center;
}

.purchase-info h3 {
  margin-bottom: 24px;
  font-size: 20px;
  color: #333;
}

.user-balance {
  margin: 20px 0;
  padding: 15px;
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.price {
  margin: 20px 0;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.label {
  color: #666;
}

.amount {
  color: #ff9900;
  font-size: 24px;
  font-weight: bold;
}

.unit {
  color: #666;
}

.purchase-notice {
  margin: 20px 0;
}

.purchase-actions {
  margin-top: 24px;
  display: flex;
  justify-content: center;
  gap: 16px;
}

.purchase-actions .el-button {
  min-width: 120px;
  height: 40px;
  font-size: 16px;
}

.image-wrapper {
  position: relative;
  margin-bottom: 20px;
  text-align: center;
}

.chapter-image {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto;
}

.image-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.update-time {
  color: #999;
  font-size: 12px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
