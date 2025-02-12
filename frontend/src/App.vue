<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-container">
    <header class="glass-header">
      <div class="logo-container">
        <img alt="ChatWithStock logo" class="logo" src="@/assets/logo.svg" width="40" height="40" />
        <h1>ChatWithStock</h1>
      </div>
      <nav class="glass-nav">
        <RouterLink to="/" class="nav-link">
          <i class="fas fa-comments"></i>
          <span>聊天</span>
        </RouterLink>
        <RouterLink to="/analysis" class="nav-link">
          <i class="fas fa-chart-line"></i>
          <span>分析</span>
        </RouterLink>
        <RouterLink to="/portfolio" class="nav-link">
          <i class="fas fa-briefcase"></i>
          <span>投资组合</span>
        </RouterLink>
        <RouterLink to="/market" class="nav-link">
          <i class="fas fa-globe"></i>
          <span>市场</span>
        </RouterLink>
      </nav>
    </header>

    <main class="main-content">
      <RouterView v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </RouterView>
    </main>
  </div>
</template>

<style>
/* 全局样式 */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');

:root {
  --primary-color: #2a52be;
  --secondary-color: #4169e1;
  --accent-color: #00bfff;
  --background-start: #1a1a2e;
  --background-end: #16213e;
  --text-color: #ffffff;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, var(--background-start), var(--background-end));
  color: var(--text-color);
  min-height: 100vh;
}

/* 玻璃拟态效果 */
.glass-effect {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
}
</style>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.glass-header {
  @extend .glass-effect;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo {
  filter: drop-shadow(0 0 8px var(--accent-color));
  animation: pulse 2s infinite;
}

.logo-container h1 {
  font-size: 1.8rem;
  font-weight: 700;
  background: linear-gradient(45deg, var(--accent-color), #fff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 10px rgba(0, 191, 255, 0.5);
}

.glass-nav {
  display: flex;
  gap: 1.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-color);
  text-decoration: none;
  padding: 0.8rem 1.2rem;
  border-radius: 12px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.nav-link::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, var(--primary-color), var(--accent-color));
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: -1;
}

.nav-link:hover::before,
.nav-link.router-link-active::before {
  opacity: 1;
}

.nav-link i {
  font-size: 1.2rem;
}

.main-content {
  flex: 1;
  padding: 2rem;
  position: relative;
}

/* 动画效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

@media (max-width: 768px) {
  .glass-header {
    flex-direction: column;
    padding: 1rem;
  }

  .glass-nav {
    margin-top: 1rem;
    width: 100%;
    justify-content: space-around;
  }

  .nav-link {
    flex-direction: column;
    padding: 0.5rem;
    font-size: 0.8rem;
  }
}
</style>
