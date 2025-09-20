<script setup lang="ts">
import { ref, computed } from 'vue'
import { Card } from 'ant-design-vue'

interface ImageItem {
  id: number
  url: string
  title?: string
  description?: string
}

interface Props {
  backgroundImage?: string
  images: ImageItem[]
  layout?: 'horizontal' | 'vertical' | 'grid'
  animationDelay?: number
  animationClass?: string
  cardStyle?: 'square' | 'round'
  aspectRatio?: '1:1' | '3:2' | '16:9' | '3.5:1' | string
}

const props = withDefaults(defineProps<Props>(), {
  layout: 'horizontal',
  animationDelay: 200,
  animationClass: 'slide-in',
  cardStyle: 'round',
  aspectRatio: '3.5:1'
})

// 计算宽高比
const getAspectRatioValue = computed(() => {
  const ratio = props.aspectRatio;
  if (ratio.includes(':')) {
    const [width, height] = ratio.split(':').map(Number);
    return width / height;
  }
  return Number(ratio);
});

// 模拟数据
const mockImages = ref<ImageItem[]>([
  {
    id: 1,
    url: '/static/def/a1.png',
    title: '蒙奇·D·路飞',
    description: '海贼王主角'
  },
  {
    id: 2,
    url: '/static/def/a2.png',
    title: '罗罗诺亚·索隆',
    description: '三刀流剑士'
  },
  {
    id: 3,
    url: '/static/def/a3.png',
    title: '文斯莫克·山治',
    description: '厨师'
  },
  {
    id: 4,
    url: '/static/def/a4.png',
    title: '文斯莫克·山治',
    description: '厨师'
  },
  {
    id: 5,
    url: '/static/def/a5.png',
    title: '文斯莫克·山治',
    description: '厨师'
  }
])

const containerClass = computed(() => ({
  'image-gallery': true,
  [`layout-${props.layout}`]: true
}))

const imageClass = computed(() => (index: number) => ({
  'gallery-item': true,
  'animate-in': true,
  [`delay-${index}`]: true,
  [props.cardStyle === 'square' ? 'square-card' : 'round-card']: true,
  [props.animationClass]: true
}))
</script>

<template>
  <div class="image-gallery-container">
    <div v-if="props.backgroundImage" class="background-image" :style="{ backgroundImage: `url(${props.backgroundImage})` }" />
    <div :class="containerClass">
      <Card v-for="(image, index) in (props.images.length ? props.images : mockImages)" 
            :key="image.id"
            :class="imageClass(index)"
            hoverable>
        <div class="image-content">
          <img :src="image.url" :alt="image.title">
          <div v-if="image.title || image.description" class="image-info">
            <h3 v-if="image.title">{{ image.title }}</h3>
            <p v-if="image.description">{{ image.description }}</p>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.image-gallery-container {
  position: relative;
  height: auto; /* calc(100vh - 64px) ;*/ /* 修改为自动高度 */
  overflow: hidden;
  background-color: #f5f5f5; /* 增加浅灰色背景 */
  display: flex;
  justify-content: center; /* 居中卡片组 */
  align-items: center; /* 居中卡片组 */
}

.background-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  opacity: 0.15;
  z-index: 0;
}

.image-gallery {
  position: relative;
  z-index: 1;
  display: flex;
  gap: 10px; /* 缩小图片间距 */
  padding: 10px; /* 缩小内边距 */
  overflow-x: hidden; /* 避免水平滚动条 */
  overflow-y: hidden; /* 避免水平滚动条 */
}

.layout-horizontal {
  flex-direction: row;
  flex-wrap: nowrap;
  overflow-x: auto;
}

.layout-vertical {
  flex-direction: column;
  align-items: center;
}

.layout-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 10px; /* 缩小网格间距 */
}

.gallery-item {
  flex: 0 0 auto;
  width: 250px;
  opacity: 0;
  transform: translateY(50px);
  border: 2px solid #333;
  box-sizing: border-box;
  aspect-ratio: v-bind(getAspectRatioValue);
  overflow: hidden;
  display: flex;
  align-items: stretch;
  justify-content: stretch;
}

.square-card {
  border-radius: 0;
  border-width: 4px;
}

.round-card {
  border-radius: 10px;
  border-width: 3px;
}

.image-content {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.image-content img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
  flex: 1;
  min-height: 0;
}

.image-content:hover img {
  transform: scale(1.05);
}

.image-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 15px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  color: white;
}

.image-info h3 {
  margin: 0;
  font-size: 1.2em;
}

.image-info p {
  margin: 5px 0 0;
  font-size: 0.9em;
  opacity: 0.8;
}

/* 动画效果 */
.animate-in {
  animation: slideIn 0.6s ease forwards;
}

.slide-in {
  animation: slideIn 0.6s ease forwards;
}

.fade-in {
  animation: fadeIn 0.6s ease forwards;
}

.zoom-in {
  animation: zoomIn 0.6s ease forwards;
}

.rotate-in {
  animation: rotateIn 0.6s ease forwards;
}

.bounce-in {
  animation: bounceIn 0.6s ease forwards;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes zoomIn {
  from {
    opacity: 0;
    transform: scale(0.5);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes rotateIn {
  from {
    opacity: 0;
    transform: rotate(-180deg);
  }
  to {
    opacity: 1;
    transform: rotate(0deg);
  }
}

@keyframes bounceIn {
  from {
    opacity: 0;
    transform: scale(0.5) translateY(100px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* 延迟动画 */
.delay-0 { animation-delay: 0s; }
.delay-1 { animation-delay: 0.2s; }
.delay-2 { animation-delay: 0.4s; }
.delay-3 { animation-delay: 0.6s; }
.delay-4 { animation-delay: 0.8s; }
</style>