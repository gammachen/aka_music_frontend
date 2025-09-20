<template>
  <Layout class="layout">
    <Layout.Content class="main-content">
      <div class="main-layout">
        <div class="content">
          <el-card class="topic-form">
            <template #header>
              <div class="card-header">
                <h2>发布主题</h2>
              </div>
            </template>
            <el-form :model="topicForm" :rules="rules" ref="formRef">
              <el-form-item label="标题" prop="title">
                <el-input v-model="topicForm.title" placeholder="请输入主题标题"></el-input>
              </el-form-item>
              <el-form-item label="分类" prop="category">
                <el-select v-model="topicForm.category" placeholder="请选择分类" popper-class="category-select">
                  <el-option label="华语" value="Mandarin">
                    <template #default>
                      <span><SoundOutlined /> 华语</span>
                    </template>
                  </el-option>
                  <el-option label="日韩" value="JapaneseKorean">
                    <template #default>
                      <span><SoundOutlined /> 日韩</span>
                    </template>
                  </el-option>
                  <el-option label="欧美" value="Western">
                    <template #default>
                      <span><SoundOutlined /> 欧美</span>
                    </template>
                  </el-option>
                  <el-option label="Remix" value="Remix">
                    <template #default>
                      <span><SoundOutlined /> Remix</span>
                    </template>
                  </el-option>
                  <el-option label="纯音乐" value="Instrumental">
                    <template #default>
                      <span><SoundOutlined /> 纯音乐</span>
                    </template>
                  </el-option>
                  <el-option label="异次元" value="AlternateDimension">
                    <template #default>
                      <span><SoundOutlined /> 异次元</span>
                    </template>
                  </el-option>
                  <el-option label="特供" value="Exclusive">
                    <template #default>
                      <span><SoundOutlined /> 特供</span>
                    </template>
                  </el-option>
                  <el-option label="百科" value="Encyclopedia">
                    <template #default>
                      <span><EditOutlined /> 百科</span>
                    </template>
                  </el-option>
                  <el-option label="站务" value="StationManagement">
                    <template #default>
                      <span><CommentOutlined /> 站务</span>
                    </template>
                  </el-option>
                </el-select>
            </el-form-item>
            <el-form-item label="内容" prop="content">
              <div class="editor-container">
                <Toolbar
                  style="border-bottom: 1px solid #ccc"
                  :editor="editorRef"
                  :defaultConfig="toolbarConfig"
                  mode="default"
                />
                <Editor
                  class="editor"
                  style="height: 200px"
                  v-model="topicForm.content"
                  :defaultConfig="editorConfig"
                  :mode="mode"
                  @onCreated="handleCreated"
                />
              </div>
            </el-form-item>
            
            <el-form-item label="隐藏" prop="hiddenContent">
              <div class="editor-container">
                <Toolbar
                  style="border-bottom: 1px solid #ccc"
                  :editor="hiddenEditorRef"
                  :defaultConfig="toolbarConfig"
                  mode="default"
                />
                <Editor
                  class="editor"
                  style="height: 200px"
                  v-model="topicForm.hiddenContent"
                  :defaultConfig="editorConfig"
                  :mode="mode"
                  @onCreated="handleHiddenCreated"
                />
              </div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitForm">发布</el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        </div>
        
        <div class="sider">
          <ACard title="站点数据" class="stats-card">
            <div class="stats-content">
              <Statistic title="主题数" :value="siteStats.topics" />
              <Statistic title="今日帖子" :value="siteStats.todayPosts" />
              <Statistic title="今日主题" :value="siteStats.todayTopics" />
            </div>
          </ACard>
          
          <ACard title="关键词" class="tags-card">
            <div class="tags-container">
              <Tag v-for="tag in hotTags" :key="tag" class="tag">
                {{ tag }}
              </Tag>
            </div>
          </ACard>
        </div>
      </div>
    </Layout.Content>
  </Layout>
</template>

<script lang="ts" setup>
import { ref, reactive, onBeforeUnmount, shallowRef } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ElCard, ElForm, ElFormItem, ElInput, ElSelect, ElOption, ElButton, ElSwitch } from 'element-plus'
import { Layout, Card as ACard, Tag, Statistic } from 'ant-design-vue'
import { SoundOutlined, EditOutlined, CommentOutlined } from '@ant-design/icons-vue'
import '@wangeditor/editor/dist/css/style.css'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import { createTopic } from '../../api/topic'

const router = useRouter()
const formRef = ref()

// 站点数据
const siteStats = reactive({
  topics: 80055,
  todayPosts: 9052,
  todayTopics: 40
})

// 热门标签
const hotTags = ref(['流行', '摇滚', '民谣', '电子', '古典', '爵士', '说唱', '乡村'])

// 编辑器实例，必须用 shallowRef
const editorRef = shallowRef()
const hiddenEditorRef = shallowRef()

// 编辑器内容
const valueHtml = ref('')
const hiddenValueHtml = ref('')

// 模式
const mode = 'default'

const topicForm = reactive({
  title: '',
  category: '',
  content: '',
  hasHiddenContent: false,
  hiddenContent: '',
  hiddenContentCondition: 'reply' // 'reply' | 'vip'
})

const editorConfig = {
  placeholder: '请输入内容...',
  autoFocus: false,
  MENU_CONF: {
    uploadImage: {
      server: '/api/upload/image',
      fieldName: 'file',
      maxFileSize: 10 * 1024 * 1024,
      maxNumberOfFiles: 10,
      allowedFileTypes: ['image/*'],
      metaWithUrl: true,
      withCredentials: true,
      timeout: 5 * 1000,
      customInsert: (result, insertFn) => {
        // 从服务器响应中获取图片URL
        const url = result.data.url
        // 调用insertFn将图片插入到编辑器
        insertFn(url)
      }
    }
  }
}

const toolbarConfig = {
  toolbarKeys: [
    'headerSelect',
    'bold',
    'italic',
    'underline',
    'through',
    'color',
    'bgColor',
    'bulletedList',
    'numberedList',
    'uploadImage',
    'insertLink',
    'code',
    'blockquote',
    'divider'
  ]
}

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }],
  hiddenContent: [{ required: false, message: '请输入隐藏内容', trigger: 'blur' }]
}

const handleCreated = (editor) => {
  editorRef.value = editor
}

const handleHiddenCreated = (editor) => {
  hiddenEditorRef.value = editor
}

// 组件销毁时，销毁编辑器
onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor == null) return
  editor.destroy()

  const hiddenEditor = hiddenEditorRef.value
  if (hiddenEditor == null) return
  hiddenEditor.destroy()
})

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        const response = await createTopic({
          title: topicForm.title,
          category: topicForm.category,
          content: topicForm.content,
          hidden_content: topicForm.hiddenContent
        })
        ElMessage.success('发布成功')
        router.push(`/topic/${response.data.id}`)
      } catch (error: any) {
        ElMessage.error(error.message || '发布失败')
      }
    } else {
      ElMessage.error('请完善表单信息')
      return false
    }
  })
}

const resetForm = () => {
  if (!formRef.value) return
  formRef.value.resetFields()
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
}

.main-content {
  padding: 24px;
  background: #f0f2f5;
}

.main-layout {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 24px;
}

.topic-form {
  background: #fff;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.editor-container {
  border: 1px solid #ccc;
  z-index: 100;
  width: 100%;
  margin-bottom: 16px;
  border-radius: 4px;
}

.editor {
  height: 500px;
  overflow-y: hidden;
  width: 100%;
  padding: 0 16px;
}

.stats-card,
.tags-card {
  margin-bottom: 24px;
}

.stats-content {
  display: grid;
  gap: 16px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  cursor: pointer;
}

@media (max-width: 768px) {
  .main-layout {
    grid-template-columns: 1fr;
  }
  
  .sider {
    order: -1;
  }
}
.topic-form :deep(.el-form-item__label) {
  width: 70px;
  text-align: right;
  padding-right: 12px;
  box-sizing: border-box;
}

.topic-form :deep(.el-form-item__content) {
  margin-left: 10px !important;
}
</style>