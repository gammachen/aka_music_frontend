<template>
    <ColorSlider
            :class="[`${baseClassName}__alpha`, `${baseClassName}--bg-alpha`]"
            :color="color"
            :value="color.alpha * 100"
            @change="handleChange"
            :rail-style="railStyle"
            :max-value="100"
            :disabled="disabled"
            type="alpha"
    />
</template>
<script lang="ts">
import { computed, defineComponent, PropType } from 'vue';
import ColorSlider from './slider.vue';
import { GColor } from '../utils';
import { useBaseClassName } from '../hooks';

export default defineComponent({
    name: 'AlphaSlider',
    inheritAttrs: false,
    props: {
        color: {
            type: Object as PropType<GColor>,
        },
        disabled: {
            type: Boolean,
            default: false,
        },
        onChange: {
            type: Function,
            default: () => {
                return () => {
                };
            },
        },
    },
    setup(props) {
        const baseClassName = useBaseClassName();
        const handleChange = (v: number, isDragEnd?: boolean) => {
            props.onChange(v / 100, isDragEnd);
        };
        const railStyle = computed(() => {
            return {
                background: `linear-gradient(to right, rgba(0, 0, 0, 0), ${props.color.rgb})`,
            };
        });
        return {
            baseClassName,
            railStyle,
            handleChange,
        };
    },
    components: {
        ColorSlider
    }
})
</script>
<style scoped>

</style>
