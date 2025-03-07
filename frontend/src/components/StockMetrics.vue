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

const getChangeIcon = (metric: Metric) => {
  if (metric.change === undefined) return ''
  return metric.change > 0 ? 'fa-arrow-up' : metric.change < 0 ? 'fa-arrow-down' : ''
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
    <div 
      v-for="(metric, index) in metrics" 
      :key="metric.name" 
      class="metric-card"
      :style="{ animationDelay: `${index * 0.1}s` }"
    >
      <div class="metric-header">
        <div class="metric-name">{{ metric.name }}</div>
        <i v-if="metric.change !== undefined" 
           :class="['fas', getChangeIcon(metric)]" 
           class="change-icon"></i>
      </div>
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
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.2rem;
  margin: 1rem 0;
}

.metric-card {
  background: rgba(255, 255, 255, 0.08);
  padding: 1.2rem;
  border-radius: 12px;
  text-align: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
  transform: translateY(20px);
  position: relative;
  overflow: hidden;
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
  opacity: 0.7;
}

.metric-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  background: rgba(255, 255, 255, 0.12);
}

.metric-header {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.metric-name {
  font-size: 1rem;
  opacity: 0.9;
  font-weight: 500;
}

.change-icon {
  font-size: 0.8rem;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0.8rem 0;
  transition: all 0.3s ease;
}

.metric-value.positive {
  color: #4CAF50;
}

.metric-value.negative {
  color: #F44336;
}

.metric-description {
  font-size: 0.85rem;
  opacity: 0.7;
  line-height: 1.4;
  margin-top: 0.8rem;
}

.positive .change-icon {
  color: #4CAF50;
}

.negative .change-icon {
  color: #F44336;
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .stock-metrics {
    grid-template-columns: 1fr;
  }
}
</style> 