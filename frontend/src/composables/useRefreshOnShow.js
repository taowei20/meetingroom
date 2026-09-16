import { onMounted, onUnmounted } from 'vue'

export function useRefreshOnShow(callback) {
  const handler = () => {
    if (document.visibilityState === 'visible') {
      callback()
    }
  }
  onMounted(() => {
    document.addEventListener('visibilitychange', handler)
  })
  onUnmounted(() => {
    document.removeEventListener('visibilitychange', handler)
  })
}