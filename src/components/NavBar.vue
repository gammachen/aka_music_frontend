<template>
  <el-header class="navbar">
    <div class="nav-container">
      <div class="logo-section">
        <router-link to="/">
          <img src="../assets/logo.png" alt="AKA Music" class="logo" />
        </router-link>
      </div>

      <div class="nav-menu">
        <el-menu
          mode="horizontal"
          :router="false"
          :ellipsis="false"
          class="nav-menu-items"
          @select="handleSelect"
        >
          <el-menu-item index="/">Discover</el-menu-item>
          <el-sub-menu index="genre">
            <template #title>分类</template>
            <el-menu-item index="/beaulanding">图库</el-menu-item>
            <el-menu-item index="/">音乐</el-menu-item>
            <el-menu-item index="/education/genre">教育</el-menu-item>
            <el-menu-item index="/comiclanding">漫画</el-menu-item>
            <el-menu-item index="/beaulist/2fbcd878905dbc01aba09aed83c6e465">医疗</el-menu-item>
            <el-menu-item index="/genre">全部分类</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="music">
            <template #title>音乐</template>
            <el-menu-item index="/mugrid/4">经典粤语</el-menu-item>
            <el-menu-item index="/mugrid/6">一人一首</el-menu-item>
            <el-menu-item index="/mugrid/16">8090后的回忆</el-menu-item>
            <el-menu-item index="/mugrid/3">经典</el-menu-item>
            <el-menu-item index="/genre">全部分类</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="medical">
            <template #title>图库</template>
            <el-menu-item index="/beaulist/37e3808047553cedb34daa9b1d7ab2a3">写真</el-menu-item>
            <el-menu-item index="/beaulist/54bfa7dddf34a32bf94daf15abe844e2">商务</el-menu-item>
            <el-menu-item index="/beaulist/622b43dc6337cf2ae6e0600d5db07483">家庭</el-menu-item>
            <el-menu-item index="/beaulist/4675fbaf3ec53d12ec85cf79c0a04718">爵士</el-menu-item>
            <el-menu-item index="/beaulist/2fbcd878905dbc01aba09aed83c6e465">医疗</el-menu-item>
            <el-menu-item index="/beaulist/f2cbe035b67b61d214b4ba2f6bb43f26">人脸</el-menu-item>
            <el-menu-item index="/beaulist/4675fbaf3ec53d12ec85cf79c0a04718">动物</el-menu-item>
            <el-menu-item index="/beaulist/f7d29dfae05b5d049b64b040b14d9a00">城市</el-menu-item>
            <el-menu-item index="/beaulist/35d9969dfa48df5544b9a005ac4f3f92">学生</el-menu-item>
            <el-menu-item index="/beaulist/d4c38977656e2356a6837e7b771bd408">家居</el-menu-item>
            <el-menu-item index="/beaulist/622b43dc6337cf2ae6e0600d5db07483">家庭</el-menu-item>
            <el-menu-item index="/beaulist/4b7aab3e91bec2962cf8ea132fb65808">建筑</el-menu-item>
            <el-menu-item index="/beaulist/5edd2814297895fb781eaac417218183">机械</el-menu-item>
            <el-menu-item index="/beaulanding">图片分类</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="comic">
            <template #title>动漫</template>
            <el-menu-item index="/comiclanding">首页</el-menu-item>
            <el-menu-item index="/comic/9fb8f2e5-4758-4d74-9b5d-a680598cf080">海贼王</el-menu-item>
            <el-menu-item index="/comic/genre">漫画分类</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="教育">
            <template #title>教育</template>
            <el-menu-item index="/education/genre">首页</el-menu-item>
            <el-menu-item index="/education/DIdi%E2%80%99s%20Day%20%E5%B9%BC%E5%84%BF%E8%8B%B1%E8%AF%AD%E5%90%AF%E8%92%99%E5%8A%A8%E7%94%BB%E5%85%A830%E9%9B%86">Didi's Day</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="topic">
            <template #title>论坛</template>
            <el-menu-item index="/topics/Mandarin">华语论坛</el-menu-item>
            <el-menu-item index="/topics/JapaneseKorean">日韩论坛</el-menu-item>
            <el-menu-item index="/topics/Western">欧美论坛</el-menu-item>
            <el-menu-item index="/topics/Remix">Remix</el-menu-item>
            <el-menu-item index="/topics/Instrumental">纯音乐论坛</el-menu-item>
            <el-menu-item index="/topics/AlternateDimension">异次元论坛</el-menu-item>
            <!-- <el-menu-item index="/topics/Exclusive">特供</el-menu-item>
            <el-menu-item index="/topics/Encyclopedia">百科</el-menu-item> -->
            <el-menu-item index="/topics/StationManagement">站务</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="living">
            <template #title>直播</template>
            <el-menu-item index="/livinglanding">直播学习中心</el-menu-item>
            <el-menu-item index="/rtc/about_video.html" target="_blank">关于直播与录播</el-menu-item>
            <el-menu-item index="/rtc/5-2_音视频编码格式简介.html" target="_blank">音视频编码格式简介</el-menu-item>
            <el-menu-item index="/rtc/5-3_音视频封装格式.html">音视频封装格式</el-menu-item>
            <el-menu-item index="/rtc/5-4_流媒体协议.html">流媒体协议</el-menu-item>
            <el-menu-item index="/rtc/5-5_直播业务介绍.html">直播业务介绍</el-menu-item>
            <el-menu-item index="/rtc/5-6_一个直播的整个流程及背后的故事.html">一个直播的整个流程及背后的故事</el-menu-item>
            <el-menu-item index="/rtc/5-7_本章知识点总结.html">本章知识点总结</el-menu-item>
            <el-menu-item index="/online/living">直播与录播（需要后端发起）</el-menu-item>
            <el-menu-item index="/online/meeting">多人会议</el-menu-item>
          </el-sub-menu>
          
          <el-menu-item index="/geo">浙江旅游</el-menu-item>
          
          <el-menu-item index="/topic/create">请求帮助</el-menu-item>
        </el-menu>
      </div>

      <div class="user-section">
        <UserInfo />
      </div>
    </div>
  </el-header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import UserInfo from './UserInfo.vue'

const router = useRouter()

const handleSelect = (index: string, indexPath: string[], item: any) => {
  // 检查是否是静态HTML文件
  if (index.endsWith('.html')) {
    // 直接在新窗口打开，不经过Vue Router
    window.open(index, '_blank')
  } else {
    // 使用Vue Router进行正常导航
    router.push(index)
  }
}
</script>

<style scoped>
.navbar {
  border-bottom: 1px solid #eee;
  background-color: #fff;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-section {
  display: flex;
  align-items: center;
}

.logo {
  height: 40px;
  margin-right: 20px;
}

.nav-menu {
  flex-grow: 1;
}

.nav-menu-items {
  border-bottom: none;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
</style>