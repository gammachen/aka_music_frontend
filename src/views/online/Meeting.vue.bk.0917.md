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

// 确保视频列表正确显示所有远程用户视频和备用图片
function updateVideoList() {
  if (!remoteVideos.value) return;
  
  console.log(`[WebRTC] updateVideoList - 开始更新视频列表，用户数量: ${otherUserIds.value.length}`);
  
  // 获取当前存在的用户容器ID
  const existingUserIds = new Set<string>();
  const currentUserContainers = remoteVideos.value.querySelectorAll('.user-video-container');
  currentUserContainers.forEach(container => {
    const userId = container.getAttribute('data-user-id');
    if (userId) existingUserIds.add(userId);
  });
  
  // 为每个活跃用户创建或更新用户容器（包含视频和图片）
  otherUserIds.value.forEach((userId, index) => {
    let userContainer = document.querySelector(`.user-video-container[data-user-id="${userId}"]`) as HTMLDivElement | null;
    let videoElement: HTMLVideoElement | null = null;
    let imageElement: HTMLImageElement | null = null;
    
    // 如果用户容器不存在，创建新的
    if (!userContainer) {
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
      videoElement.muted = false;
      videoElement.style.width = '45%';
      videoElement.style.height = 'auto';
      videoElement.classList.add('remote-video');
      videoElement.id = `${userId}-video`;
      videoElement.setAttribute('data-user-id', userId); // 添加data-user-id属性，便于选择
      videoElement.setAttribute('data-video', '2'); // 与HTML结构保持一致
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
      imageElement.style.opacity = '1'; // 始终显示图片
      
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
      
      // 尝试从peerConnections获取已有的媒体流
      if (peerConnections[userId]) {
        const pc = peerConnections[userId];
        // 获取连接中的所有接收流
        const receivers = pc.getReceivers();
        const tracks = receivers.map(receiver => receiver.track).filter(track => track !== null);
        
        if (tracks.length > 0) {
          try {
            // 创建一个新的MediaStream并添加所有轨道
            const stream = new MediaStream(tracks);
            videoElement.srcObject = stream;
            console.log(`[WebRTC] updateVideoList - 成功从peerConnections获取媒体流并设置到视频元素，用户ID: ${userId}`);
          } catch (error) {
            console.error(`[WebRTC] updateVideoList - 从peerConnections设置媒体流失败:`, error);
          }
        }
      }
      
      // 添加点击事件到容器
      userContainer.addEventListener('click', () => {
        console.log(`[WebRTC] 用户容器被点击，尝试设置为主视频流，用户ID: ${userId}`);
        if (videoElement && videoElement.srcObject) {
          setMainStream(videoElement.srcObject as MediaStream, userId);
        } else {
          // 尝试从peerConnections重新获取媒体流
          if (peerConnections[userId]) {
            console.log(`[WebRTC] 用户容器被点击，尝试从peerConnections获取媒体流，用户ID: ${userId}`);
            const pc = peerConnections[userId];
            const receivers = pc.getReceivers();
            const tracks = receivers.map(receiver => receiver.track).filter(track => track !== null);
            
            if (tracks.length > 0) {
              try {
                const stream = new MediaStream(tracks);
                videoElement.srcObject = stream;
                setMainStream(stream, userId);
                console.log(`[WebRTC] 用户容器被点击，成功从peerConnections获取媒体流，用户ID: ${userId}`);
                return;
              } catch (error) {
                console.error(`[WebRTC] 从peerConnections获取媒体流失败:`, error);
              }
            } else {
              console.warn(`[WebRTC] peerConnections中没有找到可用的媒体轨道，用户ID: ${userId}`);
            }
          } else {
            console.warn(`[WebRTC] 未找到对应用户ID的peerConnection: ${userId}`);
          }
          console.log(`[WebRTC] 用户容器被点击，但暂无视频流，用户ID: ${userId}`);
        }
      });
      
      remoteVideos.value.appendChild(userContainer);
      console.log(`[WebRTC] updateVideoList - 为用户 ${userId} 创建了用户容器（包含视频和图片），data-video: ${index + 2}`);
    } else {
      // 更新现有用户容器的data-video属性
      userContainer.setAttribute('data-video', String(index + 2));
      videoElement = userContainer.querySelector(`.remote-video`);
      imageElement = userContainer.querySelector(`.remote-user-avatar`);
      // 确保视频元素有必要的属性
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
      }
      console.log(`[WebRTC] updateVideoList - 更新用户 ${userId} 的用户容器，data-video: ${index + 2}`);
    }
    
    // 移除排他显示逻辑，使视频和图片始终并排显示
      if (videoElement && imageElement) {
        imageElement.style.opacity = '1'; // 始终显示图片
        videoElement.style.opacity = '1'; // 始终显示视频
      }
    
    // 从存在列表中移除，剩下的就是需要删除的
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

// 创建RTCPeerConnection
async function createPeerConnection(userId: string) {
  console.log(`[WebRTC] createPeerConnection - 开始为用户创建连接，用户ID: ${userId}`)
  
  if (!peerConnections[userId]) {
    console.log(`[WebRTC] createPeerConnection - 用户 ${userId} 不存在PeerConnection，创建新的连接`)
    
    // 创建PeerConnection实例
    console.log(`[WebRTC] createPeerConnection - 初始化RTCPeerConnection，使用Google STUN服务器`)
    peerConnections[userId] = new RTCPeerConnection({
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' }
      ]
    })
    console.log(`[WebRTC] createPeerConnection - RTCPeerConnection创建成功`)

    // 设置ontrack事件处理器
    console.log(`[WebRTC] createPeerConnection - 设置ontrack事件处理器，用于接收远程媒体流`)
    peerConnections[userId].ontrack = (event) => {
      console.log(`[WebRTC] createPeerConnection - 接收到来自用户 ${userId} 的媒体轨道事件`)
      
      // 确保事件包含有效的流
      if (!event.streams || event.streams.length === 0) {
        console.warn(`[WebRTC] createPeerConnection - 接收到ontrack事件，但没有可用的媒体流`)
        return;
      }
      
      const stream = event.streams[0]; // 只处理第一个流
      console.log(`[WebRTC] createPeerConnection - 检测到媒体流，包含 ${stream.getTracks().length} 个轨道`);
      
      // 检查媒体流中是否包含视频轨道
      const videoTracks = stream.getVideoTracks();
      const audioTracks = stream.getAudioTracks();
      console.log(`[WebRTC] createPeerConnection - 媒体流包含 ${videoTracks.length} 个视频轨道和 ${audioTracks.length} 个音频轨道`);
      
      // 确保用户在otherUserIds中
      if (!otherUserIds.value.includes(userId)) {
        otherUserIds.value.push(userId);
        console.log(`[WebRTC] createPeerConnection - 将用户 ${userId} 添加到用户列表`);
        // 触发视频列表更新
        updateVideoList();
      }
      
      // 尝试多次设置媒体流，确保视频元素已创建
      const MAX_RETRIES = 8; // 增加重试次数
      let retries = 0;
      
      const trySetMediaStream = () => {
        // 找到用户容器
        const userContainer = document.querySelector(`.user-video-container[data-user-id="${userId}"]`) as HTMLDivElement;
        // 找到容器内的视频元素
        const videoElement = userContainer ? userContainer.querySelector('.remote-video') as HTMLVideoElement : null;
        // 找到容器内的图片元素
        const imageElement = userContainer ? userContainer.querySelector('.remote-user-avatar') as HTMLImageElement : null;
        
        if (videoElement && imageElement) {
          try {
            // 检查当前是否已有相同的流
            if (videoElement.srcObject !== stream) {
              // 移除所有事件监听器，避免重复监听
              const newVideoElement = videoElement.cloneNode(true) as HTMLVideoElement;
              // 确保新视频元素具有正确的自动播放和内联播放属性
              newVideoElement.autoplay = true;
              newVideoElement.playsInline = true;
              newVideoElement.muted = false;
              videoElement.parentNode?.replaceChild(newVideoElement, videoElement);
              
              // 添加媒体流事件监听
              stream.addEventListener('addtrack', () => {
                console.log(`[WebRTC] createPeerConnection - 用户 ${userId} 的媒体流添加了新轨道`);
                // 移除排他显示逻辑，使视频和图片始终并排显示
                if (imageElement && newVideoElement) {
                  imageElement.style.opacity = '1';
                  newVideoElement.style.opacity = '1';
                }
              });
              
              stream.addEventListener('removetrack', () => {
                console.log(`[WebRTC] createPeerConnection - 用户 ${userId} 的媒体流移除了轨道`);
                // 移除排他显示逻辑，使视频和图片始终并排显示
                  if (imageElement && newVideoElement) {
                    imageElement.style.opacity = '1';
                    newVideoElement.style.opacity = '1';
                  }
              });
              
              // 设置媒体流到新的视频元素
              newVideoElement.srcObject = stream;
              
              // 添加视频元素事件监听
              newVideoElement.addEventListener('loadedmetadata', () => {
                console.log(`[WebRTC] createPeerConnection - 用户 ${userId} 的视频元数据已加载，准备播放，显示视频，隐藏图片`);
                // 强制触发播放
                attemptToPlayVideo(newVideoElement, userId);
                if (imageElement) {
                  imageElement.style.opacity = '1';
                  newVideoElement.style.opacity = '1';
                }
              });
              
              newVideoElement.addEventListener('playing', () => {
                console.log(`[WebRTC] createPeerConnection - 用户 ${userId} 的视频正在播放，显示视频，隐藏图片`);
                if (imageElement) {
                  imageElement.style.opacity = '1';
                  newVideoElement.style.opacity = '1';
                }
              });
              
              newVideoElement.addEventListener('pause', () => {
                console.log(`[WebRTC] createPeerConnection - 用户 ${userId} 的视频暂停，检查视频轨道状态`);
                const currentVideoTracks = stream.getVideoTracks();
                if (currentVideoTracks.length === 0 && imageElement) {
                  imageElement.style.opacity = '1';
                  newVideoElement.style.opacity = '0';
                }
              });
              
              newVideoElement.addEventListener('error', (err) => {
                console.error(`[WebRTC] createPeerConnection - 用户 ${userId} 的视频播放错误:`, err);
              });
              
              console.log(`[WebRTC] createPeerConnection - 成功为用户 ${userId} 设置媒体流并添加事件监听`);
            } else {
              console.log(`[WebRTC] createPeerConnection - 用户 ${userId} 的视频元素已包含相同的媒体流，无需更新`);
              // 即使流相同，也检查播放状态
              if (videoElement.paused) {
                console.log(`[WebRTC] createPeerConnection - 视频元素处于暂停状态，尝试恢复播放`);
                attemptToPlayVideo(videoElement, userId);
              }
            }
          } catch (error) {
            console.error(`[WebRTC] createPeerConnection - 设置媒体流时出错:`, error);
          }
        } else if (retries < MAX_RETRIES) {
          // 如果未找到视频元素，重试
          retries++;
          console.log(`[WebRTC] createPeerConnection - 尝试 ${retries}/${MAX_RETRIES}: 未找到用户 ${userId} 的用户容器或视频元素，将重试`);
          setTimeout(trySetMediaStream, 300 * retries); // 递增延迟
        } else {
          console.error(`[WebRTC] createPeerConnection - 达到最大重试次数，无法为用户 ${userId} 设置媒体流`);
          // 作为最后的备选方案，尝试直接创建用户容器并添加到DOM
          createUserContainerFallback(userId, stream);
        }
      };
      
      // 创建备选用户容器的函数
      const createUserContainerFallback = (userId: string, stream: MediaStream) => {
        console.log(`[WebRTC] createPeerConnection - 执行备选方案，直接创建用户容器，用户ID: ${userId}`);
        try {
          if (remoteVideos.value) {
            // 创建用户容器
            const fallbackContainer = document.createElement('div');
            fallbackContainer.classList.add('user-video-container');
            fallbackContainer.classList.add('fallback-container'); // 添加特殊类名便于识别
            fallbackContainer.setAttribute('data-user-id', userId);
            fallbackContainer.setAttribute('data-video', String(otherUserIds.value.length + 1));
            fallbackContainer.id = `${userId}-container-fallback`;
            fallbackContainer.style.position = 'relative';
            fallbackContainer.style.width = '100%';
            fallbackContainer.style.height = '100%';
            fallbackContainer.style.display = 'flex';
            fallbackContainer.style.flexDirection = 'row';
            fallbackContainer.style.alignItems = 'center';
            fallbackContainer.style.justifyContent = 'space-around';
            fallbackContainer.style.margin = '5px';
            fallbackContainer.style.padding = '5px';
            fallbackContainer.style.borderRadius = '8px';
            fallbackContainer.style.backgroundColor = '#f0f0f0';
            fallbackContainer.style.cursor = 'pointer';
            
            // 创建视频元素
            const fallbackVideo = document.createElement('video');
            fallbackVideo.autoplay = true;
            fallbackVideo.playsInline = true;
            fallbackVideo.muted = false;
            fallbackVideo.style.width = '100%';
            fallbackVideo.style.height = 'auto';
            fallbackVideo.classList.add('remote-video');
            fallbackVideo.id = `${userId}-video-fallback`;
            fallbackVideo.setAttribute('data-user-id', userId); // 添加data-user-id属性，便于选择
            fallbackVideo.setAttribute('data-video', '2'); // 与HTML结构保持一致
            fallbackVideo.style.borderRadius = '8px';
            fallbackVideo.style.zIndex = '2';
            fallbackVideo.style.position = 'relative';
            fallbackVideo.srcObject = stream;
          
          // 添加加载事件处理，确保视频能正常播放
          fallbackVideo.addEventListener('loadedmetadata', () => {
            console.log(`[WebRTC] 备选视频元素loadedmetadata事件触发，用户ID: ${userId}`);
            fallbackVideo.play().catch(err => {
              console.error(`[WebRTC] 备选视频播放失败:`, err);
            });
          });
          
          // 添加点击事件
          fallbackVideo.addEventListener('click', (e) => {
            e.stopPropagation(); // 防止事件冒泡
            if (fallbackVideo.srcObject) {
              setMainStream(fallbackVideo.srcObject as MediaStream, userId);
            }
          });
            
            // 创建备用图片元素
              const fallbackImage = document.createElement('img');
              // fallbackImage.src = `https://api.dicebear.com/7.x/avataaars/svg?seed=${userId}`;
              fallbackImage.src = `/static/def/01.jpeg`;
              fallbackImage.style.width = '45%';
              fallbackImage.style.height = 'auto';
              fallbackImage.classList.add('remote-user-avatar');
              fallbackImage.id = `${userId}-avatar-fallback`;
              fallbackImage.style.position = 'relative';
              fallbackImage.style.borderRadius = '8px';
              fallbackImage.style.zIndex = '1';
              fallbackImage.style.opacity = '1'; // 始终显示图片
              fallbackImage.style.marginRight = '10px'; // 添加右边距，使图片和视频更好地并排显示
              fallbackImage.style.objectFit = 'cover'; // 确保图片填充容器且不变形
            
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
            fallbackContainer.appendChild(fallbackImage);
            fallbackContainer.appendChild(fallbackVideo);
            fallbackContainer.appendChild(userIdLabel);
            
            // 添加点击事件
            fallbackContainer.addEventListener('click', () => {
              console.log(`[WebRTC] 备选容器被点击，尝试设置为主视频流，用户ID: ${userId}`);
              if (fallbackVideo.srcObject) {
                setMainStream(fallbackVideo.srcObject as MediaStream, userId);
              }
            });
            
            // 尝试播放视频
            fallbackVideo.play().catch(err => {
              console.error(`[WebRTC] createPeerConnection - 备选视频播放失败:`, err);
            });
            
            // 添加视频事件监听
            fallbackVideo.addEventListener('loadedmetadata', () => {
              console.log(`[WebRTC] createPeerConnection - 备选视频元数据已加载，显示视频和图片`);
              fallbackImage.style.opacity = '1';
              fallbackVideo.style.opacity = '1';
            });
            
            fallbackVideo.addEventListener('play', () => {
              console.log(`[WebRTC] createPeerConnection - 备选视频开始播放，显示视频和图片`);
              fallbackImage.style.opacity = '1';
              fallbackVideo.style.opacity = '1';
            });
            
            remoteVideos.value.appendChild(fallbackContainer);
            console.log(`[WebRTC] createPeerConnection - 备选用户容器已添加到DOM`);
          }
        } catch (error) {
          console.error(`[WebRTC] createPeerConnection - 创建备选用户容器失败:`, error);
        }
      };
      
      // 立即尝试设置媒体流
      trySetMediaStream();
    }

    // 设置onicecandidate事件处理器
    console.log(`[WebRTC] createPeerConnection - 设置onicecandidate事件处理器，用于发送ICE候选`)
    peerConnections[userId].onicecandidate = (event) => {
      if (event.candidate) {
        console.log(`[WebRTC] createPeerConnection - 生成ICE候选，准备发送给用户 ${userId}`)
        socket.emit('ice_candidate', {
          candidate: event.candidate,
          user_id: socket.id,
          other_user_id: userId
        })
        console.log(`[WebRTC] createPeerConnection - ICE候选已发送，用户ID: ${userId}`)
      }
    }
  } else {
    console.log(`[WebRTC] createPeerConnection - 用户 ${userId} 已存在PeerConnection，直接返回`)
  }
  
  console.log(`[WebRTC] createPeerConnection - 操作完成，返回PeerConnection实例，用户ID: ${userId}`)
  return peerConnections[userId]
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
    
    socket.emit('join_room', { room: 'room1' });
    
    // 显示自己加入会议的事件
    console.log(`[WebRTC] 初始化视频会议，房间: room1`)
    
    // 监听连接成功事件，在成功后显示用户信息
    socket.on('connect', () => {
      console.log(`[WebRTC] 初始化视频会议，当前用户ID: ${socket.id}`)
      // 更新UI显示当前用户ID
      const userIdElement = document.getElementById('current-user-id');
      if (userIdElement) {
        userIdElement.textContent = socket.id;
      }
      
      showEvent(`${socket.id} 已加入会议`, 'join')
      
      // 请求当前房间的用户列表
      socket.emit('get_users_in_room', { room: 'room1' })
    })
    
    // 处理房间用户列表
    socket.on('users_in_room', (data) => {
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
        updateVideoList();
    })

    // 处理新用户加入
    socket.on('new_user', async (data) => {
      const otherUserId = data.user_id
      console.log(`[WebRTC] 检测到新用户加入，用户ID: ${otherUserId}，当前用户ID: ${socket.id}`)
      
      // 显示用户加入事件
      showEvent(`${otherUserId} 加入了会议`, 'join')
      
      // 添加到用户列表，避免重复添加
      if (!otherUserIds.value.includes(otherUserId)) {
        otherUserIds.value.push(otherUserId)
        console.log(`[WebRTC] 用户已添加到用户列表，当前用户总数: ${otherUserIds.value.length}`)
      } else {
        console.log(`[WebRTC] 用户 ${otherUserId} 已在列表中，跳过重复添加`)
      }

      // 创建新的PeerConnection
      console.log(`[WebRTC] 开始为新用户创建PeerConnection，用户ID: ${otherUserId}`)
      const pc = await createPeerConnection(otherUserId)
      console.log(`[WebRTC] PeerConnection创建成功，准备添加媒体轨道`)
      
      // 添加本地媒体轨道
      const trackCount = localStream.getTracks().length
      localStream.getTracks().forEach((track, index) => {
        console.log(`[WebRTC] 添加第${index+1}/${trackCount}个媒体轨道，类型: ${track.kind}`)
        pc.addTrack(track, localStream)
      })
      console.log(`[WebRTC] 所有媒体轨道添加完成`)

      // 创建并发送offer
      console.log(`[WebRTC] 开始创建offer`)
      const offer = await pc.createOffer()
      console.log(`[WebRTC] offer创建成功，类型: ${offer.type}`)
      
      await pc.setLocalDescription(offer)
      console.log(`[WebRTC] 本地描述设置成功，准备发送offer`)
      
      socket.emit('offer', {
        offer: { type: offer.type, sdp: offer.sdp },
        user_id: socket.id,
        other_user_id: otherUserId
      })
      console.log(`[WebRTC] offer已发送至新用户，用户ID: ${otherUserId}`)
      
      // 更新视频列表
      updateVideoList();
    })

    // 处理offer
    socket.on('offer', async (offer) => {
      console.log(`[WebRTC] 接收到来自用户 ${offer.user_id} 的offer，当前用户ID: ${socket.id}`)
      console.log(`[WebRTC] offer详情:`, {
        type: offer.offer.type,
        sdpLength: offer.offer.sdp?.length || 0,
        timestamp: new Date().toISOString()
      })
      
      const pc = await createPeerConnection(offer.user_id)
      
      try {
        console.log(`[WebRTC] 开始设置远程描述，用户ID: ${offer.user_id}`)
        await pc.setRemoteDescription(new RTCSessionDescription(offer.offer))
        console.log(`[WebRTC] 远程描述设置成功，创建answer响应`)
        
        const answer = await pc.createAnswer()
        console.log(`[WebRTC] answer创建成功，类型: ${answer.type}`)
        
        await pc.setLocalDescription(answer)
        console.log(`[WebRTC] 本地描述设置成功`)
        
        socket.emit('answer', {
          answer: { type: answer.type, sdp: answer.sdp },
          user_id: socket.id,
          other_user_id: offer.user_id
        })
        console.log(`[WebRTC] answer已发送至用户 ${offer.user_id}`)
      } catch (error) {
        console.error(`[WebRTC] 处理offer失败，用户ID: ${offer.user_id}`, error)
      }
    })

    // 处理answer
    socket.on('answer', async (answer) => {
      console.log(`[WebRTC] 接收到来自用户 ${answer.user_id} 的answer，当前用户ID: ${socket.id}`)
      console.log(`[WebRTC] answer详情:`, {
        type: answer.answer.type,
        sdpLength: answer.answer.sdp?.length || 0,
        timestamp: new Date().toISOString()
      })
      
      const pc = peerConnections[answer.user_id]
      if (pc && pc.signalingState !== 'stable') {
        console.log(`[WebRTC] 准备设置answer的远程描述，连接状态: ${pc.signalingState}`)
        try {
          await pc.setRemoteDescription(new RTCSessionDescription(answer.answer))
          console.log(`[WebRTC] answer远程描述设置成功，用户ID: ${answer.user_id}`)
          console.log(`[WebRTC] 更新后的连接状态: ${pc.signalingState}`)
        } catch (error) {
          console.error(`[WebRTC] 设置answer远程描述失败，用户ID: ${answer.user_id}`, error)
        }
      } else if (!pc) {
        console.warn(`[WebRTC] 未找到对应用户ID: ${answer.user_id} 的PeerConnection`)
      } else if (pc.signalingState === 'stable') {
        console.info(`[WebRTC] 连接状态已稳定(stable)，跳过设置answer，用户ID: ${answer.user_id}`)
      }
    })

    // 处理ICE候选
    socket.on('ice_candidate', async (candidate) => {
      console.log(`[WebRTC] 接收到来自用户 ${candidate.user_id} 的ICE候选，当前用户ID: ${socket.id}`)
      console.log(`[WebRTC] ICE候选详情:`, {
        candidateType: candidate.candidate.candidate?.split(' ')[7] || 'unknown',
        foundation: candidate.candidate.foundation || 'unknown',
        priority: candidate.candidate.priority || 'unknown',
        timestamp: new Date().toISOString()
      })
      
      try {
        if (peerConnections[candidate.user_id]) {
          console.log(`[WebRTC] 准备添加ICE候选，目标用户ID: ${candidate.user_id}`)
          await peerConnections[candidate.user_id].addIceCandidate(
            new RTCIceCandidate(candidate.candidate)
          )
          console.log(`[WebRTC] ICE候选添加成功，目标用户ID: ${candidate.user_id}`)
        } else {
          console.warn(`[WebRTC] 未找到对应用户ID: ${candidate.user_id} 的PeerConnection，无法添加ICE候选`)
        }
      } catch (error) {
        console.error(`[WebRTC] 添加ICE候选失败，用户ID: ${candidate.user_id}`, error)
      }
    })

    // 处理消息
    socket.on('message', (messageData) => {
      const { user_id, content } = messageData
      console.log(`[WebRTC] 接收到来自用户 ${user_id} 的消息:`, {
        content: content,
        length: content.length,
        timestamp: new Date().toISOString()
      })
      
      // 检查消息是否来自当前用户，如果不是则显示
      if (user_id !== socket.id) {
        if (messageList.value) {
          console.log(`[WebRTC] 准备在消息列表中显示消息`)
          const li = document.createElement('li')
          li.textContent = `${user_id}: ${content}`
          li.setAttribute('data-user-id', user_id)
          messageList.value.querySelector('ul')?.appendChild(li)
          messageList.value.scrollTop = messageList.value.scrollHeight
          console.log(`[WebRTC] 消息显示成功，消息列表已更新并滚动到底部`)
        } else {
          console.warn(`[WebRTC] 消息列表DOM元素未找到，无法显示消息`)
        }
        
        // 在事件日志中显示消息事件
        showEvent(`${user_id} 发送了消息`, 'message')
      }
    })
    
    // 处理用户离开
    socket.on('user_left', (data) => {
      const { user_id } = data
      console.log(`[WebRTC] 用户离开会议，用户ID: ${user_id}`)
      
      // 从用户列表中移除
      const index = otherUserIds.value.indexOf(user_id)
      if (index > -1) {
        otherUserIds.value.splice(index, 1)
      }
      
      // 关闭对应的PeerConnection
      if (peerConnections[user_id]) {
        peerConnections[user_id].close()
        delete peerConnections[user_id]
      }
      
      // 移除对应的视频元素
      const videoElement = document.querySelector(`.remote-video[data-user-id="${user_id}"]`)
      if (videoElement) {
        videoElement.remove()
        console.log(`[WebRTC] 用户 ${user_id} 的视频元素已移除`)
      }
      
      // 显示用户离开事件
      showEvent(`${user_id} 离开了会议`, 'leave')
      
      // 更新视频列表
      updateVideoList();
    })
  } catch (error) {
    console.error('初始化错误:', error);
    message.error('初始化视频会议失败: ' + error);
  }
}

// 显示事件日志
function showEvent(message: string, type: 'join' | 'leave' | 'message') {
  console.log(`[WebRTC] 显示事件日志: ${message}`)
  
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
  // 首先尝试直接播放
  videoElement.play().catch(err => {
    console.warn(`[WebRTC] 视频自动播放失败 (用户 ${userId}):`, err);
    
    // 尝试静音播放，这通常可以绕过自动播放限制
    const originalMuted = videoElement.muted;
    videoElement.muted = true;
    videoElement.play().then(() => {
      console.log(`[WebRTC] 视频成功以静音模式播放 (用户 ${userId})`);
      // 保存播放状态，以便在用户交互后取消静音
      const handleUserInteraction = () => {
        try {
          videoElement.muted = originalMuted;
          console.log(`[WebRTC] 用户交互后尝试取消视频静音 (用户 ${userId})`);
        } catch (e) {
          console.error(`[WebRTC] 用户交互后取消视频静音失败:`, e);
        }
        document.removeEventListener('click', handleUserInteraction);
        document.removeEventListener('keydown', handleUserInteraction);
      };
      
      // 监听用户交互事件，以便在用户交互后取消静音
      document.addEventListener('click', handleUserInteraction);
      document.addEventListener('keydown', handleUserInteraction);
    }).catch(err => {
      console.error(`[WebRTC] 视频静音播放也失败 (用户 ${userId}):`, err);
      
      // 最后尝试在用户交互时播放
      const handleUserClick = () => {
        videoElement.play().catch(err => {
          console.error(`[WebRTC] 用户交互后播放仍失败 (用户 ${userId}):`, err);
        });
        document.removeEventListener('click', handleUserClick);
      };
      
      document.addEventListener('click', handleUserClick, { once: true });
      console.log(`[WebRTC] 已设置用户交互时自动播放视频 (用户 ${userId})`);
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
    console.log('[WebRTC] 正在离开会议室...')
    
    // 显示离开事件
    showEvent(`${socket.id} 主动离开了会议室`, 'leave')
    
    // 断开WebSocket连接
    if (socket) {
      socket.disconnect()
      console.log('[WebRTC] WebSocket连接已断开')
    }
    
    // 关闭所有PeerConnection
    Object.values(peerConnections).forEach(pc => {
      pc.close()
    })
    peerConnections = {}
    console.log('[WebRTC] 所有PeerConnection已关闭')
    
    // 停止本地媒体流
    if (localStream) {
      localStream.getTracks().forEach(track => track.stop())
      console.log('[WebRTC] 本地媒体流已停止')
    }
    
    // 清空其他用户列表
    otherUserIds.value = []
    
    // 更新视频列表
    updateVideoList()
    
    // 更新状态
    isInMeeting.value = false
    
    message.success('已成功离开会议室')
  } catch (error) {
    console.error('[WebRTC] 离开会议室失败:', error)
    message.error('离开会议室失败: ' + error)
  }
}

// 加入会议室
async function joinMeeting() {
  try {
    console.log('[WebRTC] 正在加入会议室...')
    
    // 重置状态
    isInMeeting.value = true
    
    // 初始化会议
    await init()
    
    message.success('已成功加入会议室')
  } catch (error) {
    console.error('[WebRTC] 加入会议室失败:', error)
    message.error('加入会议室失败: ' + error)
    isInMeeting.value = false
  }
}

// 设置主视频流
function setMainStream(stream: MediaStream, userId: string) {
  mainStream.value = stream;
  mainStreamIsLocal.value = userId === 'local';
  selectedUserId.value = userId;
  
  // 更新主视频显示
  if (mainVideo.value) {
    mainVideo.value.srcObject = stream;
  } else {
    // 如果没有主视频元素，TODO 则创建一个
    console.error('[WebRTC] 没有主视频元素，无法设置主视频流');
  }
  
  // 更新视频列表中的选中状态
  updateSelectedVideoStyle();
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
  gap: 10px;
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
</style>