<script setup lang="ts">
import { RouterView } from 'vue-router'
import LoginModal from './components/LoginModal.vue'
import NavBar from './components/NavBar.vue'
// import { initTracing } from './config/tracing'

// 初始化 OpenTelemetry 追踪
// initTracing();

// import agent from 'skywalking-backend-js';

// try {
//     agent.start({
//         serviceName: 'aka-music-frontend',
//         serviceInstance: 'aka-music-frontend-instance-0',
//         collectorAddress: '127.0.0.1:11800',
//         // disablePlugins: 'pg/lib/client,mysql/lib/Connection,ioredis,mongoose,express/lib/router,amqplib/lib/channel,mongodb/lib/collection,aws-sdk,mongodb/lib/cursor,mongodb/lib/db',
//         // disablePlugins: `"pg/lib/client","mysql/lib/Connection","ioredis","mongoose","express/lib/router","amqplib/lib/channel","mongodb/lib/collection","aws-sdk","mongodb/lib/cursor","mongodb/lib/db"`,
//     });
// } catch (error) {
//     console.log(error);
// }

</script>

<template>
  <div class="app-container">
    <NavBar />
    <RouterView />
    <LoginModal />
  </div>
</template>

<style scoped>
.app-container {
  width: 100%;
  min-height: 100vh;
  box-sizing: border-box;
}

.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  margin: 0;
  font-size: 24px;
  color: #1890ff;
}
</style>
