import { ref, onUnmounted } from 'vue'

const TOAST_LIMIT = 1
const TOAST_REMOVE_DELAY = 1000000 // Keep toasts visible for now

const toasts = ref([])
let count = 0

function genId() {
  count = (count + 1) % Number.MAX_VALUE
  return count
}

function addToasts(props) {
  const id = genId()
  const toast = { id, ...props }
  toasts.value = [toast, ...toasts.value].slice(0, TOAST_LIMIT)
  return toast
}

function dismissToast(id) {
  toasts.value = toasts.value.filter(toast => toast.id !== id)
}

export function useToast() {
  const toast = (props) => {
    const newToast = addToasts(props)
    setTimeout(() => dismissToast(newToast.id), TOAST_REMOVE_DELAY)
    return newToast
  }

  onUnmounted(() => {
    // Clear all toasts when component unmounts (optional, depending on desired behavior)
    toasts.value = []
  })

  return {
    toasts,
    toast,
    dismiss: dismissToast,
  }
}
