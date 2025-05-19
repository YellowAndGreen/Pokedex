<script setup lang="ts">
import { 
  ElCard, 
  ElImage, 
  ElTooltip
} from 'element-plus';
import type { ImageRead } from '../types';

const props = defineProps<{
  image: ImageRead;
}>();

const emit = defineEmits<{
  (e: 'view-detail', imageId: string): void;
}>();
</script>

<template>
  <ElCard class="image-thumbnail" shadow="hover">
    <ElImage
      :src="props.image.imageUrl" 
      fit="cover"
      lazy
      class="thumbnail-image"
      @click="emit('view-detail', image.id)"
    />
    
    <div class="image-info">
      <div class="image-title">{{ image.title }}</div>
      
      <!-- Show a snippet of description -->
      <ElTooltip v-if="image.description" :content="image.description" placement="top">
        <div class="image-description">
          {{ image.description.length > 50 
            ? image.description.substring(0, 50) + '...' 
            : image.description }}
        </div>
      </ElTooltip>
      
      <!-- File info -->
      <div class="file-info">
        <span>{{ image.metadata.fileSize }}</span>
        <span class="upload-date">{{ new Date(image.createdDate).toLocaleDateString() }}</span>
      </div>
    </div>
  </ElCard>
</template>

<style scoped>
.image-thumbnail {
  transition: transform 0.2s;
  margin-bottom: 20px;
  height: 100%;
  cursor: pointer;
}

.image-thumbnail:hover {
  transform: translateY(-5px);
}

.thumbnail-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.image-info {
  padding: 12px 0 0;
}

.image-title {
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 8px;
}

.image-description {
  color: #606266;
  font-size: 0.9em;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.file-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.8em;
  color: #909399;
  margin: 8px 0;
}
</style>