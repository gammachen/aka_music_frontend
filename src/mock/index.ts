import Mock from 'mockjs';

// 配置MockJS
Mock.setup({
  timeout: '600-1000',
})

// 保存原始XHR
const OriginalXHR = window.XMLHttpRequest;

// 创建新的XHR构造函数，在MockJS加载前拦截
function PatchedXHR(this: any) {
  const xhr = new OriginalXHR();
  
  // 保存原始方法
  const originalOpen = xhr.open;
  const originalSend = xhr.send;
  
  // 重写open方法
  xhr.open = function(method: string, url: string, async?: boolean, user?: string, password?: string) {
    // 检查是否是视频或静态资源请求
    const isVideoRequest = /\.(m3u8|ts|mp4|webm|ogg|avi|mov|m4s)$/i.test(url) ||
                          url.includes('/static/') ||
                          url.includes('/uploads/') ||
                          url.startsWith('blob:');
    
    if (isVideoRequest) {
      // 使用原始XHR
      return originalOpen.call(xhr, method, url, async, user, password);
    } else {
      // 让MockJS处理其他请求
      return originalOpen.call(xhr, method, url, async, user, password);
    }
  };
  
  return xhr;
}

// 在MockJS加载前替换XHR
if (window.XMLHttpRequest !== PatchedXHR) {
  window.XMLHttpRequest = PatchedXHR as any;
}

// 导入其他mock模块（它们将使用PatchedXHR）
import './editor'
import './font'
import './upload'
