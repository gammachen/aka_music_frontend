<template>
  <section class="app-promotion">
    <div class="app-content">
      <div class="app-info">
        <h2>{{ title }}</h2>
        <p>{{ description }}</p>
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
      <div class="app-qrcode" v-if="showQRCode">
        <img src="../assets/qrcode.png" alt="扫码下载" />
        <p>扫码下载</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { Button } from 'ant-design-vue'
import { AppleOutlined, AndroidOutlined } from '@ant-design/icons-vue'

interface Props {
  title?: string
  description?: string
  showQRCode?: boolean
}

withDefaults(defineProps<Props>(), {
  title: '下载AKAAPP',
  description: '随时随地，畅享高品质内容',
  showQRCode: true
})
</script>

<style scoped>
.app-promotion {
  margin: 40px 0;
  padding: 40px 20px;
  background: #f5f5f5;
  border-radius: 16px;
}

.app-content {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;
}

.app-info {
  flex: 1;
}

.app-info h2 {
  font-size: 28px;
  margin-bottom: 16px;
}

.app-info p {
  font-size: 16px;
  margin-bottom: 24px;
  color: #666;
}

.app-buttons {
  display: flex;
  gap: 16px;
}

.app-qrcode {
  text-align: center;
}

.app-qrcode img {
  width: 120px;
  height: 120px;
  margin-bottom: 8px;
}

.app-qrcode p {
  font-size: 14px;
  color: #666;
}

@media (max-width: 768px) {
  .app-content {
    flex-direction: column;
    text-align: center;
  }

  .app-buttons {
    justify-content: center;
  }

  .app-qrcode {
    margin-top: 20px;
  }
}
</style>