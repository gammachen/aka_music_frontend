<template>
    <a-trigger v-model="popProps.visible"
               :position="popProps.position"
               :trigger="popProps.trigger"
               :style="{ '--color-picker-panel-width': width }"
               :unmount-on-close="false">
        <div style="width: fit-content">
            <DefaultTrigger
                    :color="innerValue"
                    :disabled="disabled"
                    :clearable="clearable"
                    :input-props="inputProps"
                    :onTriggerChange="setInnerValue"
                    :mode="mode"
                    :colorModes="colorModes"
                    :size="size">
                <template v-for="(value, key) in $slots" #[key]="slotProps2" :key="key">
                    <slot :name="key" v-bind="slotProps2"></slot>
                </template>
            </DefaultTrigger>
        </div>
        <template #content>
            <div :class="[`${baseClassName}__trigger`]">
                <g-color-picker-panel
                        v-bind="newProps"
                        :disabled="disabled"
                        :value="innerValue.value"
                        :modelValue="innerValue"
                        @togglePopup="setVisible"
                        @change="onPickerChange"
                        @modeChange="changeMode"
                >
                    <!-- 循环注册 父级传递下来的slot -->
                    <template v-for="(value, key) in $slots" #[key]="slotProps" :key="key">
                        <slot :name="key" v-bind="slotProps"></slot>
                    </template>
                </g-color-picker-panel>
            </div>
        </template>
    </a-trigger>
</template>
<script lang="ts">
import {defineComponent, ref, toRefs} from 'vue';
import useVModel from '@/hooks/useVModel';
import props from './props';
import DefaultTrigger from './trigger.vue';
import {useBaseClassName} from './hooks';
import {TdColorContext} from './interfaces';

export default defineComponent({
    name: 'GColorPicker',
    props: {
        ...props,
        width: {
            type: String,
            default: '266px'
        }
    },
    setup(props) {
        const baseClassName = useBaseClassName();
        const visible = ref(false);
        const mode = ref(props.colorModes[0]);
        const setVisible = (value: boolean) => (visible.value = value);

        const {value: inputValue, modelValue} = toRefs(props);
        const [innerValue, setInnerValue] = useVModel(inputValue, modelValue, props.defaultValue, props.onChange);

        const refTrigger = ref<HTMLElement>();
        const popProps = {
            position: 'bl',
            trigger: 'click',
            overlayClassName: [baseClassName],
            visible: visible,
        };
        const newProps = {...props};
        delete newProps.onChange;
        const onPickerChange = (value: string, context: TdColorContext) => {
            setInnerValue(value, context)
        }
        const changeMode = (value: string) => {
            mode.value = value
        }
        return {
            popProps,
            newProps,
            baseClassName,
            innerValue,
            visible,
            refTrigger,
            setVisible,
            setInnerValue,
            onPickerChange,
            changeMode,
            mode,
        };
    },
    components: {
        DefaultTrigger
    }
})
</script>
<style scoped>

</style>
