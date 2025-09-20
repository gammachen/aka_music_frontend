<template>
    <a-input
            :clearable="clearable"
            :size="size"
            :disabled="disabled"
            v-model="value"
            style="width: max-content"
            @change="handleChange"
            v-bind="inputProps">
        <template #prefix>
            <div :class="[`${baseClassName}__trigger--default__color`, `${baseClassName}--bg-alpha`]">
            <span
                    v-if="colorModes.includes(mode)"
                    :class="[
                'color-inner',
                {
                  [sizeClassNames[size]]: size !== 'medium',
                },
              ]"
                    :style="{ background: value }"
            ></span>
                <span v-else>
                    <template v-for="(value, key) in $slots" :key="key">
                    <div v-if="(mode+'-view') == key">
                        <slot :name="key"></slot>
                    </div>
                </template>
                </span>
            </div>
        </template>
    </a-input>
</template>
<script lang="ts">
import { defineComponent, PropType, ref, watch } from 'vue';
import { GColor } from './utils';
import { TdColorPickerProps } from './type';
import { useBaseClassName } from './hooks';
import { useCommonClassName } from './hooks/useConfig';

export default defineComponent({
    name: 'DefaultTrigger',
    inheritAttrs: false,
    props: {
        color: {
            type: String,
            default: '',
        },
        disabled: {
            type: Boolean,
            default: false,
        },
        clearable: {
            type: Boolean,
            default: false,
        },
        inputProps: {
            type: Object as PropType<TdColorPickerProps['inputProps']>,
            default: () => {
                return {
                    autoWidth: true,
                };
            },
        },
        onTriggerChange: {
            type: Function,
            default: () => {
                return () => {
                };
            },
        },
        size: {
            type: String as PropType<TdColorPickerProps['size']>,
            default: 'mini',
        },
        mode: {
            type: String,
            default: '',
        },
        colorModes: {
            type: Array,
            default: () => ['monochrome', 'linear-gradient','radial-gradient'],
        },
    },
    setup(props) {
        const baseClassName = useBaseClassName();
        const value = ref(props.color);
        const modeV = ref(props.mode);
        const {SIZE: sizeClassNames} = useCommonClassName();
        watch(
            () => [props.color],
            () => (value.value = props.color),
        );
        watch(
            () => [props.mode],
            () => (modeV.value = props.mode),
        );

        const handleChange = (input: string) => {
            if (input === props.color) {
                return;
            }
            if (input && !GColor.isValid(input)) {
                value.value = props.color;
            } else {
                value.value = input;
            }
            console.log('value.value=',value.value)
            props.onTriggerChange(value.value);
        };

        return {
            baseClassName,
            value,
            modeV,
            handleChange,
            sizeClassNames,
        };
    },
})
</script>
<style scoped>

</style>
