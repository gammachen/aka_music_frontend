<template>
	<div class="degree">
		<div class="flex degree-box">
			<div class="degree-label">角度：</div>
			<a-slider :default-value="degree" style="width: 100%" :max="360" show-input size="mini" @change="handleChange" />
		</div>
	</div>
</template>
<script lang="ts" setup>
  const props = defineProps<{
    degree: number,
	updateColor: Function
  }>()

  const handleChange = (v: number) => {
	props.updateColor({
		degree: v
	}, 'onChange')
  }
</script>
<style lang="less" scoped>
.degree {
  padding: 0 10px 10px;
  &-box {
	display: flex;
	align-items: center;
  }
  &-label {
	width: 66px;
  }
}
</style>