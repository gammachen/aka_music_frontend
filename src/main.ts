import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import ElementPlus from 'element-plus'
import App from './App.vue'
import router from './router'
import 'ant-design-vue/dist/reset.css'
import 'element-plus/dist/index.css'
import { createPersistedState } from 'pinia-plugin-persistedstate'

import ArcoVue from '@arco-design/web-vue';

// CSS
import '@unocss/reset/tailwind-compat.css'
import 'virtual:uno.css'
import 'virtual:svg-icons-register'
import './style.less'
// import './mock'; // 禁用MockJS
import './utils/request';

// 额外引入图标库
import ArcoVueIcon from '@arco-design/web-vue/es/icon';
import IconFontPlugin from './plugins/iconFontPlugin';

// import {createCore} from './views/Editor/core'

// const core = createCore()
// import { myPlugin } from './views/testPlugin'
// core.use(myPlugin)

const app = createApp(App)
const pinia = createPinia()
pinia.use(createPersistedState)

app.use(pinia)
app.use(router)
app.use(Antd)
app.use(ElementPlus)

app.use(ArcoVue);
// app.use(core)
app.use(ArcoVueIcon);
app.use(IconFontPlugin);

app.mount('#app')


