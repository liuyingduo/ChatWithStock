<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import Chart from 'chart.js/auto'
import { CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js'

// 注册Chart.js组件
Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const props = defineProps<{
  data: {
    dates: string[]
    prices: number[]
    volumes: number[]
    predictions?: number[]
  }
}>()

const chartRef = ref<HTMLCanvasElement | null>(null)
let chart: Chart | null = null

const createChart = () => {
  if (!chartRef.value) return

  const ctx = chartRef.value.getContext('2d')
  if (!ctx) return

  // 销毁现有图表
  if (chart) {
    chart.destroy()
  }

  // 创建渐变填充
  const gradient = ctx.createLinearGradient(0, 0, 0, 400)
  gradient.addColorStop(0, 'rgba(76, 175, 80, 0.3)')
  gradient.addColorStop(1, 'rgba(76, 175, 80, 0.0)')

  const predictionGradient = ctx.createLinearGradient(0, 0, 0, 400)
  predictionGradient.addColorStop(0, 'rgba(33, 150, 243, 0.2)')
  predictionGradient.addColorStop(1, 'rgba(33, 150, 243, 0.0)')

  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: props.data.dates,
      datasets: [
        {
          label: '历史价格',
          data: props.data.prices,
          borderColor: '#4CAF50',
          backgroundColor: gradient,
          tension: 0.3,
          fill: true,
          pointRadius: 3,
          pointHoverRadius: 6,
          pointBackgroundColor: '#4CAF50',
          pointBorderColor: '#fff',
          pointBorderWidth: 2
        },
        ...(props.data.predictions ? [{
          label: '预测价格',
          data: props.data.predictions,
          borderColor: '#2196F3',
          backgroundColor: predictionGradient,
          borderDash: [5, 5],
          tension: 0.3,
          fill: true,
          pointRadius: 2,
          pointHoverRadius: 5,
          pointBackgroundColor: '#2196F3',
          pointBorderColor: '#fff',
          pointBorderWidth: 2
        }] : [])
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        intersect: false,
        mode: 'index'
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: '#fff',
            font: {
              size: 12
            },
            usePointStyle: true,
            pointStyle: 'circle'
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          titleColor: '#fff',
          bodyColor: '#fff',
          borderColor: 'rgba(255, 255, 255, 0.2)',
          borderWidth: 1,
          padding: 10,
          displayColors: true,
          callbacks: {
            label: function(context) {
              return `${context.dataset.label}: ¥${context.parsed.y.toFixed(2)}`
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            color: 'rgba(255, 255, 255, 0.1)'
          },
          ticks: {
            color: 'rgba(255, 255, 255, 0.7)',
            maxRotation: 45,
            minRotation: 45
          }
        },
        y: {
          beginAtZero: false,
          grid: {
            color: 'rgba(255, 255, 255, 0.1)'
          },
          ticks: {
            color: 'rgba(255, 255, 255, 0.7)',
            callback: function(value) {
              return '¥' + value
            }
          }
        }
      },
      animation: {
        duration: 1500,
        easing: 'easeOutQuart'
      }
    }
  })
}

// 处理窗口大小变化
const handleResize = () => {
  if (chart) {
    chart.resize()
  }
}

onMounted(() => {
  createChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chart) {
    chart.destroy()
  }
})

watch(() => props.data, () => {
  createChart()
}, { deep: true })
</script>

<template>
  <div class="stock-chart">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<style scoped>
.stock-chart {
  width: 100%;
  height: 400px;
  margin: 1.5rem 0;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.stock-chart:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .stock-chart {
    height: 300px;
  }
}
</style> 