<template>
    <div :class="[`${baseClassName}__gradient`]">
        <div :class="[`${baseClassName}__gradient-slider`]">
            <div :class="[`${baseClassName}__slider`, `${baseClassName}--bg-alpha`]"
                 tabindex="0"
                 ref="refSlider"
                 @keyup="handleKeyup">
                <ul class="gradient-thumbs"
                    @click="handleThumbBarClick"
                    :style="{ background: thumbBackground }">
                    <li v-for="t in colors"
                        :key="t.id"
                        :title="`${t.color} ${t.left}%`"
                        :style="{ color: t.color, left: `${Math.round(t.left * 100) / 100}%` }"
                        :class="[`${baseClassName}__thumb`, 'gradient-thumbs__item', selectedId === t.id ? statusClassNames.active : '']"
                        @mousedown.stop="handleStart(t.id)">
            <span class="gradient-thumbs__item-inner"
                  :class="[`${baseClassName}--bg-alpha`]"></span>
                    </li>
                </ul>
            </div>
        </div>
        <div :class="[`${baseClassName}__gradient-degree`]">

            <SwipeNumber size="small"
                         :min="0"
                         label="角度"
                         label-width="23px"
                         :max="360"
                         :step="1"
                         hide-button
                         v-model="degree"
                         @change="handleDegreeChange"
                         @swipe="handleDegreeChange"
                         :disabled="disabled">
                <template #label>
                    <SvgIcon name="bx-revision" />
                </template>
                <template #suffix>
                    <div class="absolute top-1 right-1">°</div>
                </template>
            </SwipeNumber>
<!--            <a-input-number-->
<!--                    size="small"-->
<!--                    :min="0"-->
<!--                    :max="360"-->
<!--                    :step="1"-->
<!--                    hide-button-->
<!--                    :formatter="(value) => `${value}°`"-->
<!--                    :parser="(value) => parseInt(value.replace(/°/g, ''))"-->
<!--                    v-model="degree"-->
<!--                    @change="handleDegreeChange"-->
<!--                    :disabled="disabled"-->
<!--            >-->

<!--            </a-input-number>-->
        </div>
        <div :class="[`${baseClassName}__gradient-preview`, `${baseClassName}--bg-alpha`]">
            <span class="preview-inner" :style="{ background: color.linearGradient }"></span>
        </div>
    </div>
</template>
<script lang="ts">
import { defineComponent, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue';
import cloneDeep from 'lodash/cloneDeep';
import { GRADIENT_SLIDER_DEFAULT_WIDTH } from '../const';
import { genGradientPoint, gradientColors2string, GradientColorPoint } from '../utils';
import { useBaseClassName } from '../hooks';
import { useCommonClassName } from '../hooks/useConfig';
import baseProps from './base-props';
import SwipeNumber from "@/components/swipeNumber/swipeNumber.vue";
import SvgIcon from "@/components/svgIcon/svgIcon.vue";

const DELETE_KEYS: string[] = ['delete', 'backspace'];

export default defineComponent({
    name: 'LinearGradient',
    components: {SvgIcon, SwipeNumber},

    inheritAttrs: false,
    props: {
        ...baseProps,
        enableMultipleGradient: {
            type: Boolean,
            default: true,
        },
    },
    setup(props) {
        const baseClassName = useBaseClassName();
        const {STATUS} = useCommonClassName();
        const statusClassNames = STATUS.value;
        const refSlider = ref<HTMLElement>(null);
        const sliderRect = reactive({
            left: 0,
            width: GRADIENT_SLIDER_DEFAULT_WIDTH,
        });
        const isDragging = ref<Boolean>(false);
        const isMoved = ref<Boolean>(false);
        const degree = ref(props.color.gradientDegree);
        const selectedId = ref(props.color.gradientSelectedId);
        const colors = ref<GradientColorPoint[]>(cloneDeep(props.color.gradientColors));

        watch(
            () => props.color.gradientDegree,
            (value) => (degree.value = value),
        );
        watch(
            () => props.color.gradientSelectedId,
            (value) => (selectedId.value = value),
        );
        watch(
            () => props.color.gradientColors,
            (value) => {
                colors.value = cloneDeep(value);
            },
            {
                deep: true,
            },
        );

        const handleChange = (key: 'degree' | 'selectedId' | 'colors', payload: any, addUsedColor?: boolean) => {
            if (props.disabled) {
                return;
            }
            props.onChange({
                key,
                payload,
                addUsedColor,
            });
        };

        const handleDegreeChange = (value: number) => {
            if (props.disabled || value === props.color.gradientDegree) {
                return;
            }
            degree.value = value;
            handleChange('degree', value, true);
        };

        const handleSelectedIdChange = (value: string) => {
            if (props.disabled) {
                return;
            }
            selectedId.value = value;
            handleChange('selectedId', value);
        };

        const handleColorsChange = (value: GradientColorPoint[], isEnded?: boolean) => {
            if (props.disabled) {
                return;
            }
            colors.value = value;
            handleChange('colors', value, isEnded);
        };

        /**
         * 设置bar的位置
         * @param left
         * @returns
         */
        const updateActiveThumbLeft = (left: number) => {
            const index = colors.value.findIndex((c) => c.id === selectedId.value);
            if (index === -1) {
                return;
            }
            const point = colors.value[index];
            left = Math.max(0, Math.min(sliderRect.width, left));
            const percentLeft = (left / sliderRect.width) * 100;
            colors.value.splice(index, 1, {
                color: point.color,
                left: percentLeft,
                id: point.id,
            });
            handleColorsChange(colors.value);
        };

        // 移动开始
        const handleStart = (id: string) => {
            const rect = refSlider.value.getBoundingClientRect();
            sliderRect.left = rect.left;
            sliderRect.width = rect.width || GRADIENT_SLIDER_DEFAULT_WIDTH;
            if (isDragging.value || props.disabled) {
                return;
            }
            isMoved.value = false;
            isDragging.value = true;
            handleSelectedIdChange(id);
            // 让slider获取焦点，以便键盘事件生效。
            refSlider.value.focus();
            window.addEventListener('mousemove', handleMove, false);
            window.addEventListener('mouseup', handleEnd, false);
            window.addEventListener('contextmenu', handleEnd, false);
        };

        // 移动中
        const handleMove = (e: MouseEvent) => {
            if (!isDragging.value || props.disabled) {
                return;
            }
            const left = e.clientX - sliderRect.left;
            isMoved.value = true;
            updateActiveThumbLeft(left);
        };

        // 移动结束
        const handleEnd = () => {
            if (!isDragging.value) {
                return;
            }
            setTimeout(() => {
                isDragging.value = false;
            }, 0);
            if (isMoved.value) {
                handleColorsChange(colors.value, true);
                isMoved.value = false;
            }
            window.removeEventListener('mousemove', handleMove, false);
            window.removeEventListener('mouseup', handleEnd, false);
            window.removeEventListener('contextmenu', handleEnd, false);
        };

        const handleKeyup = (e: KeyboardEvent) => {
            if (props.disabled) {
                return;
            }
            const points = colors.value;
            let pos = points.findIndex((c) => c.id === selectedId.value);
            const {length} = points;
            // 必须保证有两个点
            if (DELETE_KEYS.includes(e.key.toLocaleLowerCase()) && length > 2 && pos >= 0 && pos <= length - 1) {
                points.splice(pos, 1);
                if (!points[pos]) {
                    // eslint-disable-next-line no-nested-ternary
                    pos = points[pos + 1] ? pos + 1 : points[pos - 1] ? pos - 1 : 0;
                }
                const current = points[pos];
                handleColorsChange(points, true);
                handleSelectedIdChange(current?.id);
            }
        };

        const handleThumbBarClick = (e: MouseEvent) => {
            if (props.disabled || !props.enableMultipleGradient) {
                return;
            }
            let left = e.clientX - sliderRect.left;
            left = Math.max(0, Math.min(sliderRect.width, left));
            const percentLeft = (left / sliderRect.width) * 100;
            const newPoint = genGradientPoint(percentLeft, props.color.rgba);
            colors.value.push(newPoint);
            handleColorsChange(colors.value, true);
            handleSelectedIdChange(newPoint.id);
        };
        const thumbBackground = computed(() => {
            return gradientColors2string({
                points: props.color.gradientColors,
                degree: 90,
            });
        })

        onMounted(() => {
            const rect = refSlider.value.getBoundingClientRect();
            sliderRect.left = rect.left;
            sliderRect.width = rect.width || GRADIENT_SLIDER_DEFAULT_WIDTH;
        });

        onBeforeUnmount(() => {
            window.removeEventListener('mousemove', handleMove, false);
            window.removeEventListener('mouseup', handleEnd, false);
            window.removeEventListener('contextmenu', handleEnd, false);
        });

        return {
            baseClassName,
            statusClassNames,
            refSlider,
            degree,
            selectedId,
            colors,
            handleDegreeChange,
            handleStart,
            handleMove,
            handleEnd,
            handleKeyup,
            handleThumbBarClick,
            thumbBackground,
        };
    },
})
</script>
<style scoped>

</style>
