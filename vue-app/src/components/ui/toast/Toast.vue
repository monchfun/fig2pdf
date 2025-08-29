<script setup>
import { computed } from 'vue'
import { ToastRoot, ToastClose, ToastDescription, ToastTitle } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps({
  title: { type: String, required: false },
  description: { type: String, required: false },
  variant: { type: String, default: 'default' },
})

const classes = computed(() => {
  return cn(
    'group pointer-events-auto relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-md border p-6 pr-8 shadow-lg transition-all data-[swipe=cancel]:translate-x-0 data-[swipe=end]:translate-x-[var(--radix-toast-swipe-end-x)] data-[swipe=move]:translate-x-[var(--radix-toast-swipe-move-x)] data-[swipe=move]:transition-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[swipe=end]:animate-out data-[state=closed]:fade-out-80 data-[state=open]:slide-in-from-top-full data-[state=open]:sm:slide-in-from-bottom-full data-[state=closed]:slide-out-to-right-full data-[state=closed]:sm:slide-out-to-right-full',
    props.variant === 'destructive' && 'destructive'
  )
})
</script>

<template>
  <ToastRoot :class="classes">
    <div class="grid gap-1">
      <ToastTitle v-if="title" class="text-sm font-semibold">
        {{ title }}
      </ToastTitle>
      <ToastDescription v-if="description" class="text-sm opacity-90">
        {{ description }}
      </ToastDescription>
    </div>
    <ToastClose />
  </ToastRoot>
</template>