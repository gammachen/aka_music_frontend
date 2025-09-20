// 修复3: 改进ontrack事件处理
peerConnections[userId].ontrack = (event) => {
  console.log(`[${userId}] 📹 ontrack 事件 - 收到远程媒体流`);
  console.log('流数量:', event.streams.length);
  console.log('Track 类型:', event.track.kind);
  console.log('Track ID:', event.track.id);
  console.log('Track 状态:', event.track.readyState);

  // 确保事件包含有效的流
  if (!event.streams || event.streams.length === 0) {
    console.warn(`[WebRTC] createPeerConnection ontrack - 接收到ontrack事件，但没有可用的媒体流`);
    return;
  }

  const stream = event.streams[0]; // 使用原始流，不要重新构建
  console.log(`[WebRTC] createPeerConnection ontrack - 检测到媒体流，包含 ${stream.getTracks().length} 个轨道`);

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
          
          // 设置媒体流
          videoElement.srcObject = stream;
          
          // 强制触发加载
          videoElement.load();
          
          // 尝试播放
          videoElement.play().then(() => {
            console.log(`[WebRTC] createPeerConnection - 视频播放成功，用户ID: ${userId}`);
          }).catch(error => {
            console.error(`[WebRTC] createPeerConnection - 视频播放失败，用户ID: ${userId}:`, error);
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



// 修复4: 启用TURN服务器
peerConnections[userId] = new RTCPeerConnection({
  iceServers: [
    {
      urls: 'stun:192.168.31.27:8089',
      username: 'akamusic',
      credential: 'youhavetoberealistic'
    },
    {
      urls: 'turn:192.168.31.27:8089',
      username: 'akamusic',
      credential: 'youhavetoberealistic'
    },
    // 添加公共STUN服务器作为备选
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
  ],
  iceCandidatePoolSize: 10,
  iceTransportPolicy: 'all',
  bundlePolicy: 'max-bundle',
  rtcpMuxPolicy: 'require',
});



