<script setup lang="ts">
  import { ref, onMounted } from 'vue'
  import { useRoute } from 'vue-router'
  import { Layout, Button, Input, Card, message } from 'ant-design-vue'
  import { AppleOutlined, AndroidOutlined } from '@ant-design/icons-vue'
  import { getCategoryTree } from '../api/category'
  import HeroSearch from '../components/HeroSearch.vue'
  import AdCarousel from '../components/AdCarousel.vue'
  import MultiAd from '../components/MultiAd.vue'
  import MusicEffect from '../components/MusicEffect.vue'
  import CategoryNav from '../components/CategoryNav.vue'
  import RegisterCTA from '../components/RegisterCTA.vue'
  import AppPromotion from '../components/AppPromotion.vue'

  const category_tree = ref([])

  onMounted(async () => {
    try {
      const response = await getCategoryTree()
      console.log('获取分类:', response)

      if (response && response.data && response.data.length > 0) {
        category_tree.value = response.data
        console.log('成功获取分类列表')
      } else {
        console.log('使用兜底数据：API返回的数据为空')
      }
    } catch (error) {
      console.error('获取分类列表失败，使用兜底数据:', error)
      // message.warning('获取最新推荐音乐失败，显示默认推荐')
    }
  })

// 广告数据
const adData = {
    scrollAds: [
      {
        link: 'https://example.com/ad1',
        image: '/static/def/adb-1.webp',
        alt: '广告1'
      },
      {
        link: 'https://example.com/ad2',
        image: '/static/def/adb-1.webp',
        alt: '广告2'
      },
      {
        link: 'https://example.com/ad3',
        image: '/static/def/adb-1.webp',
        alt: '广告3'
      }
    ],
    reverseAds: [
      {
        link: 'https://example.com/ad1',
        image: '/static/def/adb-2.webp',
        alt: '广告1'
      },
      {
        link: 'https://example.com/ad2',
        image: '/static/def/adb-2.webp',
        alt: '广告2'
      },
      {
        link: 'https://example.com/ad3',
        image: '/static/def/adb-2.webp',
        alt: '广告3'
      }
    ],
    bottomAds: [
      {
        link: 'https://example.com/ad1',
        image: '/static/def/adb-3.webp',
        alt: '广告1'
      },
      {
        link: 'https://example.com/ad2',
        image: '/static/def/adb-3.webp',
        alt: '广告2'
      },
      {
        link: 'https://example.com/ad3',
        image: '/static/def/adb-3.webp',
        alt: '广告3'
      }
    ],
    videoUrl: '/static/def/video_2.mp4'
  }
</script>

<template>
  <Layout class="landing-layout">
    <HeroSearch @search="handleSearch" />

    <div class="main-content">
      <section class="ad-section">
        <div class="ad-wrapper">
          <AdCarousel :ads="[
            {
              link: 'https://example.com/ad1',
              image: '/static/def/ad1.png',
              alt: '精选音乐'
            },
            {
              link: 'https://example.com/ad2',
              image: '/static/def/ad2.png',
              alt: '热门歌单'
            },{
              link: 'https://example.com/ad1',
              image: '/static/def/ad1.png',
              alt: '精选音乐'
            },
            {
              link: 'https://example.com/ad2',
              image: '/static/def/ad2.png',
              alt: '热门歌单'
            }
          ]" />
        </div>
      </section>

        <section class="categories-section">
            <!-- <h2>分类</h2> -->
            <div class="category-tree">
            <div v-for="category in category_tree" :key="category.id" class="category-group">
                <h3 class="category-group-title">{{ category.name }}</h3>
                <div class="subcategory-grid">
                <!-- 构建关键的路径 -->
                <router-link v-for="subcategory in category.children" :key="subcategory.id" 
                    :to="`/${subcategory.prefix || 'mulist'}/${subcategory.refer_id}`" 
                    class="subcategory-card" 
                    :style="subcategory.background_style">
                    <div class="subcategory-content">
                    <h4 class="subcategory-name">{{ subcategory.name }}</h4>
                    </div>
                    <div class="subcategory-image" v-if="subcategory.desc_image">
                    <img :src="subcategory.desc_image" :alt="subcategory.name">
                    </div>
                </router-link>
                </div>
            </div>
            </div>
        </section>
      
      <MultiAd 
        class="main-ad-wrapper"
        :scroll-ads="adData.scrollAds"
        :reverse-ads="adData.reverseAds"
        :bottom-ads="adData.bottomAds"
        :video-url="adData.videoUrl"
        :current-track="currentTrack"
      />

      <MusicEffect />

      <RegisterCTA />

      <section class="banner-image main-ad-wrapper">
        <a href="https://example.com/banner" target="blank">
          <img src="../assets/adb.png" alt="横幅广告" />
        </a>
      </section>

      <AppPromotion />
    </div>
  </Layout>
</template>

<style scoped>
.multi-ad-section {
  margin: 40px 0;
  padding: 0 20px;
}

.multi-ad-container {
  position: relative;
  width: 100%;
  height: 300px;
  border-radius: 16px;
  overflow: hidden;
  background: #f5f5f5;
  display: flex;
  gap: 20px;
}

.ad-scroll-area {
  flex: 2;
  overflow: hidden;
  border-radius: 12px;
}

.ad-scroll-content {
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.ad-row {
  display: flex;
  animation: scrollLeft 60s linear infinite;
  width: fit-content;
  gap: 0;
  height: 100px;
}

.ad-row.reverse {
  animation: scrollRight 60s linear infinite;
}

.ad-row img {
  width: 400px;
  height: 100px;
  object-fit: cover;
}

@keyframes scrollLeft {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(calc(-400px * 3));
  }
}

@keyframes scrollRight {
  0% {
    transform: translateX(calc(-400px * 3));
  }
  100% {
    transform: translateX(0);
  }
}

.video-player {
  flex: 1;
  border-radius: 12px;
  overflow: hidden;
}

.video-player video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

@keyframes scrollLeft {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

.landing-layout {
  min-height: 100vh;
}

.hero-section {
  background: linear-gradient(135deg, #1a1a1a 0%, #373737 100%);
  color: white;
  padding: 80px 20px;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-content h1 {
  font-size: 3em;
  margin-bottom: 20px;
  color: white;
}

.hero-content p {
  font-size: 1.2em;
  margin-bottom: 40px;
  color: rgba(255, 255, 255, 0.8);
}

.search-box {
  max-width: 600px;
  margin: 0 auto;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.trending-section,
.categories-section,
.banner-section {
  margin-bottom: 60px;
}

.track-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin: 32px 0;
  padding: 0 16px;
}

.track-card {
  overflow: hidden;
  border-radius: 12px;
  transition: transform 0.3s ease;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.track-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.track-cover {
  position: relative;
  padding-top: 100%;
  background: #f5f5f5;
  border-radius: 8px 8px 0 0;
  overflow: hidden;
}

.track-cover img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.track-card:hover .track-cover img {
  transform: scale(1.05);
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.track-card:hover .play-overlay {
  opacity: 1;
}

.play-icon {
  color: white;
  font-size: 3em;
  transform: scale(0.8);
  transition: transform 0.3s ease;
}

.track-card:hover .play-icon {
  transform: scale(1);
}

.track-info {
  padding: 16px;
}

.track-info h3 {
  margin: 0 0 8px;
  font-size: 1.1em;
  font-weight: 600;
  line-height: 1.4;
  color: #333;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-info p {
  color: #666;
  margin: 0 0 8px;
  font-size: 0.9em;
}

.plays {
  color: #999;
  font-size: 0.85em;
  display: flex;
  align-items: center;
}

.category-tree {
  display: flex;
  flex-direction: column;
  gap: 40px;
  margin-top: 24px;
}

.category-group-title {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
  position: relative;
  padding-left: 15px;
}

.category-group-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px;
  background: linear-gradient(45deg, #FF9A9E, #FAD0C4);
  border-radius: 2px;
}

.subcategory-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.subcategory-card {
  height: 120px;
  border-radius: 12px;
  padding: 20px;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.subcategory-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.subcategory-content {
  position: relative;
  z-index: 1;
}

.subcategory-name {
  font-size: 18px;
  font-weight: bold;
  color: #fff;
  margin: 0;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
}

.subcategory-image {
  position: absolute;
  bottom: -10px;
  right: -10px;
  width: 100px;
  height: 100px;
  transform: rotate(15deg);
  opacity: 0.8;
  transition: transform 0.3s ease;
}

.subcategory-card:hover .subcategory-image {
  transform: rotate(-5deg) scale(1.1);
}

.subcategory-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.banner-section {
  background: linear-gradient(135deg, #ff9966 0%, #ff5e62 100%);
  padding: 80px 20px;
  text-align: center;
  border-radius: 8px;
  color: white;
}

.banner-content h2 {
  font-size: 2.5em;
  margin-bottom: 20px;
  color: white;
}

.banner-content p {
  font-size: 1.2em;
  margin-bottom: 30px;
  color: rgba(255, 255, 255, 0.9);
}

.cta-section {
  background: #f5f5f5;
  padding: 60px 20px;
  text-align: center;
  border-radius: 8px;
}

.cta-content h2 {
  margin-bottom: 16px;
}

.cta-content p {
  margin-bottom: 24px;
  color: #666;
}

.ad-section {
  margin: 40px 0;
  padding: 0 20px;
}

.ad-carousel {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
  border-radius: 12px;
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

.banner-image {
  width: 100%;
  margin-bottom: 5px;
  padding: 0 10px;
}

.banner-image img {
  width: 100%;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.app-promotion {
  background: linear-gradient(135deg, #1a1a1a 0%, #373737 100%);
  padding: 60px 20px;
  margin-top: 60px;
  color: white;
}

.app-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;
}

.app-info {
  flex: 1;
}

.app-info h2 {
  font-size: 2.5em;
  margin-bottom: 20px;
  color: white;
}

.app-info p {
  font-size: 1.2em;
  margin-bottom: 30px;
  color: rgba(255, 255, 255, 0.8);
}

.app-buttons {
  display: flex;
  gap: 16px;
}

.app-qrcode {
  text-align: center;
}

.app-qrcode img {
  width: 160px;
  height: 160px;
  margin-bottom: 12px;
  background: white;
  padding: 12px;
  border-radius: 8px;
}

.app-qrcode p {
  color: rgba(255, 255, 255, 0.8);
}

.music-effect-section {
  padding: 60px 0;
  overflow: hidden;
  background-color: #000;
}

.effect-container {
  position: relative;
  height: 500px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.background-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('../assets/sky.webp') center/cover no-repeat;
  opacity: 0.6;
  z-index: 1;
}

.wave-effect {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 300px;
  height: 300px;
}

.wave-circle {
  position: absolute;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  width: 100%;
  height: 100%;
  animation: wave 2s infinite;
  opacity: 0;
}

.wave-circle:nth-child(2) {
  animation-delay: 0.5s;
}

.wave-circle:nth-child(3) {
  animation-delay: 1s;
}

@keyframes wave {
  0% {
    transform: scale(0.1);
    opacity: 0.8;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

.phone-layer {
  position: absolute;
  bottom: 20px;
  right: 20px;
  z-index: 3;
  width: 200px;
  height: 400px;
}

.phone-layer img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.fixed-player {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  padding: 16px;
}

.player-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 24px;
}

.now-playing {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.now-playing img {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
}

.track-details h4 {
  margin: 0 0 4px;
  font-size: 1.1em;
  color: #333;
}

.track-details p {
  margin: 0;
  color: #666;
  font-size: 0.9em;
}

.audio-player {
  width: 400px;
  height: 36px;
}

@media (max-width: 768px) {
  .app-content {
    flex-direction: column;
    text-align: center;
  }

  .app-buttons {
    justify-content: center;
  }

  .app-info h2 {
    font-size: 2em;
  }
}
</style>

```
