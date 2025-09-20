<template>
  <section class="cta-section">
    <div class="cta-content">
      <h2>{{ title }}</h2>
      <p>{{ description }}</p>
      <Button type="primary" size="large" @click="onRegister">{{ buttonText }}</Button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { Button } from 'ant-design-vue'

interface Props {
  title?: string
  description?: string
  buttonText?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '加入我们的社区',
  description: '分享你喜爱的，与志同道合的爱好者交流',
  buttonText: '立即注册'
})

const emit = defineEmits<{
  (e: 'register'): void
}>()

const onRegister = () => {
  emit('register')
}
</script>

<style scoped>
.cta-section {
  margin: 40px 0;
  padding: 40px 20px;
  background: linear-gradient(45deg, #1a1a1a, #333);
  color: #fff;
  border-radius: 16px;
}

.cta-content {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.cta-content h2 {
  font-size: 28px;
  margin-bottom: 16px;
  color: #fff;
}

.cta-content p {
  font-size: 16px;
  margin-bottom: 24px;
  color: rgba(255, 255, 255, 0.8);
}

@media (max-width: 768px) {
  .cta-section {
    padding: 32px 16px;
  }

  .cta-content h2 {
    font-size: 24px;
  }

  .cta-content p {
    font-size: 14px;
  }
}
</style>