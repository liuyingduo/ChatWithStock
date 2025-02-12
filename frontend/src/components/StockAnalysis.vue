<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted, nextTick, watch } from 'vue'
import StockMetrics from '@/components/StockMetrics.vue'
import * as echarts from 'echarts'
import { getApiUrl } from '@/config/api'

interface Metric {
  name: string
  value: string | number
  description: string
  change?: number
}

const props = defineProps<{
  symbol: string
  startDate: string
}>()

const emit = defineEmits<{
  (e: 'analysis-complete'): void
  (e: 'analysis-error', message: string): void
}>()

interface StockData {
  total_return: number
  volatility: number
  sharp_ratio: number
  max_drawdown: number
  sudden_changes: Array<{
    date: string
    change: number
    price: number
  }>
  daily_stats: Array<{
    date: string
    close: number
    volume: number
    change: number
  }>
}

const stockData = ref<Partial<StockData>>({})
const chartRef = ref<HTMLElement | null>(null)
const chart = ref<echarts.ECharts | null>(null)

const loadingStates = ref({
  basicMetrics: false,
  priceChart: false,
  suddenChanges: false
})

const metrics = computed(() => [
  {
    name: '总收益率',
    value: stockData.value?.total_return ? `${stockData.value.total_return}%` : '-',
    change: stockData.value?.total_return,
    description: '投资期间的总体收益表现'
  },
  {
    name: '年化波动率',
    value: stockData.value?.volatility ? `${stockData.value.volatility}%` : '-',
    description: '反映价格波动的剧烈程度'
  },
  {
    name: '夏普比率',
    value: stockData.value?.sharp_ratio ?? '-',
    description: '每承担一单位风险所获得的超额收益'
  },
  {
    name: '最大回撤',
    value: stockData.value?.max_drawdown ? `${stockData.value.max_drawdown}%` : '-',
    change: stockData.value?.max_drawdown,
    description: '最大亏损幅度'
  }
] as Metric[])

const initChart = async () => {
  try {
    await nextTick()
    if (!chartRef.value) {
      console.warn('Chart container not found')
      return false
    }

    // 如果已经存在 chart 实例，先销毁
    if (chart.value) {
      chart.value.dispose()
    }

    // 创建新的 chart 实例
    chart.value = echarts.init(chartRef.value)
    
    // 返回 resize 处理函数
    return () => chart.value?.resize()
  } catch (error) {
    console.error('Failed to initialize chart:', error)
    return false
  }
}

const updateChart = async (data: any) => {
  try {
    if (!data?.daily_stats?.length) {
      console.warn('No daily stats data available for chart')
      return
    }

    if (!chart.value) {
      console.warn('Chart not initialized')
      await initChart() // 尝试重新初始化
      if (!chart.value) return // 如果还是失败就退出
    }

    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        },
        formatter: (params: any) => {
          const data = params[0].data
          return `日期：${params[0].axisValue}<br/>
                 价格：${data.toFixed(2)}<br/>`
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: data.daily_stats.map((item: any) => item.date),
        axisLine: {
          lineStyle: {
            color: '#fff'
          }
        }
      },
      yAxis: {
        type: 'value',
        axisLine: {
          lineStyle: {
            color: '#fff'
          }
        },
        splitLine: {
          lineStyle: {
            color: 'rgba(255, 255, 255, 0.1)'
          }
        }
      },
      series: [
        {
          name: '收盘价',
          type: 'line',
          data: data.daily_stats.map((item: any) => item.close),
          itemStyle: {
            color: '#42b983'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {
                offset: 0,
                color: 'rgba(66, 185, 131, 0.3)'
              },
              {
                offset: 1,
                color: 'rgba(66, 185, 131, 0.1)'
              }
            ])
          },
          smooth: true
        }
      ]
    }

    chart.value.setOption(option, true)
  } catch (error) {
    console.error('Error updating chart:', error)
    throw error
  }
}

const fetchBasicMetrics = async () => {
  try {
    const url = getApiUrl(`/api/stock/analysis/${props.symbol}/basic`)
    const response = await fetch(url + `?start_date=${props.startDate}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    console.log('Basic metrics data:', data)
    stockData.value = { ...stockData.value, ...data }
    loadingStates.value.basicMetrics = false
  } catch (error) {
    console.error('Error fetching basic metrics:', error)
    emit('analysis-error', '获取基础指标失败')
  }
}

const fetchPriceData = async () => {
  try {
    const url = getApiUrl(`/api/stock/analysis/${props.symbol}/price`)
    const response = await fetch(url + `?start_date=${props.startDate}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    console.log('Price data:', data)
    
    if (!data?.daily_stats?.length) {
      throw new Error('No price data available')
    }

    // 更新数据
    stockData.value.daily_stats = data.daily_stats
    
    // 确保容器已经渲染
    await nextTick()
    
    // 更新图表
    await updateChart(data)
    
    // 最后更新加载状态
    loadingStates.value.priceChart = false
    
    console.log('Price chart updated successfully')
  } catch (error) {
    console.error('Error fetching price data:', error)
    emit('analysis-error', '获取价格数据失败')
    loadingStates.value.priceChart = false
  }
}

const fetchSuddenChanges = async () => {
  try {
    const url = getApiUrl(`/api/stock/analysis/${props.symbol}/changes`)
    const response = await fetch(url + `?start_date=${props.startDate}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    console.log('Sudden changes data:', data)
    stockData.value.sudden_changes = data.sudden_changes
    loadingStates.value.suddenChanges = false
  } catch (error) {
    console.error('Error fetching sudden changes:', error)
    emit('analysis-error', '获取突变点数据失败')
  }
}

const isVisible = ref(true)

// Add visibility change handler
const handleVisibilityChange = () => {
  isVisible.value = document.visibilityState === 'visible'
}

// 移除 watch，改为方法调用
const startAnalysis = () => {
  if (!props.symbol) return

  // 重置加载状态
  loadingStates.value = {
    basicMetrics: true,
    priceChart: true,
    suddenChanges: true
  }
  
  // 重置数据
  stockData.value = {}
  
  fetchBasicMetrics()
    .then(() => fetchPriceData())
    .then(() => fetchSuddenChanges())
    .then(() => {
      emit('analysis-complete')
    })
    .catch((error) => {
      console.error('Error during data loading:', error)
      emit('analysis-error', '数据加载失败')
    })
}

let resizeHandler: (() => void) | null = null

onMounted(async () => {
  // 添加可见性变化监听器
  document.addEventListener('visibilitychange', handleVisibilityChange)
  
  // 初始化图表并保存 resize 处理函数
  resizeHandler = await initChart()
})

onUnmounted(() => {
  // 清理可见性监听器
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  
  // 清理 resize 事件监听器
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
  }
  
  // 销毁图表
  if (chart.value) {
    chart.value.dispose()
    chart.value = null
  }
})

defineExpose({
  startAnalysis
})
</script>

<template>
  <div class="stock-analysis">
    <h2>{{ symbol }} 股票分析</h2>
    
    <!-- 只在有数据时显示内容 -->
    <template v-if="Object.keys(stockData).length > 0 || loadingStates.basicMetrics">
      <div class="metrics-section">
        <div v-if="loadingStates.basicMetrics" class="loading-indicator">
          <i class="fas fa-spinner fa-spin"></i> 加载基础指标...
        </div>
        <StockMetrics v-else :metrics="metrics" />
      </div>
      
      <div class="chart-section">
        <template v-if="loadingStates.priceChart">
          <div class="loading-indicator">
            <i class="fas fa-spinner fa-spin"></i> 加载价格数据...
          </div>
        </template>
        <div 
          ref="chartRef" 
          class="chart-container"
        ></div>
      </div>
      
      <div class="sudden-changes">
        <div v-if="loadingStates.suddenChanges" class="loading-indicator">
          <i class="fas fa-spinner fa-spin"></i> 分析价格突变...
        </div>
        <template v-else-if="stockData.sudden_changes?.length">
          <h3>重要价格变动</h3>
          <div class="changes-list">
            <div
              v-for="change in stockData.sudden_changes"
              :key="change.date"
              class="change-item"
              :class="{ positive: change.change > 0, negative: change.change < 0 }"
            >
              <span class="date">{{ change.date }}</span>
              <span class="change">{{ change.change }}%</span>
              <span class="price">¥{{ change.price }}</span>
            </div>
          </div>
        </template>
      </div>
    </template>
  </div>
</template>

<style scoped>
.stock-analysis {
  padding: 1rem;
}

.chart-container {
  width: 100%;
  height: 400px;
  margin: 2rem 0;
  background: rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.sudden-changes {
  margin-top: 2rem;
}

.changes-list {
  display: grid;
  gap: 0.5rem;
}

.change-item {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  padding: 0.5rem;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
}

.positive {
  color: #4CAF50;
}

.negative {
  color: #F44336;
}

.loading-indicator {
  text-align: center;
  padding: 2rem;
  color: var(--accent-color);
}

.loading-indicator i {
  margin-right: 0.5rem;
}

.metrics-section,
.chart-section,
.sudden-changes {
  margin-bottom: 2rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}
</style> 