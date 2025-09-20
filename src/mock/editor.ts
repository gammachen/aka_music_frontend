import Mock from 'mockjs';
import setupMock, { successResponseWrap } from '@/utils/setup-mock';
import templateData from '@/assets/data/templateData.json'
import graphData from '@/assets/data/graphData.json'
import imageData from '@/assets/data/imageData.json'
import textData from '@/assets/data/textData.json'
import bgImgData from '@/assets/data/bgImgData.json'
import elementData from '@/assets/data/elementData.json'
import {MockParams} from "@/types/mock";

/**
 * TODO 优化图库，抓取unsplash图片
 */
setupMock({
    setup() {

        Mock.mock(new RegExp('/mockapi/template/templateList'), (params:MockParams) => {
            const { pageNum, pageSize } = JSON.parse(params.body);
            console.log('Mock Request URL:', params.url);
            console.log('Mock Request Params:', { pageNum, pageSize });
            var newDataList = templateData.list.slice((pageNum - 1) * pageSize, pageNum * pageSize)
            const response = successResponseWrap({records:newDataList,total:templateData.list.length});
            console.log('Mock Response Data:', response);
            return response;
        });

        Mock.mock(new RegExp('/mockapi/text/materialList'), (params:MockParams) => {
            const { pageNum, pageSize } = JSON.parse(params.body);
            console.log('Request URL:', params.url);
            console.log('Request Params:', { pageNum, pageSize });
            var newDataList = textData.list.slice((pageNum - 1) * pageSize, pageNum * pageSize)
            const response = successResponseWrap({records:newDataList,total:textData.list.length});
            console.log('Response Data:', response);
            return response;
        });

        Mock.mock(new RegExp('/mockapi/image/materialList'), (params:MockParams) => {
            const { pageNum, pageSize } = JSON.parse(params.body);
            console.log('Request URL:', params.url);
            console.log('Request Params:', { pageNum, pageSize });
            var newDataList = imageData.list.slice((pageNum - 1) * pageSize, pageNum * pageSize)
            const response = successResponseWrap({records:newDataList,total:imageData.list.length});
            console.log('Response Data:', response);
            return response;
        });

        Mock.mock(new RegExp('/mockapi/graph/category'), (params:MockParams) => {
            console.log('Request URL:', params.url);
            const response = successResponseWrap({records:graphData.cate,total:graphData.cate.length});
            console.log('Response Data:', response);
            return response;
        });

        Mock.mock(new RegExp('/mockapi/graph/list'), (params:MockParams) => {
            const { pageNum, pageSize, query } = JSON.parse(params.body);
            console.log('Request URL:', params.url);
            console.log('Request Params:', { pageNum, pageSize, query });
            const list = graphData.list.filter(v=>{
                return v.category == query.categoryId
            })
            var newDataList = list.slice((pageNum - 1) * pageSize, pageNum * pageSize)
            const response = successResponseWrap({records:newDataList,total:list.length});
            console.log('Response Data:', response);
            return response;
        });

        Mock.mock(new RegExp('/mockapi/background/imageList'), (params:MockParams) => {
            const { pageNum, pageSize } = JSON.parse(params.body);
            console.log('Request URL:', params.url);
            console.log('Request Params:', { pageNum, pageSize });
            var newDataList = bgImgData.list.slice((pageNum - 1) * pageSize, pageNum * pageSize)
            const response = successResponseWrap({records:newDataList,total:bgImgData.list.length});
            console.log('Response Data:', response);
            return response;
        });

        Mock.mock(new RegExp('/mockapi/element/category'), (params:MockParams) => {
            console.log('Request URL:', params.url);
            const response = successResponseWrap({records:elementData.cate,total:elementData.cate.length});
            console.log('Response Data:', response);
            return response;
        });

        Mock.mock(new RegExp('/mockapi/element/list'), (params:MockParams) => {
            const { pageNum, pageSize, query } = JSON.parse(params.body);
            console.log('Request URL:', params.url);
            console.log('Request Params:', { pageNum, pageSize, query });
            const list = elementData.list.filter(v=>{
                return v.category == query.categoryId
            })
            var newDataList = list.slice((pageNum - 1) * pageSize, pageNum * pageSize)
            const response = successResponseWrap({records:newDataList,total:list.length});
            console.log('Response Data:', response);
            return response;
        });
    },
});