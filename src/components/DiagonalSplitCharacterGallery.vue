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
  characters: () => []
})

// 默认数据
const characters = ref<Character[]>([
  {
    id: 1,
    name: 'Didi s Day',
    image: '/static/covers/education/ed-1.jpeg',
    description: 'Didi s Day',
    color: '#3498db'
  },
  {
    id: 2,
    name: '小小科学探索家',
    image: '/static/covers/education/ed-2.jpeg',
    description: '小小科学探索家',
    color: '#2ecc71'
  },
  {
    id: 3,
    name: '小猪佩奇',
    image: '/static/covers/education/ed-3.jpeg',
    description: '小猪佩奇',
    color: '#e74c3c'
  },
  {
    id: 4,
    name: '洪恩',
    image: '/static/covers/education/ed-2.jpeg',
    description: '洪恩幼儿英语',
    color: '#f1c40f'
  },
  {
    id: 5,
    name: '瓜瓜英语',
    image: '/static/covers/education/ed-3.jpeg',
    description: '瓜瓜英语',
    color: '#e67e22'
  }
])

// 计算最终显示的数据，优先使用传入的数据，如果没有则使用默认数据
const displayCharacters = computed(() => {
  return props.characters.length > 0 ? props.characters : characters.value
})
</script>

<template>
  <div class="character-gallery">
    <div class="gallery-container">
      <Card v-for="char in displayCharacters" 
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
  /* padding: 20px; */
  /* box-sizing: border-box; */
}

.gallery-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  max-width: 1200px;
  margin: 0 auto;
  /* padding: 20px; */
  padding-inline: inherit;
}

.character-card {
  width: 200px;
  position: relative;
  aspect-ratio: 9/26;
  border: none;
  overflow: hidden;
  transition: transform 0.3s ease;
  border-radius: 0;
  padding: 0;
  background-color: var(--card-color, #000);
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
  overflow: hidden;
  clip-path: polygon(0 0, 100% 0, 85% 100%, 0% 100%);
}

.image-container::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, transparent 50%, var(--card-color) 50%);
  opacity: 0.2;
  transition: opacity 0.3s ease;
}

.character-card:hover .image-container::after {
  opacity: 0.4;
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
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
  background: linear-gradient(to top right, var(--card-color) 60%, transparent);
  color: white;
  clip-path: polygon(15% 0, 100% 0, 100% 100%, 0 100%);
  transform: translateY(100%);
  transition: transform 0.3s ease;
  text-align: center;
}

.character-card:hover .info-overlay {
  transform: translateY(0);
}

.info-overlay h3 {
  margin: 0;
  font-size: 1.2em;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.info-overlay p {
  margin: 5px 0 0;
  font-size: 0.9em;
  opacity: 0.8;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}
</style>