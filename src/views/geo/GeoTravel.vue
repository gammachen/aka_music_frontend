<template>
  <div class="geo-travel-container">
    <div class="section-title">
      <h2>浙江省旅游地图</h2>
      <p>探索浙江省各地级市的风景名胜和旅游路线</p>
    </div>

    <div class="content-container">
      <!-- 左侧图片列表 -->
      <div class="image-list">
        <h3>城市风光</h3>
        <div class="image-grid">
          <div v-for="(city, index) in cities" :key="index" class="image-card" @click="selectCity(city)">
            <img :src="`/gis/travel/img/${city.name}.jpeg`" :alt="city.name" />
            <div class="image-caption">
              <h4>{{ city.name }}</h4>
              <p v-if="city.city_intro">{{ city.city_intro }}</p>
              <p v-else-if="city.special_note">{{ city.special_note }}</p>
              <p v-else>点击查看详情</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧地图 -->
      <div class="map-container">
        <div id="map" ref="mapContainer"></div>
        
        <!-- 城市详情 -->
        <div v-if="selectedCity" class="city-detail">
          <h3>{{ selectedCity.name }} 详情</h3>
          <div class="detail-content">
            <p v-if="selectedCity.city_intro"><strong>简介：</strong> {{ selectedCity.city_intro }}</p>
            <p v-if="selectedCity.elevation"><strong>海拔：</strong> {{ selectedCity.elevation }}米</p>
            <p v-if="selectedCity.special_note"><strong>特色：</strong> {{ selectedCity.special_note }}</p>
            
            <!-- 景点列表 -->
            <div v-if="selectedCity.must_see && selectedCity.must_see.length > 0" class="attractions">
              <h4>必游景点：</h4>
              <ul>
                <li v-for="(spot, idx) in selectedCity.must_see" :key="idx">
                  {{ Object.keys(spot)[0] }} - {{ spot[Object.keys(spot)[0]] }}
                </li>
              </ul>
            </div>
            
            <!-- 历史遗址 -->
            <div v-if="selectedCity.historical_site" class="historical-sites">
              <h4>历史遗址：</h4>
              <ul>
                <li v-for="(value, key) in selectedCity.historical_site" :key="key">
                  {{ key }}: {{ value }}
                </li>
              </ul>
            </div>
            
            <!-- 文化符号 -->
            <div v-if="selectedCity.cultural_symbol" class="cultural-symbols">
              <h4>文化符号：</h4>
              <ul>
                <li v-for="(value, key) in selectedCity.cultural_symbol" :key="key">
                  {{ key }}: {{ value }}
                </li>
              </ul>
            </div>
            
            <!-- 文学遗产 -->
            <div v-if="selectedCity.literary_heritage && selectedCity.literary_heritage.length > 0" class="literary-heritage">
              <h4>文学遗产：</h4>
              <ul>
                <li v-for="(heritage, idx) in selectedCity.literary_heritage" :key="idx">
                  {{ Object.keys(heritage)[0] }}: {{ heritage[Object.keys(heritage)[0]] }}
                </li>
              </ul>
            </div>
            
            <!-- 特产 -->
            <div v-if="selectedCity.specialty" class="specialty">
              <h4>特产：</h4>
              <ul>
                <li v-for="(value, key) in selectedCity.specialty" :key="key">
                  {{ key }}: {{ value }}
                </li>
              </ul>
            </div>
            
            <!-- 港口信息 -->
            <div v-if="selectedCity.port_info" class="port-info">
              <h4>港口信息：</h4>
              <ul>
                <li v-for="(value, key) in selectedCity.port_info" :key="key">
                  {{ key }}: {{ value }}
                </li>
              </ul>
            </div>
            
            <!-- 群岛信息 -->
            <div v-if="selectedCity.archipelago" class="archipelago">
              <h4>群岛信息：</h4>
              <ul>
                <li v-for="(value, key) in selectedCity.archipelago" :key="key">
                  {{ key }}: {{ value }}
                </li>
              </ul>
            </div>
            
            <!-- 生态数据 -->
            <div v-if="selectedCity.ecological_data" class="ecological-data">
              <h4>生态数据：</h4>
              <ul>
                <li v-for="(value, key) in selectedCity.ecological_data" :key="key">
                  {{ key }}: {{ value }}
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <!-- 路线推荐 -->
        <div class="route-recommendation">
          <h3>推荐路线</h3>
          <ul>
            <li v-for="(path, index) in routeOptimization.recommended_path" :key="index">
              {{ path }}
            </li>
          </ul>
          <h4>最佳旅游季节</h4>
          <ul>
            <li v-for="(season, region) in routeOptimization.best_season" :key="region">
              <strong>{{ region }}：</strong> {{ season }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// 地图容器引用
const mapContainer = ref(null)
const map = ref(null)
const markers = ref([])
const polylines = ref([])

// 城市数据
const geoData = ref(null)
const cities = ref([])
const selectedCity = ref(null)
const routeOptimization = ref({
  recommended_path: [],
  best_season: {}
})

// 加载地理数据
const loadGeoData = async () => {
  try {
    const response = await fetch('/gis/travel/zhejiang.json')
    geoData.value = await response.json()
    cities.value = geoData.value.cities
    routeOptimization.value = geoData.value.route_optimization
  } catch (error) {
    console.error('加载地理数据失败:', error)
  }
}

// 初始化地图
const initMap = () => {
  if (!mapContainer.value) return
  
  // 创建地图实例，设置中心点为浙江省中心位置
  map.value = L.map(mapContainer.value).setView([29.5, 120.5], 8)
  
  // 添加底图图层
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map.value)
  
  // 添加城市标记
  addCityMarkers()
  
  // 添加推荐路线
  addRecommendedRoutes()
}

// 添加城市标记
const addCityMarkers = () => {
  if (!map.value || !cities.value.length) return
  
  // 清除现有标记
  markers.value.forEach(marker => map.value.removeLayer(marker))
  markers.value = []
  
  // 添加新标记
  cities.value.forEach(city => {
    const { lat, lng } = city.coordinates
    
    // 创建自定义图标，使用城市图片
    const icon = L.icon({
      iconUrl: `/gis/travel/img/${city.name}.jpeg`,
      iconSize: [45, 45],
      iconAnchor: [22, 45],
      popupAnchor: [0, -45],
      className: 'city-marker-icon'
    })
    
    // 创建标记并添加到地图
    const marker = L.marker([lat, lng], { icon }).addTo(map.value)
    
    // 添加点击事件
    marker.on('click', () => {
      selectCity(city)
    })
    
    // 添加弹出信息
    marker.bindPopup(`<b>${city.name}</b><br>${city.city_intro || ''}`)
    
    // 保存标记引用
    markers.value.push(marker)
  })
}

// 添加推荐路线
const addRecommendedRoutes = () => {
  if (!map.value || !routeOptimization.value.recommended_path) return
  
  // 清除现有路线
  polylines.value.forEach(line => map.value.removeLayer(line))
  polylines.value = []
  
  // 路线颜色
  const colors = ['#FF5733', '#33FF57', '#3357FF']
  
  // 解析并添加路线
  routeOptimization.value.recommended_path.forEach((path, index) => {
    // 提取城市名称
    const cityNames = path.split('→').map(part => part.split('（')[0].trim())
    
    // 查找城市坐标
    const routePoints = []
    cityNames.forEach(name => {
      const city = cities.value.find(c => c.name === name)
      if (city) {
        routePoints.push([city.coordinates.lat, city.coordinates.lng])
      }
    })
    
    // 如果有足够的点，创建路线
    if (routePoints.length >= 2) {
      const polyline = L.polyline(routePoints, {
        color: colors[index % colors.length],
        weight: 3,
        opacity: 0.7,
        dashArray: '5, 10'
      }).addTo(map.value)
      
      // 添加路线信息
      polyline.bindTooltip(path)
      
      // 保存路线引用
      polylines.value.push(polyline)
    }
  })
}

// 选择城市
const selectCity = (city) => {
  selectedCity.value = city
  
  // 如果地图已初始化，将视图中心移动到所选城市
  if (map.value) {
    map.value.setView([city.coordinates.lat, city.coordinates.lng], 10)
  }
}

// 组件挂载时初始化
onMounted(async () => {
  await loadGeoData()
  initMap()
})
</script>

<style scoped>
.geo-travel-container {
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
}

.section-title {
  text-align: center;
  margin-bottom: 30px;
}

.section-title h2 {
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
}

.section-title p {
  font-size: 16px;
  color: #666;
}

.content-container {
  display: flex;
  gap: 20px;
  height: calc(100vh - 200px);
  min-height: 600px;
}

/* 图片列表样式 */
.image-list {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.image-list h3 {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.image-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  background-color: white;
}

.image-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.image-card img {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.image-caption {
  padding: 10px;
}

.image-caption h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
}

.image-caption p {
  margin: 0;
  font-size: 14px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 地图容器样式 */
.map-container {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

#map {
  height: 60%;
  min-height: 300px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

/* 城市详情样式 */
.city-detail {
  background-color: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 15px;
  max-height: 300px;
  overflow-y: auto;
}

.city-detail h3 {
  margin-top: 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.detail-content {
  font-size: 14px;
}

.detail-content h4 {
  margin: 15px 0 5px 0;
  color: #333;
}

.detail-content ul {
  margin: 5px 0;
  padding-left: 20px;
}

.detail-content li {
  margin-bottom: 5px;
}

/* 路线推荐样式 */
.route-recommendation {
  background-color: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.route-recommendation h3 {
  margin-top: 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.route-recommendation ul {
  margin: 10px 0;
  padding-left: 20px;
}

.route-recommendation li {
  margin-bottom: 8px;
  line-height: 1.5;
}

/* 自定义标记样式 */
.marker-pin {
  background-color: #3388ff;
  color: white;
  border-radius: 50% 50% 50% 0;
  width: 30px;
  height: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 12px;
  font-weight: bold;
  border: 2px solid white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.6);
  transform: rotate(-45deg);
  transition: all 0.3s ease;
  position: relative;
}

.marker-pin:hover {
  transform: rotate(-45deg) scale(1.15);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.7);
}

/* 城市图片标记样式 */
.city-marker-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.6);
  overflow: hidden;
  transition: all 0.3s ease;
  object-fit: cover;
}

.city-marker-icon:hover {
  transform: scale(1.15);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.7);
}

/* Pin样式容器 */
.pin-container {
  position: relative;
  width: 50px;
  height: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  transform-origin: bottom center;
  transition: all 0.3s ease;
}

.pin-container:hover {
  transform: scale(1.1);
}

.pin-top {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.6);
  z-index: 2;
  background-color: white;
}

.pin-bottom {
  width: 20px;
  height: 20px;
  background-color: white;
  transform: rotate(45deg);
  margin-top: -10px;
  box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3);
  z-index: 1;
}

.leaflet-marker-icon {
  background: transparent !important;
  border: none !important;
}
</style>