import { computed } from 'vue';
// import { useConfig } from '../config-provider/useConfig';
import isString from 'lodash/isString';
import isFunction from 'lodash/isFunction';
function useConfig(name?: string) {
    // 处理正则表达式
    const t = function <T>(pattern: T, ...args: any[]) {
        const [data] = args;
        if (isString(pattern)) {
            if (!data) return pattern;
            const regular = /\{\s*([\w-]+)\s*\}/g;
            const translated = pattern.replace(regular, (match, key) => {
                if (data) {
                    return String(data[key]);
                }
                return '';
            });
            return translated;
        }
        if (isFunction(pattern)) {
            // 重要：组件的渲染必须存在参数 h，不能移除
            if (!args.length) return pattern(h);
            return pattern(...args);
        }
        return '';
    };
    return {
        t,
        classPrefix: ref('t'),
    }
}
export function usePrefixClass(componentName?: string) {
  const { classPrefix } = useConfig('classPrefix');
  return computed(() => {
    return componentName ? `${classPrefix.value}-${componentName}` : classPrefix.value;
  });
}

export function useCommonClassName() {
  const { classPrefix } = useConfig('classPrefix');

  return {
    SIZE: computed(() => ({
      small: `${classPrefix.value}-size-s`,
      medium: `${classPrefix.value}-size-m`,
      large: `${classPrefix.value}-size-l`,
      default: '',
      xs: `${classPrefix.value}-size-xs`,
      xl: `${classPrefix.value}-size-xl`,
      block: `${classPrefix.value}-size-full-width`,
    })),
    STATUS: computed(() => ({
      loading: `${classPrefix.value}-is-loading`,
      loadMore: `${classPrefix.value}-is-load-more`,
      disabled: `${classPrefix.value}-is-disabled`,
      focused: `${classPrefix.value}-is-focused`,
      success: `${classPrefix.value}-is-success`,
      error: `${classPrefix.value}-is-error`,
      warning: `${classPrefix.value}-is-warning`,
      selected: `${classPrefix.value}-is-selected`,
      active: `${classPrefix.value}-is-active`,
      checked: `${classPrefix.value}-is-checked`,
      current: `${classPrefix.value}-is-current`,
      hidden: `${classPrefix.value}-is-hidden`,
      visible: `${classPrefix.value}-is-visible`,
      expanded: `${classPrefix.value}-is-expanded`,
      indeterminate: `${classPrefix.value}-is-indeterminate`,
    })),
  };
}

export { useConfig };
