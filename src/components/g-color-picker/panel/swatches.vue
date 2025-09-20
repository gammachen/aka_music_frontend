<template>
    <div :class="swatchesClass">
        <h3 :class="[`${swatchesClass}--title`]">
            <span>{{ title }}</span>
            <template v-if="editable">
                <a-space>
                    <span role="button" :class="`${baseClassName}__icon`" @click="handleAddColor">
                        <icon-plus/>
                    </span>
                            <span v-if="colors.length > 0" role="button" :class="`${baseClassName}__icon`"
                                  @click="handleRemoveColor">
                      <icon-delete/>
                    </span>
                </a-space>
            </template>
        </h3>
        <ul :class="[`${swatchesClass}--items`, 'narrow-scrollbar']">
            <li v-for="color in colors" :key="color"
                :class="[`${swatchesClass}--item`, isEqualCurrentColor(color) && editable ? statusClassNames.active : '']"
                :title="color"
                @click="handleClick(color)">
                <div :class="[`${swatchesClass}--color`, `${baseClassName}--bg-alpha`]">
                    <span :class="[`${swatchesClass}--inner`]" :style="{ background: color }"></span>
                </div>
            </li>
        </ul>
    </div>
</template>
<script lang="ts">
import {computed, defineComponent, PropType, ref} from 'vue';

import {GColor} from '../utils';
import {useBaseClassName} from '../hooks';
import {useCommonClassName} from '../hooks/useConfig';
import baseProps from './base-props';

export default defineComponent({
    name: 'SwatchesPanel',
    props: {
        ...baseProps,
        colors: {
            type: Array as PropType<string[]>,
            default: () => [] as PropType<string[]>,
        },
        title: {
            type: String,
            default: '系统色彩',
        },
        editable: {
            type: Boolean,
            default: false,
        },
        onSetColor: {
            type: Function,
            default: () => {
                return () => {
                };
            },
        },
        handleAddColor: {
            type: Function,
            default: () => {
                return () => {
                };
            },
        },
    },
    setup(props) {
        const baseClassName = useBaseClassName();
        const swatchesClass = `${baseClassName}__swatches`;
        const {STATUS} = useCommonClassName();
        const statusClassNames = STATUS.value;
        const visiblePopConfirm = ref<boolean>(false);
        const setVisiblePopConfirm = (visible: boolean) => {
            visiblePopConfirm.value = visible;
        };

        const handleClick = (color: string) => props.onSetColor(color);

        const isEqualCurrentColor = (color: string) => {
            return GColor.compare(color, props.color.css);
        };

        const selectedColorIndex = computed(() => {
            return props.colors.findIndex((color) => isEqualCurrentColor(color));
        });

        /**
         * 移除颜色
         */
        const handleRemoveColor = () => {
            const colors = [...props.colors];
            const selectedIndex = selectedColorIndex.value;
            if (selectedIndex > -1) {
                colors.splice(selectedIndex, 1);
            } else {
                colors.length = 0;
            }
            props.onChange(colors);
            setVisiblePopConfirm(false);
        };

        return {
            baseClassName,
            swatchesClass,
            statusClassNames,
            selectedColorIndex,
            visiblePopConfirm,
            setVisiblePopConfirm,
            handleClick,
            isEqualCurrentColor,
            handleRemoveColor,
        };
    },
})
</script>
<style scoped>

</style>
