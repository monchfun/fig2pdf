<script setup>
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Progress } from '@/components/ui/progress'

const props = defineProps({
  selectedFile: Object,
  colorMappings: Array,
})

const emit = defineEmits(['historyUpdated']) // Add this line

const convertTextToCurves = ref(false)
const processing = ref(false)
const cmykDownloadUrl = ref('')
const finalDownloadUrl = ref('')

const API_URL = '' // Use relative path for API calls

const processPdf = async () => {
  processing.value = true
  cmykDownloadUrl.value = ''
  finalDownloadUrl.value = ''

  const formData = new FormData()
  formData.append('pdf_file', props.selectedFile)
  formData.append('json_file', new Blob([JSON.stringify({ mappings: props.colorMappings }, null, 2)], { type: 'application/json' }), 'color_mapping.json')
  formData.append('convert_text', convertTextToCurves.value ? 'true' : 'false')

  try {
    const response = await fetch(`${API_URL}/process`, {
      method: 'POST',
      body: formData,
    })

    const result = await response.json()

    if (result.success) {
      if (result.cmyk_pdf_filename) {
        cmykDownloadUrl.value = `${API_URL}/download/${result.upload_id}/${result.cmyk_pdf_filename}`
      }
      if (result.final_pdf_filename) {
        finalDownloadUrl.value = `${API_URL}/download/${result.upload_id}/${result.final_pdf_filename}`
      }
      // Emit historyUpdated event
      emit('historyUpdated', result.history)
    } else {
      alert('处理失败: ' + result.message)
    }
  } catch (error) {
    console.error('处理失败:', error)
    alert('处理失败: ' + error.message)
  } finally {
    processing.value = false
  }
}
</script>

<template>
  <Card class="w-full max-w-4xl mx-auto">
    <CardHeader>
      <CardTitle>步骤 3: 处理与下载</CardTitle>
    </CardHeader>
    <CardContent class="space-y-6">
      <div class="flex items-center p-4 bg-gray-50 rounded-lg border border-gray-200">
        <Checkbox id="convert-text" v-model:checked="convertTextToCurves" />
        <label for="convert-text" class="ml-3 text-sm font-medium text-gray-700">
          将文字转为曲线（适用于印刷）
        </label>
      </div>

      <Button @click="processPdf" :disabled="processing" class="w-full">
        <span v-if="!processing" class="flex items-center justify-center">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          开始处理
        </span>
        <span v-else class="flex items-center justify-center">
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          处理中...
        </span>
      </Button>

      <div v-if="processing" class="text-center py-6">
        <div class="inline-flex items-center justify-center">
          <Progress :model-value="50" class="w-full" />
          <p class="ml-4 text-sm text-gray-600 font-medium">正在处理PDF文件，请稍候...</p>
        </div>
      </div>

      <div v-if="cmykDownloadUrl || finalDownloadUrl" class="text-center space-y-4 p-6 bg-green-50 rounded-xl border border-green-200">
        <h3 class="text-lg font-semibold text-green-800">处理完成！</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a v-if="cmykDownloadUrl" :href="cmykDownloadUrl" download class="inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-md">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
            </svg>
            CMYK PDF
          </a>
          <a v-if="finalDownloadUrl" :href="finalDownloadUrl" download class="inline-flex items-center justify-center px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium shadow-md">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
            </svg>
            最终PDF
          </a>
        </div>
      </div>
    </CardContent>
  </Card>
</template>
