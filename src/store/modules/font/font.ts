import {getFonts} from "@/api/editor/font";
import FontFaceObserver from 'fontfaceobserver'

const defaultFonts = [
    {
        code: 'arial',
        name: 'Arial',
    },
    {
        code: 'Times New Roman',
        name: 'Times New Roman',
    },
    {
        code: 'Microsoft Yahei',
        name: '微软雅黑',
    },
]
export const useFontStore = defineStore('font', () => {
    const fontList = ref<any>([])

    // 跳过加载的字体
    const skipLoadFonts = ref<any>(defaultFonts.map(value => value.name))


    /**
     * 初始化部分字体
     */
    async function initFonts() {
        let list = []
    
        // 改进版本控制逻辑
        const currentVersion = '1'
        if (localStorage.getItem('FONTS_VERSION') !== currentVersion) {
            localStorage.removeItem('FONTS')
            localStorage.setItem('FONTS_VERSION', currentVersion)
        }

        // 安全获取本地字体数据
        const localFonts = (() => {
            try {
                const stored = localStorage.getItem('FONTS')
                return stored ? JSON.parse(stored) : []
            } catch (e) {
                console.error('字体数据解析失败，重置存储', e)
                localStorage.removeItem('FONTS')
                return []
            }
        })()

        // 合并数据逻辑
        if (localFonts?.length > 0) {
            list.push(...localFonts)
        } else {
            // API请求增加错误处理
            try {
                const res = await getFonts({pageNum: 1, pageSize: 1000})
                if (res.data?.records) {
                    list = res.data.records
                    localStorage.setItem('FONTS', JSON.stringify(list))
                }
            } catch (error) {
                console.error('字体接口请求失败', error)
            }
        }

        fontList.value = defaultFonts.concat(list)
        return list
    }

    return {
        fontList,
        skipLoadFonts,
        initFonts,
    }
})
