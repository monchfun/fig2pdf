<script setup>
import { ref } from 'vue'
import { Button } from '@/components/ui/button'

const emit = defineEmits(['fileSelected'])

const fileInputRef = ref(null)
const selectedFileName = ref('')
const isDragOver = ref(false)

const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (file && file.type === 'application/pdf') {
    selectedFileName.value = file.name
    emit('fileSelected', file)
  }
}

const triggerFileInput = () => {
  fileInputRef.value.click()
}

const handleDrop = (event) => {
  event.preventDefault()
  isDragOver.value = false

  const files = event.dataTransfer.files
  if (files.length > 0) {
    const file = files[0]
    if (file.type === 'application/pdf') {
      selectedFileName.value = file.name
      emit('fileSelected', file)
    }
  }
}

const handleDragOver = (event) => {
  event.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = (event) => {
  event.preventDefault()
  isDragOver.value = false
}

const handleDragEnter = (event) => {
  event.preventDefault()
  isDragOver.value = true
}
</script>

<template>
  <!-- File Upload Area -->
  <div class="w-full">
    <div
      class="border-2 border-dashed rounded-xl p-12 text-center transition-all duration-200 cursor-pointer"
      :class="[
        isDragOver
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-300 bg-white hover:border-gray-400'
      ]"
      @drop="handleDrop"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @dragenter="handleDragEnter"
      @click="triggerFileInput"
    >
      <input
        type="file"
        accept=".pdf"
        class="hidden"
        ref="fileInputRef"
        @change="handleFileChange"
      />
      <div class="space-y-6">
        <div class="mx-auto w-24 h-24 bg-blue-50 rounded-full flex items-center justify-center">
          <svg
            class="w-12 h-12 text-blue-600"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </div>
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">
            {{ isDragOver ? '松开以上传 PDF 文件' : '上传您的 PDF 文件' }}
          </h3>
          <p class="text-sm text-gray-500 mb-6">支持将 Figma 导出的 PDF 转换为印刷级 CMYK 格式</p>
          <Button @click.stop="triggerFileInput" size="lg">
            选择 PDF 文件
          </Button>
          <p class="mt-4 text-sm text-gray-500">
            {{ selectedFileName ? selectedFileName : "或将文件拖拽到此处" }}
          </p>
          <p v-if="selectedFileName" class="mt-2 text-sm text-green-600 font-medium">
            ✓ 已选择: {{ selectedFileName }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>