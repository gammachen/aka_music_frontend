import { PropType } from 'vue';
import { GColor } from '../utils';

export default {
  /** 是否禁用组件 */
  disabled: Boolean,
  /** Color Instance */
  color: {
    type: Object as PropType<GColor>,
  },
  onChange: {
    type: Function,
    default: () => () => {},
  },
};
