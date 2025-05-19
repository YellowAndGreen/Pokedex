<template>
  <el-card class="image-card" shadow="hover">
    <el-image :src="displayImageUrl" fit="contain" class="image-item" lazy>
      <template #placeholder><div class="image-slot">加载中...</div></template>
      <template #error><div class="image-slot"><el-icon><Picture /></el-icon> <span>图片加载失败</span></div></template>
    </el-image>
    <div class="image-info">
      <p class="image-title">{{ image.title || '无标题' }}</p>
      <p class="image-description">{{ image.description || '暂无描述。' }}</p>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { ImageRead } from '../types';
import { Picture } from '@element-plus/icons-vue';

interface Props { image: ImageRead; }
const props = defineProps<Props>();

const BACKEND_STATIC_BASE_URL = 'http://localhost:8000'; // 应通过环境变量配置
const displayImageUrl = computed(() => {
  if (!props.image.image_url) return '';
  if (props.image.image_url.startsWith('http://') || props.image.image_url.startsWith('https://')) return props.image.image_url;
  if (props.image.image_url.startsWith('/')) return `${BACKEND_STATIC_BASE_URL}${props.image.image_url}`;
  return `${BACKEND_STATIC_BASE_URL}/static/uploads/${props.image.image_url}`;
});
</script>

<style scoped>
/* 样式应与原有UI风格一致或基于Element Plus统一设计 */
.image-card { height: 100%; display: flex; flex-direction: column; }
.image-item { width: 100%; height: 200px; background-color: #f5f7fa; border-radius: 4px; }
.image-slot { display: flex; flex-direction: column; justify-content: center; align-items: center; width: 100%; height: 200px; background-color: #f5f7fa; color: #c0c4cc; font-size: 14px; }
.image-slot .el-icon { font-size: 28px; margin-bottom: 8px; }
.image-info { padding: 10px 0 0; flex-grow: 1; }
.image-title { font-weight: bold; font-size: 1rem; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.image-description { font-size: 0.85rem; color: #606266; line-height: 1.4; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
</style> 