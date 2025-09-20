<template>
  <div class="video-player-container">
    <video
      ref="videoPlayer"
      class="video-js vjs-default-skin"
      :class="{ 'vjs-fluid': options.fluid }"
    ></video>
    <div v-if="errorMessage" class="error-overlay">
      <div class="error-content">
        <p>{{ errorMessage }}</p>
        <button @click="retryPlayback">重试</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, defineExpose } from 'vue'
import videojs from 'video.js'
import flvjs from 'flv.js'
import 'video.js/dist/video-js.css'

const props = defineProps<{
  options: {
    autoplay?: boolean
    controls?: boolean
    source: {
      src: string
      type: string
    }
    fluid?: boolean
    aspectRatio?: string
    muted?: boolean
    loop?: boolean
    poster?: string
  }
}>()

const videoPlayer = ref<HTMLVideoElement | null>(null)
const player = ref<any>(null)
const errorMessage = ref<string>('')

// 初始化播放器
const initializePlayer = () => {
  if (videoPlayer.value) {
    try {
      // 检查是否是FLV格式
      if (props.options.source.type === 'flv' || props.options.source.src.includes('.flv')) {
        console.log('检测到FLV格式，使用flv.js播放');
        
        // 检查flv.js支持
        if (flvjs.isSupported()) {
          const flvPlayer = flvjs.createPlayer({
            type: 'flv',
            url: props.options.source.src,
            isLive: true,
            cors: true,
            withCredentials: false,
          });
          
          flvPlayer.attachMediaElement(videoPlayer.value);
          flvPlayer.load();
          
          if (props.options.autoplay) {
            flvPlayer.play().catch((error: any) => {
              console.error('flv.js播放失败:', error);
              handlePlayerError(error);
            });
          }
          
          // 保存flvPlayer实例
          (player.value as any) = flvPlayer;
          errorMessage.value = '';
          return;
        } else {
          errorMessage.value = '浏览器不支持flv.js，请使用现代浏览器';
          return;
        }
      }

      // 原有的HLS/video.js逻辑
      const isHlsSupported = videojs.getTech('html5') && videojs.getTech('html5').isSupported && 
                           videojs.getTech('html5').supportsNativeHls !== false
      
      console.log('HLS支持状态:', { 
        isHlsSupported, 
        nativeHls: videojs.getTech('html5')?.supportsNativeHls,
        userAgent: navigator.userAgent,
        sourceType: props.options.source.type,
        sourceSrc: props.options.source.src
      })

      // 确保video.js加载HLS支持 - 使用更简单的方式
      if (!videojs.getPlugin('reloadSourceOnError')) {
        videojs.registerPlugin('reloadSourceOnError', function() {
          const player = this
          let retryCount = 0
          const maxRetries = 3
          
          player.on('error', () => {
            const error = player.error()
            console.error('Video.js错误事件:', error)
            
            if (error && retryCount < maxRetries) {
              retryCount++
              console.log(`第${retryCount}次重试加载视频...`)
              
              setTimeout(() => {
                try {
                  const currentSrc = player.currentSrc()
                  console.log('重新加载源:', currentSrc)
                  player.src(currentSrc)
                  player.load()
                  player.play().catch(playError => {
                    console.error('重试播放失败:', playError)
                  })
                } catch (loadError) {
                  console.error('重新加载失败:', loadError)
                }
              }, 1000 * retryCount)
            }
          })
        })
      }

      const playerOptions = {
        autoplay: props.options.autoplay || false,
        controls: props.options.controls !== false,
        fluid: props.options.fluid || true,
        aspectRatio: props.options.aspectRatio || '16:9',
        muted: props.options.muted || false,
        loop: props.options.loop || false,
        poster: props.options.poster || '',
        preload: 'auto',
        techOrder: ['html5'],
        html5: {
          hls: {
            enableLowInitialPlaylist: true,
            smoothQualityChange: true,
            bandwidth: 2000000,
            overrideNative: !isHlsSupported,
            limitRenditionByPlayerDimensions: false,
            useDevicePixelRatio: true
          }
        },
        sources: [props.options.source]
      }

      console.log('初始化播放器配置:', playerOptions)

      player.value = videojs(videoPlayer.value, playerOptions, function onPlayerReady() {
        console.log('播放器已就绪')
        errorMessage.value = ''
        
        // 监听加载事件
        this.on('loadstart', () => {
          console.log('开始加载视频')
        })
        
        this.on('loadeddata', () => {
          console.log('视频数据已加载')
        })
        
        this.on('loadedmetadata', () => {
          console.log('元数据已加载，时长:', this.duration())
        })
        
        this.on('canplay', () => {
          console.log('可以开始播放')
        })
        
        this.on('waiting', () => {
          console.log('缓冲中...')
        })
        
        this.on('playing', () => {
          console.log('开始播放')
        })
      })

      // 监听错误事件
      player.value.on('error', handlePlayerError)

      // 应用reloadSourceOnError插件
      player.value.reloadSourceOnError()

    } catch (error) {
      console.error('播放器初始化失败:', error)
      handlePlayerError(error)
    }
  }
}

// 播放控制方法
const play = () => {
  if (player.value) {
    return player.value.play()
  }
}

const pause = () => {
  if (player.value) {
    return player.value.pause()
  }
}

const togglePlay = () => {
  if (player.value) {
    if (player.value.paused()) {
      return player.value.play()
    } else {
      return player.value.pause()
    }
  }
}

const isPlaying = () => {
  return player.value && !player.value.paused()
}

const isPaused = () => {
  return player.value && player.value.paused()
}

// 获取当前播放状态
const getCurrentTime = () => {
  return player.value ? player.value.currentTime() : 0
}

const getDuration = () => {
  return player.value ? player.value.duration() : 0
}

const getVolume = () => {
  return player.value ? player.value.volume() : 0
}

const setVolume = (volume: number) => {
  if (player.value) {
    player.value.volume(volume)
  }
}

const isMuted = () => {
  return player.value ? player.value.muted() : false
}

const setMuted = (muted: boolean) => {
  if (player.value) {
    player.value.muted(muted)
  }
}

// 处理播放器错误
const handlePlayerError = (event: any) => {
  console.error('播放器详细错误信息:', event)
  
  let errorCode = ''
  let errorDetails = ''
  
  try {
    if (event && typeof event === 'object') {
      // 处理video.js的错误对象
      if (player.value && player.value.error) {
        const error = player.value.error()
        if (error) {
          errorCode = error.code || 'UNKNOWN'
          errorDetails = error.message || JSON.stringify(error)
          console.error('Video.js错误详情:', { code: error.code, message: error.message, type: error.type })
        } else {
          errorCode = 'MEDIA_ERR_UNKNOWN'
          errorDetails = '未知媒体错误'
        }
      } else if (event.code || event.type) {
        // 直接错误对象
        errorCode = event.code || event.type
        errorDetails = event.message || event.toString()
      } else {
        errorCode = 'EVENT_ERROR'
        errorDetails = event.type || '播放器事件错误'
      }
    } else {
      errorCode = 'UNKNOWN_ERROR'
      errorDetails = String(event)
    }
  } catch (e) {
    console.error('解析错误时发生异常:', e)
    errorCode = 'PARSE_ERROR'
    errorDetails = '无法解析错误信息'
  }
  
  switch (errorCode) {
    case 1:
    case 'MEDIA_ERR_ABORTED':
      errorMessage.value = '用户取消了视频播放'
      break
    case 2:
    case 'MEDIA_ERR_NETWORK':
      errorMessage.value = '网络错误，请检查网络连接'
      break
    case 3:
    case 'MEDIA_ERR_DECODE':
      errorMessage.value = '视频解码失败，可能是格式不兼容'
      break
    case 4:
    case 'MEDIA_ERR_SRC_NOT_SUPPORTED':
      errorMessage.value = '视频格式不支持或源文件损坏'
      break
    case 5:
      errorMessage.value = '视频源不可用'
      break
    default:
      errorMessage.value = `播放失败: ${errorDetails}`
  }
  
  console.error('设置错误消息:', errorMessage.value)
}

// 增强的重试播放
const retryPlayback = () => {
  console.log('开始重试播放...')
  errorMessage.value = ''
  
  if (player.value) {
    try {
      // 先停止当前播放
      player.value.pause()
      
      // 重新设置源
      const source = props.options.source
      console.log('重设视频源:', source)
      
      player.value.src(source)
      player.value.load()
      
      // 延迟播放，确保加载完成
      setTimeout(() => {
        if (player.value && !errorMessage.value) {
          player.value.play().catch((playError: any) => {
            console.error('自动播放失败:', playError)
            handlePlayerError({ target: player.value, type: 'PLAY_ERROR' })
          })
        }
      }, 1000)
      
    } catch (error) {
      console.error('重试播放失败:', error)
      handlePlayerError(error)
    }
  } else {
    console.log('播放器未初始化，重新初始化...')
    initializePlayer()
  }
}

// 监听options变化
watch(
  () => props.options,
  (newOptions) => {
    if (player.value && newOptions.source?.src) {
      try {
        console.log('更新播放源:', newOptions.source.src)
        player.value.src(newOptions.source)
        
        if (newOptions.autoplay) {
          player.value.play()
        }
      } catch (error) {
        console.error('更新播放源失败:', error)
        handlePlayerError(error)
      }
    }
  },
  { deep: true }
)

onMounted(() => {
  // 延迟初始化以避免MockJS干扰
  setTimeout(() => {
    initializePlayer()
  }, 100)
})

onBeforeUnmount(() => {
  if (player.value) {
    try {
      // 检查是否是flv.js播放器
      if (props.options.source.src.startsWith('rtmp://')) {
        if (player.value.destroy) {
          player.value.destroy();
        }
      } else {
        // video.js播放器
        player.value.dispose();
      }
    } catch (error) {
      console.error('播放器销毁失败:', error);
    }
  }
})

// 暴露方法给父组件
defineExpose({
  play,
  pause,
  togglePlay,
  isPlaying,
  isPaused,
  getCurrentTime,
  getDuration,
  getVolume,
  setVolume,
  isMuted,
  setMuted
})
</script>

<style scoped>
.video-player-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

.video-js {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.error-content {
  text-align: center;
  color: white;
  padding: 20px;
}

.error-content button {
  margin-top: 10px;
  padding: 8px 16px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.error-content button:hover {
  background: #40a9ff;
}

/* 自定义播放器主题 */
:deep(.vjs-default-skin) {
  /* 控制栏背景 */
  --vjs-control-bar-background: rgba(0, 0, 0, 0.7);
  /* 进度条颜色 */
  --vjs-progress-bar-color: #1890ff;
  /* 播放按钮颜色 */
  --vjs-play-button-color: #fff;
}

:deep(.vjs-big-play-button) {
  background-color: rgba(0, 0, 0, 0.6) !important;
  border-color: #fff !important;
}

:deep(.vjs-control-bar) {
  background-color: var(--vjs-control-bar-background) !important;
}

:deep(.vjs-play-progress) {
  background-color: var(--vjs-progress-bar-color) !important;
}

:deep(.vjs-big-play-button:hover),
:deep(.vjs-play-control:hover) {
  color: var(--vjs-play-button-color) !important;
}
</style>


const getPlayerOptions = (stream: Stream) => {
  const baseOptions = {
    autoplay: false,
    controls: true,
    fluid: true,
    aspectRatio: '16:9',
    muted: isMuted.value,
    loop: false,
    poster: stream.poster || '/default-poster.jpg',
    techOrder: ['html5']
  }

  // 根据流类型设置不同的配置
  if (stream.url.startsWith('rtmp://')) {
    // RTMP流配置 - 需要特殊处理
    return {
      ...baseOptions,
      techOrder: ['flash', 'html5'], // 优先使用Flash
      sources: [{
        src: stream.url,
        type: 'rtmp/mp4'
      }]
    }
  } else if (stream.type === 'm3u8') {
    // HLS流配置
    return {
      ...baseOptions,
      source: {
        src: stream.url,
        type: 'application/x-mpegURL'
      }
    }
  } else {
    // 其他格式
    return {
      ...baseOptions,
      source: {
        src: stream.url,
        type: 'video/mp4'
      }
    }
  }
}