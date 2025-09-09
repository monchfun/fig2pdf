<script setup>
import { ref, watch, onUnmounted } from 'vue'
import VuePdfEmbed from 'vue-pdf-embed'

const props = defineProps({
  pdfFile: {
    type: File,
    default: null,
  },
})

const source = ref('')
let objectUrl = null

watch(() => props.pdfFile, (newFile) => {
  if (objectUrl) {
    URL.revokeObjectURL(objectUrl)
    objectUrl = null
  }

  if (newFile) {
    objectUrl = URL.createObjectURL(newFile)
    source.value = objectUrl
  } else {
    source.value = ''
  }
}, { immediate: true })

onUnmounted(() => {
  if (objectUrl) {
    URL.revokeObjectURL(objectUrl)
  }
})
</script>

<template>
  <div class="border rounded-lg overflow-hidden bg-gray-50">
    <VuePdfEmbed :source="source" />
  </div>
</template>