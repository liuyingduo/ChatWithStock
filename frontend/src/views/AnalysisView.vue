<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import StockAnalysis from '@/components/StockAnalysis.vue'

const stockSymbol = ref('')
const startDate = ref('')
const isAnalyzing = ref(false)
const showResults = ref(false)
const errorMessage = ref('')
const analysisRef = ref<InstanceType<typeof StockAnalysis> | null>(null)

// 设置默认日期为一年前
const defaultStartDate = () => {
  const date = new Date()
  date.setFullYear(date.getFullYear() - 1)
  return date.toISOString().split('T')[0]
}

// 初始化日期
startDate.value = defaultStartDate()

const isValidSymbol = computed(() => {
  // 简单的股票代码验证：6位数字
  return /^\d{6}$/.test(stockSymbol.value)
})

const handleAnalyze = () => {
  if (!isValidSymbol.value) {
    errorMessage.value = '请输入正确的股票代码（6位数字）'
    return
  }
  
  errorMessage.value = ''
  isAnalyzing.value = true
  showResults.value = true
  
  nextTick(() => {
    if (analysisRef.value) {
      analysisRef.value.startAnalysis()
    }
  })
}
</script>

<template>
  <div class="analysis-view glass-effect">
    <div class="input-section">
      <h2>股票分析</h2>
      <div class="input-group">
        <input
          v-model="stockSymbol"
          type="text"
          placeholder="请输入股票代码（如：000001）"
          :class="{ 'error': errorMessage }"
          @keyup.enter="handleAnalyze"
        >
        <input
          v-model="startDate"
          type="date"
          :max="new Date().toISOString().split('T')[0]"
        >
        <button
          @click="handleAnalyze"
          :disabled="!isValidSymbol || isAnalyzing"
          class="analyze-btn"
        >
          <i class="fas fa-chart-line"></i>
          {{ isAnalyzing ? '分析中...' : '开始分析' }}
        </button>
      </div>
      <p class="error-message" v-if="errorMessage">{{ errorMessage }}</p>
    </div>

    <StockAnalysis
      ref="analysisRef"
      v-show="showResults"
      :symbol="stockSymbol"
      :start-date="startDate.replace(/-/g, '')"
      @analysis-complete="isAnalyzing = false"
      @analysis-error="(msg) => { errorMessage = msg; isAnalyzing = false }"
    />
  </div>
</template>

<style scoped>
.analysis-view {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 2rem;
  border-radius: 15px;
}

.input-section {
  text-align: center;
  margin-bottom: 2rem;
}

.input-section h2 {
  margin-bottom: 1.5rem;
  color: var(--accent-color);
}

.input-group {
  display: flex;
  gap: 1rem;
  max-width: 500px;
  margin: 0 auto;
}

input {
  flex: 1;
  padding: 0.8rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-color);
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: var(--accent-color);
}

input.error {
  border-color: #F44336;
}

.analyze-btn {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 8px;
  background: linear-gradient(45deg, var(--primary-color), var(--accent-color));
  color: white;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.analyze-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.analyze-btn:not(:disabled):hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 191, 255, 0.3);
}

.error-message {
  color: #F44336;
  margin-top: 0.5rem;
  font-size: 0.9rem;
}
</style> 