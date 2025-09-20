<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Card } from 'ant-design-vue'

interface ImageCard {
  id: number
  name: string
  image: string
  description?: string
  backgroundColor?: string
  video?: string
}

interface Props {
  images?: ImageCard[]
  expandDuration?: number
}

const props = withDefaults(defineProps<Props>(), {
  expandDuration: 1500 // 默认展开动画持续时间，单位为毫秒
})

// 默认数据
const defaultImages = ref<ImageCard[]>([
  {
    id: 1,
    name: 'Number1',
    image: '/static/def/jieba1.webp',
    description: '波动拳 Wave Movement Fist',
    backgroundColor: '#2ecc71'
  },
  {
    id: 2,
    name: '古烈',
    image: '/static/def/jieba5.webp',
    description: '报告指挥部，这里是小鹰1号',
    backgroundColor: '#3498db'
  },
  {
    id: 3,
    name: '春丽',
    image: '/static/def/jieba2.webp',
    description: '我做到啦 Supiningu Baado Kikku',
    backgroundColor: '#e74c3c',
    video: '/static/def/jieba_chunli.mp4'
  },
  {
    id: 4,
    name: '豪鬼',
    image: '/static/def/jieba4.webp',
    description: '黑暗波动能量',
    backgroundColor: '#9b59b6',
    video: '/static/def/jieba_haogui.mp4'
  },
  {
    id: 5,
    name: '桑吉尔夫',
    image: '/static/def/jieba6.webp',
    description: '我的力量是无可匹敌的!',
    backgroundColor: '#f1c40f'
  }
])

const images = computed(() => props.images || defaultImages.value)
const isExpanded = ref(false)
const centerIndex = Math.floor(images.value.length / 2)

const getCardStyle = (index: number) => {
  const totalCards = images.value.length
  const offset = index - centerIndex
  const baseRotation = 30 // 基础旋转角度
  const baseTranslate = 60 // 基础位移距离
  
  if (!isExpanded.value) {
    // 未展开状态，所有卡片叠在中间
    return {
      transform: `
        perspective(1000px)
        translateX(0)
        rotateY(0)
        scale(${index === centerIndex ? 1 : 0.8})
      `,
      opacity: index === centerIndex ? 1 : 0,
      zIndex: totalCards - Math.abs(offset),
      transition: `all ${props.expandDuration}ms ease`
    }
  }

  // 展开状态
  return {
    transform: `
      perspective(1000px)
      translateX(${offset * baseTranslate}%)
      rotateY(${-offset * baseRotation}deg)
      scale(${1 - Math.abs(offset) * 0.1})
    `,
    opacity: 1,
    zIndex: totalCards - Math.abs(offset),
    transition: `all ${props.expandDuration}ms ease`
  }
}

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}

const selectedVideo = ref<string | null>(null)
const showVideo = ref(false)

const handleCardClick = (image: ImageCard) => {
  if (image.video) {
    selectedVideo.value = image.video
    showVideo.value = true
  }
}

const closeVideo = () => {
  showVideo.value = false
  selectedVideo.value = null
}
</script>

<template>
  <div class="cards-container" @mouseenter="toggleExpand" @mouseleave="toggleExpand">
    <div v-for="(image, index) in images"
         :key="image.id"
         class="card"
         :style="getCardStyle(index)"
         @click="handleCardClick(image)">
      <div class="card-inner">
        <img :src="image.image" :alt="image.name">
        <div class="card-content">
          <h3>{{ image.name }}</h3>
          <p v-if="image.description">{{ image.description }}</p>
        </div>
        <div class="card-shine"></div>
        <!-- 添加播放按钮 -->
        <div v-if="image.video" class="play-button">
          <svg viewBox="0 0 24 24" width="48" height="48">
            <circle cx="12" cy="12" r="11" fill="rgba(255, 255, 255, 0.9)"/>
            <path d="M9.5 7.5v9l7-4.5-7-4.5z" fill="#333"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- 视频播放浮层 -->
    <div v-if="showVideo && selectedVideo" class="video-overlay" @click="closeVideo">
      <div class="video-container" @click.stop>
        <video controls autoplay>
          <source :src="selectedVideo" type="video/mp4">
        </video>
        <button class="close-button" @click="closeVideo">×</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cards-container {
  position: relative;
  width: 100%;
  max-width: 1200px;
  height: 400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  perspective: 2000px;
}

.card {
  position: absolute;
  width: 280px;
  height: 400px;
  transform-style: preserve-3d;
  cursor: pointer;
}

.card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.card-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
  color: white;
}

.card-content h3 {
  margin: 0 0 8px;
  font-size: 1.5em;
}

.card-content p {
  margin: 0;
  font-size: 0.9em;
  opacity: 0.8;
}

.card-shine {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.2) 50%,
    rgba(255, 255, 255, 0) 100%);
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.card:hover .card-shine {
  opacity: 1;
}

.card:hover img {
  transform: scale(1.1);
}

/* 播放按钮样式 */
.play-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: opacity 0.3s ease;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.card:hover .play-button {
  opacity: 1;
}

.video-container {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.video-container video {
  max-width: 100%;
  max-height: 80vh;
  border-radius: 8px;
}

.video-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.video-container {
  position: relative;
  width: 80%;
  max-width: 1200px;
}

.video-container video {
  width: 100%;
  border-radius: 8px;
}

.close-button {
  position: absolute;
  top: -40px;
  right: -40px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: white;
  border: none;
  color: #333;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s;
}

.close-button:hover {
  background-color: #f0f0f0;
}
</style>