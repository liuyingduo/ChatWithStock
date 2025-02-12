export interface Message {
  role: 'user' | 'assistant'
  content: string
  data?: {
    chartData?: {
      dates: string[]
      prices: number[]
      volumes: number[]
      predictions?: number[]
    }
    metrics?: Array<{
      name: string
      value: string | number
      change?: number
      description?: string
    }>
  }
}

export interface StockData {
  symbol: string
  name: string
  price: number
  change: number
  change_percent: number
} 