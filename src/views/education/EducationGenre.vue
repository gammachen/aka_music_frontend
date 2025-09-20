<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Layout, Button, Input, Card, message } from 'ant-design-vue'
import { AppleOutlined, AndroidOutlined } from '@ant-design/icons-vue'
import { getAllEducationGenre } from '../../api/education'

import HeroSearch from '../../components/HeroSearch.vue'
import CharacterGallery from '../../components/CharacterGallery.vue'
import DiagonalSplitCharacterGallery from '../../components/DiagonalSplitCharacterGallery.vue'
import AdCarousel from '../../components/AdCarousel.vue'
import MultiAd from '../../components/MultiAd.vue'
import MusicEffect from '../../components/MusicEffect.vue'
import CategoryNav from '../../components/CategoryNav.vue'
import RegisterCTA from '../../components/RegisterCTA.vue'
import AppPromotion from '../../components/AppPromotion.vue'

const router = useRouter()
const allEducationGeneres = ref([
    {
      "category": "冒险漫画",
      "educations": [
        {
          "author": "尾田荣一郎",
          "country": "JP",
          "is_completed": false,
          "name": "海贼王",
          "publish_date": "1997-07-22",
          "tags": [
            "海盗",
            "恶魔果实",
            "大秘宝"
          ],
          "cover_url":"../../assets//a1.png"
        }
      ]
    }
  ])

const categories = ref([
  { name: '华语', icon: '🎵' },
  { name: '日韩', icon: '🎼' },
  { name: '欧美', icon: '🎸' },
  { name: '纯音乐', icon: '🎹' },
  { name: '异次元', icon: '🎧' }
])

const videoPlayer = ref(null)
const audioPlayer = ref(null)
const currentTrack = ref(null)

onMounted(async () => {
  try {
    const response = await getAllEducationGenre()
    console.log('获取所有内容列表:', response)

    if (response && response.data && response.data.length > 0) {
      allEducationGeneres.value = response.data
      console.log('成功获取所有内容列表')
    } else {
      console.log('使用兜底数据：API返回的数据为空')
    }
  } catch (error) {
    console.error('获取所有内容列表失败，使用兜底数据:', error)
    // message.warning('获取最新所有内容失败，显示默认所有')
  }

  // 不再需要动态创建audio元素，因为已经在模板中定义
  console.log('音频播放器已就绪')
})

const playAudioTrack = (track) => {
  console.log('开始播放音轨:', track)
  currentTrack.value = track
  
  // 等待下一个tick，确保DOM已更新
  nextTick(() => {
    // 使用模板中定义的audio元素
    const audio = audioPlayer.value
    if (!audio) {
      console.error('音频播放器未找到')
      return
    }
  
    if (track.url) {
      console.log('音轨URL有效')
      const audio = audioPlayer.value
      
      console.log('音频元素状态:', {
        readyState: audio.readyState,
        networkState: audio.networkState,
        error: audio.error
      })

      if (window.Hls.isSupported()) {
        console.log('HLS格式支持')
        const hls = new window.Hls()
        hls.loadSource(track.url)
        hls.attachMedia(audio)
        hls.on(window.Hls.Events.MANIFEST_PARSED, () => {
          console.log('HLS清单解析完成，开始播放')
          audio.play().catch(error => {
            console.error('播放失败:', error)
          })
        })
        hls.on(window.Hls.Events.ERROR, (event, data) => {
          console.error('HLS错误:', { event, data })
        })
      } else if (audio.canPlayType('application/vnd.apple.mpegurl')) {
        console.log('使用原生HLS支持')
        audio.src = track.url
        audio.play().catch(error => {
          console.error('原生播放失败:', error)
        })
      } else {
        console.error('当前浏览器不支持HLS格式')
      }
    } else {
      console.warn('无效的音轨URL:', {
        hasUrl: !!track.url
      })
    }
  })
}

// 添加一个函数来获取随机默认封面
const getRandomDefaultCover = () => {
  const randomNum = Math.floor(Math.random() * 3) + 1
  return `/static/covers/education/ed-${randomNum}.jpeg`
}
</script>

<template>
  <Layout class="landing-layout">
    <HeroSearch @search="handleSearch" />

    <DiagonalSplitCharacterGallery />

    <div class="main-content">
      <section v-for="genre in allEducationGeneres" :key="genre.category" class="trending-section">
        <h2>{{ genre.category }}</h2>
        <div class="track-grid">
          <Card v-for="education in genre.educations" :key="education.name" class="track-card" hoverable>
            <div class="track-cover">
              <img :src="education.cover_url ? education.cover_url : getRandomDefaultCover()" :alt="education.name" />
            </div>
            <div class="track-info" @click="router.push(`/education/${education.name}`)">
              <h3>{{ education.name }}</h3>
              <p>{{ education.author }} · {{ education.publish_date }}</p>
              <div class="education-tags">
                <span v-for="tag in education.tags" :key="tag" class="education-tag">{{ tag }}</span>
              </div>
            </div>
          </Card>
        </div>
      </section>

      <section class="ad-section">
        <h2>值得拥有</h2>
        <div class="ad-carousel">
          <div class="ad-slides">
            <div class="ad-slide">
              <a href="https://example.com/ad1" target="_blank">
                <img src="../../assets/ad1.png" alt="广告1" />
              </a>
            </div>
            <div class="ad-slide">
              <a href="https://example.com/ad2" target="_blank">
                <img src="../../assets/ad2.png" alt="广告2" />
              </a>
            </div>
            <div class="ad-slide">
              <a href="https://example.com/ad1" target="_blank">
                <img src="../../assets/ad1.png" alt="广告1" />
              </a>
            </div>
            <div class="ad-slide">
              <a href="https://example.com/ad2" target="_blank">
                <img src="../../assets/ad2.png" alt="广告2" />
              </a>
            </div>
          </div>
        </div>
      </section>

      <section class="multi-ad-section">
        <h2>倾听就在身边</h2>
        <div class="multi-ad-container">
          <div class="ad-scroll-area">
            <div class="ad-scroll-content">
              <div class="ad-row">
                <a href="https://example.com/ad1" target="_blank">
                  <img src="/img/def/adb-1.webp" alt="广告1" />
                </a>
                <a href="https://example.com/ad2" target="_blank">
                  <img src="/img/def/adb-1.webp" alt="广告2" />
                </a>
                <a href="https://example.com/ad3" target="_blank">
                  <img src="/img/def/adb-1.webp" alt="广告3" />
                </a>
                <a href="https://example.com/ad1" target="_blank">
                  <img src="/img/def/adb-1.webp" alt="广告1" />
                </a>
                <a href="https://example.com/ad2" target="_blank">
                  <img src="/img/def/adb-1.webp" alt="广告2" />
                </a>
                <a href="https://example.com/ad3" target="_blank">
                  <img src="/img/def/adb-1.webp" alt="广告3" />
                </a>
              </div>
              <div class="ad-row reverse">
                <a href="https://example.com/ad1" target="_blank">
                  <img src="../../assets/adb-2.webp" alt="广告1" />
                </a>
                <a href="https://example.com/ad2" target="_blank">
                  <img src="../../assets/adb-2.webp" alt="广告2" />
                </a>
                <a href="https://example.com/ad3" target="_blank">
                  <img src="../../assets/adb-2.webp" alt="广告3" />
                </a>
                <a href="https://example.com/ad1" target="_blank">
                  <img src="../../assets/adb-2.webp" alt="广告1" />
                </a>
                <a href="https://example.com/ad2" target="_blank">
                  <img src="../../assets/adb-2.webp" alt="广告2" />
                </a>
                <a href="https://example.com/ad3" target="_blank">
                  <img src="../../assets/adb-2.webp" alt="广告3" />
                </a>
              </div>
              <div class="ad-row">
                <a href="https://example.com/ad1" target="_blank">
                  <img src="../../assets/adb-3.webp" alt="广告1" />
                </a>
                <a href="https://example.com/ad2" target="_blank">
                  <img src="../../assets/adb-3.webp" alt="广告2" />
                </a>
                <a href="https://example.com/ad3" target="_blank">
                  <img src="../../assets/adb-3.webp" alt="广告3" />
                </a>
                <a href="https://example.com/ad1" target="_blank">
                  <img src="../../assets/adb-3.webp" alt="广告1" />
                </a>
                <a href="https://example.com/ad2" target="_blank">
                  <img src="../../assets/adb-3.webp" alt="广告2" />
                </a>
                <a href="https://example.com/ad3" target="_blank">
                  <img src="../../assets/adb-3.webp" alt="广告3" />
                </a>
              </div>
            </div>
          </div>
          <div class="video-player">
            <video ref="videoPlayer" controls>
              <source src="../../assets/video_2.mp4" type="video/mp4">
              您的浏览器不支持视频播放
            </video>
          </div>
          <div v-if="currentTrack" class="fixed-player">
            <div class="player-content">
              <div class="now-playing">
                <img :src="currentTrack.coverUrl" :alt="currentTrack.title" />
                <div class="track-details">
                  <h4>{{ currentTrack.title }}</h4>
                  <p>{{ currentTrack.artist }}</p>
                </div>
              </div>
              <audio ref="audioPlayer" controls class="audio-player">
                <source type="application/x-mpegURL">
                  您的浏览器不支持音频播放
              </audio>
            </div>
          </div>
        </div>
      </section>

      <section class="music-effect-section">
        <div class="effect-container">
          <div class="background-layer"></div>
          <div class="wave-effect">
            <div class="wave-circle"></div>
            <div class="wave-circle"></div>
            <div class="wave-circle"></div>
            <div class="wave-circle"></div>
            <div class="wave-circle"></div>
            <div class="wave-circle"></div>
            <div class="wave-circle"></div>
          </div>
          <div class="phone-layer">
            <img src="../../assets/phone.webp" alt="手机设备" />
          </div>
        </div>
      </section>
      
      <section class="categories-section">
        <h2>分类</h2>
        <div class="category-grid">
          <Card v-for="category in categories" :key="category.name" class="category-card" hoverable>
            <div class="category-icon">{{ category.icon }}</div>
            <h3>{{ category.name }}</h3>
          </Card>
        </div>
      </section>

      <section class="cta-section">
        <div class="cta-content">
          <h2>加入我们的社区</h2>
          <p>分享你喜爱的，与志同道合的爱好者交流</p>
          <Button type="primary" size="large">立即注册</Button>
        </div>
      </section>

      <section class="banner-image">
        <a href="https://example.com/banner" target="_blank">
          <img src="../../assets/adb.png" alt="横幅广告" />
        </a>
      </section>

      <section class="app-promotion">
        <div class="app-content">
          <div class="app-info">
            <h2>下载AKAAPP</h2>
            <p>随时随地，畅享高品质内容</p>
            <div class="app-buttons">
              <Button type="primary" size="large">
                <template #icon><AppleOutlined /></template>
                App Store
              </Button>
              <Button type="primary" size="large">
                <template #icon><AndroidOutlined /></template>
                Google Play
              </Button>
            </div>
          </div>
          <div class="app-qrcode">
            <img src="../../assets/qrcode.png" alt="扫码下载" />
            <p>扫码下载</p>
          </div>
        </div>
      </section>
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

.education-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.education-tag {
  padding: 4px 8px;
  background: #f0f0f0;
  border-radius: 12px;
  font-size: 0.8em;
  color: #666;
  transition: all 0.3s ease;
}

.education-tag:hover {
  background: #e0e0e0;
  transform: translateY(-1px);
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

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 24px;
  margin-top: 24px;
}

.category-card {
  text-align: center;
  padding: 24px;
  position: relative;
  overflow: hidden;
  transition: transform 0.3s ease;
}

.category-card:nth-child(1) {
  background: linear-gradient(135deg, #FFE5E5 0%, #FFD1D1 100%);
}

.category-card:nth-child(2) {
  background: linear-gradient(135deg, #E5F4FF 0%, #D1EBFF 100%);
}

.category-card:nth-child(3) {
  background: linear-gradient(135deg, #E5FFE5 0%, #D1FFD1 100%);
}

.category-card:nth-child(4) {
  background: linear-gradient(135deg, #F4E5FF 0%, #EBD1FF 100%);
}

.category-card:nth-child(5) {
  background: linear-gradient(135deg, #FFE5F4 0%, #FFD1EB 100%);
}

.category-card:hover {
  transform: translateY(-5px);
}

.category-icon {
  font-size: 2.5em;
  margin-bottom: 16px;
}

.category-card h3 {
  margin: 0;
  font-size: 1.2em;
  color: #333;
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
  background: url('../../assets/sky.webp') center/cover  no-repeat;
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