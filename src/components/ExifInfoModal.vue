<script setup lang="ts">
import { ref, defineProps, defineEmits, watch, onMounted } from 'vue'
import { Modal } from 'ant-design-vue'
import { CameraOutlined, EnvironmentOutlined, ClockCircleOutlined, InfoCircleOutlined } from '@ant-design/icons-vue'

const props = defineProps<{
  visible: boolean
  imageUrl: string
  imageTitle?: string
}>()

const emit = defineEmits(['close', 'update:visible'])

// EXIF信息状态
const loading = ref(false)
const exifData = ref<Record<string, any>>({})

// 从后端获取EXIF数据
const fetchExifData = async () => {
    console.log('fetchExifData')
  if (!props.imageUrl) return
  
  loading.value = true
  try {
    // 从图片URL中提取文件名
    const filename = props.imageUrl.split('/').pop()
    
    // 如果是完整URL，需要先下载图片
    if (props.imageUrl.startsWith('http')) {
      // 使用fetch API获取图片
      const response = await fetch(props.imageUrl)
      const blob = await response.blob()
      
      // 创建FormData对象上传图片
      const formData = new FormData()
      formData.append('image', blob, filename)
      
      // 调用后端API获取EXIF数据
      const exifResponse = await fetch('/api/face/exif', {
        method: 'POST',
        body: formData
      })
      
      const result = await exifResponse.json()
      
      if (result.code === 200) {
        exifData.value = result.data.exif
        console.log('EXIF数据已加载:', exifData.value)
      } else {
        console.error('获取EXIF数据失败:', result.message)
        exifData.value = {}
      }
    } else {
      // 本地图片路径，直接使用文件路径调用API
      // 这里假设props.imageUrl是一个本地文件路径或者已上传到服务器的路径
      // 实际实现可能需要根据项目的具体情况调整
      const exifResponse = await fetch(`/api/face/exif?path=${encodeURIComponent(props.imageUrl)}`, {
        method: 'GET'
      })
      
      const result = await exifResponse.json()
      
      if (result.code === 200) {
        exifData.value = result.data.exif
        console.log('EXIF数据已加载:', exifData.value)
      } else {
        console.error('获取EXIF数据失败:', result.message)
        exifData.value = {}
      }
    }
  } catch (error) {
    console.error('获取EXIF数据失败:', error)
    exifData.value = {}
  } finally {
    loading.value = false
  }
}

// 当弹窗显示时获取EXIF数据
const handleAfterShow = (visible: boolean) => {
  console.log('handleAfterShow', visible)
  // 只在弹窗显示时获取EXIF数据
  if (visible) {
    fetchExifData()
  }
}

// 监听visible属性变化
watch(() => props.visible, (newVisible) => {
  console.log('watch visible change:', newVisible)
  if (newVisible) {
    fetchExifData()
  }
})

// 组件挂载后检查visible状态
onMounted(() => {
  console.log('ExifInfoModal mounted, visible:', props.visible)
  if (props.visible) {
    fetchExifData()
  }
})

// 关闭弹窗
const handleCancel = () => {
    console.log('关闭弹窗')
  emit('update:visible', false)
  emit('close')
}
</script>

<template>
  <Modal
    :visible="visible"
    title="图片EXIF信息"
    @cancel="handleCancel"
    @update:visible="(val) => emit('update:visible', val)"
    :footer="null"
    width="800px"
    class="exif-modal"
    @update:open="handleAfterShow"
    @afterVisibleChange="handleAfterShow"
  >
  <!-- TODO 这里面的浮层弹出的内容无法在第一次加载之后就显示出来，因为上面的两个监听都没有能够触发到，所以暂时没有解决方法，不知道哪里有问题，暂时先丢着，要两次点击之后才能够调用对应的获取数据的handleExifData()，比较无语 -->
    <div class="exif-container" :class="{ 'is-loading': loading }">
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>正在读取EXIF数据...</p>
      </div>
      
      <template v-else>
        <div class="exif-header">
          <div class="image-preview">
            <img :src="imageUrl" :alt="imageTitle || '图片'" />
          </div>
          <div class="image-info">
            <h3>{{ imageTitle || '未命名图片' }}</h3>
            <div class="chip-design">
              <CameraOutlined />
              {{ exifData.camera?.make }} {{ exifData.camera?.model }}
            </div>
          </div>
        </div>
        
        <div class="exif-grid">
          <!-- 相机信息 -->
          <div class="exif-card">
            <h3><CameraOutlined /> 相机信息</h3>
            <div class="exif-item">
              <div class="exif-label">相机品牌</div>
              <div class="exif-value">{{ exifData.camera?.make || '未知' }}</div>
            </div>
            <div class="exif-item">
              <div class="exif-label">相机型号</div>
              <div class="exif-value">{{ exifData.camera?.model || '未知' }}</div>
            </div>
            <div class="exif-item">
              <div class="exif-label">软件版本</div>
              <div class="exif-value">{{ exifData.camera?.software || '未知' }}</div>
            </div>
          </div>
          
          <!-- 曝光信息 -->
          <div class="exif-card">
            <h3><InfoCircleOutlined /> 曝光参数</h3>
            <div class="exif-item">
              <div class="exif-label">曝光时间</div>
              <div class="exif-value">{{ exifData.exposure?.exposureTime || '未知' }}</div>
            </div>
            <div class="exif-item">
              <div class="exif-label">光圈值</div>
              <div class="exif-value">{{ exifData.exposure?.fNumber || '未知' }}</div>
            </div>
            <div class="exif-item">
              <div class="exif-label">ISO感光度</div>
              <div class="exif-value">{{ exifData.exposure?.iso || '未知' }}</div>
            </div>
            <div class="exif-item">
              <div class="exif-label">焦距</div>
              <div class="exif-value">{{ exifData.exposure?.focalLength || '未知' }}</div>
            </div>
          </div>
          
          <!-- 图像信息 -->
          <div class="exif-card">
            <h3><InfoCircleOutlined /> 图像信息</h3>
            <div class="exif-item">
              <div class="exif-label">尺寸</div>
              <div class="exif-value">{{ exifData.image?.width || '?' }}×{{ exifData.image?.height || '?' }}</div>
            </div>
            <div class="exif-item">
              <div class="exif-label">方向</div>
              <div class="exif-value">{{ exifData.image?.orientation || '未知' }}</div>
            </div>
            <div class="exif-item">
              <div class="exif-label">色彩空间</div>
              <div class="exif-value">{{ exifData.image?.colorSpace || '未知' }}</div>
            </div>
          </div>
          
          <!-- 时间信息 -->
          <div class="exif-card">
            <h3><ClockCircleOutlined /> 时间信息</h3>
            <div class="exif-item">
              <div class="exif-label">拍摄时间</div>
              <div class="exif-value">{{ exifData.datetime?.original || '未知' }}</div>
            </div>
            <div class="exif-item">
              <div class="exif-label">数字化时间</div>
              <div class="exif-value">{{ exifData.datetime?.digitized || '未知' }}</div>
            </div>
          </div>
          
          <!-- GPS信息 -->
          <div class="exif-card" :class="{ 'disabled': !exifData.gps?.latitude }">
            <h3><EnvironmentOutlined /> 地理位置</h3>
            <div v-if="exifData.gps?.latitude" class="exif-item">
              <div class="exif-label">经纬度</div>
              <div class="exif-value">{{ exifData.gps?.latitude }}, {{ exifData.gps?.longitude }}</div>
            </div>
            <div v-else class="no-data">
              <p>未找到GPS信息</p>
            </div>
          </div>
          
          <!-- 其他信息 -->
          <div class="exif-card">
            <h3><InfoCircleOutlined /> 其他参数</h3>
            <div class="exif-item">
              <div class="exif-label">光源</div>
              <div class="exif-value">{{ exifData.other?.lightSource || '未知' }}</div>
            </div>
            <div class="exif-item">
              <div class="exif-label">测光模式</div>
              <div class="exif-value">{{ exifData.other?.meteringMode || '未知' }}</div>
            </div>
            <div class="exif-item">
              <div class="exif-label">白平衡</div>
              <div class="exif-value">{{ exifData.other?.whiteBalance || '未知' }}</div>
            </div>
            <div class="exif-item">
              <div class="exif-label">闪光灯</div>
              <div class="exif-value">{{ exifData.other?.flash || '未知' }}</div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </Modal>
</template>

<style scoped>
.exif-modal {
  --exif-primary: #1ABC9C;
  --exif-dark: #2C3E50;
  --exif-light: #ecf0f1;
  --exif-card-bg: rgba(44, 62, 80, 0.05);
}

.exif-container {
  position: relative;
  min-height: 300px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(26, 188, 156, 0.3);
  border-radius: 50%;
  border-top-color: var(--exif-primary);
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.exif-header {
  display: flex;
  margin-bottom: 24px;
  align-items: center;
}

.image-preview {
  width: 120px;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
  margin-right: 20px;
  border: 1px solid #eee;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-info {
  flex: 1;
}

.image-info h3 {
  margin-bottom: 12px;
  font-size: 18px;
  color: var(--exif-dark);
}

.chip-design {
  display: inline-flex;
  align-items: center;
  background: var(--exif-card-bg);
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 14px;
  color: var(--exif-dark);
  border-left: 3px solid var(--exif-primary);
}

.chip-design .anticon {
  margin-right: 6px;
  color: var(--exif-primary);
}

.exif-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.exif-card {
  background: var(--exif-card-bg);
  border-radius: 8px;
  padding: 16px;
  border-left: 3px solid var(--exif-primary);
  transition: all 0.3s ease;
}

.exif-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.exif-card h3 {
  font-size: 16px;
  margin-bottom: 12px;
  color: var(--exif-dark);
  display: flex;
  align-items: center;
}

.exif-card h3 .anticon {
  margin-right: 8px;
  color: var(--exif-primary);
}

.exif-item {
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
}

.exif-label {
  color: #666;
  font-size: 14px;
}

.exif-value {
  font-weight: 500;
  color: var(--exif-dark);
}

.disabled {
  opacity: 0.6;
}

.no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80px;
  color: #999;
  font-style: italic;
}
</style>