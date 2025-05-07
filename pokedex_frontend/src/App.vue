<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElContainer, ElHeader, ElAside, ElMain, ElMenu, ElMenuItem, ElButton } from 'element-plus';
import { useCategoryStore } from './store/categoryStore';

const route = useRoute();
const router = useRouter();
const categoryStore = useCategoryStore();

const activeCategoryId = computed(() => {
  if (route.name === 'category-detail' && route.params.id) {
    return Number(route.params.id);
  }
  return null;
});

const handleSelect = (key: string) => {
  if (key === 'home') {
    router.push('/');
  } else {
    router.push(`/categories/${key}`);
  }
};
</script>

<template>
  <ElContainer class="app-container">
    <ElHeader class="app-header">
      <div class="logo" @click="router.push('/')">
        <img src="./assets/vue.svg" alt="Bird Gallery Logo" class="logo-image">
        <span class="logo-text">Bird Species Gallery</span>
      </div>
    </ElHeader>
    
    <ElContainer class="main-container">
      <ElAside width="250px" class="app-sidebar">
        <ElMenu
          default-active="home"
          class="sidebar-menu"
          @select="handleSelect"
          :router="false"
        >
          <ElMenuItem index="home">
            <i class="el-icon-house"></i>
            <span>Home</span>
          </ElMenuItem>
          
          <div class="menu-category-label">
            <span>BIRD SPECIES</span>
            <ElButton 
              type="primary" 
              size="small" 
              @click.stop="router.push('/')"
              class="add-category-btn"
            >
              Add
            </ElButton>
          </div>
          
          <ElMenuItem
            v-for="category in categoryStore.categories"
            :key="category.id"
            :index="String(category.id)"
            class="category-menu-item"
          >
            <span class="category-menu-name">{{ category.name }}</span>
          </ElMenuItem>
        </ElMenu>
      </ElAside>
      
      <ElMain class="app-main">
        <router-view></router-view>
      </ElMain>
    </ElContainer>
  </ElContainer>
</template>

<style>
/* Global styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
}

#app {
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

/* App container */
.app-container {
  height: 100vh;
}

/* Header styles */
.app-header {
  background-color: #4CAF50;
  color: white;
  line-height: 60px;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 10;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.logo-image {
  height: 32px;
  margin-right: 10px;
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
}

/* Main container */
.main-container {
  height: calc(100vh - 60px);
}

/* Sidebar styles */
.app-sidebar {
  background-color: #f5f7fa;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  border-right: 1px solid #e6e6e6;
  overflow-y: auto;
}

.sidebar-menu {
  border-right: none;
}

.menu-category-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  color: #909399;
  font-size: 12px;
  font-weight: 600;
}

.add-category-btn {
  padding: 2px 8px;
  font-size: 12px;
}

.category-menu-item {
  padding-left: 12px;
}

.category-menu-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
  display: inline-block;
}

/* Main content area */
.app-main {
  padding: 0;
  overflow-y: auto;
  background-color: #f5f7fa;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .app-sidebar {
    width: 100%;
    position: fixed;
    z-index: 5;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .app-sidebar.visible {
    transform: translateX(0);
  }
}
</style>