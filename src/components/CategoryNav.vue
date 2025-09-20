<template>
  <section class="categories-section">
    <h2>{{ title }}</h2>
    <div class="category-grid">
      <router-link v-for="category in categories" :key="category.name" :to="categoryPath(category)" class="category-link">
        <Card class="category-card" hoverable>
          <div class="category-icon">{{ category.icon }}</div>
          <h3>{{ category.name }}</h3>
        </Card>
      </router-link>
    </div>
  </section>
</template>

<script setup lang="ts">
import { Card } from 'ant-design-vue'

interface Category {
  name: string
  icon: string
  refer_id: string | number
  prefix: string | number
}

interface Props {
  title?: string
  categories: Category[]
  pathPrefix?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '分类',
  categories: () => [],
  pathPrefix: '/mulist'
})

// const categoryPath = (category: Category) => `${props.pathPrefix}/${category.refer_id}`
const categoryPath = (category: Category) => `/${category.prefix}`
</script>

<style scoped>
.categories-section {
  margin: 40px 0;
  padding: 0 20px;
}

.categories-section h2 {
  font-size: 24px;
  margin-bottom: 20px;
  font-weight: bold;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.category-link {
  text-decoration: none;
  color: inherit;
}

.category-card {
  text-align: center;
  padding: 20px;
  height: 160px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border-radius: 12px;
}

.category-card:nth-child(5n+1) {
  background: linear-gradient(135deg, #FFE5E5 0%, #FFD1D1 100%);
}

.category-card:nth-child(5n+2) {
  background: linear-gradient(135deg, #E5F4FF 0%, #D1EBFF 100%);
}

.category-card:nth-child(5n+3) {
  background: linear-gradient(135deg, #E5FFE5 0%, #D1FFD1 100%);
}

.category-card:nth-child(5n+4) {
  background: linear-gradient(135deg, #F4E5FF 0%, #EBD1FF 100%);
}

.category-card:nth-child(5n+5) {
  background: linear-gradient(135deg, #FFE5F4 0%, #FFD1EB 100%);
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.category-icon {
  font-size: 36px;
  margin-bottom: 12px;
}

.category-card h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

@media (max-width: 768px) {
  .category-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 16px;
  }

  .category-card {
    height: 140px;
    padding: 16px;
  }

  .category-icon {
    font-size: 32px;
  }
}

@media (max-width: 480px) {
  .category-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 12px;
  }

  .category-card {
    height: 120px;
    padding: 12px;
  }

  .category-icon {
    font-size: 28px;
  }
}
</style>