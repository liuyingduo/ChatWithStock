<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { useChatStore } from '@/stores/chat'
import StockChart from '@/components/StockChart.vue'
import StockMetrics from '@/components/StockMetrics.vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const chatStore = useChatStore()
const inputMessage = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const showWelcome = ref(true)
const isTyping = ref(false)

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const renderMarkdown = (content: string): string => {
  const html = marked.parse(content, { async: false }) as string
  return DOMPurify.sanitize(html)
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return
  showWelcome.value = false
  
  // 显示打字指示器
  isTyping.value = true
  
  try {
    await chatStore.sendMessage(inputMessage.value)
    inputMessage.value = ''
  } catch (error) {
    console.error('发送消息失败:', error)
  } finally {
    // 隐藏打字指示器
    isTyping.value = false
    await scrollToBottom()
  }
}

const suggestions = [
  "查询贵州茅台(600519)的股票信息",
  "分析腾讯控股的投资风险",
  "预测阿里巴巴未来一周的股价走势",
  "计算平安银行的夏普比率",
  "对比茅台和五粮液的投资价值"
]

const useExample = (text: string) => {
  inputMessage.value = text
}

// 计算当前时间
const currentTime = computed(() => {
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
})

onMounted(() => {
  scrollToBottom()
})
</script>

<template>
  <div class="chat-container glass-effect">
    <!-- 欢迎界面 -->
    <div v-if="showWelcome" class="welcome-screen">
      <div class="welcome-content">
        <i class="fas fa-chart-line welcome-icon"></i>
        <h1>欢迎使用 AI 智能股票助手</h1>
        <p>我可以帮您分析股票、预测趋势、评估风险，让投资决策更明智。</p>
        <div class="suggestions">
          <div 
            v-for="(suggestion, index) in suggestions" 
            :key="index"
            class="suggestion-chip"
            @click="useExample(suggestion)"
          >
            {{ suggestion }}
          </div>
        </div>
      </div>
    </div>

    <!-- 聊天记录 -->
    <div class="messages" ref="messagesContainer" :class="{ 'hide': showWelcome }">
      <div
        v-for="(message, index) in chatStore.messages"
        :key="index"
        :class="['message-wrapper', message.role]"
        :style="{ animationDelay: `${index * 0.1}s` }"
      >
        <div class="avatar">
          <i :class="message.role === 'user' ? 'fas fa-user' : 'fas fa-robot'"></i>
        </div>
        <div class="message">
          <div class="message-content" v-html="renderMarkdown(message.content)"></div>
          <template v-if="message.data">
            <StockChart 
              v-if="message.data.chartData" 
              :data="message.data.chartData"
            />
            <StockMetrics 
              v-if="message.data.metrics" 
              :metrics="message.data.metrics"
            />
          </template>
          <div class="message-time">{{ currentTime }}</div>
        </div>
      </div>
      
      <!-- 打字指示器 -->
      <div v-if="isTyping" class="message-wrapper assistant typing-indicator">
        <div class="avatar">
          <i class="fas fa-robot"></i>
        </div>
        <div class="message">
          <div class="typing">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-container glass-effect">
      <input
        v-model="inputMessage"
        @keyup.enter="sendMessage"
        type="text"
        placeholder="输入您的问题（例如：分析贵州茅台的投资价值）"
        :disabled="chatStore.loading || isTyping"
      />
      <button @click="sendMessage" :disabled="chatStore.loading || isTyping">
        <i class="fas" :class="chatStore.loading || isTyping ? 'fa-spinner fa-spin' : 'fa-paper-plane'"></i>
      </button>
    </div>
  </div>
</template>

<style scoped>
.chat-container {
  height: calc(100vh - 100px);
  max-width: 1200px;
  margin: 20px auto;
  display: flex;
  flex-direction: column;
  border-radius: 20px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.welcome-screen {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: radial-gradient(circle at center, rgba(66, 185, 131, 0.1), transparent);
}

.welcome-content {
  text-align: center;
  max-width: 800px;
  animation: fadeIn 1s ease;
}

.welcome-icon {
  font-size: 4rem;
  color: var(--accent-color);
  margin-bottom: 2rem;
  animation: float 3s ease-in-out infinite;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

.suggestion-chip {
  background: rgba(255, 255, 255, 0.1);
  padding: 0.8rem 1.5rem;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
  transform: translateY(20px);
  animation-delay: calc(var(--i, 0) * 0.1s);
}

.suggestion-chip:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  scroll-behavior: smooth;
}

.message-wrapper {
  display: flex;
  gap: 1rem;
  max-width: 80%;
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
  transform: translateY(20px);
}

.message-wrapper.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.avatar i {
  font-size: 1.2rem;
  color: var(--accent-color);
}

.message {
  background: rgba(255, 255, 255, 0.1);
  padding: 1rem 1.5rem;
  border-radius: 18px;
  position: relative;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.message-wrapper.user .message {
  background: var(--primary-color);
  border-bottom-right-radius: 0;
}

.message-wrapper.assistant .message {
  background: rgba(255, 255, 255, 0.1);
  border-bottom-left-radius: 0;
}

.message-content {
  white-space: pre-wrap;
  line-height: 1.5;
}

.message-time {
  font-size: 0.8rem;
  opacity: 0.7;
  margin-top: 0.8rem;
  text-align: right;
}

.input-container {
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

input {
  flex: 1;
  padding: 1rem 1.5rem;
  border: none;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-color);
  font-size: 1rem;
  transition: all 0.3s ease;
}

input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 2px rgba(0, 191, 255, 0.3);
}

button {
  width: 50px;
  height: 50px;
  border: none;
  border-radius: 12px;
  background: var(--accent-color);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

button:hover:not(:disabled) {
  background: var(--primary-color);
  transform: translateY(-2px);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hide {
  display: none;
}

/* 打字指示器样式 */
.typing-indicator {
  opacity: 1;
  transform: translateY(0);
}

.typing {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 0.5rem 0;
}

.typing span {
  display: inline-block;
  width: 8px;
  height: 8px;
  background-color: var(--accent-color);
  border-radius: 50%;
  animation: bounce 1.5s infinite ease-in-out;
}

.typing span:nth-child(1) {
  animation-delay: 0s;
}

.typing span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

@keyframes float {
  0% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
  100% {
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .chat-container {
    height: calc(100vh - 80px);
    margin: 10px;
    border-radius: 15px;
  }
  
  .message-wrapper {
    max-width: 90%;
  }
  
  .suggestions {
    flex-direction: column;
  }
  
  .input-container {
    padding: 1rem;
  }
}
</style> 