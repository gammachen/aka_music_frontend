<template>
  <section class="ad-section">
    <h2>{{ title }}</h2>
    <div class="ad-carousel">
      <div class="ad-slides">
        <div v-for="(ad, index) in ads" :key="index" class="ad-slide">
          <a :href="ad.link" target="_blank">
            <img :src="ad.image" :alt="ad.alt" />
          </a>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
interface Ad {
  link: string
  image: string
  alt: string
}

interface Props {
  title?: string
  ads: Ad[]
}

withDefaults(defineProps<Props>(), {
  title: '值得拥有',
  ads: () => []
})
</script>

<style scoped>
.ad-section {
  margin: 40px 0;
  padding: 0 20px;
}

.ad-section h2 {
  font-size: 24px;
  margin-bottom: 20px;
  font-weight: bold;
}

.ad-carousel {
  position: relative;
  width: 100%;
  height: 300px;
  border-radius: 16px;
  overflow: hidden;
}

.ad-slides {
  display: flex;
  transition: transform 0.5s ease;
  animation: slideShow 10s infinite;
}

.ad-slide {
  min-width: 50%;
  position: relative;
  padding: 0 10px;
  box-sizing: border-box;
}

.ad-slide img {
  width: 100%;
  height: auto;
  object-fit: cover;
  border-radius: 8px;
}

@keyframes slideShow {
  0%, 45% {
    transform: translateX(0);
  }  
  50%, 95% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(0);
  }
}

@media (max-width: 768px) {
  .ad-carousel {
    height: 240px;
  }
}

@media (max-width: 480px) {
  .ad-carousel {
    height: 200px;
  }
}
</style>