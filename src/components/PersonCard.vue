<script setup lang="ts">
import { ref, computed } from 'vue'
import { Card } from 'ant-design-vue'

interface Person {
  id: number
  name: string
  avatar: string
  title?: string
  company?: string
  description?: string
  backgroundColor?: string
}

interface Props {
  persons?: Person[]
  layout?: 'grid' | 'masonry'
  animationDelay?: number
  cardStyle?: 'modern' | 'classic'
}

const props = withDefaults(defineProps<Props>(), {
  layout: 'grid',
  animationDelay: 100,
  cardStyle: 'modern'
})

// 默认数据
const defaultPersons = ref<Person[]>([
  {
    id: 1,
    name: 'Michael',
    avatar: '/static/def/m41.webp',
    title: '高级工程师',
    company: 'Tech Corp',
    description: '专注于前端开发和用户体验设计',
    backgroundColor: '#3498db'
  },
  {
    id: 2,
    name: '肖恩',
    avatar: '/static/def/m3.webp',
    title: '产品经理',
    company: 'Innovation Inc',
    description: '负责产品战略和用户需求分析',
    backgroundColor: '#2ecc71'
  },
  {
    id: 3,
    name: '咚咚锵',
    avatar: '/static/def/m4.webp',
    title: 'UI设计师',
    company: 'Creative Studio',
    description: '专注于用户界面和交互设计',
    backgroundColor: '#e74c3c'
  }
])

const containerClass = computed(() => ({
  'person-card-container': true,
  [`layout-${props.layout}`]: true
}))

const cardClass = computed(() => (index: number) => ({
  'person-card': true,
  [`${props.cardStyle}-style`]: true,
  'animate-in': true,
  [`delay-${index}`]: true
}))
</script>

<template>
  <div :class="containerClass">
    <Card v-for="(person, index) in (props.persons?.length ? props.persons : defaultPersons)"
          :key="person.id"
          :class="cardClass(index)"
          :style="{ '--card-color': person.backgroundColor }"
          hoverable>
      <div class="card-content">
        <div class="avatar-container">
          <img :src="person.avatar" :alt="person.name">
        </div>
        <div class="info-container">
          <h3 class="name">{{ person.name }}</h3>
          <p v-if="person.title" class="title">{{ person.title }}</p>
          <p v-if="person.company" class="company">{{ person.company }}</p>
          <p v-if="person.description" class="description">{{ person.description }}</p>
        </div>
      </div>
    </Card>
  </div>
</template>

<style scoped>
.person-card-container {
  /* position: relative; */
  min-height: 400px;
  padding: 40px;
  display: flex;
  justify-content: center;
  perspective: 1000px;
  padding-bottom: 20px;
  transform: scale(.9);
  gap:24px
}

.person-card {
  position: flex;
  flex-wrap: nowrap;
  padding-bottom: 30px;
  width: 280px;
  /* margin: 0; */
  /* opacity: 0; */
  /* transform: translateY(50px) translateX(0) rotate(-10deg) translateZ(0); */
  /* transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1); */
}

.person-card:first-child { margin: 20px 0 0;rotate:15deg; z-index: 3; }
.person-card:nth-child(2) { margin: 0 clamp(-600px, -50%, -400px) 20px; z-index: 2; }
.person-card:nth-child(3) { margin: 20px 0 0 ; rotate:-15deg; z-index: 1; }

.person-card:hover {
  transform: translateY(-20px) translateX(0) rotate(-10deg) translateZ(50px) !important;
  z-index: 10;
}

.modern-style {
  border-radius: 15px;
  overflow: hidden;
  background: linear-gradient(145deg, var(--card-color, #ffffff) 0%, rgba(255,255,255,0.9) 100%);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1), 0 6px 6px rgba(0,0,0,0.1);
}

.classic-style {
  border: 2px solid var(--card-color, #333);
  background-color: #ffffff;
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.animate-in {
  animation: stackIn 0.6s ease forwards;
}

@keyframes stackIn {
  to {
    opacity: 1;
    transform: translateY(0) rotate(var(--rotate-angle, 0deg)) translateZ(0);
  }
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  text-align: center;
}

.avatar-container {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  margin-bottom: 15px;
  border: 3px solid var(--card-color, #ffffff);
  transition: transform 0.3s ease;
}

.avatar-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.person-card:hover .avatar-container {
  transform: scale(1.05);
}

.info-container {
  width: 100%;
}

.name {
  font-size: 1.5em;
  font-weight: bold;
  margin: 0 0 5px;
  color: var(--card-color, #333);
}

.title {
  font-size: 1.1em;
  color: #666;
  margin: 5px 0;
}

.company {
  font-size: 1em;
  color: #888;
  margin: 5px 0;
}

.description {
  font-size: 0.9em;
  color: #666;
  margin: 10px 0 0;
  line-height: 1.4;
}

/* 动画效果 */
.animate-in {
  animation: slideIn 0.6s ease forwards;
}

@keyframes slideIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 延迟动画 */
.delay-0 { animation-delay: 0s; }
.delay-1 { animation-delay: 0.2s; }
.delay-2 { animation-delay: 0.4s; }
.delay-3 { animation-delay: 0.6s; }
.delay-4 { animation-delay: 0.8s; }
</style>