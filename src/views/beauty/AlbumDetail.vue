<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Layout, Button, Input, Card, Modal, message } from 'ant-design-vue'
import { EyeOutlined, DownloadOutlined, HeartOutlined, PlusOutlined, ShareAltOutlined, DownOutlined, DeleteOutlined, EditOutlined, CameraOutlined, ScanOutlined, SearchOutlined } from '@ant-design/icons-vue'
import HeroSearch from '../../components/HeroSearch.vue'
import ExifInfoModal from '../../components/ExifInfoModal.vue'
import { getBeautyList, type BeautyImage } from '../../api/beauty'
import { extractFace, type FaceExtractResponse, searchSimilarFaces, type SearchSimilarFacesResponse, type SimilarFaceResult } from '../../api/face'

const route = useRoute()
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 图片列表数据
const imageList = ref<BeautyImage[]>([])

// 控制图片预览浮层
const previewVisible = ref(false)
const currentImage = ref<BeautyImage | null>(null)

// 控制EXIF信息浮层
const exifModalVisible = ref(false)

// 控制人脸识别浮层
const faceVisible = ref(false)
const faceLoading = ref(false)
const faceError = ref('')
const faceResult = ref<FaceExtractResponse | null>(null)

// 控制相似人脸搜索浮层
const similarFacesVisible = ref(false)
const similarFacesLoading = ref(false)
const similarFacesError = ref('')
const similarFacesResults = ref<SimilarFaceResult[]>([])

// 控制AI功能浮层
const aiModalVisible = ref(false)
const bgRemoveModalVisible = ref(false)

// 获取图片列表
const fetchImageList = async () => {
  try {
    loading.value = true
    const refer_id = route.params.refer_id as string
    console.log('refer_id', refer_id)
    const response = await getBeautyList(refer_id, currentPage.value, pageSize.value)
    console.log('response', response)
    
    if (response.data) {
      imageList.value = response.data.list
      total.value = response.data.pagination.total
    }
  } catch (error) {
    console.error('获取图片列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 处理页码变化
const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchImageList()
}

// 处理每页条数变化
const handleSizeChange = (current: number, size: number) => {
  pageSize.value = size
  currentPage.value = 1 // 重置到第一页
  fetchImageList()
}

// 打开图片预览
const handlePreview = (image: BeautyImage) => {
  currentImage.value = image
  previewVisible.value = true
}

// 关闭图片预览
const handleCancel = () => {
  previewVisible.value = false
  currentImage.value = null
}

// 打开人脸识别
const handleExtractFace = async (image: BeautyImage) => {
  currentImage.value = image
  faceVisible.value = true
  faceLoading.value = true
  faceError.value = ''
  faceResult.value = null
  
  try {
    // 调用人脸识别API
    const response = await extractFace(image.url)
    if (response && response.data) {
      faceResult.value = response.data
      console.log('人脸识别结果:', faceResult.value)
    } else {
      faceError.value = '未能获取人脸识别结果'
    }
  } catch (error) {
    console.error('人脸识别失败:', error)
    faceError.value = error instanceof Error ? error.message : '人脸识别失败，请稍后重试'
    message.error(faceError.value)
  } finally {
    faceLoading.value = false
  }
}

// 关闭人脸识别
const handleExtractFaceCancel = () => {
  faceVisible.value = false
  currentImage.value = null
}

// 搜索相似人脸
const handleSearchSimilarFaces = async (image: BeautyImage) => {
  currentImage.value = image
  similarFacesVisible.value = true
  similarFacesLoading.value = true
  similarFacesError.value = ''
  similarFacesResults.value = []
  
  try {
    // 调用相似人脸搜索API
    const response = await searchSimilarFaces(image.url)
    if (response && response.data && response.data.results) {
      similarFacesResults.value = response.data.results
      console.log('相似人脸搜索结果:', similarFacesResults.value)
    } else {
      similarFacesError.value = '未能获取相似人脸搜索结果'
    }
  } catch (error) {
    console.error('相似人脸搜索失败:', error)
    similarFacesError.value = error instanceof Error ? error.message : '相似人脸搜索失败，请稍后重试'
    message.error(similarFacesError.value)
  } finally {
    similarFacesLoading.value = false
  }
}

// 关闭相似人脸搜索
const handleSimilarFacesCancel = () => {
  similarFacesVisible.value = false
  currentImage.value = null
}


// 处理AI修图
const handleAiEdit = () => {
  aiModalVisible.value = true
}

// 处理背景移除
const handleBgRemove = () => {
  bgRemoveModalVisible.value = true
}

// 关闭AI修图浮层
const handleAiModalClose = () => {
  aiModalVisible.value = false
}

// 关闭背景移除浮层
const handleBgRemoveModalClose = () => {
  bgRemoveModalVisible.value = false
}

// 打开EXIF信息浮层
const handleViewExif = (image: BeautyImage, event?: Event) => {
  if (event) {
    event.stopPropagation()
  }
  currentImage.value = image
  exifModalVisible.value = true
}

// 关闭EXIF信息浮层
const handleExifModalClose = () => {
  exifModalVisible.value = false
}

// 搜索处理
const handleSearch = (value: string) => {
  console.log('搜索:', value)
}

onMounted(() => {
  fetchImageList()
})

// 监听路由参数变化，当refer_id改变时重新加载数据
watch(() => route.params.refer_id, async (newReferId, oldReferId) => {
  if (newReferId !== oldReferId) {
    console.log('路由参数变化:', oldReferId, '->', newReferId)
    // 重置分页
    currentPage.value = 1
    // 重新加载数据
    await fetchImageList()
  }
}, { immediate: false })

// 下载状态
const downloading = ref(false)

// 处理图片下载
const handleDownload = async (size?: string) => {
  if (!currentImage.value) return
  
  try {
    downloading.value = true
    let downloadUrl = currentImage.value.url
    
    // 根据选择的尺寸获取对应的URL
    if (size) {
      const sizesMap = {
        small: '640x426',
        medium: '1920x1280',
        large: '2400x1600',
        original: '6000x4000'
      }
      downloadUrl = `${currentImage.value.url}?size=${sizesMap[size]}`
    }
    
    const response = await fetch(downloadUrl)
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = currentImage.value.title || 'image'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('下载图片失败:', error)
  } finally {
    downloading.value = false
  }
}

// 处理分享功能
const handleShare = async (platform: string) => {
  if (!currentImage.value) return

  const shareUrl = encodeURIComponent(window.location.href)
  const title = encodeURIComponent(currentImage.value.title || '分享图片')
  const imageUrl = encodeURIComponent(currentImage.value.url)

  const platformUrls = {
    wechat: `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${shareUrl}`,
    weibo: `http://service.weibo.com/share/share.php?url=${shareUrl}&title=${title}&pic=${imageUrl}`,
    douyin: `https://www.douyin.com/share/video?url=${shareUrl}&title=${title}`,
    xiaohongshu: `https://www.xiaohongshu.com/discovery/item?url=${shareUrl}`,
    copyLink: shareUrl
  }

  try {
    if (platform === 'copyLink') {
      await navigator.clipboard.writeText(decodeURIComponent(shareUrl))
      ElMessage.success('链接已复制到剪贴板')
    } else {
      window.open(platformUrls[platform], '_blank')
    }
  } catch (error) {
    console.error('分享失败:', error)
    ElMessage.error('分享失败，请稍后重试')
  }
}
</script>

<template>
  <Layout class="album-layout">
    <HeroSearch @search="handleSearch" />

    <div class="main-content">
      <!-- 图片瀑布流区域 -->
      <section class="waterfall-section">
        <div class="waterfall-container">
          <div
            v-for="image in imageList"
            :key="image.id"
            class="waterfall-item"
          >
            <div class="image-wrapper">
              <img :src="image.url" :alt="image.title" />
              <div class="image-overlay">
                <div class="overlay-buttons">
                  <a-button type="primary" class="overlay-button" @click="handlePreview(image)">
                    <EyeOutlined />
                    预览
                  </a-button>
                  <a-button type="primary" class="overlay-button exif-button" @click="(e) => handleViewExif(image, e)">
                    <CameraOutlined />
                    EXIF信息
                  </a-button>
                  <a-button type="primary" class="overlay-button" @click="handleExtractFace(image)">
                    <ScanOutlined />
                    识别人脸
                  </a-button>
                  <a-button type="primary" class="overlay-button" @click="handleSearchSimilarFaces(image)">
                    <SearchOutlined />
                    相似人脸
                  </a-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 分页组件 -->
      <div class="pagination-wrapper">
        <a-pagination
          v-model:current="currentPage"
          :total="total"
          :pageSize="pageSize"
          @change="handlePageChange"
          show-quick-jumper
          show-size-changer
          :pageSizeOptions="['10', '20', '50', '100']"
          @showSizeChange="handleSizeChange"
        />
      </div>

      <!-- 图片预览浮层 -->
      <Modal
        v-model:visible="previewVisible"
        :footer="null"
        @cancel="handleCancel"
        class="preview-modal"
        :width="'90%'"
      >
        <div class="preview-container" v-if="currentImage">
          <div class="preview-actions">
            <a-button class="action-button" @click="handleBgRemove">
              <DeleteOutlined />
              移除背景
            </a-button>
            <a-button class="action-button" @click="handleAiEdit">
              <EditOutlined />
              AI修图
            </a-button>
          </div>
          <div class="preview-image-container">
            <img :src="currentImage.url" :alt="currentImage.title" />
          </div>
          <div class="preview-info-container">
            <div class="owner-info">
              <img class="owner-avatar" :src="currentImage.owner?.avatar || '/static/def/a1.png'" :alt="currentImage.owner?.name" />
              <span class="owner-name">{{ currentImage.owner?.name || '未知用户' }}</span>
            </div>
            <div class="image-stats">
              <div class="stat-item">
                <EyeOutlined class="stat-icon" />
                <span>{{ currentImage.views || 0 }} 次浏览</span>
              </div>
              <div class="stat-item">
                <DownloadOutlined class="stat-icon" />
                <span>{{ currentImage.downloads || 0 }} 次下载</span>
              </div>
            </div>
            <div class="image-metadata">
              <div class="metadata-item">
                <div class="metadata-label">地理位置</div>
                <div>{{ currentImage.location || '未知' }}</div>
              </div>
              <div class="metadata-item">
                <div class="metadata-label">发布时间</div>
                <div>{{ currentImage.publishTime || '未知' }}</div>
              </div>
              <div class="metadata-item">
                <div class="metadata-label">拍摄设备</div>
                <div>{{ currentImage.device || '未知' }}</div>
              </div>
            </div>
            <div class="action-buttons">
              <div class="download-group">
                <a-button type="primary" class="main-download-button" @click="handleDownload('medium')">
                  <DownloadOutlined />
                  免费下载
                </a-button>
                <a-dropdown class="download-dropdown">
                  <a-button class="size-select-button">
                    <DownOutlined />
                  </a-button>
                  <template #overlay>
                    <a-menu>
                      <a-menu-item key="small" @click="handleDownload('small')">小 (640x426)</a-menu-item>
                      <a-menu-item key="medium" @click="handleDownload('medium')">中 (1920x1280)</a-menu-item>
                      <a-menu-item key="large" @click="handleDownload('large')">大 (2400x1600)</a-menu-item>
                      <a-menu-item key="original" @click="handleDownload('original')">原始大小 (6000x4000)</a-menu-item>
                    </a-menu>
                  </template>
                </a-dropdown>
              </div>
              <a-button class="action-button">
                <HeartOutlined />
                喜欢
              </a-button>
              <a-button class="action-button">
                <PlusOutlined />
                添加到相册
              </a-button>
              <a-dropdown class="share-dropdown">
                <a-button class="action-button">
                  <ShareAltOutlined />
                  分享
                </a-button>
                <template #overlay>
                  <a-menu>
                    <a-menu-item key="wechat" @click="handleShare('wechat')">微信朋友圈</a-menu-item>
                    <a-menu-item key="weibo" @click="handleShare('weibo')">微博</a-menu-item>
                    <a-menu-item key="douyin" @click="handleShare('douyin')">抖音</a-menu-item>
                    <a-menu-item key="xiaohongshu" @click="handleShare('xiaohongshu')">小红书</a-menu-item>
                    <a-menu-item key="copyLink" @click="handleShare('copyLink')">复制链接</a-menu-item>
                  </a-menu>
                </template>
              </a-dropdown>
            </div>
          </div>
        </div>
      </Modal>

      <!-- 人脸识别浮层 -->
      <Modal
        v-model:visible="faceVisible"
        title="人脸识别"
        :footer="null"
        @cancel="handleExtractFaceCancel"
        class="preview-modal"
        :width="'90%'"
      >
        <div class="face-recognition-content">
          <div v-if="faceLoading" class="loading-container">
            <div class="loading-spinner"></div>
            <p>正在识别人脸，请稍候...</p>
          </div>
          
          <div v-else-if="faceError" class="error-container">
            <p class="error-message">{{ faceError }}</p>
          </div>
          
          <div v-else-if="faceResult" class="result-container">
            <div class="image-container">
              <div class="original-image">
                <h3>原始图片</h3>
                <img :src="currentImage?.url" alt="原始图片" />
              </div>
              
              <div class="face-image">
                <h3>检测到的人脸</h3>
                <img :src="faceResult.face_path" alt="人脸图片" />
              </div>
            </div>
            
            <div class="metadata-container">
              <h3>人脸位置信息</h3>
              <p>上: {{ faceResult.face_location[0] }}px</p>
              <p>右: {{ faceResult.face_location[1] }}px</p>
              <p>下: {{ faceResult.face_location[2] }}px</p>
              <p>左: {{ faceResult.face_location[3] }}px</p>
              
              <h3>元数据信息</h3>
              <div v-if="faceResult.metadata && Object.keys(faceResult.metadata).length > 0">
                <div v-for="(value, key) in faceResult.metadata" :key="key" class="metadata-item">
                  <strong>{{ key }}:</strong> {{ value }}
                </div>
              </div>
              <p v-else>无可用元数据</p>
            </div>
          </div>
          
          <div v-else class="empty-container">
            <p>未检测到人脸信息</p>
          </div>
        </div>
      </Modal>

      <!-- AI修图提示浮层 -->
      <Modal
        v-model:visible="aiModalVisible"
        title="AI修图"
        @cancel="handleAiModalClose"
        :footer="null"
        width="600px"
      >
        <div class="feature-modal-content">
          <video class="feature-video" autoplay loop muted>
            <source src="../../assets/tooltip-animation-compressed.mp4" type="video/mp4">
          </video>
          <div class="feature-description">
            <h3>使用无限AI计划轻松修改和生成图片</h3>
            <p>新增、取代或移除图片中的某些部分，设计师品质的编辑工具帮助您轻松实现创意。</p>
          </div>
        </div>
      </Modal>

      <!-- 背景移除提示浮层 -->
      <Modal
        v-model:visible="bgRemoveModalVisible"
        title="移除背景"
        @cancel="handleBgRemoveModalClose"
        :footer="null"
        width="600px"
      >
        <div class="feature-modal-content">
          <video class="feature-video" autoplay loop muted>
            <source src="../../assets/background-removal-tooltip.mp4" type="video/mp4">
          </video>
          <div class="feature-description">
            <h3>一键移除任何图片背景</h3>
            <p>使用我们的AI技术，只需点击一下即可完美移除图片背景，无需复杂的手动操作。</p>
          </div>
        </div>
      </Modal>
      
      <!-- EXIF信息浮层 -->
      <ExifInfoModal
        v-model:visible="exifModalVisible"
        :imageUrl="currentImage?.url || ''"
        :imageTitle="currentImage?.title"
        @close="handleExifModalClose"
      />
      
      <!-- 相似人脸搜索浮层 -->
      <Modal
        v-model:visible="similarFacesVisible"
        title="相似人脸搜索"
        :footer="null"
        @cancel="handleSimilarFacesCancel"
        class="preview-modal"
        :width="'90%'"
      >
        <div class="face-recognition-content">
          <div v-if="similarFacesLoading" class="loading-container">
            <div class="loading-spinner"></div>
            <p>正在搜索相似人脸，请稍候...</p>
          </div>
          
          <div v-else-if="similarFacesError" class="error-container">
            <p class="error-message">{{ similarFacesError }}</p>
          </div>
          
          <div v-else-if="similarFacesResults.length > 0" class="result-container">
            <div class="original-image-container">
              <h3>原始图片</h3>
              <img :src="currentImage?.url" alt="原始图片" class="original-image" />
            </div>
            
            <h3>相似人脸结果 ({{ similarFacesResults.length }})</h3>
            <div class="similar-faces-grid">
              <div v-for="(result, index) in similarFacesResults" :key="index" class="similar-face-item">
                <div class="similar-face-image">
                  <img :src="result.face_path" alt="相似人脸" />
                </div>
                <div class="similar-face-info">
                  <p class="similarity-score">余弦距离: {{ (result.cosine_distance) }}</p>
                  <p class="similarity-score">相似度: {{ (result.cosine_similarity * 100).toFixed(2) }}%</p>
                  <a-button type="primary" size="small" @click="handlePreview({url: result.image_path, id: index, title: '相似图片'})">
                    <EyeOutlined />
                    查看原图
                  </a-button>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="empty-container">
            <p>未找到相似人脸</p>
          </div>
        </div>
      </Modal>

      <!-- 底部通用内容 -->
      <section class="footer-section">
        <div class="footer-content">
          <!-- 底部内容 -->
        </div>
      </section>
    </div>
  </Layout>
</template>

<style scoped>
.album-layout {
  min-height: 100vh;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 人脸识别浮层样式 */
.face-recognition-content {
  padding: 20px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid #1890ff;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.error-message {
  color: #ff4d4f;
  font-size: 16px;
}

.result-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.image-container {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
}

.original-image, .face-image {
  flex: 1;
  min-width: 300px;
}

.original-image img, .face-image img {
  max-width: 100%;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.metadata-container {
  background-color: #f9f9f9;
  padding: 16px;
  border-radius: 4px;
  border: 1px solid #e8e8e8;
}

.metadata-item {
  margin-bottom: 8px;
  line-height: 1.5;
}

.empty-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #999;
  font-size: 16px;
}

.ad-section {
  margin-bottom: 40px;
}

.waterfall-section {
  margin: 40px 0;
}

.waterfall-container {
  column-count: 4;
  column-gap: 20px;
}

@media (max-width: 1200px) {
  .waterfall-container {
    column-count: 3;
  }
}

@media (max-width: 768px) {
  .waterfall-container {
    column-count: 2;
  }
}

@media (max-width: 480px) {
  .waterfall-container {
    column-count: 1;
  }
}

.waterfall-item {
  break-inside: avoid;
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s ease;
}

.waterfall-item:hover {
  transform: translateY(-5px);
}

.image-wrapper {
  position: relative;
  overflow: hidden;
  border-radius: 8px;
}

.waterfall-item img {
  width: 100%;
  height: auto;
  display: block;
  transition: transform 0.3s ease;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-wrapper:hover .image-overlay {
  opacity: 1;
}

.overlay-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
}

.overlay-button {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.overlay-button .anticon {
  margin-right: 4px;
}

.exif-button {
  background-color: #1ABC9C;
  border-color: #1ABC9C;
}

.exif-button:hover {
  background-color: #16a085;
  border-color: #16a085;
}

.preview-modal {
  top: 20px;
}

.preview-container {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  min-height: 200px;
  max-height: 80vh;
  padding: 20px;
  position: relative;
}

.preview-actions {
  position: absolute;
  top: 20px;
  left: 20px;
  display: flex;
  gap: 10px;
  z-index: 1;
}

.feature-modal-content {
  text-align: center;
}

.feature-video {
  width: 100%;
  max-width: 500px;
  margin-bottom: 20px;
  border-radius: 8px;
}

.feature-description {
  text-align: left;
  padding: 0 20px;
}

.feature-description h3 {
  font-size: 18px;
  margin-bottom: 10px;
  color: #333;
}

.feature-description p {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}

/* 相似人脸搜索样式 */
.original-image-container {
  margin-bottom: 20px;
}

.original-image-container img {
  max-width: 300px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.similar-faces-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 16px;
}

.similar-face-item {
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.similar-face-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.similar-face-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.similar-face-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.similar-face-info {
  padding: 10px;
  background-color: #f9f9f9;
}

.similarity-score {
  font-weight: bold;
  margin-bottom: 8px;
  color: #1890ff;
}

.preview-image-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.preview-image-container img {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
}

.preview-info-container {
  width: 300px;
  margin-left: 24px;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.owner-info {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.owner-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  margin-right: 12px;
}

.owner-name {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.image-stats {
  margin-bottom: 24px;
}

.stat-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  color: #666;
}

.stat-icon {
  margin-right: 8px;
}

.image-metadata {
  margin-bottom: 24px;
}

.metadata-item {
  margin-bottom: 12px;
  color: #666;
}

.metadata-label {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.download-dropdown {
  width: 100%;
}

.action-button {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-button .anticon {
  margin-right: 8px;
}
.preview-actions {
  margin-top: 16px;
  text-align: center;
}
.preview-container img {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin: 40px 0;
}

.footer-section {
  margin-top: 60px;
  padding: 40px 0;
  background: #f5f5f5;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}
.download-group {
  display: flex;
  gap: 4px;
  width: 100%;
}

.main-download-button {
  flex: 1;
}

.size-select-button {
  min-width: 32px;
  padding: 4px 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.download-dropdown {
  width: auto;
}
</style>