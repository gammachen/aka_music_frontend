<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { Card, Button, message } from 'ant-design-vue'
import { DownloadOutlined, RedoOutlined } from '@ant-design/icons-vue'
import html2canvas from 'html2canvas'
import GIF from 'gif.js'

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
  cardStyle?: 'square' | 'round' | 'circle' | 'custom'
  aspectRatio?: '1:1' | '3:2' | '16:9' | '3.5:1' | string
}

const props = withDefaults(defineProps<Props>(), {
  backgroundImage: '/static/covers/a6.png',
  layout: 'horizontal',
  animationDelay: 500,
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

// 控制动画状态和临时数组状态
const animationEnabled = ref(true)
const tempImages = ref<ImageItem[]>([])

// 更新所有使用这些状态的地方
const imageClass = computed(() => (index: number) => ({
  'gallery-item': true,
  [`${props.cardStyle}-card`]: props.cardStyle,
  [props.animationClass]: animationEnabled.value,
  [`delay-${index}`]: animationEnabled.value
}))

const replayAnimation = async () => {
  try {
    // 先禁用动画
    animationEnabled.value = false
    
    // 等待DOM更新完成
    await nextTick()
    
    // 重置数据
    tempImages.value = []
    
    // 添加一个小延时确保DOM完全更新
    await new Promise(resolve => setTimeout(resolve, 50))
    
    // 再次等待DOM更新
    await nextTick()
    
    const sourceImages = props.images.length ? props.images : mockImages.value
    if (!Array.isArray(sourceImages)) {
      console.error('源数组不是有效的数组:', sourceImages)
      return
    }
    
    // 重新启用动画
    animationEnabled.value = true
    
    // 重新设置数据
    tempImages.value = sourceImages.map(img => ({
      id: img.id,
      url: img.url,
      title: img.title,
      description: img.description
    }))
  } catch (error) {
    console.error('重置动画时发生错误:', error)
  }
}

// 下载状态
const downloading = ref(false)
const progress = ref(0)

const galleryRef = ref(null)

// 导出为GIF
const exportToGif = async () => {
  try {
    downloading.value = true
    progress.value = 0
    
    const gallery = galleryRef.value
    if (!gallery) return

    let animationCount = 0
    const maxAnimations = 3 // 动画重复次数

    // 通过重新赋值数据来触发动画重置
    const resetAndPlayAnimation = async () => {
      // 先清空数组触发移除
      tempImages.value = []
      // 等待DOM更新
      await nextTick()
      // 重新赋值
      tempImages.value = props.images.length ? [...props.images] : [...mockImages.value]
    }

    const gif = new GIF({
      workers: 2,
      quality: 10,
      width: gallery.clientWidth,
      height: gallery.clientHeight,
      workerScript: '/gif.worker.js'
    })

    // 计算动画总时长（基础动画时长 + 最大延迟时间）
    const baseAnimationDuration = 600 // slideIn动画持续600ms
    const imagesLength = props.images.length || mockImages.value.length
    const maxDelay = (imagesLength - 1) * props.animationDelay
    const totalDuration = baseAnimationDuration + maxDelay

    // 捕获动画帧
    const frames = 60 // 增加帧数以获得更流畅的效果
    const frameInterval = totalDuration / frames

    const captureFrame = async () => {
      const canvas = await html2canvas(gallery, {
        width: gallery.clientWidth,
        height: gallery.clientHeight,
        scale: 1,
        useCORS: true,
        logging: false
      });
      gif.addFrame(canvas, { delay: frameInterval, copy: true });
    };

    // 循环播放动画并捕获
    const captureAnimation = async () => {
      resetAndPlayAnimation();
      animationCount++;

      for (let i = 0; i < frames; i++) {
        progress.value = ((animationCount - 1) * frames + i) / (frames * maxAnimations) * 50;
        await new Promise(resolve => setTimeout(resolve, frameInterval));
        await captureFrame();
      }

      if (animationCount < maxAnimations) {
        await captureAnimation();
      } else {
        // 生成GIF
        gif.on('progress', p => {
          progress.value = 50 + p * 50;
        });

        gif.on('finished', blob => {
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'gallery-animation.gif';
          a.click();
          URL.revokeObjectURL(url);
          downloading.value = false;
          progress.value = 0;
          message.success('GIF导出成功！');
        });

        gif.render();
      }
    };

    await captureAnimation();
  } catch (error: any) {
    console.error('导出GIF失败:', error)
    message.error('导出失败，请重试')
    downloading.value = false
    progress.value = 0
  }
}
</script>

<template>
  <div class="image-gallery-container"><!-- :style="{ 'animation-delay': `${props.animationDelay}ms` }" -->
    <div v-if="props.backgroundImage" class="background-image" :style="{ backgroundImage: `url(${props.backgroundImage})` }" />
    <div :class="containerClass" ref="galleryRef">
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
    <div class="control-buttons">
      <Button 
        type="primary" 
        shape="circle"
        class="replay-button"
        @click="replayAnimation">
        <template #icon><RedoOutlined /></template>
      </Button>
<!--       暂时不要这个下载功能，没调整好，简直就是噩梦
      <Button 
        type="primary" 
        shape="circle" 
        :loading="downloading"
        :disabled="downloading"
        @click="exportToGif">
        <template #icon><DownloadOutlined /></template>
      </Button> -->
      <div v-if="downloading" class="progress-text">导出进度: {{ Math.round(progress) }}%</div>
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
  opacity: 0.95;
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
  /* border-radius: 10px;
  border-width: 3px; */
  border: none;
  border-radius: 0;
  margin: 0;
  padding: 0;
  box-shadow: none;
}

.nopadding-card {
  border: none;
  border-radius: 0;
  margin: 0;
  padding: 0;
  box-shadow: none;
}

.image-content {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center; /* 水平居中 */
  justify-content: center; /* 垂直居中 */
}

.image-content img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center; /* 确保图片居中裁剪 */
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
  animation: elasticIn 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards;
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

.elastic-in {
  animation: elasticIn 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards;
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

@keyframes elasticIn {
  0% {
    opacity: 0;
    transform: translateX(200px) scale(0.7);
  }
  70% {
    opacity: 0.7;
    transform: translateX(-15px) scale(1.05);
  }
  85% {
    opacity: 0.8;
    transform: translateX(10px) scale(0.95);
  }
  100% {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

/* 延迟动画 */
.delay-0 { animation-delay: 0s; }
.delay-1 { animation-delay: 0.2s; }
.delay-2 { animation-delay: 0.4s; }
.delay-3 { animation-delay: 0.6s; }
.delay-4 { animation-delay: 0.8s; }
</style>