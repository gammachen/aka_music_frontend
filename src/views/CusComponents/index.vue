<template>
    <a-card>
      <a-space align="baseline">
          <a-card title="基于arco的颜色选择器（后续可提供扩展插槽）">
              <a-space align="start">
                  <div>
                      <a-divider orientation="left">面板使用</a-divider>
                      <g-color-picker-panel v-model="color" :enable-alpha="true"></g-color-picker-panel>
                  </div>
                  <div>
                      <a-divider orientation="left">基础使用</a-divider>
                      <!--  recentColors 在非面板组件时暂时不可用 -->
                      <g-color-picker v-model="color" :enable-alpha="true" :recentColors="null"></g-color-picker>
                  </div>
                  <div>
                      <a-divider orientation="left">tab插槽</a-divider>
                      <!--  recentColors 在非面板组件时暂时不可用 -->
                      <g-color-picker v-model="color" :enable-alpha="true" :recentColors="null" :cus-color-modes="{'image':'图片填充','image2':'图片填充2'}" width="430px">
                          <template #image-view>
                              自定义预览
                          </template>
                          <template #image-panel>
                              <div class="pattern-box">
                                  <div class="upload-box">
                                      <m-a-upload
                                                  list-type="picture-card"
                                                  :limit="1"
                                                  imagePreview
                                                  accept=".png,.jpg,.jpeg"/>
                                  </div>
                                  <a-row>
                                      <a-col>
                                          <a-select v-model="fit" :options="fitOptions">
                                              <template #prefix>
                                                  填充模式
                                              </template>
                                          </a-select>
                                      </a-col>
                                  </a-row>
                                  <a-row>
                                      <a-col>
                                          <SwipeNumber size="small" v-model="newOpacity" :min="0" :max="100" :step="1" style="padding: 0 12px" label-width="68px">
                                              <template #label>
                                                  <div style="text-align: right;padding-right: 12px"><icon-mosaic style="margin-right: 2px"/>透明度</div>
                                              </template>
                                              <template #suffix>
                                                  <div>%</div>
                                              </template>
                                          </SwipeNumber>
                                      </a-col>
                                  </a-row>

                              </div>
                          </template>
                          <template #image2-panel>
                              自定义面板2
                          </template>
                      </g-color-picker>
                  </div>
              </a-space>
          </a-card>
      </a-space>
    </a-card>
</template>

<script setup lang="ts">
import MAUpload from "../../components/upload/m-a-upload.vue";

const color = ref('#0052d9');
const color2 = ref('#0052d9');
const recCols = ref(['red']);
const fitOptions = reactive([
    {value: 'cover', label: '覆盖'},
    {value: 'fit', label: '适应'},
    {value: 'strench', label: '拉伸'},
    {value: 'clip', label: '裁剪'},
    {value: 'repeat', label: '平铺'},
])
const fit = ref('cover');
const newOpacity = ref(100);

// import GColorPicker from '@/components/design-color-picker/g-color-picker.vue';
// import GColorPickerPanel from '@/components/design-color-picker/g-color-picker-panel.vue';
import {GColorPicker,GColorPickerPanel} from '@/components/g-color-picker';
import SwipeNumber from "@/components/swipeNumber/swipeNumber.vue";
import {reactive} from "vue";
</script>
<style lang="less">
@color-picker-panel-width:350px !important;
</style>
