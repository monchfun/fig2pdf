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
const isSidebarOpen = ref(true);

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
  <div class="h-screen bg-white flex flex-col">
    <!-- Header -->
    <header class="h-16 border-b border-gray-200 flex items-center justify-between px-6 bg-white">
      <div class="flex items-center space-x-4">
        <h1 class="text-xl font-semibold text-gray-900">PDF 颜色转换工作台</h1>
        <span class="text-sm text-gray-500">Figma PDF 到印刷级 CMYK 转换器</span>
      </div>
      <div class="flex items-center space-x-3">
        <Button variant="outline" size="sm" @click="isHistoryOpen = true">
          历史记录
        </Button>
        <Button v-if="appState !== 'initial'" variant="outline" size="sm" @click="resetApp">
          新建文件
        </Button>
        <Button
          v-if="appState !== 'initial'"
          variant="outline"
          size="sm"
          @click="isSidebarOpen = !isSidebarOpen"
          class="lg:hidden"
        >
          {{ isSidebarOpen ? '隐藏工具栏' : '显示工具栏' }}
        </Button>
      </div>
    </header>

    <!-- Main Content Area -->
    <div class="flex-1 flex overflow-hidden">

      <!-- Initial State: Full screen upload -->
      <div v-if="appState === 'initial'" class="flex-1 flex items-center justify-center bg-gray-50">
        <div class="max-w-lg w-full mx-auto">
          <div class="text-center mb-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-2">开始转换 PDF</h2>
            <p class="text-gray-600">上传您的 PDF 文件以开始颜色转换流程</p>
          </div>
          <FileUpload @fileSelected="handleFileSelect" />
        </div>
      </div>

      <!-- Analyzing State -->
      <div v-if="appState === 'analyzing'" class="flex-1 flex items-center justify-center bg-gray-50">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p class="text-xl font-semibold text-gray-900">正在分析 PDF 颜色</p>
          <p class="text-gray-500 mt-2">{{ selectedFile?.name }}</p>
        </div>
      </div>

      <!-- Workspace Layout -->
      <div v-if="appState === 'file_ready' || appState === 'processing' || appState === 'done'" class="flex-1 flex">

        <!-- Left Panel: PDF Preview (Full screen) -->
        <div class="flex-1 flex flex-col bg-gray-50">
          <div class="h-12 border-b border-gray-200 px-4 flex items-center justify-between bg-white">
            <h2 class="font-medium text-gray-900">PDF 预览</h2>
            <div class="text-sm text-gray-500">
              {{ selectedFile?.name }}
            </div>
          </div>
          <div class="flex-1 overflow-hidden">
            <PdfPreview
              :key="selectedFile.name"
              :pdf-file="selectedFile"
              :show-color-preview="appState === 'file_ready'"
              :color-mappings="previewMappings"
              class="h-full w-full"
            />
          </div>
        </div>

        <!-- Right Panel: Tools & Configuration -->
        <div
          v-show="isSidebarOpen"
          class="w-80 lg:w-96 bg-white border-l border-gray-200 flex flex-col fixed lg:relative right-0 top-0 h-full z-20 lg:z-auto shadow-lg lg:shadow-none"
        >

          <!-- File Ready State -->
          <div v-if="appState === 'file_ready'" class="flex-1 flex flex-col min-h-0">
            <div class="p-4 border-b border-gray-200">
              <h3 class="font-medium text-gray-900 mb-1">颜色映射配置</h3>
              <p class="text-sm text-gray-500">调整 RGB 到 CMYK 的颜色映射</p>
            </div>
            <div class="flex-1 overflow-y-auto">
              <ColorMapping
                v-if="uniqueColors.length > 0"
                :colors="uniqueColors"
                @update:colors="uniqueColors = $event"
              />
              <div v-else class="p-8 text-center text-gray-500">
                <p>未在此 PDF 中提取到可识别的颜色</p>
              </div>
            </div>

            <div class="p-4 border-t border-gray-200 space-y-3">
              <div class="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="convertText"
                  v-model="convertTextToCurves"
                  class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-600"
                />
                <label for="convertText" class="text-sm font-medium text-gray-700">
                  文字转曲线 (用于印刷)
                </label>
              </div>
              <Button @click="handleProcessRequest" class="w-full">
                开始转换
              </Button>
            </div>
          </div>

          <!-- Processing State -->
          <div v-if="appState === 'processing'" class="flex-1 flex flex-col items-center justify-center p-8 text-center">
            <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mb-6"></div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">正在处理文件</h3>
            <p class="text-gray-500 text-sm">这可能需要一些时间，请不要关闭页面</p>
          </div>

          <!-- Done State -->
          <div v-if="appState === 'done'" class="flex-1 flex flex-col">
            <div class="p-4 border-b border-gray-200">
              <h3 class="font-medium text-gray-900 mb-1">处理完成</h3>
              <p class="text-sm text-gray-500">下载转换后的文件</p>
            </div>

            <div class="flex-1 p-4">
              <div class="space-y-3">
                <div class="p-4 bg-green-50 rounded-lg border border-green-200">
                  <div class="flex items-center space-x-2 mb-2">
                    <div class="h-2 w-2 bg-green-600 rounded-full"></div>
                    <span class="text-sm font-medium text-green-900">转换成功</span>
                  </div>
                  <p class="text-sm text-green-700">您的 PDF 已成功转换为 CMYK 格式</p>
                </div>

                <div class="space-y-2">
                  <a v-if="finalResult.cmyk_pdf_filename" :href="`/download/${finalResult.upload_id}/${finalResult.cmyk_pdf_filename}`" download>
                    <Button class="w-full justify-start" variant="outline">
                      <span class="flex-1 text-left">下载 CMYK 替换版</span>
                    </Button>
                  </a>
                  <a v-if="finalResult.final_pdf_filename" :href="`/download/${finalResult.upload_id}/${finalResult.final_pdf_filename}`" download>
                    <Button class="w-full justify-start" variant="outline">
                      <span class="flex-1 text-left">下载印刷最终版</span>
                    </Button>
                  </a>
                </div>
              </div>
            </div>

            <div class="p-4 border-t border-gray-200">
              <Button @click="resetApp" variant="outline" class="w-full">
                处理另一个文件
              </Button>
            </div>
          </div>

        </div>

        <!-- Mobile Sidebar Overlay -->
        <div
          v-if="isSidebarOpen && appState !== 'initial'"
          class="fixed inset-0 bg-black bg-opacity-50 z-10 lg:hidden"
          @click="isSidebarOpen = false"
        ></div>
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
  <Toaster />
</template>
