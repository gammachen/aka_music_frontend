<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { Layout, Button, Input, Card, message } from 'ant-design-vue'
import { AppleOutlined, AndroidOutlined } from '@ant-design/icons-vue'
import { useRoute } from 'vue-router'
import { getMusicList } from '../../api/music'
import HeroSearch from '../../components/HeroSearch.vue'
import MultiAd from '../../components/MultiAd.vue'
import AdCarousel from '../../components/AdCarousel.vue'
import CharacterGallery from '../../components/CharacterGallery.vue';
import PersonCard from '../../components/PersonCard.vue';


// import Hls from '../assets/js/hls.js@latest';

const musicList = ref([
  {
    id: 1,
    title: '陈慧娴-千千阙歌[FLAC/MP3-320K]',
    artist: '陈慧娴',
    coverUrl: '/static/def/a1.png',
    plays: '22.5K',
    url: 'static/videos/4/22/1740070100_9071.m3u8'
  },
  {
    id: 2,
    title: 'Beyond-谁伴我闯荡[FLAC/MP3-320K]',
    artist: 'Beyond',
    coverUrl: '/static/def/a2.png',
    url: 'static/videos/4/118/1740070000_3569.m3u8',
    plays: '18.3K'
  },
  {
    id: 3,
    title: 'Beyond -  光辉岁月[FLAC/MP3-320K]',
    artist: 'Beyond',
    coverUrl: '/static/def/a3.png',
    url: 'static/videos/4/122/1740070008_7195.m3u8',
    plays: '15.7K'
  },
  {
    id: 3,
    title: '张国荣 - 当年情[FLAC/MP3-320K]',
    artist: '张国荣',
    coverUrl: '/static/def/a4.png',
    url: 'static/videos/4/0399/1740070023_9867.m3u8',
    plays: '15.7K'
  },
  {
    id: 3,
    title: '李克勤-红日[FLAC/MP3-320K]',
    artist: '李克勤',
    coverUrl: '/static/def/a5.png',
    url: 'static/videos/4/44/1740070066_7599.m3u8',
    plays: '15.7K'
  },
  {
    id: 3,
    title: '张国荣-倩女幽魂[FLAC/MP3-320K]',
    artist: '张国荣',
    coverUrl: '/static/def/a6.png',
    url: 'static/videos/4/105/1740070104_7573.m3u8',
    plays: '15.7K'
  },
  {
    id: 3,
    title: '梅艳芳-一生爱你千百回[FLAC/MP3-320K]',
    artist: '梅艳芳',
    coverUrl: '/static/def/a7.png',
    url: 'static/videos/4/68/1740070126_6159.m3u8',
    plays: '15.7K'
  },
  {
    id: 3,
    title: '卢巧音_王力宏-好心分手[FLAC/MP3-320K]',
    artist: '卢巧音_王力宏',
    coverUrl: '/static/def/a8.png',
    url: 'static/videos/4/64/1740070156_4910.m3u8',
    plays: '15.7K'
  }
])

const categories = ref([
  { name: '华语', icon: '🎵' , refer_id:4},
  { name: '日韩', icon: '🎼', refer_id:5},
  { name: '欧美', icon: '🎸', refer_id:6 },
  { name: '纯音乐', icon: '🎹', refer_id:7 },
  { name: '异次元', icon: '🎧', refer_id:8 }
])

const videoPlayer = ref(null)
const audioPlayer = ref(null)
const currentTrack = ref(null)

const route = useRoute()

// 提取数据加载逻辑为独立函数
const loadMusicData = async () => {
  try {
    // 各种语法，明确categoryId为string
    let categoryId = route.params.category_id as string
    if (!categoryId || categoryId === 'null' || categoryId === 'undefined') {
      // 非常情况的配置，4这个目录是粤语歌曲，最初就是建立了这个目录，一定会存在的
      categoryId = '4'
    }

    console.log('获取推荐音乐列表:', categoryId)
    
    const response = await getMusicList({category_id:categoryId, page:1, pageSize:8})
    
    console.log('获取推荐音乐列表:', response)

    if (response && response.data && response.data.list.length > 0) {
      musicList.value = response.data.list
      console.log('成功获取推荐音乐列表')
    } else {
      console.log('使用兜底数据：API返回的数据为空')
    }
  } catch (error) {
    console.error('获取推荐音乐列表失败，使用兜底数据:', error)
    // message.warning('获取最新推荐音乐失败，显示默认推荐')
  }
}

onMounted(async () => {
  await loadMusicData()
  // 不再需要动态创建audio元素，因为已经在模板中定义
  console.log('音频播放器已就绪')
})

// 监听路由参数变化
watch(() => route.params.category_id, async (newCategoryId) => {
  console.log('路由参数变化，重新加载音乐数据:', newCategoryId)
  await loadMusicData()
}, { immediate: false })

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
        console.log('HLS格式支持', track.url)
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


// 定义角色数据
const characters = ref([
  {
    id: 1,
    name: '筑梦前行',
    image: '/editor/poster_11.png',
    description: '筑梦前行，红色革命'
  },
  {
    id: 1,
    name: '今日复盘',
    image: '/editor/poster_13.png',
    description: '今日复盘，不一样的今天'
  },
  {
    id: 1,
    name: '人才福利',
    image: '/editor/poster_14.png',
    description: '人才福利，等什么'
  },
  {
    id: 1,
    name: '品牌赋能',
    image: '/editor/poster_16.png',
    description: '品牌赋能，万众瞩目'
  },
  {
    id: 1,
    name: '年会盛宴',
    image: '/editor/poster_12.png',
    description: '年会盛宴，维你共享'
  }
])


const trendingTracks = ref([
  {
    id: 1,
    title: '海报1',
    artist: '咚咚锵',
    coverUrl: '/editor/poster_11.png',
    plays: '',
  },
  {
    id: 1,
    title: '海报2',
    artist: '咚咚锵',
    coverUrl: '/editor/poster_11.png',
    plays: '',
  },
  {
    id: 1,
    title: '海报3',
    artist: '咚咚锵',
    coverUrl: '/editor/poster_11.png',
    plays: '',
  },
  {
    id: 1,
    title: '海报4',
    artist: '咚咚锵',
    coverUrl: '/editor/poster_11.png',
    plays: '',
  },
  {
    id: 1,
    title: '海报5',
    artist: '咚咚锵',
    coverUrl: '/editor/poster_11.png',
    plays: '',
  },
  {
    id: 1,
    title: '海报6',
    artist: '咚咚锵',
    coverUrl: '/editor/poster_11.png',
    plays: '',
  },
  {
    id: 1,
    title: '海报7',
    artist: '咚咚锵',
    coverUrl: '/editor/poster_11.png',
    plays: '',
  },
  {
    id: 1,
    title: '海报8',
    artist: '咚咚锵',
    coverUrl: '/editor/poster_11.png',
    plays: '',
  },
])
</script>

<template>
  <Layout class="landing-layout">
    <HeroSearch @search="handleSearch" />

    <div class="main-content">
      <section class="ad-section">
        <div class="ad-content-container">
          <div class="ad-text-content">
            <h2>超平想象一键生成海报设计</h2>
            <p class="ad-description">利用先进的AI技术，只需简单几步，即可生成专业级别的海报设计。无需专业设计知识，人人都能成为设计师。</p>
            <p class="ad-features">• 智能排版布局<br>• 一键生成多风格<br>• 高清图像输出<br>• 个性化定制选项</p>
            <button class="try-now-btn">立即体验</button>
          </div>
          <div class="ad-media-content">
            <div class="video-container">
              <video autoplay loop muted>
                <source src="/video/ak_ai_poster.mp4" type="video/mp4">
                您的浏览器不支持视频播放
              </video>
            </div>
          </div>
        </div>
      </section>

      <CharacterGallery :characters="characters" />
      <CharacterGallery :characters="characters" />
      <CharacterGallery :characters="characters" />
      
      <section class="trending-section">
        <h2>方形海报</h2>
        <div class="track-grid">
          <Card v-for="track in trendingTracks" :key="track.id" class="track-card" hoverable>
            <div class="track-cover">
              <img :src="track.coverUrl" :alt="track.title" />
            </div>
            <div class="track-info">
              <h3>{{ track.title }}</h3>
              <p>{{ track.artist }}</p>
            </div>
          </Card>
        </div>
      </section>

      <PersonCard />
      
      <section class="categories-section">
        <h2>分类</h2>
        <div class="category-grid">
          <router-link v-for="category in categories" :key="category.name" :to="`/mulist/${category.refer_id}`" class="category-link">
            <Card class="category-card" hoverable>
              <div class="category-icon">{{ category.icon }}</div>
              <h3>{{ category.name }}</h3>
            </Card>
          </router-link>
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
  margin: 60px 0;
  padding: 0 20px;
  background-color: #f8f9fa;
  border-radius: 16px;
}

.ad-content-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  padding: 40px 20px;
  gap: 40px;
}

.ad-text-content {
  flex: 1;
  padding-right: 20px;
}

.ad-text-content h2 {
  font-size: 2.2em;
  margin-bottom: 20px;
  color: #333;
  font-weight: bold;
}

.ad-description {
  font-size: 1.1em;
  line-height: 1.6;
  margin-bottom: 24px;
  color: #555;
}

.ad-features {
  font-size: 1em;
  line-height: 1.8;
  margin-bottom: 30px;
  color: #666;
}

.try-now-btn {
  background: linear-gradient(135deg, #ff9966 0%, #ff5e62 100%);
  color: white;
  border: none;
  padding: 12px 28px;
  font-size: 1.1em;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(255, 94, 98, 0.2);
}

.try-now-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 94, 98, 0.3);
}

.ad-media-content {
  flex: 1;
}

.video-container {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.video-container video {
  width: 100%;
  height: auto;
  display: block;
}

@media (max-width: 992px) {
  .ad-content-container {
    flex-direction: column;
    text-align: center;
    padding: 30px 15px;
  }
  
  .ad-text-content {
    padding-right: 0;
    margin-bottom: 30px;
  }
  
  .ad-text-content h2 {
    font-size: 1.8em;
  }
  
  .ad-description {
    font-size: 1em;
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
  background: url('../../assets/sky.webp') center/cover no-repeat;
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