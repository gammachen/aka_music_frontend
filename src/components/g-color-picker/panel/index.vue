<template>
    <div :class="[`${baseClassName}__panel`, disabled ? statusClassNames.disabled : '']">
        <PanelHeader v-bind="$props" :mode="mode" @mode-change="handleModeChange"/>
        <div :class="[`${baseClassName}__body`]">
            <div v-if="colorModes.includes(mode)">
                <template v-if="isGradientLinear">
                    <LinearGradient v-bind="baseProps" @change="handleGradientChange"
                                    :enable-multiple-gradient="enableMultipleGradient"/>
                </template>
                <template v-if="isGradientRadial">
                    <RadialGradient v-bind="baseProps" @change="handleGradientChange"
                                    :enable-multiple-gradient="enableMultipleGradient"/>
                </template>

                <SaturationPanel v-bind="baseProps" @change="handleSatAndValueChange"/>

                <div :class="[`${baseClassName}__sliders-wrapper`]">
                    <div :class="[`${baseClassName}__sliders`]">
                        <HueSlider v-bind="baseProps" @change="handleHueChange"/>
                        <template v-if="enableAlpha">
                            <AlphaSlider v-bind="baseProps" @change="handleAlphaChange"/>
                        </template>
                    </div>

                    <template v-if="showPrimaryColorPreview">
                        <div :class="[`${baseClassName}__sliders-preview`, `${baseClassName}--bg-alpha`]">
            <span
                    :class="[`${baseClassName}__sliders-preview-inner`]"
                    :style="{ background: isGradientLinear ? color.linearGradient : isGradientRadial?color.radialGradient :color.rgba }"
            ></span>
                        </div>
                    </template>
                </div>

                <FormatPanel
                        v-bind="$props"
                        :color="color"
                        :format="formatModel"
                        @mode-change="handleFormatModeChange"
                        @input-change="handleInputChange"
                />
                <template v-if="showSystemColors || showUsedColors">
                    <div :class="`${baseClassName}__swatches-wrap`">
                        <template v-if="showUsedColors">
                            <SwatchesPanel
                                    v-bind="baseProps"
                                    :title="'最近使用颜色'"
                                    :editable="true"
                                    :colors="recentlyUsedColors"
                                    :handleAddColor="addRecentlyUsedColor"
                                    :onSetColor="(color2:string) => handleSetColor('used', color2)"
                                    :onChange="handleRecentlyUsedColorsChange"
                            />
                        </template>
                        <template v-if="showSystemColors">
                            <SwatchesPanel
                                    v-bind="baseProps"
                                    :title="'系统预设颜色'"
                                    :colors="systemColors"
                                    @set-color="color => handleSetColor('system', color)"
                            />
                        </template>
                    </div>
                </template>
            </div>
            <div v-else>
                <!-- 循环注册 父级传递下来的slot -->
                <template v-for="(value, key) in $slots" :key="key">
                    <div v-if="(mode+'-panel') == key">
                        <slot :name="key"></slot>
                    </div>
                </template>
<!--                <slot v-for="(value,index) in cusColorModes" :key="index" :name="value"></slot>-->
            </div>
        </div>
    </div>
</template>
<script lang="ts">
import {defineComponent, ref, toRefs, watch, computed,getCurrentInstance} from 'vue';
import {useCommonClassName, useConfig} from '../hooks/useConfig';
import props from '../props';
import {
    DEFAULT_COLOR,
    DEFAULT_LINEAR_GRADIENT,
    TD_COLOR_USED_COLORS_MAX_SIZE,
    DEFAULT_SYSTEM_SWATCH_COLORS, COLOR_MODES, DEFAULT_RADIAL_GRADIENT,
} from '../const';
import PanelHeader from './header.vue';
import LinearGradient from './linear-gradient.vue';
import RadialGradient from './radial-gradient.vue';
import SaturationPanel from './saturation.vue';
import HueSlider from './hue.vue';
import AlphaSlider from './alpha.vue';
import FormatPanel from './format/index.vue';
import SwatchesPanel from './swatches.vue';
import {GColor, getColorObject, GradientColorPoint} from '../utils';
import {TdColorPickerProps, ColorPickerChangeTrigger} from '../type';
import {TdColorModes} from '../interfaces';
import {useBaseClassName} from '../hooks';
import useVModel from '@/hooks/useVModel';
import useDefaultValue from '@/hooks/useDefaultValue';
import cloneDeep from 'lodash/cloneDeep';

export default defineComponent({
    name: 'ColorPanel',
    props: {
        ...props,
        togglePopup: {
            type: Function,
        },
    },

    setup(props) {
        console.log('22222222222')
        const {proxy} = getCurrentInstance()
        const baseClassName = useBaseClassName();
        const {STATUS} = useCommonClassName();
        const {t, globalConfig} = useConfig('colorPicker');
        const statusClassNames = STATUS.value;
        const {value: inputValue, modelValue, recentColors} = toRefs(props);
        console.log('recentColors=', recentColors)
        const [innerValue, setInnerValue] = useVModel(inputValue, modelValue, props.defaultValue, props.onChange);

        const defaultEmptyColor = computed(() => {
            if((isGradientLinear.value )){
                return DEFAULT_LINEAR_GRADIENT
            }else if((isGradientRadial.value )){
                return DEFAULT_RADIAL_GRADIENT
            }else{
                return DEFAULT_COLOR
            }
        });

        const mode = ref<TdColorModes>(props.colorModes?.length === 1 ? props.colorModes[0] : 'monochrome');
        const isGradientLinear = computed(() => mode.value === 'linear-gradient');
        const isGradientRadial = computed(() => mode.value === 'radial-gradient');

        const color = ref(new GColor(innerValue.value || defaultEmptyColor.value));
        const updateColor = () => color.value.update(innerValue.value || defaultEmptyColor.value);

        const formatModel = ref<TdColorPickerProps['format']>(color.value.isGradient ? 'CSS' : 'RGB');

        const [recentlyUsedColors, setRecentlyUsedColors] = useDefaultValue(
            recentColors,
            props.defaultRecentColors,
            props.onRecentColorsChange,
            'recentColors',
        );
        console.log('recentlyUsedColors=', recentlyUsedColors)
        setRecentlyUsedColors(['blue'])
        console.log('setRecentlyUsedColors=', setRecentlyUsedColors)
        const baseProps = {
            color: color.value,
            disabled: props.disabled,
        };
        const showUsedColors = computed(() => {
            return recentColors.value !== null && recentColors.value !== false
        });
        console.log('showUsedColors=', showUsedColors)
        let systemColors = props.swatchColors;
        if (systemColors === undefined) {
            systemColors = [...DEFAULT_SYSTEM_SWATCH_COLORS];
        }
        const showSystemColors = systemColors?.length > 0;
        const formatValue = () => {
            // 渐变模式下直接输出css样式
            if (mode.value === 'linear-gradient') {
                return color.value.linearGradient;
            }
            if (mode.value === 'radial-gradient') {
                return color.value.radialGradient;
            }
            return color.value.getFormatsColorMap()[props.format] || color.value.css;
        };

        /**
         * 添加最近使用颜色
         * @returns void
         */
        const addRecentlyUsedColor = () => {
            if (recentlyUsedColors.value === null || recentlyUsedColors.value === false) {
                return;
            }
            const colors = cloneDeep(recentlyUsedColors.value as string[]) || [];
            const currentColor = color.value.isGradient ? color.value.linearGradient : color.value.rgba;
            const index = colors.indexOf(currentColor);
            if (index > -1) {
                colors.splice(index, 1);
            }
            colors.unshift(currentColor);
            if (colors.length > TD_COLOR_USED_COLORS_MAX_SIZE) {
                colors.length = TD_COLOR_USED_COLORS_MAX_SIZE;
            }
            handleRecentlyUsedColorsChange(colors);
        };

        /**
         * 最近使用颜色变更时触发
         * @param colors
         */
        const handleRecentlyUsedColorsChange = (colors: string[]) => {
            setRecentlyUsedColors(colors);
        };

        /**
         * onChange
         * @param trigger
         */
        const emitColorChange = (trigger?: ColorPickerChangeTrigger) => {
            setInnerValue(formatValue(), {
                color: getColorObject(color.value),
                trigger: trigger || 'palette-saturation-brightness',
            });
        };

        watch(() => [props.defaultValue, props.enableAlpha], updateColor);

        watch(
            () => innerValue.value,
            (newColor) => {
                if (newColor !== formatValue()) {
                    updateColor();
                    mode.value = color.value.isLinerGradient ? 'linear-gradient':color.value.isRadialGradient?'radial-gradient' : 'monochrome';
                }
            },
        );

        /**
         * mode change
         * @param value
         * @returns
         */
        const handleModeChange = (value: TdColorModes) => {
            console.log('val=', value)
            mode.value = value;
            if (value === 'linear-gradient') {
                color.value.update(
                    color.value.gradientColors.length > 0 ? color.value.linearGradient : DEFAULT_LINEAR_GRADIENT,
                );
            }else if (value === 'radial-gradient') {
                color.value.update(
                    color.value.gradientColors.length > 0 ? color.value.radialGradient : DEFAULT_LINEAR_GRADIENT,
                );
            } else {
                color.value.update(color.value.rgba);
            }

            emitColorChange();
            proxy.$emit('modeChange', mode.value);
        };

        /**
         * 格式变化
         * @param format
         * @returns
         */
        const handleFormatModeChange = (format: TdColorPickerProps['format']) => (formatModel.value = format);

        /**
         * 饱和度亮度变化
         * @param param0
         */
        const handleSatAndValueChange = ({saturation, value}: { saturation: number; value: number }) => {
            const {saturation: sat, value: val} = color.value;
            let changeTrigger: ColorPickerChangeTrigger = 'palette-saturation-brightness';
            if (value !== val && saturation !== sat) {
                color.value.saturation = saturation;
                color.value.value = value;
                changeTrigger = 'palette-saturation-brightness';
            } else if (saturation !== sat) {
                color.value.saturation = saturation;
                changeTrigger = 'palette-saturation';
            } else if (value !== val) {
                color.value.value = value;
                changeTrigger = 'palette-brightness';
            } else {
                return;
            }

            color.value.update(color.value.rgba);
            emitColorChange(changeTrigger);
        };

        /**
         * 色相变化
         * @param hue
         */
        const handleHueChange = (hue: number) => {
            color.value.hue = hue;
            emitColorChange('palette-hue-bar');
            props.onPaletteBarChange?.({
                color: getColorObject(color.value),
            });
        };

        /**
         * 透明度变化
         * @param alpha
         */
        const handleAlphaChange = (alpha: number) => {
            color.value.alpha = alpha;
            emitColorChange('palette-alpha-bar');
        };

        /**
         * 输入框触发改变
         * @param input
         * @param alpha
         */
        const handleInputChange = (input: string, alpha?: number) => {
            color.value.update(input);
            color.value.alpha = alpha;
            emitColorChange('input');
        };

        /**
         * 渐变改变
         * @param param0
         */
        const handleGradientChange = ({
                                          key,
                                          payload,
                                      }: {
            key: 'degree' | 'selectedId' | 'colors';
            payload: number | string | GradientColorPoint[];
        }) => {
            let trigger: ColorPickerChangeTrigger = 'palette-saturation-brightness';
            switch (key) {
                case 'degree':
                    color.value.gradientDegree = payload as number;
                    trigger = 'input';
                    break;
                case 'selectedId':
                    color.value.gradientSelectedId = payload as string;
                    break;
                case 'colors':
                    color.value.gradientColors = payload as GradientColorPoint[];
                    break;
            }
            emitColorChange(trigger);
        };

        /**
         * 色块点击
         * @param type
         * @param value
         */
        const handleSetColor = (type: 'system' | 'used', value: string) => {
            const isGradientValue = GColor.isGradientColor(value);
            if (isGradientValue) {
                if (props.colorModes.includes('linear-gradient')) {
                    mode.value = 'linear-gradient';
                    color.value.update(value);
                    color.value.updateCurrentGradientColor();
                }if (props.colorModes.includes('radial-gradient')) {
                    mode.value = 'radial-gradient';
                    color.value.update(value);
                    color.value.updateCurrentGradientColor();
                } else {
                    console.warn('该模式不支持渐变色');
                }
            } else if (mode.value === 'linear-gradient') {
                color.value.updateStates(value);
                color.value.updateCurrentGradientColor();
            } else if (mode.value === 'radial-gradient') {
                color.value.updateStates(value);
                color.value.updateCurrentGradientColor();
            } else {
                color.value.update(value);
            }
            emitColorChange();
        };

        return {
            baseClassName,
            statusClassNames,
            t,
            globalConfig,
            color,
            mode,
            formatModel,
            recentlyUsedColors,
            // isGradient,
            isGradientLinear,
            isGradientRadial,
            systemColors,
            showSystemColors,
            showUsedColors,
            baseProps,
            addRecentlyUsedColor,
            handleModeChange,
            handleSatAndValueChange,
            handleHueChange,
            handleAlphaChange,
            handleGradientChange,
            handleSetColor,
            handleFormatModeChange,
            handleInputChange,
            handleRecentlyUsedColorsChange,
        };
    },
    components: {
        PanelHeader,
        LinearGradient,
        RadialGradient,
        SaturationPanel,
        HueSlider,
        AlphaSlider,
        FormatPanel,
        SwatchesPanel,
    }
})
</script>
<style scoped>

</style>
