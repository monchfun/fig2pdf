<script setup>
import { ref, onMounted, computed } from 'vue';
import { Button } from '@/components/ui/button';
import { useToast, Toaster } from '@/components/ui/toast';
import FileUpload from '@/components/FileUpload.vue';
import PdfPreview from '@/components/PdfPreview.vue';
import ColorMapping from '@/components/ColorMapping.vue';
import HistoryTable from '@/components/HistoryTable.vue';
import { AlertDialog, AlertDialogContent, AlertDialogHeader, AlertDialogTitle, AlertDialogFooter, AlertDialogCancel } from '@/components/ui/alert-dialog';

// --- App State ---
const appState = ref('initial'); // initial, analyzing, file_ready, processing, done
const selectedFile = ref(null);
const uniqueColors = ref([]); // Holds the array of {hex, rgb, cmyk, count}
const finalResult = ref(null);
const convertTextToCurves = ref(false);
const errorMessage = ref('');
const history = ref([]);
const isHistoryOpen = ref(false);

const previewMappings = computed(() => {
  return uniqueColors.value.map(color => ({
    name: color.hex,
    rgb_255: color.rgb,
    cmyk_100: color.cmyk,
  }));
});

const { toast } = useToast();

// --- Core Logic ---
const handleFileSelect = async (file) => {
  if (!file) return;
  selectedFile.value = file;
  appState.value = 'analyzing';
  errorMessage.value = '';
  uniqueColors.value = [];

  try {
    const formData = new FormData();
    formData.append('pdf_file', file);
    const response = await fetch('/api/analyze-colors', {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) throw new Error('颜色分析失败，请检查PDF文件是否有效。');
    
    const result = await response.json();
    if (result.success) {
      uniqueColors.value = result.colors;
      appState.value = 'file_ready';
    } else {
      throw new Error(result.message || '分析结果无效。');
    }

  } catch (error) {
    console.error('Error during file processing:', error);
    errorMessage.value = `处理失败: ${error.message}`;
    toast({ title: '错误', description: errorMessage.value, variant: 'destructive' });
    resetApp();
  }
};

const resetApp = () => {
  appState.value = 'initial';
  selectedFile.value = null;
  uniqueColors.value = [];
  errorMessage.value = '';
  finalResult.value = null;
  convertTextToCurves.value = false;
};

const handleProcessRequest = async () => {
  if (!selectedFile.value || uniqueColors.value.length === 0) {
    toast({ title: '错误', description: '缺少文件或颜色映射。' });
    return;
  }

  appState.value = 'processing';
  finalResult.value = null;

  try {
    // Prepare the color mapping JSON from the current state
    const mappingsForExport = {
      mappings: uniqueColors.value.map(color => ({
        name: color.hex, // Use hex as name
        rgb_255: color.rgb,
        cmyk_100: color.cmyk,
      }))
    };
    const jsonBlob = new Blob([JSON.stringify(mappingsForExport, null, 2)], { type: 'application/json' });

    const formData = new FormData();
    formData.append('pdf_file', selectedFile.value);
    formData.append('json_file', jsonBlob, 'color-mapping.json');
    formData.append('convert_text', convertTextToCurves.value);

    const response = await fetch('/process', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || '文件处理失败。');
    }

    const result = await response.json();
    if (result.success) {
      finalResult.value = result;
      history.value = result.history; // Update history from response
      appState.value = 'done';
      toast({ title: '成功', description: '文件处理完成！' });
    } else {
      throw new Error(result.message || '处理过程中发生未知错误。');
    }

  } catch (error) {
    console.error('Error during processing:', error);
    errorMessage.value = `处理失败: ${error.message}`;
    toast({ title: '错误', description: errorMessage.value, variant: 'destructive' });
    appState.value = 'file_ready'; // Revert to the ready state on error
  }
};

// --- History Methods ---
onMounted(() => {
  fetchHistory();
});

const fetchHistory = async () => {
  try {
    const response = await fetch(`/api/history?t=${new Date().getTime()}`);
    if (!response.ok) throw new Error('无法获取历史记录');
    const data = await response.json();
    history.value = data;
  } catch (error) {
    toast({ title: '历史记录错误', description: error.message, variant: 'destructive' });
  }
};

const clearHistory = async () => {
  if (!window.confirm('确定要清空所有历史记录吗？此操作不可撤销。')) return;
  try {
    const response = await fetch('/api/clear-history', { method: 'POST' });
    if (!response.ok) throw new Error('清空历史记录失败');
    const result = await response.json();
    if (result.success) {
      toast({ title: '成功', description: '历史记录已清空。' });
      fetchHistory(); // Refresh the list
      isHistoryOpen.value = false; // Close the dialog
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    toast({ title: '错误', description: error.message, variant: 'destructive' });
  }
};

</script>

<template>
  <div class="min-h-screen bg-gray-100 text-gray-800 p-4 sm:p-8">
    <div class="max-w-6xl mx-auto">
      <header class="text-center mb-8 relative">
        <h1 class="text-4xl font-bold text-gray-900">PDF 颜色转换工作台</h1>
        <p class="text-lg text-gray-600 mt-2">一个更现代、更直观的颜色转换流程</p>
        <div class="absolute top-0 right-0">
          <Button variant="outline" @click="isHistoryOpen = true">查看历史记录</Button>
        </div>
      </header>

      <!-- Initial State: File Upload -->
      <div v-if="appState === 'initial'" class="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-md">
        <FileUpload @fileSelected="handleFileSelect" />
      </div>

      <!-- Analyzing State -->
      <div v-if="appState === 'analyzing'" class="text-center p-8">
        <p class="text-xl font-semibold animate-pulse">正在分析 PDF 中的主要颜色，请稍候...</p>
        <p class="text-gray-500 mt-2">{{ selectedFile?.name }}</p>
      </div>

      <!-- Main Workspace -->
      <div v-if="appState === 'file_ready' || appState === 'processing' || appState === 'done'" class="grid grid-cols-1 md:grid-cols-3 gap-8">
        
        <!-- Left Panel: PDF Preview -->
        <div class="md:col-span-2 bg-white p-6 rounded-lg shadow-md">
          <h2 class="text-2xl font-bold mb-4 border-b pb-2">PDF 预览</h2>
          <div v-if="selectedFile">
            <PdfPreview 
              :key="selectedFile.name"
              :pdf-file="selectedFile" 
              :show-color-preview="appState === 'file_ready'" 
              :color-mappings="previewMappings"
            />
          </div>
        </div>

        <!-- Right Panel: Configuration & Actions -->
        <div class="md:col-span-1 bg-white p-6 rounded-lg shadow-md flex flex-col">
          
          <!-- State: File Ready (Configuration) -->
          <div v-if="appState === 'file_ready'" class="flex flex-col h-full">
            <div class="flex-grow">
              <ColorMapping 
                v-if="uniqueColors.length > 0"
                :colors="uniqueColors"
                @update:colors="uniqueColors = $event"
              />
              <p v-else class="text-gray-500 text-center pt-10">未在此 PDF 中提取到可识别的颜色。</p>
            </div>
            <div class="mt-8 space-y-4">
              <div class="flex items-center space-x-2">
                <input type="checkbox" id="convertText" v-model="convertTextToCurves" class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600" />
                <label for="convertText" class="text-sm font-medium text-gray-700">文字转曲线 (用于印刷)</label>
              </div>
              <Button @click="handleProcessRequest" class="w-full text-lg py-6">开始转换</Button>
              <Button @click="resetApp" variant="outline" class="w-full">处理另一个文件</Button>
            </div>
          </div>

          <!-- State: Processing -->
          <div v-if="appState === 'processing'" class="flex flex-col items-center justify-center h-full text-center">
            <p class="text-2xl font-semibold animate-pulse">正在处理文件...</p>
            <p class="text-gray-500 mt-4">这可能需要一些时间，请不要关闭页面。</p>
          </div>

          <!-- State: Done -->
          <div v-if="appState === 'done'" class="flex flex-col h-full">
            <div class="flex-grow">
              <h2 class="text-2xl font-bold mb-4 text-green-600">处理完成！</h2>
              <p class="text-gray-600 mb-6">您可以下载转换后的文件了。</p>
              <div class="space-y-4">
                <a v-if="finalResult.cmyk_pdf_filename" :href="`/download/${finalResult.upload_id}/${finalResult.cmyk_pdf_filename}`" download>
                  <Button class="w-full" variant="secondary">下载 CMYK 替换版</Button>
                </a>
                <a v-if="finalResult.final_pdf_filename" :href="`/download/${finalResult.upload_id}/${finalResult.final_pdf_filename}`" download>
                  <Button class="w-full" variant="secondary">下载印刷最终版</Button>
                </a>
              </div>
            </div>
            <div class="mt-8 space-y-4">
              <Button @click="resetApp" class="w-full text-lg py-6">处理另一个文件</Button>
            </div>
          </div>

        </div>
      </div>

      <!-- History Modal -->
      <AlertDialog :open="isHistoryOpen" @update:open="isHistoryOpen = $event">
        <AlertDialogContent class="max-w-4xl">
          <AlertDialogHeader>
            <AlertDialogTitle>处理历史记录</AlertDialogTitle>
          </AlertDialogHeader>
          <div class="max-h-[60vh] overflow-y-auto p-2">
            <HistoryTable 
              :history="history"
              :onFetchHistory="fetchHistory"
              :onClearHistory="clearHistory"
            />
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel>关闭</AlertDialogCancel>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

    </div>
  </div>
  <Toaster />
</template>
