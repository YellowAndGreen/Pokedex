<template>
  <el-card class="category-card" shadow="hover" @click="navigateToDetail">
    <template #header>
      <div class="card-header">
        <span class="category-name">{{ category.name }}</span>
      </div>
    </template>
    
    <div class="card-body">
      <el-image 
        v-if="displayThumbnailUrl" 
        :src="displayThumbnailUrl" 
        fit="cover" 
        class="category-thumbnail" 
        lazy
      >
        <template #placeholder>
          <div class="image-slot">加载中...</div>
        </template>
        <template #error>
          <div class="image-slot">
            <el-icon><Picture /></el-icon>
            <span>图片加载失败</span>
          </div>
        </template>
      </el-image>
      
      <div v-else class="no-thumbnail image-slot">
        <el-icon><Picture /></el-icon>
        <span>暂无缩略图</span>
      </div>
      
      <p class="category-description">
        {{ category.description || '暂无描述信息。' }}
      </p>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import type { CategoryRead } from '../types';
import { Picture } from '@element-plus/icons-vue';

const props = defineProps<{
  category: CategoryRead;
}>();

const router = useRouter();
const BACKEND_STATIC_BASE_URL = 'http://localhost:8000';

const displayThumbnailUrl = computed(() => {
  if (!props.category.thumbnailUrl) return '';
  const url = props.category.thumbnailUrl;
  
  if (url.startsWith('http')) return url;
  if (url.startsWith('/')) return `${BACKEND_STATIC_BASE_URL}${url}`;
  return `${BACKEND_STATIC_BASE_URL}/static/uploads/${url}`;
});

const navigateToDetail = () => {
  router.push({
    name: 'CategoryDetail',
    params: { id: props.category.id.toString() }
  });
};
</script>

<style scoped>
.category-card {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
}

.category-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #303133;
}

.card-body {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.category-thumbnail {
  width: 100%;
  height: 180px;
  border-radius: 4px;
  background-color: #f5f7fa;
}

.image-slot {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 180px;
  background-color: #f5f7fa;
  color: #c0c4cc;
  border-radius: 4px;
}

.image-slot .el-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.category-description {
  margin-top: 12px;
  font-size: 0.9rem;
  color: #606266;
  line-height: 1.5;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}
</style>
