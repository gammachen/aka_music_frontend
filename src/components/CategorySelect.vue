<template>
  <div class="category-select">
    <el-cascader
      v-model="selectedCategory"
      :options="categoryTree"
      :props="{
        value: 'id',
        label: 'name',
        children: 'children'
      }"
      placeholder="请选择分类"
      clearable
      @change="handleCategoryChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

interface Category {
  id: number
  name: string
  children?: Category[]
}

const categoryTree = ref<Category[]>([])
const selectedCategory = ref<number[]>([])

const emit = defineEmits(['change'])

const fetchCategoryTree = async () => {
  try {
    const response = await axios.get('/api/categories/tree')
    if (response.data.code === 200) {
      categoryTree.value = response.data.data
    }
  } catch (error) {
    console.error('获取分类树失败:', error)
  }
}

const handleCategoryChange = (value: number[]) => {
  emit('change', value[value.length - 1])
}

onMounted(() => {
  fetchCategoryTree()
})
</script>

<style scoped>
.category-select {
  width: 100%;
}
</style>