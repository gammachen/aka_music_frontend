<template>
  <div class="datalab-loading-container">
    <div class="datalab-loading-content">
      <div class="datalab-loading-image">
        <img src="/img/robot.svg" alt="AI Robot" class="robot-image" />
      </div>
      <div class="datalab-loading-text">
        <h1 class="datalab-title">AI For Document Intelligence</h1>
        <p class="datalab-description">
          We train AI models for OCR, layout analysis, PDF to markdown, and more. They're state of the art, easy to use, and open source.
        </p>
        <div class="datalab-loading-spinner">
          <div class="spinner"></div>
          <span>Processing your document...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 可以在这里添加组件的逻辑代码
</script>

<style scoped lang="less">
.datalab-loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.datalab-loading-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  max-width: 1200px;
  width: 100%;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 40px;
  margin: 20px;
  
  @media (max-width: 768px) {
    flex-direction: column;
    padding: 20px;
  }
}

.datalab-loading-image {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  
  .robot-image {
    max-width: 100%;
    height: auto;
    max-height: 300px;
  }
}

.datalab-loading-text {
  flex: 1;
  padding: 20px;
}

.datalab-title {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 16px;
  color: #333;
  line-height: 1.2;
}

.datalab-description {
  font-size: 1.1rem;
  color: #666;
  margin-bottom: 30px;
  line-height: 1.6;
}

.datalab-loading-spinner {
  display: flex;
  align-items: center;
  margin-top: 20px;
  
  .spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    border-top: 4px solid #1890ff;
    width: 30px;
    height: 30px;
    animation: spin 1s linear infinite;
    margin-right: 16px;
  }
  
  span {
    font-size: 1rem;
    color: #1890ff;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>