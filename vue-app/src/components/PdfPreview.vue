<script setup>
import { ref, watch, onUnmounted, computed } from 'vue'
import VuePdfEmbed from 'vue-pdf-embed'

const props = defineProps({
  pdfFile: {
    type: File,
    default: null,
  },
  showColorPreview: {
    type: Boolean,
    default: false,
  },
  colorMappings: {
    type: Array,
    default: () => [],
  },
})

const source = ref('')
const objectUrl = ref(null)
const scale = ref(1)

// 计算适合容器的缩放比例
const containerStyle = computed(() => {
  return {
    transform: `scale(${scale.value})`,
    transformOrigin: 'top left',
    width: `${100 / scale.value}%`,
    height: `${100 / scale.value}%`,
  }
})

watch(() => props.pdfFile, (newFile) => {
  if (objectUrl.value) {
    URL.revokeObjectURL(objectUrl.value)
    objectUrl.value = null
  }

  if (newFile) {
    objectUrl.value = URL.createObjectURL(newFile)
    source.value = objectUrl.value
  } else {
    source.value = ''
  }
}, { immediate: true })

onUnmounted(() => {
  if (objectUrl.value) {
    URL.revokeObjectURL(objectUrl.value)
  }
})

// 缩放控制
const zoomIn = () => {
  scale.value = Math.min(scale.value + 0.25, 3)
}

const zoomOut = () => {
  scale.value = Math.max(scale.value - 0.25, 0.5)
}

const resetZoom = () => {
  scale.value = 1
}
</script>

<template>
  <div class="h-full w-full flex flex-col bg-gray-50">
    <!-- Toolbar -->
    <div class="flex items-center justify-between p-2 bg-white border-b border-gray-200">
      <div class="flex items-center space-x-2">
        <button
          @click="zoomOut"
          class="p-1.5 hover:bg-gray-100 rounded text-gray-600 hover:text-gray-900"
          title="缩小"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path>
          </svg>
        </button>
        <span class="text-sm text-gray-600 min-w-[3rem] text-center">{{ Math.round(scale * 100) }}%</span>
        <button
          @click="zoomIn"
          class="p-1.5 hover:bg-gray-100 rounded text-gray-600 hover:text-gray-900"
          title="放大"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
        </button>
        <button
          @click="resetZoom"
          class="p-1.5 hover:bg-gray-100 rounded text-gray-600 hover:text-gray-900 text-xs"
          title="重置缩放"
        >
          重置
        </button>
      </div>

      <div v-if="showColorPreview && colorMappings.length > 0" class="flex items-center space-x-2">
        <span class="text-xs text-gray-500">颜色预览:</span>
        <div class="flex space-x-1">
          <div
            v-for="mapping in colorMappings.slice(0, 5)"
            :key="mapping.name"
            class="w-4 h-4 rounded border border-gray-300"
            :style="{ backgroundColor: mapping.name }"
            :title="`${mapping.name} → CMYK(${mapping.cmyk_100.join(', ')})`"
          ></div>
          <span
            v-if="colorMappings.length > 5"
            class="text-xs text-gray-500 ml-1"
          >
            +{{ colorMappings.length - 5 }}
          </span>
        </div>
      </div>
    </div>

    <!-- PDF Viewer -->
    <div class="flex-1 overflow-auto bg-gray-50 flex items-center justify-center">
      <div v-if="source" class="inline-block" :style="containerStyle">
        <VuePdfEmbed
          :source="source"
          class="shadow-lg bg-white"
        />
      </div>
      <div v-else class="text-gray-500 text-center">
        <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        <p>暂无 PDF 文件</p>
      </div>
    </div>
  </div>
</template>