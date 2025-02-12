<script setup lang="ts">
import { API_ROUTES, getApiUrl } from '@/config/api'

interface Metric {
  name: string
  value: string | number
  change?: number
  description?: string
}

const props = defineProps<{
  metrics: Metric[]
}>()

const getValueClass = (metric: Metric) => {
  if (metric.change === undefined) return ''
  return metric.change > 0 ? 'positive' : metric.change < 0 ? 'negative' : ''
}

const fetchMetrics = async () => {
  try {
    const response = await fetch(getApiUrl(API_ROUTES.METRICS))
    const data = await response.json()
    // 处理数据...
  } catch (error) {
    console.error('Error fetching metrics:', error)
  }
}
</script>

<template>
  <div class="stock-metrics">
    <div v-for="metric in metrics" :key="metric.name" class="metric-card">
      <div class="metric-name">{{ metric.name }}</div>
      <div class="metric-value" :class="getValueClass(metric)">
        {{ metric.value }}
      </div>
      <div class="metric-description" v-if="metric.description">
        {{ metric.description }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.stock-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.metric-card {
  background: rgba(255, 255, 255, 0.1);
  padding: 1rem;
  border-radius: 10px;
  text-align: center;
}

.metric-name {
  font-size: 0.9rem;
  opacity: 0.8;
}

.metric-value {
  font-size: 1.2rem;
  font-weight: bold;
  margin: 0.5rem 0;
}

.metric-value.positive {
  color: #4CAF50;
}

.metric-value.negative {
  color: #F44336;
}

.metric-description {
  font-size: 0.8rem;
  opacity: 0.7;
}
</style> 