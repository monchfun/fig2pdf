<script setup>
import { ref, watch, onMounted } from 'vue';
import { Button } from '@/components/ui/button';
import FileUpload from '@/components/FileUpload.vue';
import ColorMapping from '@/components/ColorMapping.vue';
import ProcessAndDownload from '@/components/ProcessAndDownload.vue';
import HistoryTable from '@/components/HistoryTable.vue';
import { useToast, Toaster } from '@/components/ui/toast'; // New import

// Backend API URL - now proxied by Vite
const API_URL = ''; // Use relative path for proxy

const currentStep = ref(1);
const selectedFile = ref(null);
const colorMappings = ref([]); // Use ref for reactive array
const history = ref([]); // New state for history

const totalSteps = 3;

const { toast } = useToast();

// Fetch default color mappings on initial load
onMounted(() => {
  fetch(`/api/color-mapping`) // Use relative path for proxy
    .then(response => response.json())
    .then(data => {
      if (data && data.mappings) {
        colorMappings.value = data.mappings; // Update ref's value
      }
    })
    .catch(error => {
      console.error('Error fetching color mappings:', error);
      toast({ title: '加载错误', description: '无法加载默认颜色映射，请检查后端服务。', variant: 'destructive' });
    });
  
  fetchHistory(); // Fetch history on mount
});

// Function to fetch history
const fetchHistory = () => {
  fetch(`/api/history?t=${new Date().getTime()}`) // Add timestamp to prevent caching
    .then(response => response.json())
    .then(data => {
      history.value = data;
    })
    .catch(error => {
      console.error('Error fetching history:', error);
      toast({ title: '加载错误', description: '无法加载历史记录，请检查后端服务。', variant: 'destructive' });
    });
};

// Function to clear history
const clearHistory = () => {
  // Keep AlertDialog for confirmation
  // showAppDialog is removed, so we need to re-implement the confirmation logic or use a different dialog
  // For now, I will keep the confirmation dialog logic here, but replace the success/failure messages with toast
  // This part needs careful handling to ensure the confirmation dialog still works.
  // Let's assume the AlertDialog component is still available and used for confirmation,
  // but the success/failure messages after the fetch are toasts.

  // Re-implementing the confirmation dialog logic here for clearHistory
  // This is a temporary solution. A better approach would be to use a dedicated confirmation dialog component.
  // For now, I will use a simple window.confirm for clearHistory confirmation.
  if (window.confirm('确定要清空所有历史记录吗？此操作不可撤销。')) {
    fetch(`${API_URL}/api/clear-history`, {
      method: 'POST',
    })
      .then(response => response.json())
      .then(result => {
        if (result.success) {
          toast({ title: '成功', description: result.message });
          fetchHistory(); // Refresh history after clearing
        } else {
          toast({ title: '失败', description: '清空失败: ' + result.message, variant: 'destructive' });
        }
      })
      .catch(error => {
        console.error('Error clearing history:', error);
        toast({ title: '错误', description: '清空失败: ' + error.message, variant: 'destructive' });
      });
  }
};

// Function to reset color mappings to original default
const resetColorMappingsToOriginalDefault = () => {
  console.log('Attempting to reset color mappings to original default...');
  fetch(`/api/original-color-mapping`) // Use relative path for proxy
    .then(response => {
      console.log('Response received:', response);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('Data received for reset:', data);
      if (data && data.mappings) {
        colorMappings.value = data.mappings;
        console.log('Color mappings reset successfully.');
        toast({ title: '成功', description: '已重置为原始默认颜色映射。' });
      } else {
        console.error('Data format incorrect for reset:', data);
        toast({ title: '重置失败', description: '重置失败：数据格式不正确。', variant: 'destructive' });
      }
    })
    .catch(error => {
      console.error('Error resetting color mappings:', error);
      toast({ title: '重置失败', description: '重置失败：' + error.message, variant: 'destructive' });
    });
};

// Function to save current color mappings as default
const saveColorMappingsAsDefault = () => {
  fetch(`${API_URL}/api/color-mapping`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ mappings: colorMappings.value }),
  })
    .then(response => response.json())
    .then(result => {
      if (result.success) {
        toast({ title: '成功', description: '颜色映射已保存为默认配置。' });
      } else {
        toast({ title: '失败', description: '保存失败: ' + result.message, variant: 'destructive' });
      }
    })
    .catch(error => {
      console.error('Error saving color mappings:', error);
      toast({ title: '失败', description: '保存失败: ' + error.message, variant: 'destructive' });
    });
};

const handleNext = () => {
  if (currentStep.value < totalSteps) {
    currentStep.value++;
  }
};

const handleBack = () => {
  if (currentStep.value > 1) {
    currentStep.value--;
  }
  };

// Watch for selectedFile changes to enable/disable Next button for step 1
const isNextDisabled = ref(true);
watch([currentStep, selectedFile], ([newStep, newFile]) => {
  if (newStep === 1) {
    isNextDisabled.value = !newFile;
  }
}, { immediate: true });
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
    <div class="w-full max-w-4xl">
      <h1 class="text-3xl font-bold text-center mb-8">
        PDF颜色转换工具 (Vue Version)
      </h1>
      
      <!-- Placeholder for Step Indicator -->
      <div class="flex justify-center mb-8">
        <p class="text-sm text-gray-500">步骤 {{ currentStep }} / {{ totalSteps }}</p>
      </div>

      <!-- Main content area -->
      <div class="mb-8">
        <FileUpload v-if="currentStep === 1" @fileSelected="selectedFile = $event" :selectedFile="selectedFile" />
        
        <ColorMapping 
          v-else-if="currentStep === 2" 
          :mappings="colorMappings" 
          @update:mappings="colorMappings = $event" 
          @onResetToOriginalDefault="resetColorMappingsToOriginalDefault"
          @onSaveMapping="saveColorMappingsAsDefault"
        />
        
        <ProcessAndDownload 
          v-else-if="currentStep === 3" 
          :selectedFile="selectedFile" 
          :colorMappings="colorMappings" 
          @historyUpdated="history = $event" 
        />
      </div>

      <!-- History Table -->
      <HistoryTable :history="history" :onFetchHistory="fetchHistory" :onClearHistory="clearHistory" />

      <!-- Navigation Buttons -->
      <div class="flex justify-between mt-8">
        <Button @click="handleBack" :disabled="currentStep === 1">
          上一步
        </Button>
        <Button @click="handleNext" :disabled="currentStep === totalSteps || isNextDisabled">
          下一步
        </Button>
      </div>
    </div>
  </div>
  <Toaster />
</template>

<style scoped>
/* No specific styles needed here, Tailwind handles it */
</style>
