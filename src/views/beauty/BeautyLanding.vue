<script setup lang="ts">
  import { ref, onMounted } from 'vue'
  import { useRoute } from 'vue-router'
  import { Layout, Button, Input, Card, message } from 'ant-design-vue'
  import { AppleOutlined, AndroidOutlined } from '@ant-design/icons-vue'
  import { getCategoryTree } from '../../api/category'
  import HeroSearch from '../../components/HeroSearch.vue'
  import AdCarousel from '../../components/AdCarousel.vue'
  import MultiAd from '../../components/MultiAd.vue'
  import MusicEffect from '../../components/MusicEffect.vue'
  import CategoryNav from '../../components/CategoryNav.vue'
  import RegisterCTA from '../../components/RegisterCTA.vue'
  import AppPromotion from '../../components/AppPromotion.vue'

  const category_tree = ref([])
  const categories = ref([])
  const currentTrack = ref(null)

  onMounted(async () => {
    try {
      const response = await getCategoryTree()
      console.log('获取分类:', response)

      if (response && response.data && response.data.length > 0) {
        // 过滤出美图和佳人两个分类
        category_tree.value = response.data.filter(category => 
          category.name === '美图' || category.name === '佳人'
        )
        // 设置底部分类数据
        categories.value = response.data
        console.log('成功获取分类列表', response.data)
      } else {
        console.log('使用兜底数据：API返回的数据为空')
      }
    } catch (error) {
      console.error('获取分类列表失败，使用兜底数据:', error)
    }
  })

  const handleSearch = (value: string) => {
    console.log('搜索:', value)
  }

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
    videoUrl: '/assets/video_2.mp4'
  }
</script>

<template>
  <Layout class="landing-layout">
    <HeroSearch @search="handleSearch" />

    <div class="main-content">
      <section class="categories-section">
        <div class="category-tree">
          <div v-for="category in category_tree" :key="category.id" class="category-group">
            <h3 class="category-group-title">{{ category.name }}</h3>
            <div class="subcategory-grid">
              <router-link 
                v-for="subcategory in category.children" 
                :key="subcategory.id" 
                :to="`/${subcategory.prefix || 'mulist'}/${subcategory.refer_id}`" 
                class="subcategory-card" 
                :style="subcategory.background_style"
              >
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
      
      <MultiAd 
        class="main-ad-wrapper"
        :scroll-ads="adData.scrollAds"
        :reverse-ads="adData.reverseAds"
        :bottom-ads="adData.bottomAds"
        :video-url="adData.videoUrl"
        :current-track="currentTrack"
      />

      <MusicEffect />
      
      <CategoryNav class="main-ad-wrapper" :categories="categories" />

      <RegisterCTA />

      <section class="banner-image main-ad-wrapper">
        <a href="https://example.com/banner" target="blank">
          <img src="../../assets/adb.png" alt="横幅广告" />
        </a>
      </section>

      <AppPromotion />
      
    </div>
  </Layout>
</template>

<style scoped>
.trending-section,
.categories-section,
.banner-section {
  margin-bottom: 60px;
}

.category-tree {
  max-width: 1200px;
  margin: 0 auto;
}

.category-group {
  margin-bottom: 40px;
}

.category-group-title {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
}

.subcategory-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  padding: 0 20px;
}

.subcategory-card {
  position: relative;
  height: 240px;
  border-radius: 12px;
  overflow: hidden;
  background: #f5f5f5;
  transition: transform 0.3s ease;
  text-decoration: none;
  color: inherit;
}

.subcategory-card:hover {
  transform: translateY(-5px);
}

.subcategory-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
  z-index: 2;
}

.subcategory-name {
  color: #fff;
  font-size: 18px;
  margin: 0;
  text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
}

.subcategory-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.subcategory-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.main-ad-wrapper {
  max-width: 1200px;
  margin: 60px auto;
  padding: 0 20px;
  width: 100%;
}

.multi-ad-container {
  position: relative;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  height: 300px;
  border-radius: 16px;
  overflow: hidden;
  background: #f5f5f5;
  display: flex;
  gap: 20px;
}

.ad-section {
  margin: 60px auto;
  padding: 0 20px;
  max-width: 1200px;
  width: 100%;
}

.ad-wrapper {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: #fff;
}

.ad-section h2,
.multi-ad-section h2 {
  max-width: 1200px;
  margin: 0 auto 20px;
  padding: 0 20px;
  font-size: 24px;
  color: #333;
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
  color: white;
}

.app-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.ad-slides {
  display: flex;
  width: 100%;
  height: 100%;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.ad-slide {
  flex: 0 0 100%;
  height: 400px;
}

.ad-slide img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.ad-slide:hover img {
  transform: scale(1.05);
}

.ad-scroll-area {
  flex: 2;
  overflow: hidden;
  border-radius: 12px;
  margin: 0 auto;
  max-width: 1200px;
}

.ad-scroll-content {
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ad-row {
  display: flex;
  animation: scrollLeft 60s linear infinite;
  width: fit-content;
  gap: 10px;
  height: 100px;
}

.ad-row.reverse {
  animation: scrollRight 60s linear infinite;
}

.ad-row img {
  width: 400px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
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

.music-effect-section {
  padding: 60px 0;
  overflow: hidden;
  background-color: #000;
}

.effect-container {
  position: relative;
  height: 500px;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
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
  background: url('../../assets/sky.webp')  center/cover no-repeat;
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

.category-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
  padding: 20px;
}

.category-card {
  text-align: center;
  padding: 24px;
  transition: transform 0.3s ease;
}

.category-card:hover {
  transform: translateY(-5px);
}

.category-icon {
  font-size: 36px;
  margin-bottom: 16px;
  color: #1890ff;
}

.cta-section {
  background: linear-gradient(135deg, #1a1a1a 0%, #373737 100%);
  padding: 80px 20px;
  text-align: center;
  color: white;
}

.cta-content {
  max-width: 600px;
  margin: 0 auto;
}

.cta-content h2 {
  font-size: 2.5em;
  margin-bottom: 20px;
}

.cta-content p {
  font-size: 1.2em;
  margin-bottom: 40px;
  color: rgba(255, 255, 255, 0.8);
}

.app-content {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.app-info {
  flex: 1;
  padding-right: 60px;
}

.app-info h2 {
  font-size: 2.5em;
  margin-bottom: 20px;
}

.app-info p {
  font-size: 1.2em;
  margin-bottom: 40px;
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

@media (max-width: 1200px) {
  .subcategory-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 20px;
  }

  .multi-ad-container {
    flex-direction: column;
    height: auto;
    min-height: 500px;
  }

  .ad-scroll-area {
    flex: 1;
  }

  .video-player {
    height: 200px;
  }

  .ad-carousel {
    height: 280px;
  }
}

@media (max-width: 768px) {
  .subcategory-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
  }

  .subcategory-name {
    font-size: 16px;
  }

  .app-content {
    flex-direction: column;
    text-align: center;
  }

  .app-buttons {
    justify-content: center;
  }

  .app-qrcode {
    margin-top: 20px;
  }

  .ad-carousel {
    height: 240px;
  }
}

@media (max-width: 480px) {
  .subcategory-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
    padding: 0 8px;
  }

  .main-content {
    padding: 16px 8px;
  }

  .hero-content h1 {
    font-size: 2em;
  }

  .hero-content p {
    font-size: 1em;
  }

  .category-group-title {
    font-size: 18px;
  }

  .subcategory-card {
    height: 200px;
  }

  .ad-carousel {
    height: 200px;
  }
}
</style>