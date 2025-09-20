import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import {resolve } from 'path';
import fs from 'fs';

import UnoCSS from 'unocss/vite'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ArcoResolver, AntDesignVueResolver } from 'unplugin-vue-components/resolvers'
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'

// 自定义Arco组件解析器，处理组件名称映射问题
function CustomArcoResolver() {
  return {
    type: 'component' as const,
    resolve: (name: string) => {
      if (name.startsWith('A')) {
        const componentName = name.slice(1)
        
        // 处理特殊组件名称映射
        const componentMap: Record<string, string> = {
          'RadioButton': 'radio',
          'UploadDragger': 'upload',
          'SelectOption': 'select',
          'Option': 'select',
          'UploadButton': 'upload',
          'UploadList': 'upload',
          'UploadListItem': 'upload',
          'UploadPictureItem': 'upload',
          'UploadProgress': 'upload',
          'InputPassword': 'input',
          'InputSearch': 'input',
          'InputTextarea': 'input',
          'InputNumber': 'input-number',
          'FormItem': 'form',
          'TableColumn': 'table',
          'MenuItem': 'menu',
          'MenuSubMenu': 'menu',
          'DropdownButton': 'dropdown',
          'ModalContent': 'modal',
          'DrawerContent': 'drawer',
          'TabPane': 'tabs',
          'CollapseItem': 'collapse',
          'ListItem': 'list',
          'ListItemMeta': 'list',
          'BreadcrumbItem': 'breadcrumb',
          'StepsStep': 'steps',
          'TimelineItem': 'timeline',
          'CardMeta': 'card',
          'GridItem': 'grid',
          'Row': 'grid',
          'Col': 'grid',
          'LayoutHeader': 'layout',
          'LayoutContent': 'layout',
          'LayoutFooter': 'layout',
          'LayoutSider': 'layout',
          'DescriptionsItem': 'descriptions',
          'RadioGroup': 'radio'
        }
        
        // 处理Content相关组件的映射
        if (componentName.toLowerCase().includes('content') && componentName !== 'LayoutContent') {
          // 避免尝试导入不存在的@arco-design/web-vue/es/content路径
          return null;
        }
        
        // 处理Header相关组件的映射
        if (componentName.toLowerCase().includes('header') && componentName !== 'LayoutHeader') {
          // 避免尝试导入不存在的@arco-design/web-vue/es/header路径
          return null;
        }
        
        // 处理拼写错误的组件名，如lphaslider
        if (componentName.toLowerCase().includes('lphaslider')) {
          // 这应该是slider组件
          return {
            name: componentName,
            from: `@arco-design/web-vue/es/slider`,
            sideEffects: `@arco-design/web-vue/es/slider/style/css.js`
          };
        }
        
        // 处理拼写错误的组件名，如doption
        if (componentName.toLowerCase().includes('doption')) {
          // 这应该是dropdown组件的子组件
          return {
            name: componentName,
            from: `@arco-design/web-vue/es/dropdown`,
            sideEffects: `@arco-design/web-vue/es/dropdown/style/css.js`
          };
        }
        
        // 处理DescriptionsItem组件
        if (componentName.toLowerCase() === 'descriptionsitem') {
          return {
            name: componentName,
            from: `@arco-design/web-vue/es/descriptions`,
            sideEffects: `@arco-design/web-vue/es/descriptions/style/css.js`
          };
        }
        
        const actualComponent = componentMap[componentName] || componentName.toLowerCase()
        
        // 确保不会尝试导入不存在的模块
        try {
          // 某些特殊组件路径需要额外处理
          if (actualComponent === 'content' || actualComponent === 'header') {
            // 这些应该是 layout 的子组件
            return {
              name: componentName,
              from: `@arco-design/web-vue/es/layout`,
              sideEffects: `@arco-design/web-vue/es/layout/style/css.js`
            };
          }
          
          return {
            name: componentName,
            from: `@arco-design/web-vue/es/${actualComponent}`,
            sideEffects: `@arco-design/web-vue/es/${actualComponent}/style/css.js`
          }
        } catch (e) {
          return null;
        }
      }
      return null;
    }
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    // 自动按需引入组件
    AutoImport({
      resolvers: [
          ArcoResolver({
              importStyle: 'css',
          }),
      ],
      imports: ['vue', 'vue-router', 'pinia', '@vueuse/core'],
      eslintrc: {
          enabled: true,
      },
    }),
    Components({
        directoryAsNamespace: true,
        resolvers: [
            // 优先使用Ant Design Vue解析器
            AntDesignVueResolver({
              resolveIcons: true,
              importStyle: false, // 禁用自动样式导入，使用手动导入
            }),
            // 使用自定义Arco解析器
            CustomArcoResolver(),
            ArcoResolver({
                importStyle: 'css',
                resolveIcons: true,
            }),
        ],
    }),
    UnoCSS(),
    createSvgIconsPlugin({
        // 指定需要缓存的图标文件夹
        iconDirs: [resolve(process.cwd(), 'src/assets/icons')],
        // 指定symbolId格式
        symbolId: 'icon-[dir]-[name]',
    }),
  ],
  build: {
    rollupOptions: {
      external: [
        /^\/static\/.*/, // 使用正则表达式忽略所有以 /static/ 开头的路径
      ],
    },
  },
  resolve: {
    alias: {
      '/@static': '/static', // 假设你的静态资源在 ../other_project/static 目录下
      '@': resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    https: {
      key: fs.readFileSync('certs/key.pem'),
      cert: fs.readFileSync('certs/cert.pem'),
    },
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'https://127.0.0.1:5000',
        changeOrigin: true,
        secure: false
      },
      // 静态资源代理，特别是静态图片，因为上传图片等是在服务端保存的，没有使用到oss等内容，所以要请求到后端，将来使用到oss也是同样的情况的，也是要请求到
      // 其他服务器的（暂时不包括js、css，对于js、css的请求，放置在assets目录下，作为资源来处理）
      '/static': {
        target: process.env.VITE_API_URL || 'https://127.0.0.1:5000',
        changeOrigin: true,
        secure: false
      },
      '/graphql': {
        target: process.env.GRAPHQL_API_URL || 'https://localhost:11800',
        changeOrigin: true,
        secure: false
      },
      '/api/meeting/socket.io': {
        target: process.env.VITE_API_URL || 'https://127.0.0.1:5000',
        changeOrigin: true,
        ws: true,
        secure: false,
        headers: {
          Connection: 'upgrade'
        },
        configure: (proxy, options) => {
          // 确保正确处理WebSocket连接
          options.ws = true;
        }
      },
    },
  },
  preview: {
    host: '0.0.0.0',
    port: 5173,
    cors: true,
    https: {
      key: fs.readFileSync('certs/key.pem'),
      cert: fs.readFileSync('certs/cert.pem'),
    },
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'https://127.0.0.1:5000',
        changeOrigin: true,
        secure: false
      },
      // 静态资源代理，特别是静态图片，因为上传图片等是在服务端保存的，没有使用到oss等内容，所以要请求到后端，将来使用到oss也是同样的情况的，也是要请求到
      // 其他服务器的（暂时不包括js、css，对于js、css的请求，放置在assets目录下，作为资源来处理）
      '/static': {
        target: process.env.VITE_API_URL || 'https://127.0.0.1:5000',
        changeOrigin: true,
        secure: false
      },
      '/graphql': {
        target: process.env.GRAPHQL_API_URL || 'https://localhost:11800',
        changeOrigin: true,
        secure: false
      },
      '/api/meeting/socket.io': {
        target: process.env.VITE_API_URL || 'https://127.0.0.1:5000',
        changeOrigin: true,
        ws: true,
        secure: false,
        headers: {
          Connection: 'upgrade'
        },
        configure: (proxy, options) => {
          // 确保正确处理WebSocket连接
          options.ws = true;
        }
      },
    },
    allowedHosts: ['127.0.0.1', 'localhost','alphago.ltd','25b74c26147d.ngrok-free.app','47.98.62.98', '0.0.0.0']
  }
})