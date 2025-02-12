<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import Chart from 'chart.js/auto'

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

  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: props.data.dates,
      datasets: [
        {
          label: '历史价格',
          data: props.data.prices,
          borderColor: '#4CAF50',
          tension: 0.1,
          fill: false
        },
        ...(props.data.predictions ? [{
          label: '预测价格',
          data: props.data.predictions,
          borderColor: '#2196F3',
          borderDash: [5, 5],
          tension: 0.1,
          fill: false
        }] : [])
      ]
    },
    options: {
      responsive: true,
      interaction: {
        intersect: false,
        mode: 'index'
      },
      scales: {
        y: {
          beginAtZero: false
        }
      }
    }
  })
}

onMounted(() => {
  createChart()
})

watch(() => props.data, () => {
  if (chart) {
    chart.destroy()
  }
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
  height: 300px;
  margin: 1rem 0;
}
</style> 