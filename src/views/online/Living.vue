<template>
  <div class="living-container">
    <div class="living-layout">
      <!-- 左侧播放列表 -->
      <div class="playlist-panel">
        <div class="playlist-header">
          <h3>直播列表</h3>
          <span class="live-count">{{ streams.length }} 个直播</span>
        </div>
        
        <div class="stream-list">
          <div 
            v-for="(stream, index) in streams" 
            :key="stream.id"
            :class="['stream-item', { active: currentStream?.id === stream.id }]"
            @click="selectStream(stream)"
          >
            <div class="stream-preview">
              <img :src="stream.poster || '/default-poster.jpg'" :alt="stream.title" />
              <div class="live-badge">直播中</div>
            </div>
            <div class="stream-info">
              <h4>{{ stream.title }}</h4>
              <p>{{ stream.description }}</p>
              <span class="viewer-count">{{ stream.viewers || 0 }} 人观看</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧主播放区域 -->
      <div class="main-player">
        <div v-if="currentStream" class="player-container">
          <div class="player-header">
            <h2>{{ currentStream.title }}</h2>
            <div class="player-actions">
              <button class="action-btn" @click="togglePlay" :title="isPlaying ? '暂停' : '播放'">
                <svg v-if="!isPlaying" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8 5v14l11-7z"/>
                </svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                </svg>
              </button>
              <button class="action-btn" @click="toggleMute" :title="isMuted ? '取消静音' : '静音'">
                <svg v-if="!isMuted" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                </svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 = 13.5 21 = 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 = 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
                </svg>
              </button>
              <button class="action-btn" @click="toggleFullscreen" title="全屏">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
                </svg>
              </button>
            </div>
          </div>
          
          <VideoPlayer 
            :key="currentStream.id"
            :options="getPlayerOptions(currentStream)"
            ref="videoPlayerRef"
          />
          
          <div class="stream-details">
            <div class="stream-meta">
              <span class="streamer">主播: {{ currentStream.streamer || '未知' }}</span>
              <span class="category">分类: {{ currentStream.category || '其他' }}</span>
              <span class="duration">时长: {{ formatDuration(currentStream.duration || 0) }}</span>
            </div>
            <p class="stream-description">{{ currentStream.description }}</p>
          </div>
        </div>
        
        <div v-else class="empty-state">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="#ccc">
            <path d="M21 3H3c-1.11 0-2 .89-2 2v12c0 1.1.89 2 2 2h5v2h8v-2h5c1.1 0 1.99-.9 1.99-2L23 5c0-1.11-.9-2-2-2zm0 14H3V5h18v12zm-5-6l-7 4V7z"/>
          </svg>
          <p>请选择直播开始观看</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import VideoPlayer from '../../components/VideoPlayer.vue'

interface Stream {
  id: string
  title: string
  description: string
  url: string
  poster?: string
  streamer?: string
  category?: string
  viewers?: number
  duration?: number
  type?: string
}

const streams = ref<Stream[]>([
  {
    id: '1',
    title: '（录播）海洋的世界（M3u8）',
    description: '前端开发最佳实践分享',
    url: '/static/uploads/online/playlist.m3u8',
    poster: '/static/covers/2.png',
    streamer: '技术大牛',
    category: '技术',
    viewers: 1234,
    duration: 3600,
    type: 'm3u8'
  },
  {
    id: '2',
    title: '（录播）梁静茹',
    description: '梁静茹MV',
    url: '/static/uploads/online/liang_jing_ru.m3u8',
    poster: '/static/covers/1.png',
    streamer: '音乐达人',
    category: '音乐',
    viewers: 567,
    duration: 7200,
    type: 'm3u8'
  },
  {
    id: '3',
    title: '（录播）游戏（春丽-M3u8）',
    description: '热门游戏实时对战',
    url: '/static/uploads/online/jieba_chunli.m3u8',
    poster: '/static/covers/3.png',
    streamer: '游戏主播',
    category: '游戏',
    viewers: 890,
    duration: 5400,
    type: 'm3u8'
  },
  // 恢复RTMP流配置
  {
    // 使用HTTP-FLV格式（后端RTMP转码后）
    id: '4',
    title: '游戏直播（豪鬼-M3u8）',
    description: '热门游戏实时对战2',
    // url: 'https://192.168.31.27:8443/hls/test.m3u8',
    // url: 'rtmp://192.168.31.27:1935/live/test',
    url: '/static/def/jieba_haogui.mp4',
    poster: '/static/covers/3.png',
    streamer: '游戏主播',
    category: '游戏',
    viewers: 890,
    duration: 5400,
    type: 'video/mp4' // m3u8类型
  },
  {
    // 使用HTTP-FLV格式（后端RTMP转码后）
    id: '5',
    title: '游戏直播（豪鬼-M3u8）',
    description: '热门游戏实时对战2',
    url: 'https://192.168.31.27:8443/hls/test.m3u8',
    // url: 'rtmp://192.168.31.27:1935/live/test',
    // url: '/static/def/jieba_haogui.mp4',
    poster: '/static/covers/3.png',
    streamer: '游戏主播',
    category: '游戏',
    viewers: 890,
    duration: 5400,
    type: 'm3u8' // m3u8类型
  }
])

const currentStream = ref<Stream | null>(null)
const isMuted = ref(false)
const isPlaying = ref(false)
const videoPlayerRef = ref<InstanceType<typeof VideoPlayer> | null>(null)

// 计算当前选中的直播流
const activeStream = computed(() => {
  return currentStream.value || streams.value[0]
})

// 获取播放器配置
const getPlayerOptions = (stream: Stream) => {
  const baseOptions = {
    autoplay: false, // 改为手动控制播放
    controls: true,
    fluid: true,
    aspectRatio: '16:9',
    muted: isMuted.value,
    loop: false,
    poster: stream.poster || '/default-poster.jpg'
  }

  // 根据流类型设置不同的配置
  if (stream.type === 'm3u8') {
    return {
      ...baseOptions,
      source: {
        src: stream.url,
        type: 'application/x-mpegURL'
      }
    }
  } else if (stream.type === 'rtmp') {
    return {
      ...baseOptions,
      source: {
        src: stream.url,
        type: 'rtmp/flv' // RTMP类型
      }
    }
  } else {
    return {
      ...baseOptions,
      source: {
        src: stream.url,
        type: 'video/mp4'
      }
    }
  }
}

// 选择直播流
const selectStream = async (stream: Stream) => {
  console.log('选择直播流:', stream)
  currentStream.value = stream
  isPlaying.value = false
  
  // 等待DOM更新
  await nextTick()
  
  // 自动开始播放新选择的视频
  if (videoPlayerRef.value) {
    try {
      await videoPlayerRef.value.play()
      isPlaying.value = true
    } catch (error) {
      console.error('自动播放失败:', error)
      isPlaying.value = false
    }
  }
}

// 切换播放/暂停
const togglePlay = async () => {
  if (!videoPlayerRef.value) return
  
  try {
    if (isPlaying.value) {
      await videoPlayerRef.value.pause()
      isPlaying.value = false
    } else {
      await videoPlayerRef.value.play()
      isPlaying.value = true
    }
  } catch (error) {
    console.error('播放控制失败:', error)
  }
}

// 切换静音
const toggleMute = () => {
  if (!videoPlayerRef.value) return
  
  const currentMuted = videoPlayerRef.value.isMuted()
  videoPlayerRef.value.setMuted(!currentMuted)
  isMuted.value = !currentMuted
}

// 切换全屏
const toggleFullscreen = () => {
  const element = document.querySelector('.player-container')
  if (element) {
    if (document.fullscreenElement) {
      document.exitFullscreen()
    } else {
      element.requestFullscreen()
    }
  }
}

// 格式化时长
const formatDuration = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}小时${minutes}分钟`
}

// 初始化
onMounted(() => {
  // 默认选择第一个直播
  if (streams.value.length > 0) {
    currentStream.value = streams.value[0]
  }
})
</script>

<style scoped>
.living-container {
  height: 100vh;
  background: #f5f5f5;
}

.living-layout {
  display: flex;
  height: 100%;
}

.playlist-panel {
  width: 320px;
  background: white;
  border-right: 1px solid #e8e8e8;
  overflow-y: auto;
}

.playlist-header {
  padding: 16px;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.playlist-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.live-count {
  font-size: 12px;
  color: #666;
  background: #f0f0f0;
  padding: 4px 8px;
  border-radius: 12px;
}

.stream-list {
  padding: 8px;
}

.stream-item {
  display: flex;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.stream-item:hover {
  background: #f5f5f5;
}

.stream-item.active {
  background: #e6f7ff;
  border: 1px solid #1890ff;
}

.stream-preview {
  position: relative;
  width: 120px;
  height: 68px;
  margin-right: 12px;
  flex-shrink: 0;
}

.stream-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.live-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background: #ff4d4f;
  color: white;
  padding: 2px 6px;
  font-size: 10px;
  border-radius: 2px;
}

.stream-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stream-info p {
  margin: 0 0 4px 0;
  font-size: 12px;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.viewer-count {
  font-size: 11px;
  color: #999;
}

.main-player {
  flex: 1;
  padding: 20px;
}

.player-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.player-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.player-header h2 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.player-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 8px;
  border: none;
  background: #f0f0f0;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.action-btn:hover {
  background: #e0e0e0;
}

.stream-details {
  margin-top: 16px;
  padding: 16px;
  background: white;
  border-radius: 8px;
}

.stream-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
  font-size: 14px;
  color: #666;
}

.stream-description {
  margin: 0;
  color: #333;
  line-height: 1.5;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .living-layout {
    flex-direction: column;
  }
  
  .playlist-panel {
    width: 100%;
    height: 200px;
    border-right: none;
    border-bottom: 1px solid #e8e8e8;
  }
  
  .stream-list {
    display: flex;
    overflow-x: auto;
    padding: 8px 0;
  }
  
  .stream-item {
    min-width: 280px;
    margin-right: 8px;
  }
}
</style>