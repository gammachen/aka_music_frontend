<template>
  <div class="photo-exif-container">
    <div class="section-title">
      <h2>图片EXIF信息查看器</h2>
      <p>上传图片，查看详细的EXIF信息和GPS位置</p>
    </div>

    <div class="content-container">
      <!-- 左侧上传和图片列表 -->
      <div class="upload-section">
        <div class="upload-area">
          <a-upload-dragger
            name="image"
            :multiple="true"
            :action="'/api/face/exif'"
            :headers="uploadHeaders"
            :before-upload="beforeUpload"
            @change="handleUploadChange"
            @drop="handleDrop"
          >
            <p class="ant-upload-drag-icon">
              <camera-outlined />
            </p>
            <p class="ant-upload-text">点击或拖拽图片到此区域上传</p>
            <p class="ant-upload-hint">
              支持单张或多张图片上传，查看EXIF信息和GPS位置
            </p>
          </a-upload-dragger>
        </div>

        <div class="image-list" v-if="uploadedImages.length > 0">
          <h3>已上传图片</h3>
          <div class="image-grid">
            <div
              v-for="(image, index) in uploadedImages"
              :key="index"
              class="image-card"
              :class="{ active: selectedImageIndex === index }"
              @click="selectImage(index)"
            >
              <img :src="image.url" :alt="`图片 ${index + 1}`" />
              <div class="image-caption">
                <h4>图片 {{ index + 1 }}</h4>
                <p v-if="image.exif?.camera?.model">{{ image.exif.camera.model }}</p>
                <p v-else>点击查看详情</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧EXIF信息和地图 -->
      <div class="info-section">
        <div v-if="!selectedImage" class="empty-state">
          <camera-outlined />
          <p>请上传图片或从左侧选择已上传的图片查看详情</p>
        </div>

        <template v-else>
          <!-- EXIF信息展示 -->
          <div class="exif-container">
            <div class="exif-header">
              <div class="image-preview">
                <img :src="selectedImage.url" alt="预览图" />
              </div>
              <div class="image-info">
                <h3>图片信息</h3>
                <div class="chip-design">
                  <camera-outlined />
                  {{ selectedImage.exif?.camera?.make }} {{ selectedImage.exif?.camera?.model }}
                </div>
              </div>
            </div>

            <div class="exif-grid">
              <!-- 相机信息 -->
              <div class="exif-card">
                <h3><camera-outlined /> 相机信息</h3>
                <div class="exif-item">
                  <div class="exif-label">相机品牌</div>
                  <div class="exif-value">{{ selectedImage.exif?.camera?.make || '未知' }}</div>
                </div>
                <div class="exif-item">
                  <div class="exif-label">相机型号</div>
                  <div class="exif-value">{{ selectedImage.exif?.camera?.model || '未知' }}</div>
                </div>
                <div class="exif-item">
                  <div class="exif-label">软件版本</div>
                  <div class="exif-value">{{ selectedImage.exif?.camera?.software || '未知' }}</div>
                </div>
              </div>

              <!-- 曝光信息 -->
              <div class="exif-card">
                <h3><info-circle-outlined /> 曝光参数</h3>
                <div class="exif-item">
                  <div class="exif-label">曝光时间</div>
                  <div class="exif-value">{{ selectedImage.exif?.exposure?.exposureTime || '未知' }}</div>
                </div>
                <div class="exif-item">
                  <div class="exif-label">光圈值</div>
                  <div class="exif-value">{{ selectedImage.exif?.exposure?.fNumber || '未知' }}</div>
                </div>
                <div class="exif-item">
                  <div class="exif-label">ISO感光度</div>
                  <div class="exif-value">{{ selectedImage.exif?.exposure?.iso || '未知' }}</div>
                </div>
                <div class="exif-item">
                  <div class="exif-label">焦距</div>
                  <div class="exif-value">{{ selectedImage.exif?.exposure?.focalLength || '未知' }}</div>
                </div>
              </div>

              <!-- 图像信息 -->
              <div class="exif-card">
                <h3><info-circle-outlined /> 图像信息</h3>
                <div class="exif-item">
                  <div class="exif-label">尺寸</div>
                  <div class="exif-value">{{ selectedImage.exif?.image?.width || '?' }}×{{ selectedImage.exif?.image?.height || '?' }}</div>
                </div>
                <div class="exif-item">
                  <div class="exif-label">方向</div>
                  <div class="exif-value">{{ selectedImage.exif?.image?.orientation || '未知' }}</div>
                </div>
                <div class="exif-item">
                  <div class="exif-label">色彩空间</div>
                  <div class="exif-value">{{ selectedImage.exif?.image?.colorSpace || '未知' }}</div>
                </div>
              </div>

              <!-- 时间信息 -->
              <div class="exif-card">
                <h3><clock-circle-outlined /> 时间信息</h3>
                <div class="exif-item">
                  <div class="exif-label">拍摄时间</div>
                  <div class="exif-value">{{ selectedImage.exif?.datetime?.original || '未知' }}</div>
                </div>
                <div class="exif-item">
                  <div class="exif-label">数字化时间</div>
                  <div class="exif-value">{{ selectedImage.exif?.datetime?.digitized || '未知' }}</div>
                </div>
              </div>

              <!-- 其他信息 -->
              <div class="exif-card">
                <h3><info-circle-outlined /> 其他信息</h3>
                <div class="exif-item">
                  <div class="exif-label">光源</div>
                  <div class="exif-value">{{ selectedImage.exif?.other?.lightSource || '未知' }}</div>
                </div>
                <div class="exif-item">
                  <div class="exif-label">测光模式</div>
                  <div class="exif-value">{{ selectedImage.exif?.other?.meteringMode || '未知' }}</div>
                </div>
                <div class="exif-item">
                  <div class="exif-label">白平衡</div>
                  <div class="exif-value">{{ selectedImage.exif?.other?.whiteBalance || '未知' }}</div>
                </div>
                <div class="exif-item">
                  <div class="exif-label">闪光灯</div>
                  <div class="exif-value">{{ selectedImage.exif?.other?.flash || '未知' }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 地图展示 -->
          <div class="map-container" v-if="hasGpsData">
            <h3><environment-outlined /> 拍摄位置</h3>
            <div id="map" ref="mapContainer"></div>
          </div>
          <div class="no-gps-data" v-else>
            <environment-outlined />
            <p>该图片没有GPS位置信息</p>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { message } from 'ant-design-vue'
import { CameraOutlined, EnvironmentOutlined, ClockCircleOutlined, InfoCircleOutlined } from '@ant-design/icons-vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useUserStore } from '../../store'

// 用户信息
const userStore = useUserStore()
const uploadHeaders = computed(() => {
  return {
    Authorization: userStore.token ? `Bearer ${userStore.token}` : ''
  }
})

// 上传的图片列表
interface UploadedImage {
  url: string
  exif?: any
  filename?: string
}

const uploadedImages = ref<UploadedImage[]>([])
const selectedImageIndex = ref<number | null>(null)
const selectedImage = computed(() => {
  if (selectedImageIndex.value !== null && uploadedImages.value.length > 0) {
    return uploadedImages.value[selectedImageIndex.value]
  }
  return null
})

// 判断是否有GPS数据
const hasGpsData = computed(() => {
  if (!selectedImage.value || !selectedImage.value.exif) return false
  return !!selectedImage.value.exif.gps && 
         (selectedImage.value.exif.gps.latitude !== undefined || 
          selectedImage.value.exif.gps.longitude !== undefined)
})

// 地图相关
const mapContainer = ref(null)
const map = ref(null)
const marker = ref(null)

// 上传前检查文件类型
const beforeUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    message.error('只能上传图片文件!')
  }
  return isImage || Upload.LIST_IGNORE
}

// 处理上传状态变化
const handleUploadChange = (info: any) => {
  const { status, response } = info.file
  
  if (status === 'uploading') {
    // 上传中
  } else if (status === 'done') {
    // 上传完成
    if (response && response.code === 200) {
      message.success(`${info.file.name} 上传成功`)
      
      // 添加到图片列表
      uploadedImages.value.push({
        url: info.file.response.data.url || URL.createObjectURL(info.file.originFileObj),
        exif: response.data.exif,
        filename: info.file.name
      })
      
      // 自动选择新上传的图片
      selectImage(uploadedImages.value.length - 1)
    } else {
      message.error(`${info.file.name} 上传失败: ${response?.message || '未知错误'}`)
    }
  } else if (status === 'error') {
    message.error(`${info.file.name} 上传失败`)
  }
}

// 处理拖拽上传
const handleDrop = (e: any) => {
  console.log('Dropped files', e.dataTransfer.files)
}

// 选择图片
const selectImage = (index: number) => {
  selectedImageIndex.value = index
}

// 初始化地图
const initMap = () => {
  if (!mapContainer.value) return
  
  // 如果地图已经初始化，则销毁重建
  if (map.value) {
    map.value.remove()
    map.value = null
  }
  
  // 创建地图实例
  map.value = L.map(mapContainer.value).setView([30, 120], 5)
  
  // 添加底图图层
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map.value)
}

// 更新地图标记
const updateMapMarker = () => {
  if (!map.value || !hasGpsData.value || !selectedImage.value) return
  
  const { latitude, longitude } = selectedImage.value.exif.gps
  
  // 如果没有有效的坐标，不显示标记
  if (!latitude || !longitude) return
  
  // 移除现有标记
  if (marker.value) {
    map.value.removeLayer(marker.value)
    marker.value = null
  }
  
  // 创建自定义图标，使用上传的图片
  const icon = L.icon({
    iconUrl: selectedImage.value.url,
    iconSize: [45, 45],
    iconAnchor: [22, 45],
    popupAnchor: [0, -45],
    className: 'photo-marker-icon'
  })
  
  // 创建标记并添加到地图
  marker.value = L.marker([latitude, longitude], { icon }).addTo(map.value)
  
  // 添加弹出信息
  marker.value.bindPopup(`<b>拍摄位置</b><br>经度: ${longitude}<br>纬度: ${latitude}`)
  
  // 设置地图视图中心到标记位置
  map.value.setView([latitude, longitude], 13)
}

// 监听选中图片变化，更新地图
watch(selectedImage, updateMapMarker)

</script>