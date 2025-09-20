<script setup lang="ts">
import { ref, computed } from 'vue'
import { Card } from 'ant-design-vue'

interface Character {
  id: number
  name: string
  image: string
  description?: string
  color?: string
}

interface Props {
  characters?: Character[]
}

const props = withDefaults(defineProps<Props>(), {
  characters: undefined
})

// Mock数据，作为兜底数据
const defaultCharacters = ref<Character[]>([
  {
    id: 1,
    name: '蒙奇·D·路飞',
    image: '/static/def/m41.webp',
    description: '草帽海贼团船长',
    color: '#3498db'
  },
  {
    id: 2,
    name: '罗罗诺亚·索隆',
    image: '/static/def/m3.webp',
    description: '草帽海贼团剑士',
    color: '#2ecc71'
  },
  {
    id: 3,
    name: '娜美',
    image: '/static/def/m4.webp',
    description: '草帽海贼团航海士',
    color: '#e74c3c'
  },
  {
    id: 4,
    name: '乌索普',
    image: '/static/def/m5.webp',
    description: '草帽海贼团狙击手',
    color: '#f1c40f'
  },
  {
    id: 5,
    name: '山治',
    image: '/static/def/a1.png',
    description: '草帽海贼团厨师',
    color: '#e67e22'
  }
])

// 使用计算属性来决定使用外部传入的characters还是默认的mock数据
const characters = computed(() => props.characters || defaultCharacters.value)
</script>

<template>
  <div class="character-gallery">
    <div class="gallery-container">
      <Card v-for="char in characters" 
            :key="char.id" 
            class="character-card"
            :style="{ '--card-color': char.color }">
        <div class="card-content">
          <div class="image-container">
            <img :src="char.image" :alt="char.name">
          </div>
          <div class="info-overlay">
            <h3>{{ char.name }}</h3>
            <p>{{ char.description }}</p>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.character-gallery {
  width: 100%;
  /* min-height: 100vh; */
  background: #1a1a1a;
  padding: 20px;
}

.gallery-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  max-width: 1200px;
  margin: 0 auto;
  padding-inline: inherit;
}

.character-card {
  position: relative;
  aspect-ratio: 9/26;
  border: 2px solid #333;
  overflow: hidden;
  transition: transform 0.3s ease;
  border-radius: 0;
  margin: -1px;
  padding: 0;
  background-color: #000;
}

:deep(.ant-card-body) {
  padding: 0;
  height: 100%;
}

.character-card:hover {
  transform: scale(1.05);
  z-index: 1;
}

.card-content {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.image-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.character-card:hover .image-container img {
  transform: scale(1.1);
}

.info-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  color: white;
  transform: translateY(100%);
  transition: transform 0.3s ease;
}

.character-card:hover .info-overlay {
  transform: translateY(0);
}

.info-overlay h3 {
  margin: 0;
  font-size: 1.2em;
  font-weight: bold;
}

.info-overlay p {
  margin: 5px 0 0;
  font-size: 0.9em;
  opacity: 0.8;
}
</style>