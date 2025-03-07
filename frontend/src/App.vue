<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { ref, onMounted, onUnmounted } from 'vue'

const isScrolled = ref(false)
const isMobileMenuOpen = ref(false)

// 监听滚动事件，改变导航栏样式
const handleScroll = () => {
  isScrolled.value = window.scrollY > 20
}

// 切换移动端菜单
const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

// 关闭移动端菜单
const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div class="app-container">
    <header 
      class="glass-header" 
      :class="{ 'scrolled': isScrolled }"
    >
      <div class="logo-container">
        <img alt="ChatWithStock logo" class="logo" src="@/assets/logo.svg" width="40" height="40" />
        <h1>ChatWithStock</h1>
      </div>
      
      <!-- 桌面导航 -->
      <nav class="glass-nav desktop-nav">
        <RouterLink to="/" class="nav-link" @click="closeMobileMenu">
          <i class="fas fa-comments"></i>
          <span>聊天</span>
        </RouterLink>
        <RouterLink to="/analysis" class="nav-link" @click="closeMobileMenu">
          <i class="fas fa-chart-line"></i>
          <span>分析</span>
        </RouterLink>
        <RouterLink to="/portfolio" class="nav-link" @click="closeMobileMenu">
          <i class="fas fa-briefcase"></i>
          <span>投资组合</span>
        </RouterLink>
        <RouterLink to="/market" class="nav-link" @click="closeMobileMenu">
          <i class="fas fa-globe"></i>
          <span>市场</span>
        </RouterLink>
      </nav>
      
      <!-- 移动端菜单按钮 -->
      <div class="mobile-menu-toggle" @click="toggleMobileMenu">
        <i class="fas" :class="isMobileMenuOpen ? 'fa-times' : 'fa-bars'"></i>
      </div>
    </header>
    
    <!-- 移动端导航菜单 -->
    <div class="mobile-menu" :class="{ 'open': isMobileMenuOpen }">
      <nav class="mobile-nav">
        <RouterLink to="/" class="nav-link" @click="closeMobileMenu">
          <i class="fas fa-comments"></i>
          <span>聊天</span>
        </RouterLink>
        <RouterLink to="/analysis" class="nav-link" @click="closeMobileMenu">
          <i class="fas fa-chart-line"></i>
          <span>分析</span>
        </RouterLink>
        <RouterLink to="/portfolio" class="nav-link" @click="closeMobileMenu">
          <i class="fas fa-briefcase"></i>
          <span>投资组合</span>
        </RouterLink>
        <RouterLink to="/market" class="nav-link" @click="closeMobileMenu">
          <i class="fas fa-globe"></i>
          <span>市场</span>
        </RouterLink>
      </nav>
    </div>

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
  --header-height: 70px;
  --header-height-scrolled: 60px;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, var(--background-start), var(--background-end));
  color: var(--text-color);
  min-height: 100vh;
  line-height: 1.6;
}

a {
  text-decoration: none;
  color: inherit;
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
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  height: var(--header-height);
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.glass-header.scrolled {
  height: var(--header-height-scrolled);
  background: rgba(26, 26, 46, 0.95);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo {
  filter: drop-shadow(0 0 8px var(--accent-color));
  animation: pulse 2s infinite;
  transition: all 0.3s ease;
}

.scrolled .logo {
  transform: scale(0.9);
}

.logo-container h1 {
  font-size: 1.8rem;
  font-weight: 700;
  background: linear-gradient(45deg, var(--accent-color), #fff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 10px rgba(0, 191, 255, 0.5);
  transition: all 0.3s ease;
}

.scrolled .logo-container h1 {
  font-size: 1.6rem;
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
  margin-top: var(--header-height);
  transition: margin-top 0.3s ease;
}

.scrolled + .main-content {
  margin-top: var(--header-height-scrolled);
}

/* 移动端菜单 */
.mobile-menu-toggle {
  display: none;
  cursor: pointer;
  font-size: 1.5rem;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.mobile-menu-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
}

.mobile-menu {
  position: fixed;
  top: var(--header-height);
  left: 0;
  right: 0;
  background: rgba(26, 26, 46, 0.95);
  backdrop-filter: blur(10px);
  z-index: 99;
  transform: translateY(-100%);
  opacity: 0;
  transition: all 0.3s ease;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.mobile-menu.open {
  transform: translateY(0);
  opacity: 1;
}

.mobile-nav {
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

.mobile-nav .nav-link {
  padding: 1rem;
  margin-bottom: 0.5rem;
  border-radius: 8px;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .glass-header {
    padding: 0 1rem;
  }
  
  .desktop-nav {
    display: none;
  }
  
  .mobile-menu-toggle {
    display: block;
  }
  
  .logo-container h1 {
    font-size: 1.5rem;
  }
  
  .main-content {
    padding: 1rem;
  }
}
</style>
