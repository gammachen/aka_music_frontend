<template>
  <div>
    <div class="hero-section">
      <div class="hero-content">
        <h1>{{ title }}</h1>
        <p>{{ description }}</p>
        <div class="search-box">
          <div class="search-container">
            <Input.Search
              v-model:value="searchValue"
              :placeholder="placeholder"
              size="large"
              enterButton
              @search="onSearch"
              style="width: calc(100vw - 120px)"
            />
            <Button
              type="primary"
              size="large"
              @click="handleFlyClick"
              class="fly-button"
            >
              玩的飞起
            </Button>
          </div>
        </div>
      </div>
    </div>
    <div v-for="(images, index) in filteredGalleries" :key="`gallery-${index}`" class="gallery-section">
      <div class="gallery-header">
        <h2 class="gallery-title">{{ images.animation_class }} {{images.layout}} {{images.ratio}} {{images.card_style}} {{images.animation_delay}}</h2>
      </div>
      <ImageGallery 
        :images="images.images" 
        :animation-class="images.animation_class" 
        :layout="images.layout" 
        :aspectRatio="images.ratio"
        :cardStyle="images.card_style"
        :animationDelay=images.animation_delay
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Input, Button, message } from 'ant-design-vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/index'
import ImageGallery from './ImageGallery.vue'
import { searchImages } from '../api/draw'

interface Props {
  title?: string
  description?: string
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '发现高品质资源',
  description: '探索、分享和下载来自世界各地的优质资源',
  placeholder: '搜索音乐、艺人或专辑'
})

const router = useRouter()
const userStore = useUserStore()
const searchValue = ref('')
const multiImages = ref<Array<Array<any>>>([]) // 存储多组图片数据
const showGalleries = ref<Array<boolean>>([]) // 控制每个gallery的显示状态

// 计算属性：过滤显示的图片组
const filteredGalleries = computed(() => {
  return multiImages.value.filter((_, index) => showGalleries.value[index])
})

const emit = defineEmits<{
  (e: 'search', value: string): void
  (e: 'showGallery', value: string): void
}>()

const onSearch = (value: string) => {
  searchValue.value = value
  emit('search', value)
}

const handleFlyClick = async () => {
  if (!userStore.userInfo) {
    message.warning('请先登录后再体验')
    router.push('/login')
    return
  }

  if (!searchValue.value) {
    message.warning('请输入搜索内容')
    return
  }

  try {
    const result = await searchImages({
      query: searchValue.value,
      ratios: ['9:16']
    })

    console.log('搜索结果:', result)

    if (result?.data?.results?.length > 0) {
      // 处理每组搜索结果
      multiImages.value = result.data.results.map((resultItem: any, index: number) => {
        console.log('处理结果项:', resultItem)
        // 将image_paths转换为图片数组，并添加布局相关属性
        const images = resultItem.image_paths.map((imagePath: string, imgIndex: number) => ({
          id: imgIndex + 1,
          url: imagePath,
          title: `${resultItem.keyword} - ${imgIndex + 1}`,
          description: `比例: ${resultItem.ratio}, 推荐像素: ${resultItem.recommended_pixel}`
        }))
        
        // 为整个图片数组添加布局属性
        console.log('处理图片数组:', images)
        console.log('animation_class:', resultItem.animation_class)
        console.log('layout:', resultItem.layout)
        console.log('ratio:', resultItem.ratio)
        console.log('cardStyle:', resultItem.card_style)

        return {
          images: images,
          animation_class: resultItem.animation_class || 'fade-in',
          layout: resultItem.layout || 'horizontal',
          ratio: resultItem.ratio || '1:1',
          card_style: resultItem.card_style || 'square',
          animation_delay: index * 5000 // 根据索引添加递增的延迟时间 `${index * 5000}`
        }
      })
      
      console.log('最终图片数组:', multiImages.value)
      // 更新gallery显示状态
      showGalleries.value = new Array(multiImages.value.length).fill(true)
      console.log('Gallery显示状态:', showGalleries.value)
      emit('showGallery', searchValue.value)
    } else {
      message.warning('未找到相关图片，请尝试其他关键词')
    }
  } catch (error) {
    console.error('搜索服务出错:', error)
    message.error('搜索服务暂时不可用，请稍后再试')
  }
}
</script>

<style scoped>
.hero-section {
  background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('/img/def/hero-bg.jpg');
  background-size: cover;
  background-position: center;
  padding: 60px 0;
  text-align: center;
  color: #fff;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

.hero-content h1 {
  font-size: 2.5em;
  margin-bottom: 20px;
  color: #fff;
}

.hero-content p {
  font-size: 1.2em;
  margin-bottom: 30px;
  color: #fff;
}

.search-box {
  max-width: 500px;
  margin: 0 auto;
}

.search-container {
  display: flex;
  gap: 10px;
  align-items: center;
}

.fly-button {
  white-space: nowrap;
}

.gallery-section {
  margin-top: 5px;
  padding: 20px;
  background: rgba(19, 18, 18, 0.1);
  border-radius: 8px;
  max-width: 1800px;
  margin-left: auto;
  margin-right: auto;
  position: relative;
  z-index: 1;
  min-height: 0; /* 移除最小高度限制 */
  height: auto; /* 自动调整高度 */
}
</style>