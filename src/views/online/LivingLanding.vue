<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Layout, Button, Input, Card, message } from 'ant-design-vue'
import { AppleOutlined, AndroidOutlined, PlayCircleOutlined, VideoCameraOutlined, TeamOutlined } from '@ant-design/icons-vue'

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

// 直播相关的内容数据
const streamingContent = ref([
  {
    id: '1',
    title: '直播技术基础',
    description: '了解直播技术的基本原理和架构',
    icon: '📡',
    link: '/rtc/about_video.html',
    type: '基础理论'
  },
  {
    id: '2',
    title: '音视频编码格式',
    description: '深入学习音视频编码格式的技术细节',
    icon: '🔧',
    link: '/rtc/5-2_音视频编码格式简介.html',
    type: '技术详解'
  },
  {
    id: '3',
    title: '音视频封装格式',
    description: '掌握音视频封装格式的应用场景',
    icon: '📦',
    link: '/rtc/5-3_音视频封装格式.html',
    type: '技术详解'
  },
  {
    id: '4',
    title: '流媒体协议',
    description: '学习RTMP、HLS、DASH等流媒体协议',
    icon: '🌊',
    link: '/rtc/5-4_流媒体协议.html',
    type: '协议标准'
  },
  {
    id: '5',
    title: '直播业务介绍',
    description: '了解直播业务的商业模式和应用场景',
    icon: '💼',
    link: '/rtc/5-5_直播业务介绍.html',
    type: '业务理解'
  },
  {
    id: '6',
    title: '直播完整流程',
    description: '从推流到播放的完整技术流程解析',
    icon: '🔄',
    link: '/rtc/5-6_一个直播的整个流程及背后的故事.html',
    type: '流程详解'
  },
  {
    id: '7',
    title: '知识点总结',
    description: '直播技术核心知识点总结与回顾',
    icon: '📝',
    link: '/rtc/5-7_本章知识点总结.html',
    type: '知识总结'
  }
])

const liveServices = ref([
  {
    id: 'live',
    title: '直播与录播',
    description: '实时直播和录制回放服务（需要后端发起）',
    icon: '📹',
    link: '/online/living',
    type: '实时服务'
  },
  {
    id: 'meeting',
    title: '多人会议',
    description: '支持多人实时音视频互动会议',
    icon: '👥',
    link: '/online/meeting',
    type: '协作服务'
  }
])

const features = ref([
  { name: '实时推流', icon: '📡', description: '支持RTMP协议推流' },
  { name: '多清晰度', icon: '📺', description: '自动适配不同网络环境' },
  { name: '低延迟', icon: '⚡', description: '毫秒级延迟体验' },
  { name: '跨平台', icon: '🌐', description: '支持Web、移动端' },
  { name: '录制回放', icon: '💾', description: '自动录制，随时回看' },
  { name: '多人互动', icon: '💬', description: '实时聊天和互动'
  }
])

const videoPlayer = ref(null)

onMounted(() => {
  console.log('LivingLanding页面加载完成')
})

const navigateTo = (path: string) => {
  if (path.startsWith('http')) {
    window.open(path, '_blank')
  } else {
    router.push(path)
  }
}
</script>

<template>
  <Layout class="landing-layout">
    <HeroSearch />

    <!-- <CharacterGallery /> -->

    <div class="main-content">
      <!-- 直播技术学习区域 -->
      <section class="learning-section">
        <h2>📚 直播技术学习路径</h2>
        <p class="section-subtitle">从零开始，系统学习直播技术栈</p>
        <div class="content-grid">
          <Card 
            v-for="item in streamingContent" 
            :key="item.id" 
            class="content-card" 
            hoverable
            @click="navigateTo(item.link)"
          >
            <div class="card-icon">{{ item.icon }}</div>
            <div class="card-content">
              <h3>{{ item.title }}</h3>
              <p>{{ item.description }}</p>
              <span class="card-type">{{ item.type }}</span>
            </div>
          </Card>
        </div>
      </section>

      <!-- 直播服务区域 -->
      <section class="services-section">
        <h2>🎯 直播服务</h2>
        <p class="section-subtitle">体验完整的直播和会议服务</p>
        <div class="services-grid">
          <Card 
            v-for="service in liveServices" 
            :key="service.id" 
            class="service-card" 
            hoverable
            @click="navigateTo(service.link)"
          >
            <div class="service-icon">
              <PlayCircleOutlined v-if="service.id === 'live'" />
              <TeamOutlined v-if="service.id === 'meeting'" />
            </div>
            <div class="service-content">
              <h3>{{ service.title }}</h3>
              <p>{{ service.description }}</p>
              <Button type="primary" size="small">
                {{ service.id === 'live' ? '开始直播' : '加入会议' }}
              </Button>
            </div>
          </Card>
        </div>
      </section>

      <!-- 功能特性区域 -->
      <section class="features-section">
        <h2>✨ 核心功能特性</h2>
        <div class="features-grid">
          <div v-for="feature in features" :key="feature.name" class="feature-item">
            <div class="feature-icon">{{ feature.icon }}</div>
            <h3>{{ feature.name }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </div>
      </section>

      <!-- 环境配置指南区域 -->
      <section class="environment-guide-section">
        <h2>🏗️ 真实环境搭建必备要素（复杂系统构建）</h2>
        <div class="environment-content">
          <div class="tech-stack">
            <div class="stack-category">
              <h3>🖥️ 流媒体服务器</h3>
              <ul>
                <li><strong>Nginx-Https</strong>
                    <div class="code-block"> 
                        <pre><code>
    # HTTP server - redirect to HTTPS
    server {
        listen 8080;
        return 301 https://$host:8443$request_uri;
    }
    # HTTPS server
    server {
        listen 8443 ssl;
        # SSL configuration
        ssl_certificate /etc/nginx/certs/cert.pem;
        ssl_certificate_key /etc/nginx/certs/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;</code></pre>
                    </div>
                </li>
                <li><strong>RTMP模块</strong> - Nginx-RTMP、SRS流媒体服务器</li>
                <li><strong>HLS模块</strong> - Nginx-HLS、SRS-HLS</li>
                <li><strong>DASH模块</strong> - Nginx-DASH、SRS-DASH</li>
                <li><strong>RTC模块</strong> - WebRTC、Flutter-WebRTC、Android-WebRTC、iOS-WebRTC</li>
                <li><strong>CDN模块</strong> - Nginx-CDN、SRS-CDN</li>
                <li>
                  <strong>CORS配置</strong>
                  <div class="code-block">
                    <pre><code># CORS setup
add_header 'Access-Control-Allow-Origin' '*' always;
add_header 'Access-Control-Expose-Headers' 'Content-Length';

# allow CORS preflight requests
if ($request_method = 'OPTIONS') {
    add_header 'Access-Control-Allow-Origin' '*';
    add_header 'Access-Control-Max-Age' 1728000;
    add_header 'Content-Type' 'text/plain charset=UTF-8';
    add_header 'Content-Length' 0;
    return 204;
}</code></pre>
                  </div>
                </li>
                <li>
                  <strong>Docker部署</strong>
                  <div class="code-block">
                    <pre><code>docker run -d --name nginx-hls-https \
                    -p 1935:1935 -p 8443:8443 \
                    -v nginx_config_for_rtmp_https.conf:/etc/nginx/nginx.conf \
                    -v certs:/etc/nginx/certs \
                    alqutami/rtmp-hls
                    </code></pre>
                  </div>
                </li>
              </ul>
            </div>

            <div class="stack-category">
              <h3>📱 流媒体播放器</h3>
              <ul>
                <li><strong>Flutter</strong> - WebRTC、HLS、DASH协议支持</li>
                <li><strong>Android</strong> - ExoPlayer、MediaPlayer</li>
                <li><strong>iOS</strong> - AVPlayer、MediaPlayer</li>
                <li><strong>hls.js</strong>
                    <div class="code-block">
                        <pre><code>
https://github.com/video-dev/hls.js

import Hls from 'hls.js';
const hls = new Hls();
hls.loadSource('https://hls_server:8080/live/test.m3u8');
hls.attachMedia(videoElement);
hls.on(Hls.Events.MANIFEST_PARSED, () => {
videoElement.play();
});
                        </code></pre>
                    </div>
                </li>
                <li><strong>vedio.js</strong>
                <div class="code-block">
                    <pre><code>
import videojs from 'video.js'
import flvjs from 'flv.js'
import 'video.js/dist/video-js.css'
                    </code></pre>
                </div>
                </li>
              </ul>
            </div>

            <div class="stack-category">
              <h3>📁 流媒体文件格式</h3>
              <div class="format-group">
                <h4>HLS (HTTP Live Streaming)</h4>
                <code>test.m3u8</code>
                <code>test_high.m3u8</code>
                <code>test_mid.m3u8</code>
                <code>test_src.m3u8</code>
              </div>
              <div class="format-group">
                <h4>DASH (Dynamic Adaptive Streaming)</h4>
                <code>test_high.mpd</code>
                <code>test_low.mpd</code>
                <code>test_mid.mpd</code>
              </div>
            </div>

            <div class="stack-category">
              <h3>🎥 推流工具</h3>
              <ul>
                <li><strong>OBS Studio</strong> - 免费开源直播推流（https://obsproject.com）</li>
                <li><strong>StreamLabs OBS</strong> - 增强版OBS（https://streamlabs.com）</li>
                <li><strong>XSplit</strong> - 专业直播推流软件（https://www.xsplit.com）</li>
              </ul>
            </div>

            <div class="stack-category">
              <h3>🎬 直播工具</h3>
              <ul>
                <li><strong>VLC</strong> - 跨平台媒体播放器</li>
                <li><strong>FFmpeg</strong> - 音视频处理瑞士军刀</li>
                <li><strong>Movist Pro</strong> - macOS专业播放器</li>
                <li><strong>网页直播</strong> - 基于浏览器的直播平台</li>
              </ul>
            </div>

            <div class="stack-category full-width">
              <h3>🌐 直播地址配置</h3>
              <div class="address-grid">
                <div class="address-group">
                  <h4>RTMP推流地址</h4>
                  <code>rtmp://rtmp_server:1935/live/test</code>
                  <code>rtmp://rtmp_server:1935/live/test_high</code>
                  <code>rtmp://rtmp_server:1935/live/test_mid</code>
                  <code>rtmp://rtmp_server:1935/live/test_src</code>
                </div>
                <div class="address-group">
                  <h4>HLS播放地址</h4>
                  <code>https://hls_server:8080/live/test.m3u8</code>
                  <code>https://hls_server:8080/live/test_high.m3u8</code>
                  <code>https://hls_server:8080/live/test_mid.m3u8</code>
                  <code>https://hls_server:8080/live/test_src.m3u8</code>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 快速开始区域 -->
      <section class="quick-start-section">
        <div class="quick-start-content">
          <h2>🚀 快速开始直播</h2>
          <p>只需三步，即可开始你的直播之旅</p>
          <div class="steps">
            <div class="step">
              <div class="step-number">1</div>
              <h3>准备推流</h3>
              <p>配置OBS或其他推流软件</p>
            </div>
            <div class="step">
              <div class="step-number">2</div>
              <h3>开始直播</h3>
              <p>点击开始直播，获取推流地址</p>
            </div>
            <div class="step">
              <div class="step-number">3</div>
              <h3>观看直播</h3>
              <p>分享直播链接给观众</p>
            </div>
          </div>
          <Button type="primary" size="large" @click="navigateTo('/online/living')">
            立即开始
          </Button>
        </div>
      </section>

      <!-- 技术架构图 -->
      <section class="architecture-section">
        <h2>🏗️ 技术架构</h2>
        <div class="architecture-content">
          <div class="architecture-diagram">
            <div class="layer">
              <h4>推流端</h4>
              <p>OBS / 手机APP / WebRTC</p>
            </div>
            <div class="arrow">↓</div>
            <div class="layer">
              <h4>RTMP服务器</h4>
              <p>Nginx-RTMP / SRS</p>
            </div>
            <div class="arrow">↓</div>
            <div class="layer">
              <h4>转码处理</h4>
              <p>FFmpeg / 多清晰度</p>
            </div>
            <div class="arrow">↓</div>
            <div class="layer">
              <h4>分发网络</h4>
              <p>HLS / HTTP-FLV / DASH</p>
            </div>
            <div class="arrow">↓</div>
            <div class="layer">
              <h4>播放端</h4>
              <p>Web播放器 / 移动端</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 广告轮播 -->
      <section class="ad-section">
        <h2>📢 直播工具推荐</h2>
        <div class="ad-carousel">
          <div class="ad-slides">
            <div class="ad-slide">
              <a href="https://obsproject.com" target="_blank">
                <img src="../../assets/obs-logo.png" alt="OBS Studio" />
                <h4>OBS Studio - 免费开源直播软件</h4>
              </a>
            </div>
            <div class="ad-slide">
              <a href="https://www.ffmpeg.org" target="_blank">
                <img src="../../assets/ffmpeg-logo.png" alt="FFmpeg" />
                <h4>FFmpeg - 音视频处理瑞士军刀</h4>
              </a>
            </div>
            <div class="ad-slide">
              <a href="https://github.com/ossrs/srs" target="_blank">
                <img src="../../assets/srs-logo.png" alt="SRS" />
                <h4>SRS - 简单高效的实时视频服务器</h4>
              </a>
            </div>
          </div>
        </div>
      </section>

      <!-- 社区区域 -->
      <section class="cta-section">
        <div class="cta-content">
          <h2>🤝 加入直播技术社区</h2>
          <p>与开发者、主播和技术爱好者交流学习</p>
          <Button type="primary" size="large">立即加入</Button>
        </div>
      </section>

      <!-- App推广 -->
      <section class="app-promotion">
        <div class="app-content">
          <div class="app-info">
            <h2>📱 下载直播助手APP</h2>
            <p>随时随地管理你的直播和会议</p>
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
.landing-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.section-subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
  font-size: 1.1em;
}

/* 学习内容卡片 */
.learning-section,
.services-section {
  margin-bottom: 60px;
}

.content-grid,
.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.content-card,
.service-card {
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border-radius: 12px;
  overflow: hidden;
}

.content-card:hover,
.service-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.card-icon {
  font-size: 2em;
  text-align: center;
  margin-bottom: 15px;
}

.card-content h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.card-content p {
  margin: 0 0 10px 0;
  color: #666;
  line-height: 1.5;
}

.card-type {
  display: inline-block;
  background: #f0f0f0;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8em;
  color: #666;
}

.service-icon {
  font-size: 3em;
  color: #1890ff;
  text-align: center;
  margin-bottom: 15px;
}

.service-content {
  text-align: center;
}

/* 功能特性 */
.features-section {
  margin-bottom: 60px;
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 30px;
  margin-top: 30px;
}

.feature-item {
  text-align: center;
  padding: 20px;
}

.feature-icon {
  font-size: 2.5em;
  margin-bottom: 15px;
}

.feature-item h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.feature-item p {
  margin: 0;
  color: #666;
  font-size: 0.9em;
}

/* 环境配置指南 */
.environment-guide-section {
  margin-bottom: 60px;
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.environment-content {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 30px;
}

.tech-stack {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
}

.stack-category {
  background: white;
  border-radius: 10px;
  padding: 25px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  border-left: 4px solid #667eea;
}

.stack-category.full-width {
  grid-column: 1 / -1;
}

.stack-category h3 {
  color: #333;
  font-size: 1.3rem;
  margin-bottom: 15px;
  font-weight: 600;
}

.stack-category ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.stack-category li {
  color: #555;
  margin-bottom: 8px;
  padding-left: 15px;
  position: relative;
}

.stack-category li::before {
  content: "▸";
  color: #667eea;
  font-weight: bold;
  position: absolute;
  left: 0;
}

.format-group {
  margin-bottom: 15px;
}

.format-group h4 {
  color: #444;
  font-size: 1.1rem;
  margin-bottom: 8px;
  font-weight: 600;
}

.format-group code {
  display: inline-block;
  background: #e9ecef;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  margin: 2px;
  color: #495057;
}

.address-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 30px;
}

.address-group h4 {
  color: #333;
  font-size: 1.2rem;
  margin-bottom: 15px;
  font-weight: 600;
}

.address-group code {
  display: block;
  background: #f1f3f4;
  padding: 10px 15px;
  border-radius: 8px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  margin-bottom: 8px;
  color: #333;
  border-left: 3px solid #667eea;
}

/* 代码块样式 */
.code-block {
  background: #1e1e1e;
  border-radius: 8px;
  padding: 20px;
  margin: 15px 0;
  overflow-x: auto;
  border: 1px solid #333;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  position: relative;
}

.code-block::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 8px 8px 0 0;
}

.code-block pre {
  margin: 0;
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #d4d4d4;
}

.code-block code {
  color: #d4d4d4;
  background: none;
  padding: 0;
  margin: 0;
  border: none;
  font-family: inherit;
  font-size: inherit;
  white-space: pre;
  display: block;
}

/* 代码高亮 */
.code-block .keyword { color: #569cd6; }
.code-block .string { color: #ce9178; }
.code-block .comment { color: #6a9955; }
.code-block .function { color: #dcdcaa; }
.code-block .variable { color: #9cdcfe; }
.code-block .number { color: #b5cea8; }

/* 复制按钮 */
.code-block-container {
  position: relative;
}

.copy-button {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #333;
  color: #fff;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.3s;
}

.copy-button:hover {
  opacity: 1;
}

/* 快速开始 */
.quick-start-section {
  margin-bottom: 60px;
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  text-align: center;
}

.steps {
  display: flex;
  justify-content: space-around;
  margin: 40px 0;
  flex-wrap: wrap;
}

.step {
  flex: 1;
  min-width: 200px;
  margin: 10px;
}

.step-number {
  width: 50px;
  height: 50px;
  background: #1890ff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
  font-weight: bold;
  font-size: 1.2em;
}

.step h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.step p {
  margin: 0;
  color: #666;
}

/* 技术架构 */
.architecture-section {
  margin-bottom: 60px;
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.architecture-diagram {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  margin-top: 30px;
}

.layer {
  background: #f5f5f5;
  padding: 20px 40px;
  border-radius: 8px;
  text-align: center;
  min-width: 200px;
  border: 2px solid #e0e0e0;
}

.layer h4 {
  margin: 0 0 5px 0;
  color: #333;
}

.layer p {
  margin: 0;
  color: #666;
  font-size: 0.9em;
}

.arrow {
  font-size: 1.5em;
  color: #1890ff;
}

/* 广告轮播 */
.ad-section {
  margin-bottom: 60px;
}

.ad-carousel {
  position: relative;
  overflow: hidden;
  height: 200px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.ad-slides {
  display: flex;
  animation: slide 15s infinite;
}

.ad-slide {
  min-width: 100%;
  text-align: center;
  padding: 20px;
}

.ad-slide img {
  height: 120px;
  object-fit: contain;
  margin-bottom: 10px;
}

.ad-slide h4 {
  margin: 0;
  color: #333;
}

@keyframes slide {
  0%, 33% { transform: translateX(0); }
  33.33%, 66.66% { transform: translateX(-100%); }
  66.66%, 100% { transform: translateX(-200%); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content-grid,
  .services-grid,
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .steps {
    flex-direction: column;
  }
  
  .step {
    margin: 10px 0;
  }

  .environment-guide-section {
    padding: 25px 15px;
  }

  .environment-content {
    padding: 20px;
  }

  .tech-stack {
    grid-template-columns: 1fr;
  }

  .address-grid {
    grid-template-columns: 1fr;
  }

  .address-group code {
    font-size: 0.8rem;
    padding: 8px 10px;
  }
}

h2 {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}
</style>