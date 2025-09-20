import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router'
import { useUserStore } from '../store'

// import Editor from '@/views/Editor/editor.vue'
// import PsParser from '@/views/PsParser/index.vue'
// import CusComponents from '@/views/CusComponents/index.vue'
// import Home from '@/views/Home/home.vue'

// import Editor from '../views/Editor/editor.vue'
// import PsParser from '../views/PsParser/index.vue'
// import CusComponents from '../views/CusComponents/index.vue'
import Home from '../views/Home/home.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/topics/:cid?',
      name: 'topics',
      component: () => import('../views/Topics.vue'),
      props: true
    },
    {
      path: '/',
      name: 'landing',
      component: () => import('../views/Landing.vue')
    },
    {
      path: '/list',
      name: 'list',
      component: () => import('../views/Home.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/Register.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/Login.vue')
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/Profile.vue')
    },
    {
      path: '/topic/:id',
      name: 'topic-detail',
      component: () => import('../views/TopicDetail.vue')
    },
    {
      path: '/topic/create',
      name: 'create-topic',
      component: () => import('../views/topic/CreateTopic.vue')
    },
    {
      path: '/payment',
      name: 'payment',
      component: () => import('../views/profile/Recharge.vue')
    },
    {
      path: '/payment/result',
      name: 'payment-result',
      component: () => import('../views/PaymentSuccess.vue')
    },
    {
      path: '/genre',
      name: 'genre',
      component: () => import('../views/Genre.vue')
    },
    {
      path: '/mugrid/:category_id?',
      name: 'music-grid',
      component: () => import('../views/music/Mugrid.vue')
    },
    {
      path: '/mulist/:category_id?',
      name: 'music-list',
      component: () => import('../views/music/Mulist.vue')
    },
    {
      path: '/beaulanding',
      name: 'beauty-landing',
      component: () => import('../views/beauty/BeautyLanding.vue')
    },
    {
      path: '/beaulist/:refer_id?',
      name: 'beauty-detail',
      component: () => import('../views/beauty/AlbumDetail.vue')
    },
    {
      path: '/comiclanding',
      name: 'comic-home',
      component: () => import('../views/comic/ComicLanding.vue')
    },
    {
      path: '/comic/:id',
      name: 'comic-detail',
      component: () => import('../views/comic/ComicDetail.vue')
    },
    {
      path: '/comic/genre',
      name: 'comic-genre',
      component: () => import('../views/comic/ComicGenre.vue')
    },
    {
      path: '/backend/content/adm',
      name: 'content-adm',
      component: () => import('../views/backend/content/index.vue')
    },
    {
      path: '/backend/rtmp/adm',
      name: 'rtmp-adm',
      component: () => import('../views/backend/rtmp/Advideo.vue')
    },
    {
      path: '/educationlanding',
      name: 'education-home',
      component: () => import('../views/education/EducationLanding.vue')
    },
    {
      path: '/education/:id',
      name: 'education-detail',
      component: () => import('../views/education/EducationDetail.vue')
    },
    {
      path: '/education/genre',
      name: 'education-genre',
      component: () => import('../views/education/EducationGenre.vue')
    },
    {
      path: '/livinglanding',
      name: 'living-landing',
      component: () => import('../views/online/LivingLanding.vue')
    },
    {
      path: '/online/living',
      name: 'online-living',
      component: () => import('../views/online/Living.vue')
    },
    {
      path: '/online/meeting',
      name: 'online-meeting',
      component: () => import('../views/online/Meeting.vue')
    },
    {
      path: '/geo',
      name: 'geo-travel',
      component: () => import('../views/geo/index.vue')
    },
    {
      path: '/photo/exif',
      name: 'photo-exif',
      component: () => import('../views/photo/PhotoExif.vue')
    },
    {
      path: '/poster/landing',
      name: 'poster-landing',
      component: () => import('../views/poster/PosterLanding.vue')
    },
    {
      path: '/editorhome',
      name: 'Home',
      component: Home,
      // component: Editor,
    },
    // {
    //   path: '/editor',
    //   name: 'Editor',
    //   component: Editor,
    // },
    // {
    //   path: '/psParser',
    //   name: 'PsParser',
    //   component: PsParser,
    // },
    // {
    //   path: '/components',
    //   name: 'CusComponents',
    //   component: CusComponents,
    // },
    {
      path: '/promptguide',
      name: 'Promptguide',
      component: () => import('../components/PromptGuide.vue'),
    },
  ]
})

// 需要登录才能访问的路由
const authRoutes = ['create-topic', 'profile', 'payment', 'payment-result', 'content-adm', 'rtmp-adm']

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (authRoutes.includes(to.name as string) && !userStore.token) {
    // 如果访问需要登录的页面且未登录，重定向到登录页
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router