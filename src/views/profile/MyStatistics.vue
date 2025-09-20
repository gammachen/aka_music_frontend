<template>
  <div class="my-statistics">
    <a-row :gutter="[16, 16]">
      <a-col :span="8">
        <a-card>
          <template #title>主题统计</template>
          <a-statistic title="发布主题" :value="statistics.topicCount" />
          <a-statistic title="主题回复" :value="statistics.replyCount" />
          <a-statistic title="主题浏览" :value="statistics.viewCount" />
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card>
          <template #title>积分统计</template>
          <a-statistic title="当前积分" :value="statistics.currentPoints" />
          <a-statistic title="累计获得" :value="statistics.totalEarnedPoints" />
          <a-statistic title="累计消费" :value="statistics.totalSpentPoints" />
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card>
          <template #title>互动统计</template>
          <a-statistic title="获得点赞" :value="statistics.receivedLikes" />
          <a-statistic title="收到评论" :value="statistics.receivedComments" />
          <a-statistic title="被收藏数" :value="statistics.receivedFavorites" />
        </a-card>
      </a-col>
    </a-row>

    <a-card class="chart-card" :bordered="false">
      <template #title>近期活跃度</template>
      <div class="chart-container">
        <div class="chart-placeholder">图表区域（需要集成图表库展示活跃度趋势）</div>
      </div>
    </a-card>

    <a-card class="chart-card" :bordered="false">
      <template #title>主题分类分布</template>
      <div class="chart-container">
        <div class="chart-placeholder">图表区域（需要集成图表库展示主题分类分布）</div>
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Row, Col, Card, Statistic } from 'ant-design-vue'

const statistics = ref({
  topicCount: 0,
  replyCount: 0,
  viewCount: 0,
  currentPoints: 0,
  totalEarnedPoints: 0,
  totalSpentPoints: 0,
  receivedLikes: 0,
  receivedComments: 0,
  receivedFavorites: 0
})

const fetchStatistics = async () => {
  try {
    // TODO: 替换为实际的API调用
    const response = await fetch('/api/user/statistics')
    const data = await response.json()
    statistics.value = data
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

onMounted(() => {
  fetchStatistics()
})
</script>

<style scoped>
.my-statistics {
  background: #fff;
}

.chart-card {
  margin-top: 16px;
}

.chart-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafa;
  border-radius: 2px;
}

.chart-placeholder {
  color: #999;
  font-size: 14px;
}

.ant-statistic {
  margin-bottom: 16px;
}

.ant-statistic:last-child {
  margin-bottom: 0;
}
</style>