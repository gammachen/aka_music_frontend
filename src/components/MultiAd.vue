<template>
  <section class="multi-ad-section">
    <h2>{{ title }}</h2>
    <div class="multi-ad-container">
      <div class="ad-scroll-area">
        <div class="ad-scroll-content">
          <div class="ad-row">
            <a v-for="(ad, index) in scrollAds" :key="'scroll-'+index" :href="ad.link" target="_blank" class="ad-item">
              <img :src="ad.image" :alt="ad.alt" />
            </a>
          </div>
          <div class="ad-row reverse">
            <a v-for="(ad, index) in reverseAds" :key="'reverse-'+index" :href="ad.link" target="_blank" class="ad-item">
              <img :src="ad.image" :alt="ad.alt" />
            </a>
          </div>
          <div class="ad-row">
            <a v-for="(ad, index) in bottomAds" :key="'bottom-'+index" :href="ad.link" target="_blank" class="ad-item">
              <img :src="ad.image" :alt="ad.alt" />
            </a>
          </div>
        </div>
      </div>

        <div class="video-player">
            <video ref="videoPlayer" controls>
                <source :src="videoUrl" type="video/mp4">
                您的浏览器不支持视频播放
            </video>
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
  scrollAds: Ad[]
  reverseAds: Ad[]
  bottomAds: Ad[]
  videoUrl: string
  currentTrack?: any
}

withDefaults(defineProps<Props>(), {
  title: '倾听就在身边',
  scrollAds: () => [],
  reverseAds: () => [],
  bottomAds: () => [],
  videoUrl: '',
  currentTrack: null
})
</script>

<style scoped>
.multi-ad-section {
  margin: 40px 0;
  padding: 0 20px;
}

.multi-ad-section h2 {
  font-size: 24px;
  margin-bottom: 20px;
  font-weight: bold;
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

.phone-preview {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.phone-preview img {
  max-height: 100%;
  max-width: 100%;
  object-fit: contain;
}

@media (max-width: 768px) {
  .multi-ad-container {
    height: auto;
    flex-direction: column;
  }

  .phone-preview {
    display: none;
  }

  .ad-row {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }
}
</style>