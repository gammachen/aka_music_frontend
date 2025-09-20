<template>
    <div :class="[`${baseClassName}__format`]">
        <div :class="[`${baseClassName}__format--item`]">
<!--            <TSelect-->
<!--                    size="small"-->
<!--                    :class="[`${baseClassName}__format-mode-select`]"-->
<!--                    v-model="formatModel"-->
<!--                    @change="handleModeChange"-->
<!--                    :popupProps="{ overlayClassName: `${baseClassName}__select-options` }"-->
<!--                    v-bind="selectInputProps">-->
<!--                <TOption v-for="format in formats" :key="format" :value="format" :label="format.toUpperCase()" style="font-size: 12px" />-->
<!--            </TSelect>-->
            <a-select
                    size="mini"
                    :class="[`${baseClassName}__format-mode-select`]"
                    v-model="formatModel"
                    @change="handleModeChange"
                    :popupProps="{ overlayClassName: `${baseClassName}__select-options` }"
                    v-bind="selectInputProps">
                <a-option v-for="format in formats" :key="format" :value="format" :label="format.toUpperCase()" style="font-size: 12px"></a-option>
            </a-select>
        </div>
        <div :class="[`${baseClassName}__format--item`]">
            <FormatInputs v-bind="newProps" />
        </div>
    </div>
</template>
<script lang="ts">
import { defineComponent, PropType, ref, watch } from 'vue';
import upperCase from 'lodash/upperCase';
import { TdColorPickerProps } from '../../type';
import props from '../../props';
import { FORMATS } from '../../const';
import { GColor } from '../../utils';
import FormatInputs from './inputs.vue';
import { useBaseClassName } from '../../hooks';

export default defineComponent({
    name: 'FormatPanel',
    inheritAttrs: false,
    props: {
        ...props,
        color: {
            type: Object as PropType<GColor>,
        },
        onModeChange: {
            type: Function,
            default: () => {
                return () => {
                };
            },
        },
        onInputChange: {
            type: Function,
            default: () => {
                return () => {
                };
            },
        },
    },
    setup(props) {
        const baseClassName = useBaseClassName();
        const formatModel = ref<TdColorPickerProps['format']>(props.format);
        const formats: TdColorPickerProps['format'][] = [...FORMATS];
        const selectInputProps = {
            ...((props.selectInputProps as Object) || {}),
        };
        watch(
            () => [props.format],
            () => (formatModel.value = props.format),
        );

        /**
         * 格式化类型改变触发
         * @param v
         */
        const handleModeChange = (v: TdColorPickerProps['format']) => {
            formatModel.value = v;
            props.onModeChange(v);
        };
        const newProps = computed(() => {
            return {
            ...props,
                format: formatModel.value,
            };
        })
        return {
            formats,
            newProps,
            formatModel,
            baseClassName,
            handleModeChange,
        };
    },
    components:{
        FormatInputs
    }
})
</script>
<style scoped>

</style>
