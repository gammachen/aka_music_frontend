<template>
  <Layout class="landing-layout">
    <HeroSearch />

    <CharacterGallery />
    <div class="meeting-container">
      <div class="video-container">
        <div class="main-video">
          <!-- 主视频区域 -->
          <video v-if="mainStream" ref="mainVideo" autoplay :muted="mainStreamIsLocal"></video>
        </div>
        <div class="video-list">
          <!-- 视频列表区域 -->
          <video ref="localVideo" autoplay muted></video>
          <div ref="remoteVideos"></div>
          <!-- <video id="test-video" ref="testVideo" autoplay muted>
            <source src="https://192.168.31.27:5173/src/assets/video_2.mp4" type="video/mp4">
          </video> -->
        </div>
      </div>

      <div class="control-panel">
        <div class="message-panel">
          <div class="message-list" ref="messageList">
            <ul></ul>
          </div>
          <div class="message-input">
            <input type="text" v-model="messageInput" placeholder="发送消息..." @keyup.enter="sendMessage">
            <button @click="sendMessage">发送</button>
          </div>
        </div>

        <div class="user-info-panel">
          <h4>当前用户信息</h4>
          <div class="user-info-content">
            <p>用户ID: <span id="current-user-id">正在连接...</span></p>
            <p>房间号: room1</p>
          </div>
        </div>

        <div class="events-panel">
          <h4>事件日志</h4>
          <div class="events-list" ref="eventsList">
            <ul></ul>
          </div>
        </div>

        <div class="media-controls">
          <button @click="toggleAudio" :class="{ active: !isAudioMuted }">
            {{ isAudioMuted ? '取消静音' : '静音' }}
          </button>
          <button @click="toggleVideo" :class="{ active: !isVideoMuted }">
            {{ isVideoMuted ? '开启视频' : '关闭视频' }}
          </button>
          <button @click="leaveMeeting" style="background: #f44336; color: white;">
            离开会议室[room1]
          </button>
          <button @click="joinMeeting" :disabled="isInMeeting" style="background: #4CAF50; color: white;">
            加入会议[room1]
          </button>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { io, Socket } from 'socket.io-client'
import { Layout, Button, Input, Card, message } from 'ant-design-vue'

import HeroSearch from '../../components/HeroSearch.vue'
import CharacterGallery from '../../components/CharacterGallery.vue'
import { forEach } from 'lodash'

// 状态变量
const localVideo = ref<HTMLVideoElement | null>(null)
const mainVideo = ref<HTMLVideoElement | null>(null)
const remoteVideos = ref<HTMLDivElement | null>(null)
const messageList = ref<HTMLDivElement | null>(null)
const messageInput = ref('')
const isAudioMuted = ref(false)
const isVideoMuted = ref(false)
const mainStream = ref<MediaStream | null>(null)
const mainStreamIsLocal = ref(true)
const selectedUserId = ref<string | null>(null)
const eventsList = ref<HTMLDivElement | null>(null)
const isInMeeting = ref(true) // 用于跟踪是否在会议室中

// WebRTC相关变量
let socket: Socket
let localStream: MediaStream
let peerConnections: { [key: string]: RTCPeerConnection } = {}
const otherUserIds = ref<string[]>([])

// 添加连接状态跟踪
const connectionStates = new Map<string, {
  signalingState: string;
  iceConnectionState: string;
  connectionState: string;
  retryCount: number;
  lastRetryTime: number;
}>();

// 确保视频列表正确显示所有远程用户视频和备用图片
function updateVideoList() {
  console.log(`[WebRTC] updateVideoList - 开始更新视频列表`);
  
  if (!remoteVideos.value) {
    console.error(`[WebRTC] updateVideoList - 其他参会者的视频占位符【remoteVideos】不存在`);
    return;
  }

  console.log(`[WebRTC] updateVideoList - 开始更新视频列表，其他远程用户数量: ${otherUserIds.value.length}`);

  // 获取当前存在的用户容器ID
  const existingUserIds = new Set<string>();
  const currentUserContainers = remoteVideos.value.querySelectorAll('.user-video-container');
  currentUserContainers.forEach(container => {
    const userId = container.getAttribute('data-user-id');
    if (userId) existingUserIds.add(userId);
  });

  // 为每个活跃用户创建或更新用户容器
  otherUserIds.value.forEach((userId, index) => {
    let userContainer = document.querySelector(`.user-video-container[data-user-id="${userId}"]`) as HTMLDivElement | null;
    
    let videoElement: HTMLVideoElement | null = null;
    let imageElement: HTMLImageElement | null = null;

    // 如果用户容器不存在，创建新的
    if (!userContainer) {
      console.log(`[WebRTC] updateVideoList - 为用户 ${userId} 创建新的视频容器`);

      // 创建用户容器
      userContainer = document.createElement('div');
      userContainer.classList.add('user-video-container');
      userContainer.setAttribute('data-user-id', userId);
      userContainer.setAttribute('data-video', String(index + 2));
      userContainer.id = `${userId}-container`;
      userContainer.style.position = 'relative';
      userContainer.style.width = '100%';
      userContainer.style.height = '100%';
      userContainer.style.display = 'flex';
      userContainer.style.flexDirection = 'row';
      userContainer.style.alignItems = 'center';
      userContainer.style.justifyContent = 'space-around';
      userContainer.style.margin = '2px';
      userContainer.style.padding = '3px';
      userContainer.style.borderRadius = '8px';
      userContainer.style.backgroundColor = '#f0f0f0';
      userContainer.style.cursor = 'pointer';

      // 创建视频元素
      videoElement = document.createElement('video');
      videoElement.autoplay = true;
      videoElement.playsInline = true;
      videoElement.muted = true;
      videoElement.style.width = '45%';
      videoElement.style.height = 'auto';
      videoElement.classList.add('remote-video');
      videoElement.id = `${userId}-video`;
      videoElement.setAttribute('data-user-id', userId);
      videoElement.setAttribute('data-video', '2');
      videoElement.style.borderRadius = '8px';
      videoElement.style.zIndex = '1';
      videoElement.style.position = 'relative';

      // 创建备用图片元素
      imageElement = document.createElement('img');
      imageElement.src = `/static/def/01.jpeg`;
      imageElement.style.width = '45%';
      imageElement.style.height = 'auto';
      imageElement.classList.add('remote-user-avatar');
      imageElement.id = `${userId}-avatar`;
      imageElement.style.position = 'relative';
      imageElement.style.borderRadius = '8px';
      imageElement.style.zIndex = '1';
      imageElement.style.opacity = '1';

      // 创建用户ID标签
      const userIdLabel = document.createElement('div');
      userIdLabel.textContent = `用户: ${userId}...`;
      userIdLabel.style.position = 'absolute';
      userIdLabel.style.bottom = '5px';
      userIdLabel.style.left = '5px';
      userIdLabel.style.padding = '2px 6px';
      userIdLabel.style.backgroundColor = 'rgba(0,0,0,0.7)';
      userIdLabel.style.color = 'white';
      userIdLabel.style.fontSize = '12px';
      userIdLabel.style.borderRadius = '4px';
      userIdLabel.style.zIndex = '3';

      // 添加元素到容器
      userContainer.appendChild(imageElement);
      userContainer.appendChild(videoElement);
      userContainer.appendChild(userIdLabel);

      // 关键修复：使用缓存的MediaStream而不是重新构建
      if (peerConnections[userId]) {
        const pc = peerConnections[userId];
        console.log(`[WebRTC] updateVideoList - PeerConnection状态检查: 用户ID: ${userId}, signalingState: ${pc.signalingState}, iceConnectionState: ${pc.iceConnectionState}`);

        // 检查是否有缓存的流
        if (streamCache && streamCache.has(userId)) {
          const cachedStream = streamCache.get(userId);
          console.log(`[WebRTC] updateVideoList - 使用缓存的媒体流，用户ID: ${userId}`);
          
          // 设置媒体流
          videoElement.srcObject = cachedStream;
          
          // 强制触发加载和播放
          videoElement.load();
          
          // 尝试播放
          videoElement.play().then(() => {
            console.log(`[WebRTC] updateVideoList - 视频播放成功，用户ID: ${userId}`);
          }).catch(error => {
            console.error(`[WebRTC] updateVideoList - 视频播放失败，用户ID: ${userId}:`, error);
          });
        } else {
          console.log(`[WebRTC] updateVideoList - 没有缓存的媒体流，等待ontrack事件，用户ID: ${userId}`);
        }
      }

      // 添加点击事件到容器
      userContainer.addEventListener('click', () => {
        console.log(`[WebRTC] 用户容器被点击，尝试设置为主视频流，用户ID: ${userId}`);
        
        if (videoElement && videoElement.srcObject) {
          console.log(`[WebRTC] 设置主视频流，用户ID: ${userId}`);
          setMainStream(videoElement.srcObject as MediaStream, userId);
        } else {
          console.warn(`[WebRTC] 用户容器被点击，但videoElement或srcObject为空，用户ID: ${userId}`);
        }
      });

      remoteVideos.value.appendChild(userContainer);
      console.log(`[WebRTC] updateVideoList - 为用户 ${userId} 创建了用户容器`);
    } else {
      // 更新现有用户容器
      userContainer.setAttribute('data-video', String(index + 2));
      videoElement = userContainer.querySelector(`.remote-video`);
      imageElement = userContainer.querySelector(`.remote-user-avatar`);
      
      if (videoElement) {
        if (!videoElement.hasAttribute('data-user-id')) {
          videoElement.setAttribute('data-user-id', userId);
        }
        if (!videoElement.hasAttribute('data-video')) {
          videoElement.setAttribute('data-video', String(index + 2));
        }
        if (!videoElement.hasAttribute('autoplay')) {
          videoElement.setAttribute('autoplay', '');
        }
        if (!videoElement.hasAttribute('playsinline')) {
          videoElement.setAttribute('playsinline', '');
        }
        try {
          videoElement.muted = true;
        } catch (e) {
          console.warn('[WebRTC] 无法设置远端视频为静音', e);
        }
      }
    }

    // 从存在列表中移除
    existingUserIds.delete(userId);
  });

  // 删除不在用户列表中的用户容器
  existingUserIds.forEach(userId => {
    const containerToRemove = document.querySelector(`.user-video-container[data-user-id="${userId}"]`);
    if (containerToRemove) {
      containerToRemove.remove();
      console.log(`[WebRTC] updateVideoList - 移除用户 ${userId} 的用户容器`);
    }
  });
}

// 修复2: 添加流缓存机制
const streamCache = new Map<string, MediaStream>();

// 修复5: 改进setMainStream中的流比较
function setMainStream(stream: MediaStream, userId: string) {
  console.log(`[WebRTC] setMainStream - 开始设置主流媒体，用户ID: ${userId}, 本地流: ${userId === 'local'}`);

  // 记录媒体流详细信息
  if (stream) {
    const tracks = stream.getTracks();
    console.log(`[WebRTC] setMainStream - 媒体流包含 ${tracks.length} 个轨道`);

    // 打印每个轨道的详细信息
    tracks.forEach((track, index) => {
      console.log(`[WebRTC] setMainStream - 轨道 ${index + 1}: 类型=${track.kind}, 就绪状态=${track.readyState}, 启用=${track.enabled}`);
    });

    // 检查是否包含视频轨道
    const hasVideoTrack = tracks.some(track => track.kind === 'video');
    // 检查是否包含音频轨道
    const hasAudioTrack = tracks.some(track => track.kind === 'audio');
    console.log(`[WebRTC] setMainStream - 媒体流类型: 视频=${hasVideoTrack}, 音频=${hasAudioTrack}`);
  } else {
    console.error('[WebRTC] setMainStream - 传入的媒体流为空');
    return;
  }

  // 修复：正确比较MediaStream对象
  if (mainStream.value && mainStream.value === stream) {
    console.log('[WebRTC] setMainStream - 传入流与当前主流相同，跳过重设');
    return;
  }

  mainStream.value = stream;
  mainStreamIsLocal.value = userId === 'local';
  selectedUserId.value = userId;

  console.log(`[WebRTC] setMainStream - 主流媒体设置完成，当前selectedUserId: ${selectedUserId.value}`);

  // 更新主视频显示
  if (mainVideo.value) {
    console.log(`[WebRTC] setMainStream - 主视频元素存在，准备设置srcObject`);

    try {
      // 在切换流之前，先暂停并清空srcObject，避免浏览器中止前一次获取而报错
      if (!mainVideo.value.paused && !mainVideo.value.ended) {
        try { 
          mainVideo.value.pause(); 
          console.log('[WebRTC] setMainStream - 主视频元素暂停');
        } catch {
          console.error('[WebRTC] setMainStream - 主视频元素暂停失败');
        }
      }
      
      // 清空srcObject
      mainVideo.value.srcObject = null;

      // 强制设置自动播放属性与内联播放，并默认静音以满足自动播放策略
      mainVideo.value.autoplay = true;
      mainVideo.value.playsInline = true;
      mainVideo.value.muted = true;

      // 设置新媒体流
      mainVideo.value.srcObject = stream;
      
      console.warn('[WebRTC] setMainStream - 主视频元素srcObject设置完成，当前readyState:', mainVideo.value.readyState);
      // see:https://developer.mozilla.org/zh-CN/docs/Web/API/HTMLMediaElement/readyState
      // 一个数字，为 HTMLMediaElement 接口上定义的五个可能的状态常量之一：

      // HTMLMediaElement.HAVE_NOTHING（0）

      //     没有可用的关于媒体资源的信息。
      // HTMLMediaElement.HAVE_METADATA（1）

      //     已检索到足够的媒体资源，元数据属性已经初始化。查询操作将不再引发异常。
      // HTMLMediaElement.HAVE_CURRENT_DATA（2）

      //     当前播放位置的数据已经可用，但不足以实际播放多个帧。
      // HTMLMediaElement.HAVE_FUTURE_DATA（3）

      //     当前播放位置和提供至少一小段时间的数据已经可用（换句话说，至少有两个视频帧）。
      // HTMLMediaElement.HAVE_ENOUGH_DATA（4）

      //     有足够的数据可用，并且下载速度足够高，因此媒体可以不间断地播放到最后。

      const playSafely = () => {
        console.log('[WebRTC] setMainStream - 开始安全播放，当前readyState:', mainVideo.value!.readyState);
        
        // 再次确保静音
        mainVideo.value!.muted = true;
        mainVideo.value!.autoplay = true;
        mainVideo.value!.playsInline = true;
        
        mainVideo.value!.play().then(() => {
          console.log('[WebRTC] setMainStream - 主视频播放成功');
        }).catch((error) => {
          console.error('[WebRTC] setMainStream - 主视频播放失败:', error);
          
          // 如果是aborted错误，不需要重试
          if (error.name === 'AbortError' || error.message.includes('aborted')) {
            console.log('[WebRTC] setMainStream - 主视频播放被中止，可能是连接被清理');
            return;
          }
          
          // 其他错误可以重试
          const handleUserInteraction = () => {
            mainVideo.value!.play().then(() => {
              console.log('[WebRTC] setMainStream - 用户交互后播放成功');
            }).catch(e => {
              console.error('[WebRTC] setMainStream - 用户交互后播放仍失败:', e);
            });
            document.removeEventListener('click', handleUserInteraction);
          };
          document.addEventListener('click', handleUserInteraction, { once: true });
        });
      };

      // 检查当前readyState
      if (mainVideo.value.readyState >= HTMLMediaElement.HAVE_METADATA) {
        console.log('[WebRTC] setMainStream - 视频元数据已加载，直接播放');
        playSafely();
      } else {
        console.log('[WebRTC] setMainStream - 等待元数据加载，当前readyState:', mainVideo.value.readyState);
        
        // 添加多个事件监听器确保捕获到加载事件
        const onLoadedMetadata = () => {
          console.log('[WebRTC] setMainStream - loadedmetadata事件触发');
          mainVideo.value?.removeEventListener('loadedmetadata', onLoadedMetadata);
          mainVideo.value?.removeEventListener('loadeddata', onLoadedData);
          mainVideo.value?.removeEventListener('canplay', onCanPlay);
          playSafely();
        };

        const onLoadedData = () => {
          console.log('[WebRTC] setMainStream - loadeddata事件触发');
          mainVideo.value?.removeEventListener('loadedmetadata', onLoadedMetadata);
          mainVideo.value?.removeEventListener('loadeddata', onLoadedData);
          mainVideo.value?.removeEventListener('canplay', onCanPlay);
          playSafely();
        };

        const onCanPlay = () => {
          console.log('[WebRTC] setMainStream - canplay事件触发');
          mainVideo.value?.removeEventListener('loadedmetadata', onLoadedMetadata);
          mainVideo.value?.removeEventListener('loadeddata', onLoadedData);
          mainVideo.value?.removeEventListener('canplay', onCanPlay);
          playSafely();
        };

        // 添加事件监听器
        mainVideo.value.addEventListener('loadedmetadata', onLoadedMetadata);
        mainVideo.value.addEventListener('loadeddata', onLoadedData);
        mainVideo.value.addEventListener('canplay', onCanPlay);
        
        // 添加超时处理
        setTimeout(() => {
          console.log('[WebRTC] setMainStream - 超时检查，当前readyState:', mainVideo.value?.readyState);
          
          if (mainVideo.value && mainVideo.value.readyState < HTMLMediaElement.HAVE_METADATA) {
            console.warn('[WebRTC] setMainStream - 元数据加载超时，强制尝试播放');
            
            // 移除事件监听器
            mainVideo.value.removeEventListener('loadedmetadata', onLoadedMetadata);
            mainVideo.value.removeEventListener('loadeddata', onLoadedData);
            mainVideo.value.removeEventListener('canplay', onCanPlay);
            
            // 强制尝试播放
            playSafely();
          }
        }, 2000);
      }

    } catch (err) {
      console.error('[WebRTC] setMainStream - 设置主视频失败:', err);
    }
  } else {
    console.error('[WebRTC] setMainStream - 没有主视频元素，无法设置主视频流');
  }

  // 更新选中样式
  if (typeof updateSelectedVideoStyle === 'function') {
    updateSelectedVideoStyle();
    console.log('[WebRTC] setMainStream - 调用updateSelectedVideoStyle完成');
  }
}

// 创建RTCPeerConnection
async function createPeerConnection(userId: string) {
  console.log(`[WebRTC] createPeerConnection - 开始为用户创建连接，用户ID: ${userId}`)

  // 检查是否已存在连接
  if (peerConnections[userId]) {
    const existingPc = peerConnections[userId];
    console.log(`[WebRTC] createPeerConnection - 用户 ${userId} 已存在PeerConnection，当前状态: signalingState=${existingPc.signalingState}, iceConnectionState=${existingPc.iceConnectionState}`);
    
    // 如果连接已关闭，清理并重新创建
    if (existingPc.signalingState === 'closed') {
      console.log(`[WebRTC] createPeerConnection - 现有连接已关闭，清理并重新创建，用户ID: ${userId}`);
      cleanupPeerConnection(userId);
    } else {
      return existingPc;
    }
  }

  console.log(`[WebRTC] createPeerConnection - 用户 ${userId} 不存在PeerConnection，创建新的连接`)

  // 创建PeerConnection实例
  console.log(`[WebRTC] createPeerConnection - 初始化RTCPeerConnection，使用本地TURN服务器和公共STUN服务器`)
  peerConnections[userId] = new RTCPeerConnection({
    iceServers: [
      {
        urls: 'stun:192.168.31.27:8999',
      },
      // {
      //   urls: 'turn:192.168.31.27:8999?transport=tcp',
      //   username: 'akamusic',
      //   credential: 'youhavetoberealistic'
      // },
      // 添加公共STUN服务器作为备选
      // { urls: 'stun:stun.l.google.com:19302' },
      // { urls: 'stun:stun1.l.google.com:19302' },
    ],
    iceCandidatePoolSize: 10,
    iceTransportPolicy: 'all',
    bundlePolicy: 'max-bundle',
    rtcpMuxPolicy: 'require',
  })
  console.log(`[WebRTC] createPeerConnection - RTCPeerConnection创建成功`)

  // 初始化连接状态跟踪
  connectionStates.set(userId, {
    signalingState: peerConnections[userId].signalingState,
    iceConnectionState: peerConnections[userId].iceConnectionState,
    connectionState: peerConnections[userId].connectionState,
    retryCount: 0,
    lastRetryTime: 0
  });

  // 检查PeerConnection初始状态
  console.log(`[WebRTC] createPeerConnection - PeerConnection初始状态: signalingState: ${peerConnections[userId].signalingState}, iceConnectionState: ${peerConnections[userId].iceConnectionState}`)

  // 设置ICE连接状态变化监听
  peerConnections[userId].oniceconnectionstatechange = () => {
    const newState = peerConnections[userId].iceConnectionState;
    const oldState = connectionStates.get(userId)?.iceConnectionState;
    console.log(`[WebRTC] createPeerConnection oniceconnectionstatechange - ICE连接状态变化: 用户ID: ${userId}, 从 ${oldState} 到 ${newState}`);
    
    // 更新状态跟踪
    const state = connectionStates.get(userId);
    if (state) {
      state.iceConnectionState = newState;
      connectionStates.set(userId, state);
    }

    // 检查ICE连接是否成功
    if (newState === 'connected' || newState === 'completed') {
      console.log(`[WebRTC] createPeerConnection - ICE连接成功建立，用户ID: ${userId}`);
    } else if (newState === 'failed' || newState === 'disconnected') {
      console.warn(`[WebRTC] createPeerConnection - ICE连接失败或断开，用户ID: ${userId}, 状态: ${newState}`);
    }
  };

  // 设置信号状态变化监听
  peerConnections[userId].onsignalingstatechange = () => {
    const newState = peerConnections[userId].signalingState;
    const oldState = connectionStates.get(userId)?.signalingState;
    console.log(`[WebRTC] createPeerConnection onsignalingstatechange - 信号状态变化: 用户ID: ${userId}, 从 ${oldState} 到 ${newState}`);
    
    // 更新状态跟踪
    const state = connectionStates.get(userId);
    if (state) {
      state.signalingState = newState;
      connectionStates.set(userId, state);
    }
  };

  // 设置onconnectionstatechange事件处理器
  peerConnections[userId].onconnectionstatechange = () => {
    const newState = peerConnections[userId].connectionState;
    const oldState = connectionStates.get(userId)?.connectionState;
    console.log(`[WebRTC] createPeerConnection onconnectionstatechange - 连接状态变化: 用户ID: ${userId}, 从 ${oldState} 到 ${newState}`);
    
    // 更新状态跟踪
    const state = connectionStates.get(userId);
    if (state) {
      state.connectionState = newState;
      connectionStates.set(userId, state);
    }

    // 检查连接是否已关闭或失败
    if (newState === 'failed' || newState === 'disconnected' || newState === 'closed') {
      console.warn(`[WebRTC] createPeerConnection onconnectionstatechange - 连接状态异常: 用户ID: ${userId}, 状态: ${newState}`);
      
      // 改进的重连逻辑
      if (newState === 'failed') {
        const currentState = connectionStates.get(userId);
        if (currentState) {
          const now = Date.now();
          const timeSinceLastRetry = now - currentState.lastRetryTime;
          const maxRetries = 3;
          const retryDelay = 15000; // 5秒延迟

          if (currentState.retryCount < maxRetries && timeSinceLastRetry > retryDelay) {
            console.log(`[WebRTC] createPeerConnection onconnectionstatechange - 开始重连逻辑: 用户ID: ${userId}, 重试次数: ${currentState.retryCount + 1}/${maxRetries}`);
            
            // 更新重试计数
            currentState.retryCount++;
            currentState.lastRetryTime = now;
            connectionStates.set(userId, currentState);

            // 延迟后重连
            setTimeout(() => {
              if (userId && otherUserIds.value.includes(userId)) {
                console.log(`[WebRTC] createPeerConnection onconnectionstatechange - 执行重连: 用户ID: ${userId}`);
                
                // 先清理现有连接
                cleanupPeerConnection(userId);
                
                // 等待清理完成后再重新创建连接
                setTimeout(() => {
                  createPeerConnection(userId).then(() => {
                    if (peerConnections[userId] && localStream) {
                      // 重新添加媒体轨道
                      localStream.getTracks().forEach(track => {
                        peerConnections[userId].addTrack(track, localStream);
                      });
                      
                      // 重新发送offer
                      startPeerConnection(userId, localStream);
                    }
                  });
                }, 1000); // 给清理一些时间
              }
            }, retryDelay);
          } else {
            console.error(`[WebRTC] createPeerConnection onconnectionstatechange - 重连次数已达上限或时间间隔不足，停止重连: 用户ID: ${userId}`);
          }
        }
      }
    } else if (newState === 'connected') {
      console.log(`[WebRTC] createPeerConnection onconnectionstatechange - 连接成功建立，用户ID: ${userId}`);
      
      // 重置重试计数
      const state = connectionStates.get(userId);
      if (state) {
        state.retryCount = 0;
        connectionStates.set(userId, state);
      }
    }
  };

  // 设置ontrack事件处理器
  peerConnections[userId].ontrack = (event) => {
    console.log(`[${userId}] 📹 ontrack 事件 - 收到远程媒体流`);
    console.log('流数量:', event.streams.length);
    console.log('Track 类型:', event.track.kind);
    console.log('Track ID:', event.track.id);
    console.log('Track 状态:', event.track.readyState);

    // 确保事件包含有效的流
    if (!event.streams || event.streams.length === 0) {
      console.warn(`[WebRTC] createPeerConnection ontrack - 接收到ontrack事件，但没有可用的媒体流`)
      return;
    }

    const stream = event.streams[0]; // 使用原始流，不要重新构建
    console.log(`[WebRTC] createPeerConnection ontrack - 检测到媒体流，包含 ${stream.getTracks().length} 个轨道`);
    // 临时将视频流设置到测试元素test-video
    const testVideo = document.getElementById('test-video') as HTMLVideoElement;
    if (testVideo) {
      testVideo.srcObject = stream;
      testVideo.play();
    }

    // 缓存流
    streamCache.set(userId, stream);
    console.log(`[WebRTC] createPeerConnection ontrack - 媒体流已缓存，用户ID: ${userId}`);

    // 验证媒体轨道可用性
    const videoTracks = stream.getVideoTracks();
    const audioTracks = stream.getAudioTracks();
    console.log(`[WebRTC] createPeerConnection ontrack - 媒体流包含 ${videoTracks.length} 个视频轨道和 ${audioTracks.length} 个音频轨道`);

    // 详细检查每个轨道的状态
    stream.getTracks().forEach((track, index) => {
      console.log(`[WebRTC] createPeerConnection - 轨道${index + 1}: type=${track.kind}, readyState=${track.readyState}, enabled=${track.enabled}`);
    });

    // 确保用户在otherUserIds中
    if (!otherUserIds.value.includes(userId)) {
      otherUserIds.value.push(userId);
      console.log(`[WebRTC] createPeerConnection - 将用户 ${userId} 添加到用户列表`);
      // 触发视频列表更新
      updateVideoList();
    }

    // 尝试设置媒体流到视频元素
    const trySetMediaStream = () => {
      const userContainer = document.querySelector(`.user-video-container[data-user-id="${userId}"]`) as HTMLDivElement;
      const videoElement = userContainer ? userContainer.querySelector('.remote-video') as HTMLVideoElement : null;

      if (videoElement) {
        try {
          // 检查当前是否已有相同的流
          if (videoElement.srcObject !== stream) {
            console.log(`[WebRTC] createPeerConnection - 设置媒体流到视频元素，用户ID: ${userId}`);
            
            // 先暂停现有播放
            if (!videoElement.paused) {
              videoElement.pause();
            }
            
            // 设置媒体流
            videoElement.srcObject = stream;
            
            // 强制触发加载
            videoElement.load();
            
            // 尝试播放，添加错误处理
            videoElement.play().then(() => {
              console.log(`[WebRTC] createPeerConnection - 视频播放成功，用户ID: ${userId}`);
            }).catch(error => {
              console.error(`[WebRTC] createPeerConnection - 视频播放失败，用户ID: ${userId}:`, error);
              
              // 如果是aborted错误，可能是连接被清理了，不需要重试
              if (error.name === 'AbortError' || error.message.includes('aborted')) {
                console.log(`[WebRTC] createPeerConnection - 视频播放被中止，可能是连接被清理，用户ID: ${userId}`);
                return;
              }
            });
          } else {
            console.log(`[WebRTC] createPeerConnection - 视频元素已有相同的媒体流，用户ID: ${userId}`);
          }
        } catch (error) {
          console.error(`[WebRTC] createPeerConnection - 设置媒体流时发生错误:`, error);
        }
      } else {
        console.log(`[WebRTC] createPeerConnection - 视频元素未找到，用户ID: ${userId}`);
      }
    };

    // 立即尝试设置媒体流
    trySetMediaStream();
  };

  // 设置onicecandidate事件处理器
  peerConnections[userId].onicecandidate = (event) => {
    if (event.candidate) {
      // 发送ICE候选到信令服务器
      console.log(`[WebRTC] createPeerConnection - 接收到ICE候选，发送到信令服务器，用户ID: ${userId}`);
      console.log('候选类型:', event.candidate.type);
      console.log('协议:', event.candidate.protocol);
      console.log('地址:', event.candidate.address + ':' + event.candidate.port);
      console.log('候选类型:', event.candidate.candidate.includes('relay') ? 'relay (TURN)' :
        event.candidate.candidate.includes('srflx') ? 'srflx (STUN)' : 'host');

      socket.emit('ice_candidate', {
        user_id: socket.id,  // 发送者ID（当前用户）
        other_user_id: userId,  // 接收者ID（目标用户）
        candidate: event.candidate
      });
    } else {
      console.log(`[WebRTC] createPeerConnection - ICE收集完成，用户ID: ${userId}`);
    }
  };

  return peerConnections[userId];
}

// 初始化
async function init() {
  try {
    // 检查浏览器是否支持WebRTC
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.error('浏览器不支持WebRTC API');
      message.error('您的浏览器不支持视频会议功能，请使用Chrome、Firefox或Safari的最新版本');
      return;
    }

    try {
      localStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      });
    } catch (mediaError) {
      console.error('无法访问媒体设备:', mediaError);
      message.error('无法访问摄像头或麦克风，请确保已授予权限并且设备正常工作');
      // 尝试只获取音频
      try {
        localStream = await navigator.mediaDevices.getUserMedia({
          video: false,
          audio: true
        });
        message.warning('已切换到仅音频模式');
      } catch (audioError) {
        console.error('无法访问音频设备:', audioError);
        message.error('无法访问麦克风，请确保已授予权限');
        return;
      }
    }

    if (localVideo.value) {
      localVideo.value.srcObject = localStream;

      // 初始时将本地视频设为主视频
      setMainStream(localStream, 'local');

      // 为本地视频添加点击事件
      localVideo.value.addEventListener('click', () => {
        setMainStream(localStream, 'local');
      });
    }

    // 连接WebSocket
    try {
      socket = io('/', {
        transports: ['websocket'],
        path: '/api/meeting/socket.io'
      });
    } catch (socketError) {
      console.error('WebSocket连接失败:', socketError);
      message.error('连接服务器失败，请稍后再试');
      return;
    }

    // 显示自己加入会议的事件
    console.log(`[WebRTC] 初始化视频会议，房间: room1`)

    // 监听连接成功事件，在成功后显示用户信息
    socket.on('connect', () => {
      console.log(`[WebRTC] socket on connect 初始化视频会议，当前用户ID: ${socket.id}`)
      // 更新UI显示当前用户ID
      const userIdElement = document.getElementById('current-user-id');
      if (userIdElement) {
        userIdElement.textContent = socket.id;
      }

      showEvent(`${socket.id} 已加入会议`, 'join')

      console.log(`[WebRTC] emit join_room: room1`)
      socket.emit('join_room', { room: 'room1' });

      // 请求当前房间的用户列表
      console.log(`[WebRTC] emit get_users_in_room: room1`)
      socket.emit('get_users_in_room', { room: 'room1' })
    })

    // 处理房间用户列表
    socket.on('users_in_room', (data) => {
      console.log(`[WebRTC] socket on users_in_room 收到房间用户列表，共 ${data.users.length} 位用户`)

      const { users } = data
      console.log(`[WebRTC] 收到房间用户列表，共 ${users.length} 位用户`)

      // 清除旧的用户列表
      otherUserIds.value = []

      // 只添加其他用户（排除自己）
      users.forEach((userId: string) => {
        if (userId !== socket.id && !otherUserIds.value.includes(userId)) {
          otherUserIds.value.push(userId)
          console.log(`[WebRTC] 添加现有用户到列表: ${userId}`)
        }
      })

      // 更新视频列表
      if (otherUserIds.value.length > 0) {
        console.log(`[WebRTC] socket on users_in_room 当前房间[room1] 有 ${otherUserIds.value.length} 位其他用户: ${otherUserIds.value}`)

        updateVideoList();
      } else {
        console.log(`[WebRTC] socket on users_in_room 当前房间[room1] 没有其他用户!`)
      }
    })

    // 处理新用户加入
    socket.on('new_user', async (data) => {
      const otherUserId = data.user_id;
      console.log(`[WebRTC] socket on new_user 检测到新用户加入，用户ID: ${otherUserId}，当前用户ID: ${otherUserId} socket.id: ${socket.id}`)

      // 显示用户加入事件
      showEvent(`${otherUserId} 加入了会议`, 'join')

      // 添加到用户列表，避免重复添加
      if (!otherUserIds.value.includes(otherUserId)) {
        otherUserIds.value.push(otherUserId)
        console.log(`[WebRTC] socket on new_user 用户已添加到用户列表，当前用户总数: ${otherUserIds.value.length}`)
      } else {
        console.log(`[WebRTC] socket on new_user 用户 ${otherUserId} 已在列表中，跳过重复添加`)
      }

      // 创建新的PeerConnection
      console.log(`[WebRTC] socket on new_user 开始为新用户创建PeerConnection，用户ID: ${otherUserId}`)
      const pc = await createPeerConnection(otherUserId)
      console.log(`[WebRTC] socket on new_user PeerConnection创建成功，用户ID: ${otherUserId}，准备添加媒体轨道`)

      // 重要修复：将创建的PeerConnection添加到全局peerConnections对象中
      peerConnections[otherUserId] = pc;
      console.log(`[WebRTC] socket on new_user PeerConnection已添加到全局peerConnections对象中`)

      // 添加本地媒体轨道
      const trackCount = localStream.getTracks().length
      localStream.getTracks().forEach((track, index) => {
        console.log(`[WebRTC] 添加第${index + 1}/${trackCount}个媒体轨道，类型: ${track.kind}`)
        peerConnections[otherUserId].addTrack(track, localStream)
      })
      console.log(`[WebRTC] socket on new_user 所有媒体轨道添加完成`)

      // 创建并发送offer
      console.log(`[WebRTC] socket on new_user 开始创建offer`)
      const offer = await peerConnections[otherUserId].createOffer()
      console.log(`[WebRTC] socket on new_user offer创建成功，类型: ${offer.type}`)

      await peerConnections[otherUserId].setLocalDescription(offer)
      console.log(`[WebRTC] socket on new_user 本地描述设置成功，准备发送offer`)

      console.log(`[WebRTC] socket on new_user 发送offer，用户ID: ${otherUserId}`)
      socket.emit('offer', {
        offer: { type: offer.type, sdp: offer.sdp },
        user_id: socket.id,
        other_user_id: otherUserId
      });
      console.log(`[WebRTC] socket on new_user offer(connection请求）已发送至新用户，用户ID: ${otherUserId}`)

      // 更新视频列表
      updateVideoList();
    })

    // 处理offer
    socket.on('offer', async (offer) => {
      try {
        // 添加参数验证
        if (!offer || typeof offer !== 'object') {
          console.error('[WebRTC] socket on offer 收到无效的offer对象:', offer)
          return
        }
        
        const userId = offer.user_id
        const offerData = offer.offer
        
        if (!userId || !offerData) {
          console.error('[WebRTC] socket on offer 缺少必要参数: userId=', userId, 'offerData=', offerData)
          return
        }
        
        if (typeof offerData !== 'object' || !offerData.type || !offerData.sdp) {
          console.error('[WebRTC] socket on offer offer格式不正确:', offerData)
          return
        }
        
        console.log(`[WebRTC] socket on offer 接收到来自用户 ${userId} 的offer，当前用户ID: ${socket.id}`)
        console.log(`[WebRTC] socket on offer offer详情:`, {
          type: offerData.type,
          sdpLength: offerData.sdp?.length || 0,
          timestamp: new Date().toISOString(),
          otherUserId: offer.other_user_id,
          userId: userId
        })

        const pc = await createPeerConnection(userId)
        
        // 确保pc对象存在且有效
        if (!pc || typeof pc.setRemoteDescription !== 'function') {
          console.error(`[WebRTC] socket on offer PeerConnection对象无效:`, pc)
          return
        }

        // 检查当前信令状态
        const currentSignalingState = pc.signalingState
        console.log(`[WebRTC] socket on offer 当前信令状态: ${currentSignalingState}, 用户ID: ${userId}`)

        // 只有在stable状态下才能设置offer
        if (currentSignalingState === 'stable') {
          console.log(`[WebRTC] 开始设置远程描述，用户ID: ${userId}`)
          
          // 安全地创建RTCSessionDescription对象
          let sessionDescription
          try {
            sessionDescription = new RTCSessionDescription(offerData)
            console.log(`[WebRTC] socket on offer RTCSessionDescription创建成功`)
          } catch (sdpError) {
            console.error(`[WebRTC] socket on offer 创建RTCSessionDescription失败:`, sdpError)
            console.error(`[WebRTC] 失败的offer数据:`, offerData)
            return
          }

          await pc.setRemoteDescription(sessionDescription)
          console.log(`[WebRTC] socket on offer 远程描述设置成功，用户ID: ${userId}，创建answer响应`)

          // 关键修复：在创建answer之前将本地媒体轨道添加到连接中，保证双向媒体
          try {
            const sendersBefore = pc.getSenders().length;
            const tracks = localStream ? localStream.getTracks() : [];
            tracks.forEach(track => {
              const exists = pc.getSenders().some(sender => sender.track && sender.track.id === track.id);
              if (!exists) {
                pc.addTrack(track, localStream);
                console.log(`[WebRTC] socket on offer 已添加本地轨道到连接: ${track.kind}`);
              }
            });
            console.log(`[WebRTC] socket on offer 添加本地轨道完成。之前sender数量=${sendersBefore}，现在=${pc.getSenders().length}`);
          } catch (addTrackErr) {
            console.error('[WebRTC] socket on offer 添加本地轨道失败:', addTrackErr);
          }

          const answer = await pc.createAnswer()
          console.log(`[WebRTC] socket on offer answer创建成功，类型: ${answer.type}`)

          await pc.setLocalDescription(answer)
          console.log(`[WebRTC] socket on offer 本地描述设置成功，用户ID: ${userId}`)

          socket.emit('answer', {
            answer: { type: answer.type, sdp: answer.sdp },
            user_id: socket.id,
            other_user_id: userId
          })
          console.log(`[WebRTC] socket on offer answer已发送至用户 ${userId}`)
        } else {
          console.warn(`[WebRTC] socket on offer 信令状态不正确，无法设置offer: 当前状态=${currentSignalingState}, 期望状态=stable, 用户ID: ${userId}`)
          
          // 如果是have-local-offer状态，说明可能已经处理过这个offer
          if (currentSignalingState === 'have-local-offer') {
            console.log(`[WebRTC] socket on offer 连接已处于have-local-offer状态，可能已处理过此offer，用户ID: ${userId}`)
          }
        }
      } catch (error) {
        console.error(`[WebRTC] socket on offer 处理offer失败，详细错误:`, error)
        console.error(`[WebRTC] 失败的offer对象:`, offer)
        // 确保错误被捕获，防止未处理的Promise拒绝
        if (error instanceof Error) {
          console.error(`[WebRTC] 错误类型: ${error.name}, 错误消息: ${error.message}`)
        }
      }
    })

    // 处理answer
    socket.on('answer', async (answer) => {
      console.log(`[WebRTC] socket on answer 接收到来自用户 ${answer.user_id} 的answer，当前用户ID: ${socket.id}`)
      console.log(`[WebRTC] socket on answer answer详情:`, {
        type: answer.answer.type,
        sdpLength: answer.answer.sdp?.length || 0,
        timestamp: new Date().toISOString()
      })

      const pc = peerConnections[answer.user_id]
      
      // 检查PeerConnection是否存在
      if (!pc) {
        console.warn(`[WebRTC] socket on answer 未找到对应用户ID: ${answer.user_id} 的PeerConnection`)
        return
      }

      // 检查当前信令状态
      const currentSignalingState = pc.signalingState
      console.log(`[WebRTC] socket on answer 当前信令状态: ${currentSignalingState}, 用户ID: ${answer.user_id}`)

      // 只有在have-local-offer状态下才能设置answer
      if (currentSignalingState === 'have-local-offer') {
        console.log(`[WebRTC] socket on answer 准备设置answer的远程描述，连接状态: ${currentSignalingState}`)
        try {
          await pc.setRemoteDescription(new RTCSessionDescription(answer.answer))
          console.log(`[WebRTC] socket on answer answer远程描述设置成功，用户ID: ${answer.user_id}`)
          console.log(`[WebRTC] socket on answer 更新后的连接状态: ${pc.signalingState}`)
        } catch (error) {
          console.error(`[WebRTC] socket on answer 设置answer远程描述失败，用户ID: ${answer.user_id}`, error)
          
          // 如果是状态错误，记录详细信息
          if (error instanceof DOMException && error.name === 'InvalidStateError') {
            console.error(`[WebRTC] socket on answer 状态错误详情: 当前状态=${pc.signalingState}, 期望状态=have-local-offer`)
          }
        }
      } else {
        console.warn(`[WebRTC] socket on answer 信令状态不正确，无法设置answer: 当前状态=${currentSignalingState}, 期望状态=have-local-offer, 用户ID: ${answer.user_id}`)
        
        // 如果是stable状态，说明可能已经处理过这个answer
        if (currentSignalingState === 'stable') {
          console.log(`[WebRTC] socket on answer 连接已稳定，可能已处理过此answer，用户ID: ${answer.user_id}`)
        }
      }
    })

    // 处理ICE候选
    socket.on('ice_candidate', async (candidate) => {
      console.log(`[WebRTC] socket on ice_candidate 接收到来自用户 ${candidate.user_id} 的ICE候选，当前用户ID: ${socket.id}`)
      console.log(`[WebRTC] socket on ice_candidate ICE候选详情:`, {
        candidateType: candidate.candidate.candidate?.split(' ')[7] || 'unknown',
        foundation: candidate.candidate.foundation || 'unknown',
        priority: candidate.candidate.priority || 'unknown',
        timestamp: new Date().toISOString()
      })

      try {
        if (peerConnections[candidate.user_id]) {
          console.log(`[WebRTC] socket on ice_candidate 准备添加ICE候选，目标用户ID: ${candidate.user_id}`)
          await peerConnections[candidate.user_id].addIceCandidate(
            new RTCIceCandidate(candidate.candidate)
          )
          console.log(`[WebRTC] socket on ice_candidate ICE候选添加成功，目标用户ID: ${candidate.user_id}`)
        } else {
          console.warn(`[WebRTC] socket on ice_candidate 未找到对应用户ID: ${candidate.user_id} 的PeerConnection，无法添加ICE候选`)
        }
      } catch (error) {
        console.error(`[WebRTC] socket on ice_candidate 添加ICE候选失败，用户ID: ${candidate.user_id}`, error)
      }
    })

    // 处理消息
    socket.on('message', (messageData) => {
      const { user_id, content } = messageData
      console.log(`[WebRTC] socket on message 接收到来自用户 ${user_id} 的消息:`, {
        content: content,
        length: content.length,
        timestamp: new Date().toISOString()
      })

      // 检查消息是否来自当前用户，如果不是则显示
      if (user_id !== socket.id) {
        if (messageList.value) {
          console.log(`[WebRTC] socket on message 准备在消息列表中显示消息`)
          const li = document.createElement('li')
          li.textContent = `${user_id}: ${content}`
          li.setAttribute('data-user-id', user_id)
          messageList.value.querySelector('ul')?.appendChild(li)
          messageList.value.scrollTop = messageList.value.scrollHeight
          console.log(`[WebRTC] socket on message 消息显示成功，消息列表已更新并滚动到底部`)
        } else {
          console.warn(`[WebRTC] socket on message 消息列表DOM元素未找到，无法显示消息`)
        }

        // 在事件日志中显示消息事件
        showEvent(`${user_id} 发送了消息`, 'message')
      }
    })

    // 处理用户离开
    socket.on('user_left', (data) => {
      const { user_id } = data
      console.log(`[WebRTC] socket on user_left 用户离开会议，用户ID: ${user_id}`)

      // 从用户列表中移除
      const index = otherUserIds.value.indexOf(user_id)
      if (index > -1) {
        otherUserIds.value.splice(index, 1)
      }

      // 关闭对应的PeerConnection
      if (peerConnections[user_id]) {
        // 调用清理函数处理资源释放
        cleanupPeerConnection(user_id);
      }

      // 显示用户离开事件
      showEvent(`${user_id}... 离开了会议`, 'leave')

      // 更新视频列表
      updateVideoList();
    })
  } catch (error) {
    console.error('[WebRTC] 初始化错误:', error);
    message.error('初始化视频会议失败: ' + error);
  }
}

// 显示事件日志
function showEvent(message: string, type: 'join' | 'leave' | 'message') {
  console.log(`[WebRTC] showEvent 显示事件日志: ${message}`)

  if (eventsList.value) {
    const li = document.createElement('li')
    li.classList.add(type)

    // 尝试解析消息中的用户ID
    let formattedMessage = `[${new Date().toLocaleTimeString()}] `;

    // 使用正则表达式匹配Socket.IO风格的用户ID
    const userIdRegex = /([a-zA-Z0-9_-]{10,})/;
    const userIdMatch = message.match(userIdRegex);

    if (userIdMatch && userIdMatch[1]) {
      const userId = userIdMatch[1];

      // 替换用户ID为可点击的span元素
      const parts = message.split(userId);
      formattedMessage += parts[0];

      const userIdSpan = document.createElement('span');
      userIdSpan.textContent = userId;
      userIdSpan.classList.add('clickable-user-id');
      userIdSpan.dataset.userId = userId;

      // 添加点击事件以跳转到与该用户的通信
      userIdSpan.addEventListener('click', (e) => {
        e.stopPropagation();
        console.log(`[WebRTC] 点击用户ID: ${userId}，尝试获取对话`);

        // 滚动到消息列表，并高亮显示与该用户相关的消息
        if (messageList.value) {
          messageList.value.scrollIntoView({ behavior: 'smooth' });

          // 高亮显示该用户的消息
          const userMessages = messageList.value.querySelectorAll(`li[data-user-id="${userId}"]`);
          userMessages.forEach(msg => {
            (msg as HTMLElement).style.backgroundColor = '#e6f7ff';
            setTimeout(() => {
              (msg as HTMLElement).style.backgroundColor = '';
            }, 2000);
          });

          // 如果有消息，滚动到最新的一条
          if (userMessages.length > 0) {
            userMessages[userMessages.length - 1].scrollIntoView({ behavior: 'smooth' });
          }
        }
      });

      li.appendChild(document.createTextNode(formattedMessage));
      li.appendChild(userIdSpan);
      li.appendChild(document.createTextNode(parts[1] || ''));
    } else {
      li.textContent = formattedMessage + message;
    }

    eventsList.value.querySelector('ul')?.appendChild(li);
    eventsList.value.scrollTop = eventsList.value.scrollHeight;
  }
}

// 发送消息
function sendMessage() {
  if (messageInput.value.trim()) {
    const messageData = {
      user_id: socket.id,
      content: messageInput.value.trim()
    }

    socket.emit('message', messageData)

    // 立即在本地消息列表显示自己发送的消息
    if (messageList.value) {
      const li = document.createElement('li')
      li.textContent = `${socket.id}: ${messageInput.value.trim()}`
      li.setAttribute('data-user-id', socket.id)
      li.classList.add('own-message')
      messageList.value.querySelector('ul')?.appendChild(li)
      messageList.value.scrollTop = messageList.value.scrollHeight
    }

    messageInput.value = ''
  }
}

// 尝试播放视频的辅助函数
function attemptToPlayVideo(videoElement: HTMLVideoElement, userId: string) {
  console.log(`[WebRTC] attemptToPlayVideo 尝试播放视频 (用户 ${userId})`);
  console.log(`[WebRTC] attemptToPlayVideo 视频元素信息: muted=${videoElement.muted}, autoplay=${videoElement.hasAttribute('autoplay')}, playsinline=${videoElement.hasAttribute('playsinline')}`);

  // 添加Promise超时处理，防止无限pending
  const playWithTimeout = (videoEl: HTMLVideoElement, timeoutMs = 5000): Promise<void> => {
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error(`视频播放Promise超时 (${timeoutMs}ms)，状态: pending`));
      }, timeoutMs);

      videoEl.play().then(() => {
        clearTimeout(timeoutId);
        resolve();
      }).catch(error => {
        clearTimeout(timeoutId);
        reject(error);
      });
    });
  };

  // 首先尝试直接播放
  playWithTimeout(videoElement)
    .then(() => {
      console.log(`[WebRTC] attemptToPlayVideo 视频直接播放成功 (用户 ${userId})`);
      // 监听视频事件以确保播放正常
      videoElement.onplaying = () => {
        console.log(`[WebRTC] attemptToPlayVideo 视频开始播放 (用户 ${userId})`);
        videoElement.onplaying = null; // 避免重复触发
      };
      
      videoElement.onended = () => {
        console.warn(`[WebRTC] attemptToPlayVideo 视频意外结束播放 (用户 ${userId})`);
        videoElement.onended = null;
      };
    })
    .catch(err => {
      console.warn(`[WebRTC] attemptToPlayVideo 视频直接播放失败 (用户 ${userId}):`, err);

      // 尝试静音播放，这通常可以绕过自动播放限制
      const originalMuted = videoElement.muted;
      videoElement.muted = true;
      
      playWithTimeout(videoElement)
        .then(() => {
          console.log(`[WebRTC] attemptToPlayVideo 视频成功以静音模式播放 (用户 ${userId})`);
          // 保存播放状态，以便在用户交互后取消静音
          const handleUserInteraction = () => {
            try {
              videoElement.muted = originalMuted;
              console.log(`[WebRTC] attemptToPlayVideo 用户交互后尝试取消视频静音 (用户 ${userId})`);
            } catch (e) {
              console.error(`[WebRTC] attemptToPlayVideo 用户交互后取消视频静音失败 (用户 ${userId}):`, e);
            }
            document.removeEventListener('click', handleUserInteraction);
            document.removeEventListener('keydown', handleUserInteraction);
          };

          // 监听用户交互事件，以便在用户交互后取消静音
          document.addEventListener('click', handleUserInteraction);
          document.addEventListener('keydown', handleUserInteraction);
        })
        .catch(err => {
          console.error(`[WebRTC] attemptToPlayVideo 视频静音播放也失败 (用户 ${userId}):`, err);

          // 最后尝试在用户交互时播放
          const handleUserClick = () => {
            videoElement.play().then(() => {
              console.log(`[WebRTC] attemptToPlayVideo 用户交互后播放成功 (用户 ${userId})`);
            }).catch(err => {
              console.error(`[WebRTC] attemptToPlayVideo 用户交互后播放仍失败 (用户 ${userId}):`, err);
              // 尝试强制设置视频属性并重新播放
              try {
                videoElement.autoplay = true;
                videoElement.playsInline = true;
                console.log(`[WebRTC] attemptToPlayVideo 已设置强制播放属性 (用户 ${userId})`);
              } catch (e) {
                console.error(`[WebRTC] attemptToPlayVideo 设置强制播放属性失败 (用户 ${userId}):`, e);
              }
            });
            document.removeEventListener('click', handleUserClick);
          };

          document.addEventListener('click', handleUserClick, { once: true });
          console.log(`[WebRTC] attemptToPlayVideo 已设置用户交互时自动播放视频 (用户 ${userId})`);
        });
    });
}

// 切换音频
function toggleAudio() {
  const audioTrack = localStream.getAudioTracks()[0]
  if (audioTrack) {
    audioTrack.enabled = !audioTrack.enabled
    isAudioMuted.value = !audioTrack.enabled
  }
}

// 切换视频
function toggleVideo() {
  const videoTrack = localStream.getVideoTracks()[0]
  if (videoTrack) {
    videoTrack.enabled = !videoTrack.enabled
    isVideoMuted.value = !videoTrack.enabled
  }
}

// 离开会议室
function leaveMeeting() {
  try {
    console.log('[WebRTC] leaveMeeting 正在离开会议室...')

    // 显示离开事件
    showEvent(`${socket.id.substring(0, 8)}... 主动离开了会议室`, 'leave')

    // 断开WebSocket连接
    if (socket) {
      socket.disconnect()
      console.log('[WebRTC] leaveMeeting WebSocket连接已断开')
    }

    // 关闭所有PeerConnection
    Object.keys(peerConnections).forEach(userId => {
      cleanupPeerConnection(userId);
    });
    peerConnections = {};
    console.log('[WebRTC] leaveMeeting 所有PeerConnection已关闭');

    // 停止本地媒体流
    if (localStream) {
      localStream.getTracks().forEach(track => track.stop())
      console.log('[WebRTC] leaveMeeting 本地媒体流已停止')
    }

    // 清空其他用户列表
    otherUserIds.value = []

    // 更新视频列表
    updateVideoList()

    // 更新状态
    isInMeeting.value = false

    message.success('已成功离开会议室')
  } catch (error) {
    console.error('[WebRTC] leaveMeeting 离开会议室失败:', error)
    message.error('leaveMeeting 离开会议室失败: ' + error)
  }
}

// 加入会议室
async function joinMeeting() {
  try {
    console.log('[WebRTC] joinMeeting 正在加入会议室...')

    // 重置状态
    isInMeeting.value = true

    // 重新初始化init
    console.warn('[WebRTC] joinMeeting 重新初始化init...')
    await init()

    message.success('leaveMeeting 已成功加入会议室')
  } catch (error) {
    console.error('[WebRTC] joinMeeting 加入会议室失败:', error)
    message.error('joinMeeting 加入会议室失败: ' + error)
    isInMeeting.value = false
  }
}

// 改进的cleanupPeerConnection函数
function cleanupPeerConnection(userId: string) {
  console.log(`[WebRTC] cleanupPeerConnection - 开始清理用户 ${userId} 的PeerConnection资源`);

  // 首先停止视频播放，避免"fetching process aborted"错误
  const userContainer = document.querySelector(`.user-video-container[data-user-id="${userId}"]`);
  if (userContainer) {
    const videoElement = userContainer.querySelector('.remote-video') as HTMLVideoElement;
    if (videoElement) {
      try {
        // 先暂停视频播放
        if (!videoElement.paused) {
          videoElement.pause();
          console.log(`[WebRTC] cleanupPeerConnection - 视频已暂停，用户ID: ${userId}`);
        }
        
        // 清空srcObject
        if (videoElement.srcObject) {
          const stream = videoElement.srcObject as MediaStream;
          // 停止所有轨道
          stream.getTracks().forEach(track => track.stop());
          // 清空视频元素的srcObject
          videoElement.srcObject = null;
          console.log(`[WebRTC] cleanupPeerConnection - 已重置视频元素的媒体流，用户ID: ${userId}`);
        }
      } catch (error) {
        console.error(`[WebRTC] cleanupPeerConnection - 清理视频元素时发生错误:`, error);
      }
    }
  }

  // 检查并关闭PeerConnection
  if (peerConnections[userId]) {
    try {
      peerConnections[userId].close();
      console.log(`[WebRTC] cleanupPeerConnection - PeerConnection已关闭，用户ID: ${userId}`);
    } catch (error) {
      console.error(`[WebRTC] cleanupPeerConnection - 关闭PeerConnection时发生错误:`, error);
    }
    delete peerConnections[userId];
  }

  // 清理状态跟踪
  connectionStates.delete(userId);

  // 清理流缓存
  streamCache.delete(userId);

  console.log(`[WebRTC] cleanupPeerConnection - 资源清理完成，用户ID: ${userId}`);
}

// 改进的startPeerConnection函数
async function startPeerConnection(userId: string, stream: MediaStream) {
  console.log(`[WebRTC] startPeerConnection - 开始启动与用户 ${userId} 的连接`);

  try {
    // 检查PeerConnection是否存在
    if (!peerConnections[userId]) {
      console.log(`[WebRTC] startPeerConnection - PeerConnection不存在，先创建，用户ID: ${userId}`);
      await createPeerConnection(userId);

      if (!peerConnections[userId]) {
        throw new Error(`创建PeerConnection失败，用户ID: ${userId}`);
      }
    }

    const pc = peerConnections[userId];

    // 检查当前信令状态
    const currentSignalingState = pc.signalingState;
    console.log(`[WebRTC] startPeerConnection - 当前信令状态: ${currentSignalingState}, 用户ID: ${userId}`);
    
    // 避免在已有未完成的offer/answer时创建新offer
    if (['have-local-offer', 'have-remote-offer'].includes(currentSignalingState)) {
      console.log(`[WebRTC] startPeerConnection - 连接已处于协商中状态(${currentSignalingState})，跳过创建新offer，用户ID: ${userId}`);
      return true;
    }

    // 添加媒体轨道
    const trackCount = stream.getTracks().length;
    const sortedTracks = [...stream.getTracks()].sort((a, b) => {
      if (a.kind === 'audio' && b.kind === 'video') return -1;
      if (a.kind === 'video' && b.kind === 'audio') return 1;
      return 0;
    });

    sortedTracks.forEach((track, index) => {
      // 检查轨道是否已经添加到PeerConnection中
      const existingSender = pc.getSenders().find(sender =>
        sender.track && sender.track.id === track.id
      );

      if (!existingSender) {
        console.log(`[WebRTC] startPeerConnection - 添加第${index + 1}/${trackCount}个媒体轨道，类型: ${track.kind}`);
        pc.addTrack(track, stream);
      } else {
        console.log(`[WebRTC] startPeerConnection - 跳过已存在的媒体轨道，类型: ${track.kind}，ID: ${track.id}`);
      }
    });
    
    console.log(`[WebRTC] startPeerConnection - 开始创建offer，用户ID: ${userId}`);
    const offer = await pc.createOffer({
      offerToReceiveAudio: true,
      offerToReceiveVideo: true,
      iceRestart: currentSignalingState === 'stable' // 仅在稳定状态下允许ICE重启
    });

    console.log(`[WebRTC] startPeerConnection - offer创建成功，类型: ${offer.type}，用户ID: ${userId}`);

    await pc.setLocalDescription(offer);
    console.log(`[WebRTC] startPeerConnection - 本地描述设置成功，准备发送offer，用户ID: ${userId}`);

    socket.emit('offer', {
      offer: { type: offer.type, sdp: offer.sdp },
      user_id: socket.id,
      other_user_id: userId
    });

    console.log(`[WebRTC] startPeerConnection - offer已从socket.id ${socket.id} 发送至用户 ${userId}`);
    return true;
  } catch (error) {
    console.error(`[WebRTC] startPeerConnection - 启动连接失败，用户ID: ${userId}`, error);
    return false;
  }
}

// 更新视频列表中的选中状态样式
function updateSelectedVideoStyle() {
  // 移除所有视频的选中样式
  const allVideos = document.querySelectorAll('.video-list video');
  allVideos.forEach(video => {
    video.classList.remove('selected');
  });
  
  // 为当前选中的视频添加样式
  if (selectedUserId.value === 'local' && localVideo.value) {
    localVideo.value.classList.add('selected');
  } else if (selectedUserId.value && selectedUserId.value !== 'local') {
    const selectedVideo = document.querySelector(`.remote-video[data-user-id="${selectedUserId.value}"]`);
    if (selectedVideo) {
      selectedVideo.classList.add('selected');
    }
  }
}

// 生命周期钩子
onMounted(() => {
  init()
})

onUnmounted(() => {
  // 清理资源
  localStream?.getTracks().forEach(track => track.stop())
  Object.values(peerConnections).forEach(pc => pc.close())
  socket?.disconnect()
})
</script>




<style scoped>
.meeting-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 20px;
  box-sizing: border-box;
}

.video-container {
  display: flex;
  flex: 1;
  gap: 20px;
  margin-bottom: 20px;
}

.main-video {
  flex: 3;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow-y: auto;
}

.video-list video {
  width: 100%;
  border-radius: 4px;
  background: #000;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.video-list video:hover {
  transform: scale(1.02);
}

.video-list video.selected {
  border-color: #4CAF50;
  box-shadow: 0 0 8px rgba(76, 175, 80, 0.6);
}

.main-video video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.control-panel {
  display: flex;
  gap: 20px;
  height: 200px;
}

.message-panel {
  flex: 2;
  display: flex;
  flex-direction: column;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.events-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.events-panel h4 {
  margin: 0;
  padding: 10px;
  background: #f0f0f0;
  border-bottom: 1px solid #ddd;
  font-size: 14px;
}

.events-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.events-list ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.events-list li {
  margin-bottom: 6px;
  padding: 6px;
  font-size: 12px;
  border-radius: 4px;
}

.events-list li.join {
  background: #e8f5e9;
  color: #2e7d32;
}

.events-list li.leave {
  background: #ffebee;
  color: #c62828;
}

.events-list li.message {
  background: #e3f2fd;
  color: #1565c0;
}

/* 可点击用户ID样式 */
.clickable-user-id {
  color: #1890ff;
  text-decoration: underline;
  cursor: pointer;
  padding: 0 2px;
  border-radius: 2px;
  transition: background-color 0.2s;
}

.clickable-user-id:hover {
  background-color: rgba(24, 144, 255, 0.1);
}

.user-info-panel {
  flex: 0.5;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 10px;
}

.user-info-panel h4 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.user-info-content p {
  margin: 4px 0;
  font-size: 13px;
  color: #666;
}

.user-info-content span {
  color: #1890ff;
  font-family: monospace;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.message-list ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.message-list li {
  margin-bottom: 8px;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
}

.message-list li.own-message {
  background: #e3f2fd;
  color: #1565c0;
  text-align: right;
}

.message-list li[data-user-id] {
  position: relative;
}

.message-input {
  display: flex;
  padding: 10px;
  border-top: 1px solid #ddd;
}

.message-input input {
  flex: 1;
  margin-right: 10px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.media-controls {
  flex: 1;
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.media-controls button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  background: #f5f5f5;
  cursor: pointer;
  transition: all 0.3s;
}

.media-controls button:hover {
  background: #e0e0e0;
}

.media-controls button.active {
  background: #4CAF50;
  color: white;
}

/* 远程视频样式 */
.remote-video {
  width: 45%;
  height: auto;
  object-fit: cover;
  border-radius: 8px;
  z-index: 1;
  position: relative;
  background: #000;
  transition: all 0.3s ease;
}

.remote-video:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* 修复选中视频样式 - 本地视频和远程视频都能应用选中样式 */
.video-list>video.selected {
  border-color: #4CAF50;
  box-shadow: 0 0 8px rgba(76, 175, 80, 0.6);
}

.video-list .remote-video.selected {
  border: 2px solid #4CAF50;
  box-shadow: 0 0 8px rgba(76, 175, 80, 0.6);
}

/* 远程用户头像样式 */
.remote-user-avatar {
  width: 45%;
  height: auto;
  border-radius: 8px;
  z-index: 1;
  position: relative;
  background: #f0f0f0;
  transition: all 0.3s ease;
  object-fit: cover;
}

.remote-user-avatar:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
</style>