<template>
    <div class="arco-input-outer">
        <div class="arco-input-prepend" v-if="$slots.prepend">
            <slot name="prepend"></slot>
        </div>
        <div class="arco-input-wrapper">
            <div class="arco-input-prefix" v-if="$slots.prefix">
                <slot name="prefix"></slot>
            </div>
            <slot></slot>
            <div class="arco-input-suffix" v-if="$slots.suffix">
                <slot name="suffix"></slot>
            </div>
        </div>
        <div class="arco-input-append" v-if="$slots.append">
            <slot name="append"></slot>
        </div>
    </div>
</template>

<script setup lang="ts">
const slots = useSlots()
const props = defineProps<{
    label?: string
}>()

const hasLabel = computed(() => !!props.label || !!slots.label)
</script>

<style scoped>

</style>
