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
    <!-- <div class="diagonal-line"></div> -->
    <Card class="pk-card left-card" hoverable>
      <div class="card-content">
        <div class="image-container">
          <img :src="leftImageData.image" :alt="leftImageData.name">
        </div>
        <div class="info-container">
          <h3 class="name">{{ leftImageData.name }}</h3>
          <p v-if="leftImageData.description" class="description">{{ leftImageData.description }}</p>
        </div>
      </div>
    </Card>
    <Card class="pk-card right-card" hoverable>
      <div class="card-content">
        <div class="image-container">
          <img :src="rightImageData.image" :alt="rightImageData.name">
        </div>
        <div class="info-container">
          <h3 class="name">{{ rightImageData.name }}</h3>
          <p v-if="rightImageData.description" class="description">{{ rightImageData.description }}</p>
        </div>
      </div>
    </Card>
  </div>
</template>

<style scoped>
.pk-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0;
  perspective: 1000px;
  gap: 0;
}

.diagonal-line {
  position: absolute;
  top: 0;
  left: 50%;
  width: 1px;
  height: 100%;
  background: linear-gradient(to bottom, rgba(255,255,255,0.2), rgba(255,255,255,0.4), rgba(255,255,255,0.2));
  transform: translateX(-50%);
  z-index: 2;
  box-shadow: 0 0 8px rgba(255,255,255,0.3);
}

.vs-badge {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 48px;
  font-weight: bold;
  color: rgba(255,255,255,0.9);
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  z-index: 10;
  animation: pulse 1.5s infinite;
}

.pk-card {
  width: 50%;
  transform-style: preserve-3d;
  transition: transform 0.3s ease;
  border: none;
  border-radius: 0;
  overflow: hidden;
}

.left-card {
  clip-path: polygon(0 0, 100% 0, 95% 100%, 0 100%);
}

.right-card {
  clip-path: polygon(5% 0, 100% 0, 100% 100%, 0 100%);
  margin-left: -20px;
}

.pk-card:hover {
  transform: translateZ(10px);
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.image-container {
  width: 200px;
  height: 200px;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 15px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.pk-card:hover .image-container img {
  transform: scale(1.1);
}

.info-container {
  text-align: center;
  width: 100%;
}

.name {
  font-size: 1.5em;
  font-weight: bold;
  margin: 0 0 10px;
  color: #333;
}

.description {
  font-size: 1em;
  color: #666;
  margin: 0;
  line-height: 1.4;
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