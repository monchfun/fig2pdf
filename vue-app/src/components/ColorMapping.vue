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
    <h3 class="text-lg font-semibold">编辑颜色映射</h3>
    <p class="text-sm text-gray-500">以下是从此PDF中提取出的、出现频率最高的颜色。您可以直接修改它们对应的CMYK值。</p>
    <div class="border rounded-lg overflow-hidden max-h-[45vh] overflow-y-auto">
      <Table>
        <TableHeader class="sticky top-0 bg-gray-50 z-10">
          <TableRow>
            <TableHead class="w-1/4">颜色</TableHead>
            <TableHead class="w-1/6">出现次数</TableHead>
            <TableHead class="w-1/2">CMYK (0-100)</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="(color, index) in colors" :key="color.hex">
            <TableCell>
              <div class="flex items-center gap-2">
                <div 
                  class="w-6 h-6 rounded-full border border-gray-300"
                  :style="{ backgroundColor: color.hex }"
                ></div>
                <span class="font-mono text-sm">{{ color.hex }}</span>
              </div>
            </TableCell>
            <TableCell>
              <span class="font-medium">{{ color.count }}</span>
            </TableCell>
            <TableCell>
              <div class="grid grid-cols-4 gap-2">
                <input
                  type="text" 
                  :value="color.cmyk[0]"
                  @input="val => handleCmykChange(index, 0, val.target.value)"
                  class="h-8 text-center border rounded-md px-2 w-full"
                />
                <input
                  type="text" 
                  :value="color.cmyk[1]"
                  @input="val => handleCmykChange(index, 1, val.target.value)"
                  class="h-8 text-center border rounded-md px-2 w-full"
                />
                <input
                  type="text" 
                  :value="color.cmyk[2]"
                  @input="val => handleCmykChange(index, 2, val.target.value)"
                  class="h-8 text-center border rounded-md px-2 w-full"
                />
                <input
                  type="text" 
                  :value="color.cmyk[3]"
                  @input="val => handleCmykChange(index, 3, val.target.value)"
                  class="h-8 text-center border rounded-md px-2 w-full"
                />
              </div>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  </div>
</template>

