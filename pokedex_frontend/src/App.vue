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
  <el-config-provider namespace="ep">
    <el-container class="app-container">
      <el-header class="app-header">
        <div class="logo-title">
          <span>Pokedex 图鉴</span>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
      <el-footer class="app-footer">
        Pokedex App &copy; 2025
      </el-footer>
    </el-container>
  </el-config-provider>
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
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 头部样式 */
.app-header {
  background-color: #409EFF;
  color: white;
  padding: 0 20px;
  height: 60px;
  line-height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-title {
  font-size: 1.5rem;
  font-weight: bold;
}

/* 主容器 */
.app-main {
  flex-grow: 1;
  padding: 20px;
  background-color: #f4f6f9;
}

.app-footer {
  height: 40px;
  line-height: 40px;
  text-align: center;
  font-size: 0.85rem;
  color: #909399;
  background-color: #ffffff;
  border-top: 1px solid #e4e7ed;
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