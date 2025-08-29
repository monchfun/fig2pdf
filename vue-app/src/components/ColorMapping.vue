<script setup>
import { ref, watch } from 'vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Textarea } from '@/components/ui/textarea'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'

const props = defineProps({
  mappings: { type: Array, required: true },
})

const emit = defineEmits(['update:mappings', 'onResetToOriginalDefault', 'onSaveMapping'])

const jsonText = ref('')

// State for AlertDialog
const showAlertDialog = ref(false)
const alertDialogTitle = ref('')
const alertDialogDescription = ref('')
const alertDialogAction = ref(null) // Function to execute on confirm
const alertDialogCancelText = ref('取消')
const alertDialogConfirmText = ref('确定')

// Function to show AlertDialog
const showDialog = (title, description, onConfirm, cancelText = '取消', confirmText = '确定') => {
  alertDialogTitle.value = title
  alertDialogDescription.value = description
  alertDialogAction.value = onConfirm
  alertDialogCancelText.value = cancelText
  alertDialogConfirmText.value = confirmText
  showAlertDialog.value = true
}

// Sync JSON text from mappings prop
watch(() => props.mappings, (newMappings) => {
  jsonText.value = JSON.stringify({ mappings: newMappings }, null, 2)
}, { immediate: true, deep: true })

// Sync mappings from JSON text
const syncTableFromJson = () => {
  try {
    const data = JSON.parse(jsonText.value)
    if (data && Array.isArray(data.mappings)) {
      emit('update:mappings', data.mappings)
    } else {
      showDialog('JSON格式错误', '上传的JSON文件内容不符合预期的颜色映射格式。', null, '关闭', '确定')
    }
  } catch (e) {
    console.error("Invalid JSON:", e)
    showDialog('JSON格式错误', '上传的JSON文件格式无效，请检查。', null, '关闭', '确定')
  }
}

// Handlers for table interactions
const handleTableInputChange = (index, field, value) => {
  const newMappings = [...props.mappings]
  if (field === 'name') {
    newMappings[index].name = value
  } else if (field === 'rgb_255') {
    const rgb = value.split(',').map(Number)
    if (rgb.length === 3 && rgb.every(v => !isNaN(v) && v >= 0 && v <= 255)) {
      newMappings[index].rgb_255 = rgb
    }
  }
  emit('update:mappings', newMappings)
}

const handleDeleteColor = (index) => {
  showDialog(
    '确认删除',
    '确定要删除此颜色映射吗？此操作不可撤销。',
    () => {
      const newMappings = props.mappings.filter((_, i) => i !== index)
      emit('update:mappings', newMappings)
    },
    '取消',
    '删除'
  )
}

const handleAddNewColor = () => {
  const newMappings = [
    ...props.mappings,
    { name: '新颜色', rgb_255: [0, 0, 0], cmyk_100: [0, 0, 0, 100] },
  ]
  emit('update:mappings', newMappings)
}

const handleJsonUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target.result)
      if (data && Array.isArray(data.mappings)) {
        emit('update:mappings', data.mappings)
      }
    } catch (error) {
      showDialog('JSON文件格式错误', '上传的JSON文件格式无效，请检查。', null, '关闭', '确定')
    }
  }
  reader.readAsText(file)
}

const resetToOriginalDefault = () => {
  showDialog(
    '重置确认',
    '确定要重置为原始默认颜色映射吗？所有当前修改将丢失。',
    () => {
      emit('onResetToOriginalDefault') // Emit event instead of calling prop
    },
    '取消',
    '重置'
  )
}

const saveMapping = () => {
  showDialog(
    '保存确认',
    '确定要将当前颜色映射保存为默认配置吗？这将覆盖之前的默认设置。',
    () => {
      emit('onSaveMapping') // Emit event instead of calling prop
    },
    '取消',
    '保存'
  )
}
</script>

<template>
  <Card class="w-full max-w-4xl mx-auto">
    <CardHeader>
      <CardTitle>步骤 2: 配置颜色映射</CardTitle>
    </CardHeader>
    <CardContent class="space-y-6">
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <h3 class="text-lg font-semibold text-gray-800">颜色映射配置</h3>
        <div class="flex flex-wrap gap-2">
          <Button variant="outline" @click="resetToOriginalDefault">重置为默认</Button>
          <Button variant="outline" @click="saveMapping">保存为默认</Button>
          <Button @click="handleAddNewColor">➕ 添加颜色</Button>
        </div>
      </div>

      <div>
        <Label for="json-upload">上传自定义JSON文件 (可选)</Label>
        <Input id="json-upload" type="file" accept=".json" class="mt-2" @change="handleJsonUpload" />
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <!-- Table View -->
        <div class="space-y-3">
          <h4 class="text-sm font-semibold text-gray-700">映射表格</h4>
          <div class="border rounded-xl overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>颜色名称</TableHead>
                  <TableHead>RGB</TableHead>
                  <TableHead>CMYK</TableHead>
                  <TableHead>操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="(mapping, index) in mappings" :key="index">
                  <TableCell>
                    <Input
                      type="text"
                      :model-value="mapping.name"
                      @update:model-value="(value) => handleTableInputChange(index, 'name', value)"
                      class="h-8"
                    />
                  </TableCell>
                  <TableCell>
                    <Input
                      type="text"
                      :model-value="mapping.rgb_255.join(', ')"
                      @update:model-value="(value) => handleTableInputChange(index, 'rgb_255', value)"
                      class="h-8"
                    />
                  </TableCell>
                  <TableCell>
                    <Input
                      type="text"
                      :model-value="mapping.cmyk_100.join(', ')"
                      @update:model-value="(value) => handleTableInputChange(index, 'cmyk_100', value)"
                      class="h-8"
                    />
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="destructive"
                      size="sm"
                      @click="() => handleDeleteColor(index)"
                    >
                      删除
                    </Button>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </div>

        <!-- JSON View -->
        <div class="space-y-3">
          <h4 class="text-sm font-semibold text-gray-700">JSON配置</h4>
          <Textarea
            class="w-full h-64 font-mono text-sm"
            placeholder="JSON配置将在这里显示..."
            :model-value="jsonText"
            @update:model-value="jsonText = $event; syncTableFromJson()"
          />
        </div>
      </div>
    </CardContent>
  </Card>

  <!-- AlertDialog Component -->
  <AlertDialog :open="showAlertDialog" @update:open="showAlertDialog = $event">
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>{{ alertDialogTitle }}</AlertDialogTitle>
        <AlertDialogDescription>{{ alertDialogDescription }}</AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel @click="showAlertDialog = false">{{ alertDialogCancelText }}</AlertDialogCancel>
        <AlertDialogAction @click="alertDialogAction && alertDialogAction(); showAlertDialog = false;">
          {{ alertDialogConfirmText }}
        </AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
</template>