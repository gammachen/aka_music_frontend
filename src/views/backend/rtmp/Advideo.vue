<template>
  <Layout class="layout">
    <Layout.Content class="main-content">
      <div class="main-layout">
        <div class="content">
          <a-card title="视频上传" class="upload-card">
            <a-upload-dragger
              v-model:fileList="fileList"
              name="file"
              :multiple="true"
              :before-upload="beforeUpload"
              @change="handleChange"
              :accept="acceptFileTypes"
              :customRequest="customUpload"
              class="upload-area"
            >
              <p class="ant-upload-drag-icon">
                <inbox-outlined />
              </p>
              <p class="ant-upload-text">点击或拖拽文件到此区域上传</p>
              <p class="ant-upload-hint">支持上传视频文件</p>
            </a-upload-dragger>
            <div class="upload-list" v-if="fileList.length">
              <a-list :data-source="fileList" size="small">
                <template #renderItem="{ item }">
                  <a-list-item>
                    <a-list-item-meta>
                      <template #title>
                        {{ item.name }}
                      </template>
                      <template #description>
                        <a-progress
                          v-if="item.status === 'uploading'"
                          :percent="item.percent"
                          size="small"
                        />
                        <span v-else-if="item.status === 'done'" class="success-text">
                          上传成功
                        </span>
                        <span v-else-if="item.status === 'error'" class="error-text">
                          上传失败
                        </span>
                      </template>
                    </a-list-item-meta>
                  </a-list-item>
                </template>
              </a-list>
            </div>
          </a-card>
        </div>
        
        <div class="sider">
          <a-card title="上传说明" class="info-card">
            <div class="info-content">
              <p>• 支持的视频格式：MP4、AVI、WAV</p>
              <p>• 单个文件大小不超过500MB</p>
              <p>• 视频分辨率建议：1920×1080</p>
            </div>
          </a-card>
        </div>
      </div>
    </Layout.Content>
  </Layout>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import { InboxOutlined } from '@ant-design/icons-vue'
import type { UploadProps } from 'ant-design-vue'
import { Layout } from 'ant-design-vue'
import { uploadAdvideo } from '../../../api/backend'

const fileList = ref<any[]>([])
const acceptFileTypes = '.wav,.mp4,.avi'

const customUpload = async (options: any) => {
  const { file, onProgress, onSuccess, onError } = options
  const formData = new FormData()
  formData.append('files', file)

  try {
    const response = await uploadAdvideo(formData, (progressEvent: any) => {
      const percent = Math.floor((progressEvent.loaded / progressEvent.total) * 100)

      onProgress({ percent })
    })

    if (response.code === 200) {
      onSuccess(response)
    } else {
      onError(new Error(response.message || '上传失败'))
    }
  } catch (error: any) {
    onError(error)
  }
}

const beforeUpload = (file: File) => {
  const isValidType = acceptFileTypes.split(',').some(type => 
    file.name.toLowerCase().endsWith(type.toLowerCase())
  )
  if (!isValidType) {
    message.error('不支持的文件类型！')
    return false
  }
  return true
}

const handleChange: UploadProps['onChange'] = async (info) => {
  fileList.value = info.fileList
  const file = info.file

  console.log('文件上传状态变更:', {
    fileName: file.name,
    fileSize: file.size,
    fileType: file.type,
    status: file.status
  })

  if (file.status === 'uploading') {
    console.log('文件正在上传中:', file.name, '进度:', file.percent, '%')
    return
  }

  if (file.status === 'done') {
    const response = file.response
    if (response && response.code === 200) {
      message.success(`${file.name} 上传成功 ${response.data.online_url}`)
      console.log('文件上传成功:', file.name)
    } else {
      file.status = 'error'
      console.error('文件上传失败:', {
        fileName: file.name,
        errorCode: response?.code,
        errorMessage: response?.message
      })
      message.error(`${file.name} 上传失败: ${response?.message || '服务器错误'}`)
    }
  } else if (file.status === 'error') {
    console.error('文件上传失败:', file.name)
    message.error(`${file.name} 上传失败`)
  }
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
  background-color: #f0f2f5;
}

.main-content {
  padding: 24px;
}

.main-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.content {
  width: 100%;
}

.upload-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.upload-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.upload-area {
  padding: 32px;
  transition: all 0.3s ease;
}

.upload-list {
  margin-top: 16px;
  padding: 0 32px 32px;
}

.success-text {
  color: #52c41a;
  display: flex;
  align-items: center;
  gap: 4px;
}

.error-text {
  color: #ff4d4f;
  display: flex;
  align-items: center;
  gap: 4px;
}

.sider {
  width: 100%;
}

.info-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.info-content {
  padding: 16px;
}

.info-content p {
  margin-bottom: 12px;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

:deep(.ant-upload-drag) {
  border-radius: 8px;
  border: 2px dashed #d9d9d9;
  transition: all 0.3s ease;
}

:deep(.ant-upload-drag:hover) {
  border-color: #1890ff;
}

:deep(.ant-upload-drag-icon) {
  color: #1890ff;
  font-size: 48px;
  margin-bottom: 16px;
}

:deep(.ant-upload-text) {
  font-size: 16px;
  color: #262626;
  margin: 8px 0;
}

:deep(.ant-upload-hint) {
  color: #595959;
}

:deep(.ant-card-head) {
  border-bottom: 1px solid #f0f0f0;
  padding: 16px 32px;
}

:deep(.ant-card-head-title) {
  font-size: 16px;
  font-weight: 500;
}

:deep(.ant-card-body) {
  padding: 0;
}

:deep(.ant-list-item) {
  padding: 12px 0;
  transition: background-color 0.3s ease;
}

:deep(.ant-list-item:hover) {
  background-color: #fafafa;
}

:deep(.ant-list-item-meta-title) {
  color: #262626;
  margin-bottom: 4px;
}

:deep(.ant-progress) {
  margin-top: 4px;
}

@media (max-width: 768px) {
  .main-layout {
    grid-template-columns: 1fr;
  }
  
  .main-content {
    padding: 16px;
  }
  
  .upload-area {
    padding: 24px;
  }
  
  .upload-list {
    padding: 0 24px 24px;
  }
}
</style>