<script setup>
import { computed } from 'vue';
// import { Input } from '@/components/ui/input'; // Temporarily remove shadcn-vue Input
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

const props = defineProps({
  colors: { type: Array, required: true },
});

const emit = defineEmits(['update:colors']);

const handleCmykChange = (index, cmykIndex, value) => {
  console.log('handleCmykChange called:', { index, cmykIndex, value });
  const newColors = JSON.parse(JSON.stringify(props.colors));
  let newValue = Number(value);

  if (isNaN(newValue)) {
    newValue = 0; 
  } else {
    newValue = Math.max(0, Math.min(100, newValue)); 
  }

  newColors[index].cmyk[cmykIndex] = newValue;
  console.log('Emitting update with newColors:', newColors);
  emit('update:colors', newColors);
};

const previewMappings = computed(() => {
  return props.colors.map(color => ({
    name: color.hex,
    rgb_255: color.rgb,
    cmyk_100: color.cmyk,
  }));
});

</script>

<template>
  <div class="space-y-4">
    <!-- Color List -->
    <div class="space-y-3 p-4">
      <div
        v-for="(color, index) in colors"
        :key="color.hex"
        class="p-4 border border-gray-200 rounded-lg"
      >
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center space-x-3">
            <div
              class="w-8 h-8 rounded-lg border border-gray-300 shadow-sm"
              :style="{ backgroundColor: color.hex }"
            ></div>
            <div>
              <div class="font-medium text-sm text-gray-900">{{ color.hex }}</div>
              <div class="text-xs text-gray-500">RGB: {{ color.rgb.join(', ') }}</div>
            </div>
          </div>
          <div class="text-xs text-gray-500">
            出现 {{ color.count }} 次
          </div>
        </div>

        <!-- CMYK Inputs -->
        <div class="space-y-2">
          <div class="grid grid-cols-4 gap-2">
            <div class="text-center">
              <label class="text-xs font-medium text-gray-600 block mb-1">C</label>
              <input
                type="number"
                min="0"
                max="100"
                :value="color.cmyk[0]"
                @input="val => handleCmykChange(index, 0, val.target.value)"
                class="w-full h-8 text-sm text-center border border-gray-300 rounded-md focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div class="text-center">
              <label class="text-xs font-medium text-gray-600 block mb-1">M</label>
              <input
                type="number"
                min="0"
                max="100"
                :value="color.cmyk[1]"
                @input="val => handleCmykChange(index, 1, val.target.value)"
                class="w-full h-8 text-sm text-center border border-gray-300 rounded-md focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div class="text-center">
              <label class="text-xs font-medium text-gray-600 block mb-1">Y</label>
              <input
                type="number"
                min="0"
                max="100"
                :value="color.cmyk[2]"
                @input="val => handleCmykChange(index, 2, val.target.value)"
                class="w-full h-8 text-sm text-center border border-gray-300 rounded-md focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div class="text-center">
              <label class="text-xs font-medium text-gray-600 block mb-1">K</label>
              <input
                type="number"
                min="0"
                max="100"
                :value="color.cmyk[3]"
                @input="val => handleCmykChange(index, 3, val.target.value)"
                class="w-full h-8 text-sm text-center border border-gray-300 rounded-md focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          <div class="text-xs text-gray-500 text-center">
            CMYK: {{ color.cmyk.join(', ') }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

