const MOBILE_BREAKPOINT = 768

function getViewportWidth() {
  // 优先用视觉视口（visualViewport），它反映真实可见宽度，比 innerWidth 更可靠
  if (window.visualViewport && typeof window.visualViewport.width === 'number') {
    return window.visualViewport.width
  }
  return window.innerWidth
}

function isTouchDevice() {
  return window.matchMedia('(pointer: coarse)').matches ||
    (navigator.maxTouchPoints || 0) > 1
}

export function isMobile() {
  // 核心：按视觉视口宽度判断（修复高DPI安卓机上 innerWidth 被错误放大的问题）
  const width = getViewportWidth()
  if (width < MOBILE_BREAKPOINT) return true

  // 兜底：窄屏 + 触屏设备（防止布局视口异常时误判为桌面）
  if (window.innerWidth < MOBILE_BREAKPOINT) return true
  if (window.innerWidth > 900 && isTouchDevice() && window.innerWidth < 600) return true

  return false
}

export function isStandalone() {
  return window.matchMedia('(display-mode: standalone)').matches ||
    window.navigator.standalone === true
}

export function onResize(callback) {
  const listener = () => callback(isMobile())
  window.addEventListener('resize', listener)
  if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', listener)
  }
}