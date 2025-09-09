<script setup>
import { ref, watch, onUnmounted } from 'vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import VuePdfEmbed from 'vue-pdf-embed'

const props = defineProps({
  originalPdfFile: {
    type: File,
    required: true,
  },
  processedPdfFile: {
    type: File,
    default: null,
  },
})

const originalSource = ref('')
const processedSource = ref('')

let originalObjectUrl = null
let processedObjectUrl = null

watch(() => props.originalPdfFile, (newFile) => {
  if (originalObjectUrl) {
    URL.revokeObjectURL(originalObjectUrl)
  }
  if (newFile) {
    originalObjectUrl = URL.createObjectURL(newFile)
    originalSource.value = originalObjectUrl
  } else {
    originalSource.value = ''
  }
}, { immediate: true })

watch(() => props.processedPdfFile, (newFile) => {
  if (processedObjectUrl) {
    URL.revokeObjectURL(processedObjectUrl)
  }
  if (newFile) {
    processedObjectUrl = URL.createObjectURL(newFile)
    processedSource.value = processedObjectUrl
  } else {
    processedSource.value = ''
  }
}, { immediate: true })

onUnmounted(() => {
  if (originalObjectUrl) {
    URL.revokeObjectURL(originalObjectUrl)
  }
  if (processedObjectUrl) {
    URL.revokeObjectURL(processedObjectUrl)
  }
})
</script>

<template>
  <Card class="w-full">
    <CardHeader>
      <CardTitle>PDF 对比预览</CardTitle>
    </CardHeader>
    <CardContent>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Original PDF -->
        <div>
          <h3 class="text-sm font-medium text-gray-700 mb-2 text-center">原始PDF</h3>
          <div class="border rounded-lg overflow-hidden bg-gray-50">
            <VuePdfEmbed :source="originalSource" />
          </div>
        </div>

        <!-- Processed PDF -->
        <div>
          <h3 class="text-sm font-medium text-green-700 mb-2 text-center">处理后PDF</h3>
          <div v-if="processedPdfFile" class="border rounded-lg overflow-hidden bg-gray-50">
            <VuePdfEmbed :source="processedSource" />
          </div>
          <div v-else class="text-center text-gray-500 p-8 border rounded-lg border-dashed">
            等待处理完成...
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
</template>
