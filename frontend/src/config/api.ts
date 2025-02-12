// API 基础配置
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  // 可以添加其他 API 相关的配置
}

// API 路径
export const API_ROUTES = {
  // 在这里定义所有的 API 路径
  STOCKS: '/api/stocks',
  METRICS: '/api/metrics',
  // ... 其他路径
}

// 获取完整的 API URL
export const getApiUrl = (path: string): string => {
  return `${API_CONFIG.BASE_URL}${path}`
} 