<script setup>
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const emit = defineEmits(['fileSelected'])

const fileInputRef = ref(null)
const selectedFileName = ref('')

const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFileName.value = file.name
    emit('fileSelected', file)
  }
}

const triggerFileInput = () => {
  fileInputRef.value.click()
}
</script>

<template>
  <div class="space-y-6">
    <!-- File Upload Card -->
    <Card class="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>步骤 1: 上传PDF文件</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center bg-gray-50 transition-colors hover:border-gray-300">
          <input
            type="file"
            accept=".pdf"
            class="hidden"
            ref="fileInputRef"
            @change="handleFileChange"
          />
          <div class="space-y-4">
            <svg
              class="mx-auto h-16 w-16 text-gray-400"
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
            <div>
              <Button @click="triggerFileInput">
                选择PDF文件
              </Button>
              <p class="mt-3 text-sm text-gray-600">
                {{ selectedFileName ? selectedFileName : "或拖拽文件到此处" }}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
</template>