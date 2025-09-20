<script setup lang="ts">
</script>

<template>
    <div class="home-container">
        <div class="button-group">
            <button 
                class="action-btn" 
                @click="$router.push({ name: 'Editor' })"
            >
                进入编辑器
            </button>
            <button 
                class="action-btn" 
                @click="$router.push({ name: 'CusComponents' })"
            >
                自定义组件演示
            </button>
        </div>
    </div>
</template>

<style scoped>
.home-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.button-group {
    display: flex;
    flex-direction: column;
    gap: 20px;
    align-items: center;
}

.action-btn {
    padding: 16px 32px;
    font-size: 18px;
    font-weight: 500;
    color: white;
    background: rgba(255, 255, 255, 0.2);
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
    min-width: 200px;
}

.action-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
    transform: translateY(-2px);
}

.action-btn:active {
    transform: translateY(0);
}
</style>
