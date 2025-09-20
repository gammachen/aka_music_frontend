<template>
  <section class="music-effect-section">
    <div class="effect-container">
      <div class="background-layer"></div>
      <div class="wave-effect">
        <div class="wave-circle"></div>
        <div class="wave-circle"></div>
        <div class="wave-circle"></div>
        <div class="wave-circle"></div>
        <div class="wave-circle"></div>
        <div class="wave-circle"></div>
        <div class="wave-circle"></div>
      </div>
      <div class="phone-layer">
        <img src="../assets/phone.webp" alt="手机设备" />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
// 无需props，使用固定的动效展示
</script>

<style scoped>
.music-effect-section {
  padding: 60px 0;
  overflow: hidden;
  background-color: #f5f5f5;
}

.effect-container {
  position: relative;
  height: 500px;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
}

.background-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('../assets/sky.webp') center/cover no-repeat;
  opacity: 0.6;
  z-index: 1;
}

.wave-effect {
  position: absolute;
  width: 300px;
  height: 300px;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.wave-circle {
  position: absolute;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  width: 100%;
  height: 100%;
  animation: wave 2s infinite;
  opacity: 0;
}

.wave-circle:nth-child(2) {
  animation-delay: 0.5s;
}

.wave-circle:nth-child(3) {
  animation-delay: 1s;
}

@keyframes wave {
  0% {
    transform: scale(0.1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 0;
  }
}

.phone-layer {
  position: absolute;
  right: 5%;
  z-index: 5;
  max-width: 250px;
  max-height: 100%;
}

.phone-layer img {
  width: 100%;
  height: auto;
  object-fit: contain;
}

@media (max-width: 768px) {
  .music-effect-section {
    height: 300px;
  }
  
  .phone-layer {
    max-width: 200px;
  }
}

@media (max-width: 480px) {
  .music-effect-section {
    height: 250px;
  }
  
  .phone-layer {
    max-width: 150px;
  }
}
</style>