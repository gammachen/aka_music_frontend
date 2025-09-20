<template>
  <div class="content-manager">
    <a-row :gutter="16">
      <a-col :span="8">
        <a-card title="内容分类">
          <a-tree
            v-model:selectedKeys="selectedKeys"
            v-model:expandedKeys="expandedKeys"
            :tree-data="treeData"
            :replaceFields="{ title: 'name', key: 'id' }"
          >
            <template #title="{ name, type }">
              <span>{{ name }}</span>
              <a-dropdown>
                <template #overlay>
                  <a-menu>
                    <a-menu-item key="1" @click="showAddModal(type)">添加子节点</a-menu-item>
                  </a-menu>
                </template>
                <more-outlined class="action-icon" />
              </a-dropdown>
            </template>
          </a-tree>
        </a-card>
      </a-col>
      <a-col :span="16">
        <a-card title="内容详情">
          <div v-if="!selectedKeys.length">
            <p>请选择左侧的节点查看详情</p>
          </div>
          <div v-else class="upload-section">
            <a-upload-dragger
              v-model:fileList="fileList"
              name="file"
              :multiple="true"
              :before-upload="beforeUpload"
              @change="handleChange"
              :accept="acceptFileTypes"
              action="/api/backend/content/upload_chapters"
            >
              <p class="ant-upload-drag-icon">
                <inbox-outlined />
              </p>
              <p class="ant-upload-text">点击或拖拽文件到此区域上传</p>
              <p class="ant-upload-hint">
                支持上传音频、视频、PDF、Mobi、Txt格式文件，可同时上传多个文件
              </p>
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
                    <template #actions>
                      <a-button
                        v-if="item.status !== 'uploading'"
                        type="link"
                        @click="handleRemove(item)"
                      >
                        删除
                      </a-button>
                    </template>
                  </a-list-item>
                </template>
              </a-list>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 添加节点的模态框 -->
    <a-modal
      v-model:visible="modalVisible"
      title="添加节点"
      @ok="handleAddNode"
      @cancel="handleCancel"
    >
      <a-form :model="formState" :rules="rules">
        <a-form-item label="名称" name="name">
          <a-input v-model:value="formState.name" />
        </a-form-item>
        <a-form-item label="类型" name="type">
          <a-select v-model:value="formState.type">
            <a-select-option value="COMIC">漫画</a-select-option>
            <a-select-option value="MUSIC">音乐</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { MoreOutlined } from '@ant-design/icons-vue'
import { InboxOutlined } from '@ant-design/icons-vue'
import type { UploadProps } from 'ant-design-vue'

// 文件上传相关
const fileList = ref<any[]>([])
const acceptFileTypes = '.mp3,.wav,.mp4,.avi,.pdf,.mobi,.txt,.jpg,.png,.jpeg,.gif,.epub,.bmp'

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

  if (file.status === 'uploading') {
    // 处理上传中状态
    return
  }

  if (file.status === 'done') {
    try {
      const formData = new FormData()
      formData.append('content_id', selectedKeys.value[0])
      formData.append('files', file.originFileObj)

      const response = await uploadChapters(formData)
      if (response.code === 200) {
        message.success(`${file.name} 上传成功`)
      } else {
        file.status = 'error'
        message.error(`${file.name} 上传失败: ${response.message}`)
      }
    } catch (error) {
      file.status = 'error'
      message.error(`${file.name} 上传失败：${error.message}`)
    }
  } else if (file.status === 'error') {
    message.error(`${file.name} 上传失败`)
  }
}

const handleRemove = (file: any) => {
  const index = fileList.value.indexOf(file)
  const newFileList = fileList.value.slice()
  newFileList.splice(index, 1)
  fileList.value = newFileList
}
import type { TreeDataItem } from 'ant-design-vue/es/tree/Tree'
import { getContentTree, addContentNode, uploadChapters, type ContentNode } from '../../../api/backend'

// 树形数据
const treeData = ref<TreeDataItem[]>([])
const selectedKeys = ref<string[]>([])
const expandedKeys = ref<string[]>([])

// 模态框相关
const modalVisible = ref(false)
const formState = ref({
  name: '',
  type: 'COMIC'
})

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }]
}

// 显示添加节点模态框
const showAddModal = (type: string) => {
  formState.value.type = type
  modalVisible.value = true
}

// 处理添加节点
const handleAddNode = async () => {
  try {
    const { data } = await addContentNode({
      name: formState.value.name,
      type: formState.value.type,
      parentId: selectedKeys.value[0]
    })
    message.success('添加成功')
    modalVisible.value = false
    await loadTreeData()
  } catch (error) {
    message.error('添加失败')
  }
}

// 加载树形数据
const loadTreeData = async () => {
  try {
    const { data } = await getContentTree()
    if (Array.isArray(data)) {
      treeData.value = data
    } else {
      message.error('数据格式错误')
    }
  } catch (error) {
    message.error('加载数据失败')
  }
}

// 取消添加
const handleCancel = () => {
  modalVisible.value = false
  formState.value = {
    name: '',
    type: 'COMIC'
  }
}

onMounted(() => {
  loadTreeData()
})
</script>

<style scoped>
.content-manager {
  padding: 24px;
}

.action-icon {
  margin-left: 8px;
  font-size: 14px;
  color: #999;
  cursor: pointer;
}

.action-icon:hover {
  color: #1890ff;
}

.upload-section {
  padding: 16px;
  height: calc(100vh - 150px);
  overflow-y: auto;
}

.upload-list {
  margin-top: 16px;
}

.success-text {
  color: #52c41a;
}

.error-text {
  color: #ff4d4f;
}

:deep(.ant-card) {
  height: calc(100vh - 100px);
  position: sticky;
  top: 24px;
}

:deep(.ant-card-body) {
  height: calc(100% - 57px);
  overflow-y: auto;
}
</style>