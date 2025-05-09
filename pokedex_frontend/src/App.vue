<script setup lang="ts">
import { useRouter } from 'vue-router';
import { ElContainer, ElHeader, ElAside, ElMain, ElMenu, ElMenuItem, ElButton } from 'element-plus';
import { useCategoryStore } from './store/categoryStore';

const router = useRouter();
const categoryStore = useCategoryStore();

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
        <img src="./assets/vue.svg" alt="鸟类图库 Logo" class="logo-image">
        <span class="logo-text">鸟类物种图库</span>
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
            <span>首页</span>
          </ElMenuItem>
          
          <div class="menu-category-label">
            <span>鸟类物种</span>
            <ElButton 
              type="primary" 
              size="small" 
              @click.stop="router.push('/')"
              class="add-category-btn"
            >
              添加
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
/* 全局样式 */
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

/* 应用容器 */
.app-container {
  height: 100vh;
}

/* 头部样式 */
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

/* 主容器 */
.main-container {
  height: calc(100vh - 60px);
}

/* 侧边栏样式 */
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

/* 主内容区域 */
.app-main {
  padding: 0;
  overflow-y: auto;
  background-color: #f5f7fa;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .app-sidebar {
    width: 0 !important;
    position: fixed;
    z-index: 5;
    transform: translateX(-100%);
    transition: transform 0.3s ease, width 0s 0.3s;
  }
  
  .app-sidebar.visible {
    width: 250px !important;
    transform: translateX(0);
    transition: transform 0.3s ease;
  }
  
  .app-main {
    width: 100% !important;
  }
}

/* Element Plus 栅格适配 */
.el-row {
  margin-left: -10px !important;
  margin-right: -10px !important;
}

.el-col {
  padding-left: 10px !important;
  padding-right: 10px !important;
}
</style>