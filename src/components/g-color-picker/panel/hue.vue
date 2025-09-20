<template>
    <ColorSlider
            :class="`${baseClassName}__hue`"
            :color="color"
            :value="color.hue"
            :onChange="onChange"
            :disabled="disabled"
            type="hue"
    />
</template>
<script lang="ts">
import { defineComponent } from 'vue';
import ColorSlider from './slider.vue';
import { useBaseClassName } from '../hooks';
import baseProps from './base-props';

export default defineComponent({
    name: 'HueSlider',

    inheritAttrs: false,
    props: {
        ...baseProps,
    },
    setup() {
        const baseClassName = useBaseClassName();
        return {
            baseClassName,
        };
    },
    components: {
        ColorSlider
    }
})
</script>
<style scoped>

</style>
