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
    <div class="gallery-section" v-if="showGallery1">
      <ImageGallery :images="images" :animation-class="'rotate-in'" layout="horizontal" aspectRatio="1:1"/>
    </div>
    <div class="gallery-section" v-if="showGallery2">
      <ImageGallery :images="images2" :animation-class="'slide-in'" :layout="'horizontal'" card-style="square" aspectRatio="3:4"/>
    </div>
    <div class="gallery-section" v-if="showGallery3">
      <ImageGallery :images="images3" :animation-class="'zoom-in'" :layout="'horizontal'" aspectRatio="2:3"/>
    </div>
    <div class="gallery-section" v-if="showGallery4">
      <ImageGallery :images="images3" :animation-class="'zoom-in'" :layout="'horizontal'" aspectRatio="9:16"/>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Input, Button, message } from 'ant-design-vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/index'
import ImageGallery from './ImageGallery.vue'

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
const showGallery1 = ref(false)
const showGallery2 = ref(false)
const showGallery3 = ref(false)
const showGallery4 = ref(false)
const images = ref([
  {
    id: 1,
    url: '/static/def/m1.webp',
    title: '蒙奇·D·路飞',
    description: '海贼王主角'
  },
  {
    id: 2,
    url: '/static/def/m2.webp',
    title: '罗罗诺亚·索隆',
    description: '三刀流剑士'
  },
  {
    id: 3,
    url: '/static/def/m3.webp',
    title: '文斯莫克·山治',
    description: '厨师'
  },
  {
    id: 4,
    url: '/static/def/m4.webp',
    title: '文斯莫克·山治',
    description: '厨师'
  }
])

const images2 = ref([
  {
    id: 1,
    url: '/static/def/m41.webp',
    title: '蒙奇·D·路飞',
    description: '海贼王主角'
  },
  {
    id: 4,
    url: '/static/def/m44.webp',
    title: '文斯莫克·山治',
    description: '厨师'
  },
  {
    id: 5,
    url: '/static/def/m45.webp',
    title: '文斯莫克·山治',
    description: '厨师'
  },
  {
    id: 6,
    url: '/static/def/m46.webp',
    title: '文斯莫克·山治',
    description: '厨师'
  }
])

const images3 = ref([
  {
    id: 1,
    url: '/static/def/m11.webp',
    title: '蒙奇·D·路飞',
    description: '海贼王主角'
  },
  {
    id: 2,
    url: '/static/def/m12.webp',
    title: '罗罗诺亚·索隆',
    description: '三刀流剑士'
  },
  {
    id: 3,
    url: '/static/def/m13.webp',
    title: '文斯莫克·山治',
    description: '厨师'
  },
  {
    id: 4,
    url: '/static/def/m14.webp',
    title: '文斯莫克·山治',
    description: '厨师'
  },
  {
    id: 5,
    url: '/static/def/m15.webp',
    title: '文斯莫克·山治',
    description: '厨师'
  },
  {
    id: 6,
    url: '/static/def/m16.webp',
    title: '文斯莫克·山治',
    description: '厨师'
  },
  {
    id: 7,
    url: '/static/def/m16.webp',
    title: '文斯莫克·山治',
    description: '厨师'
  }
])

const emit = defineEmits<{
  (e: 'search', value: string): void
  (e: 'showGallery', value: string): void
}>()

const onSearch = (value: string) => {
  searchValue.value = value
  emit('search', value)
}

const handleFlyClick = () => {
  if (!userStore.userInfo) {
    message.warning('请先登录后再体验')
    router.push('/login')
    return
  }

  if (!searchValue.value) {
    message.warning('请输入搜索内容')
    return
  }

  showGallery1.value = true
  showGallery2.value = true
  showGallery3.value = true
  showGallery4.value = true
  emit('showGallery', searchValue.value)
}
</script>

<style scoped>
.hero-section {
  background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('/static/def/images/hero-bg.jpg');
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