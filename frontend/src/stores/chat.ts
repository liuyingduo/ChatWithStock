import { defineStore } from 'pinia'
import type { Message } from '@/types/chat'

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [] as Message[],
    loading: false
  }),
  
  actions: {
    async sendMessage(content: string) {
      this.loading = true
      try {
        const userMessage: Message = { role: 'user', content }
        this.messages.push(userMessage)
        
        const response = await fetch('http://localhost:8000/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(userMessage)
        })
        
        const data = await response.json()
        this.messages.push(data)
      } catch (error) {
        console.error('Error:', error)
      } finally {
        this.loading = false
      }
    }
  }
}) 