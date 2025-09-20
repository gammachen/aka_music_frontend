<script setup lang="ts">
const json = {
    "tag": "Frame",
    "fill": [
        {
            "type": "solid",
            "color": "#FFFFFF"
        }
    ],
    "id": "6acf7492-8ff8-4216-a05e-2442eb3466d7",
    "name": "workspace",
    "width": 2362,
    "height": 3543,
    "children": [
        {
            "tag": "Image2",
            "name": "背景",
            "blendMode": "normal",
            "opacity": 1,
            "visible": true,
            "zIndex": 1,
            "x": 0,
            "y": 0,
            "width": 2362,
            "height": 3543,
            "draggable": true,
            "editable": true,
            "fill":"#fff"
        },
        {
            "tag": "Image2",
            "name": "图层 1",
            "blendMode": "normal",
            "opacity": 1,
            "visible": true,
            "zIndex": 2,
            "x": -93,
            "y": -34,
            "width": 2499,
            "height": 3809,
            "draggable": true,
            "editable": true,
            "fill": {
                "type":"image",
                "url":"https://ossc.guozimi.cn/gzm-design/lixia2/"
            }
        },
        {
            "tag": "Image2",
            "name": "图层 3",
            "blendMode": "normal",
            "opacity": 1,
            "visible": true,
            "zIndex": 3,
            "x": 1359,
            "y": 551,
            "width": 872,
            "height": 102,
            "draggable": true,
            "editable": true,
            "fill": [
                {
                    "type":"image",
                    "url":"https://ossc.guozimi.cn/gzm-design/lixia2/图层 3"
                }
            ]
        },
        {
            "tag": "Image2",
            "name": "矢量智能对象 副本 2",
            "blendMode": "normal",
            "opacity": 0.25098039215686274,
            "visible": true,
            "zIndex": 4,
            "x": -572,
            "y": -470,
            "width": 1632,
            "height": 1624,
            "draggable": true,
            "editable": true,
            "fill": {
                "type":"image",
                "url":"https://ossc.guozimi.cn/gzm-design/lixia2/矢量智能对象 副本 2.png"
            }
        },
        {
            "tag": "Image2",
            "name": "夏",
            "blendMode": "normal",
            "opacity": 1,
            "visible": true,
            "zIndex": 5,
            "x": 1907,
            "y": 747,
            "width": 323,
            "height": 725,
            "draggable": true,
            "editable": true,
            "fill": [
                {
                    "type":"image",
                    "url":"https://ossc.guozimi.cn/gzm-design/lixia2/夏.png"
                }
            ]
        },
        {
            "tag": "Image2",
            "name": "图层 4",
            "blendMode": "normal",
            "opacity": 1,
            "visible": true,
            "zIndex": 6,
            "x": -268,
            "y": 2578,
            "width": 2362,
            "height": 965,
            "draggable": true,
            "editable": true,
            "fill": {
                "type":"image",
                "url":"https://ossc.guozimi.cn/gzm-design/lixia2/图层 4.png"
            }
        },
        {
            "tag": "Image2",
            "name": "图层 5",
            "blendMode": "normal",
            "opacity": 1,
            "visible": true,
            "zIndex": 7,
            "x": 647,
            "y": 861,
            "width": 634,
            "height": 629,
            "draggable": true,
            "editable": true,
            "fill": {
                "type":"image",
                "url":"https://ossc.guozimi.cn/gzm-design/lixia2/图层 5.png"
            }
        },
        {
            "tag": "Image2",
            "name": "图层 6",
            "blendMode": "normal",
            "opacity": 1,
            "visible": true,
            "zIndex": 8,
            "x": -548,
            "y": 1333,
            "width": 2491,
            "height": 2323,
            "draggable": true,
            "editable": true,
            "fill": {
                "type":"image",
                "url":"https://ossc.guozimi.cn/gzm-design/lixia2/图层 6.png"
            }
        },
        {
            "tag": "Image2",
            "name": "图层 60 拷贝 2",
            "blendMode": "normal",
            "opacity": 1,
            "visible": true,
            "zIndex": 9,
            "x": 495,
            "y": 2495,
            "width": 864,
            "height": 343,
            "draggable": true,
            "editable": true,
            "fill": {
                "type":"image",
                "url":"https://ossc.guozimi.cn/gzm-design/lixia2/图层 60 拷贝 2.png"
            }
        },
        {
            "tag": "Image2",
            "name": "图层 60 拷贝 3",
            "blendMode": "normal",
            "opacity": 1,
            "visible": true,
            "zIndex": 10,
            "x": 890,
            "y": 1871,
            "width": 939,
            "height": 494,
            "draggable": true,
            "editable": true,
            "fill": {
                "type":"image",
                "url":"https://ossc.guozimi.cn/gzm-design/lixia2/图层 60 拷贝 3.png"
            }
        },
        {
            "tag": "Image2",
            "name": "图层 12",
            "blendMode": "normal",
            "opacity": 0.6392156862745098,
            "visible": true,
            "zIndex": 11,
            "x": -404,
            "y": 1508,
            "width": 899,
            "height": 987,
            "draggable": true,
            "editable": true,
            "fill": {
                "type":"image",
                "url":"https://ossc.guozimi.cn/gzm-design/lixia2/图层 12.png"
            }
        }
    ]
}
const test = () => {
    setChildUrl(json.children)
    console.log('json =',json)
}
const setChildUrl = (child) => {
    for (let i = 0; i < child.length; i++) {
        let item = child[i]
        if (item.tag==='Image'){
            item.url = 'https://ossc.guozimi.cn/gzm-design/lixia2/'  + item.name + '.png'
            item.fill.url = 'https://ossc.guozimi.cn/gzm-design/lixia/'  + item.name + '.png'
        }else{
            if (item.children && item.children.length>0){
                setChildUrl(item.children)
            }
        }
    }
}
</script>

<template>
    <div>
        <a-button @click="test">测试</a-button>
    </div>
</template>

<style scoped>

</style>
