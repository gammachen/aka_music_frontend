<template>
  <Modal
    :visible="visible"
    @update:visible="emit('update:visible', $event)"
    title="打赏作者"
    @ok="handleConfirm"
    @cancel="handleCancel"
    :confirmLoading="loading"
    class="reward-modal"
  >
    <div class="reward-content">
      <div class="reward-header">
        <img :src="duckImage" class="reward-icon" />
        <div class="reward-text">
          <h3>小月亮 (0.1金币)</h3>
          <p>捐赠66金币，获得小月亮</p>
        </div>
      </div>
      
      <div class="reward-options">
        <div
          v-for="option in rewardOptions"
          :key="option.coins"
          class="reward-option"
          :class="{ active: selectedOption === option.coins }"
          @click="selectOption(option.coins)"
        >
          <span class="icon-wrapper">
            <StarOutlined v-if="option.coins === 10" />
            <el-icon v-else-if="option.coins === 66"><Moon /></el-icon>
            <el-icon v-else-if="option.coins === 188"><Sunny /></el-icon>
            <HeartOutlined v-else-if="option.coins === 520" />
          </span>
          <div class="text-content">
            <span class="coins">{{ option.coins }}</span>
            <span class="reward">{{ option.reward }}</span>
          </div>
        </div>
      </div>

      <div class="reward-info">
        <p><GoldOutlined /> 当前余额：{{ balance }} 金币</p>
        <a-button type="link" @click="handleRecharge"><WalletOutlined /> 充值</a-button>
      </div>
    </div>
  </Modal>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits } from 'vue'
import { Modal } from 'ant-design-vue'
import { ElMessage } from 'element-plus'
// import { StarOutlined, MoonOutlined, SunOutlined, HeartOutlined, GoldOutlined, WalletOutlined } from '@ant-design/icons-vue'
import { StarOutlined, HeartOutlined, GoldOutlined, WalletOutlined } from '@ant-design/icons-vue'
import { Moon, Sunny } from '@element-plus/icons-vue'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  (e: 'update:visible', visible: boolean): void
  (e: 'confirm', amount: number): void
}>()

const loading = ref(false)
const balance = ref(100) // 用户余额，实际应该从API获取
const selectedOption = ref(10)

const rewardOptions = [
  { coins: 10, reward: '小星星' },
  { coins: 66, reward: '小月亮' },
  { coins: 188, reward: '小太阳' },
  { coins: 520, reward: '小彩虹' },
]

const duckImage = 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix' // 示例图片

const selectOption = (coins: number) => {
  selectedOption.value = coins
}

const handleConfirm = async () => {
  if (balance.value < selectedOption.value) {
    ElMessage.warning('余额不足，请先充值')
    return
  }

  loading.value = true
  try {
    emit('confirm', selectedOption.value)
    emit('update:visible', false)
  } catch (error) {
    console.error('打赏失败:', error)
    ElMessage.error('打赏失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  emit('update:visible', false)
}

const handleRecharge = () => {
  // TODO: 实现充值功能
  ElMessage.info('充值功能开发中...')
}
</script>

<style scoped>
.reward-content {
  padding: 20px;
}

.reward-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.reward-icon {
  width: 48px;
  height: 48px;
  margin-right: 16px;
}

.reward-text h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.reward-text p {
  margin: 4px 0 0;
  font-size: 14px;
  color: #666;
}

.reward-modal :deep(.ant-modal-content) {
  border-radius: 8px;
  position: relative;
}

.reward-modal :deep(.ant-modal-content)::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-top: 10px solid #fff;
  filter: drop-shadow(0 2px 2px rgba(0, 0, 0, 0.1));
}

.reward-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.reward-option {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.reward-option:hover {
  border-color: #1890ff;
}

.reward-option.active {
  border-color: #1890ff;
  background-color: #e6f7ff;
}

.icon-wrapper {
  font-size: 20px;
  color: #1890ff;
  margin-right: 12px;
}

.reward-option .text-content {
  display: flex;
  flex-direction: column;
}

.reward-option .coins {
  font-size: 16px;
  font-weight: bold;
  color: #1890ff;
  line-height: 1.2;
}

.reward-option .reward {
  font-size: 12px;
  color: #666;
}

.reward-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.reward-info p {
  margin: 0;
  color: #666;
  display: flex;
  align-items: center;
  gap: 4px;
}

.reward-info .anticon {
  font-size: 16px;
  color: #1890ff;
}
</style>