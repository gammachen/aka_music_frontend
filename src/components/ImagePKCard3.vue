<script setup lang="ts">
import { ref, computed } from 'vue'
import { Card } from 'ant-design-vue'

interface ImagePK {
  id: number
  name: string
  image: string
  description?: string
  backgroundColor?: string
}

interface Props {
  leftImage?: ImagePK
  rightImage?: ImagePK
  vsColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  vsColor: '#ff4d4f'
})

// 默认数据
const defaultLeftImage = ref<ImagePK>({
  id: 1,
  name: '罗宾',
  image: '/static/def/m41.webp',
  description: '花花果实',
  backgroundColor: '#3498db'
})

const defaultRightImage = ref<ImagePK>({
  id: 2,
  name: '索罗',
  image: '/static/def/m3.webp',
  description: '三刀流',
  backgroundColor: '#e74c3c'
})

const leftImageData = computed(() => props.leftImage || defaultLeftImage.value)
const rightImageData = computed(() => props.rightImage || defaultRightImage.value)
</script>

<template>
  <div class="pk-container">
    <div class="vs-badge">VS</div>
    <div class="pk-images-container">
      <div class="pk-image left-image">
        <img :src="leftImageData.image" :alt="leftImageData.name">
      </div>
      
      <div class="pk-image right-image">
        <img :src="rightImageData.image" :alt="rightImageData.name">
      </div>
      <div class="diagonal-line"></div>
    </div>
  </div>
</template>

<style scoped>
.pk-container {
  position: relative;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  perspective: 1000px;
}

.pk-images-container {
  position: relative;
  width: 100%;
  height: 400px;
  overflow: hidden;
  /* border-radius: 12px; */
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.pk-image {
  position: absolute;
  top: 0;
  width: 50%;
  height: 100%;
  overflow: hidden;
  transition: transform 0.3s ease;
}

.left-image {
  left: 0;
  clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%);
}

.right-image {
  right: 0;
  clip-path: polygon(15% 0, 100% 0, 100% 100%, 0 100%);
}

.pk-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.pk-image:hover img {
  transform: scale(1.1);
}

.diagonal-line {
  position: absolute;
  top: 0;
  left: 50%;
  width: 4px;
  height: 100%;
  background: linear-gradient(135deg, 
    rgba(255,255,255,0.8),
    rgba(255,255,255,0.3)
  );
  transform: translateX(-50%) rotate(15deg);
  z-index: 2;
  box-shadow: 0 0 15px rgba(255,255,255,0.6);
}

.vs-badge {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 48px;
  font-weight: bold;
  color: rgba(255,255,255,0.9);
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5),
             -2px -2px 4px rgba(0, 0, 0, 0.5);
  z-index: 10;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    transform: translate(-50%, -50%) scale(1.1);
  }
  100% {
    transform: translate(-50%, -50%) scale(1);
  }
}
</style>