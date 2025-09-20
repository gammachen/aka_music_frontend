<template>
    <ColorPanel v-bind="newProps" :popupProps="null" :close-btn="false" :class="`${prefix}-is-inline`" />
</template>

<script lang="ts">
import './style/index';
import { computed, defineComponent } from 'vue';
import props from './props';
import ColorPanel from './panel/index.vue';
import { usePrefixClass } from './hooks/useConfig';
import pickBy from 'lodash/pickBy';

export default defineComponent({
    name: 'GColorPickerPanel',
    inheritAttrs: false,
    props: {
        ...props,
    },
    setup(props, { attrs }) {
        const newProps = computed(() => pickBy({ ...props, ...attrs }, (v) => v !== undefined));
        const prefix = usePrefixClass();
        return {
            newProps,
            prefix
        };
    },
    components: {
        ColorPanel
    }
});
</script>

<style lang="less">
</style>
