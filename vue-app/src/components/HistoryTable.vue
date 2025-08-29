<script setup>
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

const props = defineProps({
  history: { type: Array, required: true },
  onFetchHistory: { type: Function, required: true },
  onClearHistory: { type: Function, required: true },
})

const API_URL = '' // Proxy will handle forwarding

// Function to get download URL
const getDownloadUrl = (uploadId, filename) => {
  return `${API_URL}/download/${uploadId}/${filename}`
}
</script>

<template>
  <Card class="w-full max-w-4xl mx-auto mt-8">
    <CardHeader>
      <div class="flex justify-between items-center">
        <CardTitle>📋 历史记录</CardTitle>
        <Button variant="outline" @click="onFetchHistory">🔄 刷新</Button>
      </div>
    </CardHeader>
    <CardContent>
      <div v-if="history.length === 0" class="text-center py-12">
        <svg class="mx-auto h-16 w-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="text-gray-500 text-lg">暂无历史记录</p>
        <p class="text-gray-400 text-sm mt-2">处理PDF文件后，记录将显示在这里</p>
      </div>

      <div v-else class="overflow-x-auto rounded-xl border border-gray-200">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>时间</TableHead>
              <TableHead>原始PDF</TableHead>
              <TableHead>CMYK PDF</TableHead>
              <TableHead>最终PDF</TableHead>
              <TableHead>映射JSON</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="record in history" :key="record.upload_id">
              <TableCell>{{ record.timestamp }}</TableCell>
              <TableCell>
                <a v-if="record.original_pdf" :href="getDownloadUrl(record.upload_id, record.original_pdf)" download class="text-blue-600 hover:underline">
                  {{ record.original_pdf }}
                </a>
                <span v-else class="text-gray-400">-</span>
              </TableCell>
              <TableCell>
                <a v-if="record.cmyk_pdf" :href="getDownloadUrl(record.upload_id, record.cmyk_pdf)" download class="text-blue-600 hover:underline">
                  {{ record.cmyk_pdf }}
                </a>
                <span v-else class="text-gray-400">-</span>
              </TableCell>
              <TableCell>
                <a v-if="record.final_pdf" :href="getDownloadUrl(record.upload_id, record.final_pdf)" download class="text-green-600 hover:underline">
                  {{ record.final_pdf }}
                </a>
                <span v-else class="text-gray-400">-</span>
              </TableCell>
              <TableCell>
                <a v-if="record.json_mapping" :href="getDownloadUrl(record.upload_id, record.json_mapping)" download class="text-purple-600 hover:underline">
                  {{ record.json_mapping }}
                </a>
                <span v-else class="text-gray-400">-</span>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>

      <div class="mt-6 flex justify-end">
        <Button variant="destructive" @click="onClearHistory">
          🗑️ 清空历史记录
        </Button>
      </div>
    </CardContent>
  </Card>
</template>
