<script setup lang="ts">
import { 
  ElCard, 
  ElImage, 
  ElButton, 
  ElPopconfirm, 
  ElTooltip
} from 'element-plus';
import type { ImageRead } from '../types';

const props = defineProps<{
  image: ImageRead;
}>();

const emit = defineEmits<{
  (e: 'view-detail', imageId: string): void;
  (e: 'edit-meta', imageId: string): void;
  (e: 'delete', imageId: string): void;
}>();

const handleDeleteEmit = (id: string) => {
  console.log('[ImageThumbnail] Emitting delete for image.id:', id);
  emit('delete', id);
}
</script>

<template>
  <ElCard class="image-thumbnail" shadow="hover">
    <ElImage
      :src="props.image.imageUrl" 
      :preview-src-list="[props.image.imageUrl]"
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
      
      <!-- Tags removed -->
      <!-- <div class="image-tags">
        <ElTag 
          v-for="tag in image.tags" 
          :key="tag" 
          size="small" 
          type="info" 
          class="tag"
        >
          {{ tag }}
        </ElTag>
      </div> -->
      
      <!-- File info -->
      <div class="file-info">
        <span>{{ image.metadata.fileSize }}</span>
        <span class="upload-date">{{ new Date(image.createdDate).toLocaleDateString() }}</span>
      </div>
      
      <!-- Action buttons -->
      <div class="image-actions">
        <ElButton 
          type="primary" 
          size="small" 
          @click="emit('view-detail', image.id)"
        >
          View
        </ElButton>
        
        <ElButton 
          type="warning" 
          size="small" 
          @click="emit('edit-meta', image.id)"
        >
          Edit
        </ElButton>
        
        <ElPopconfirm
          title="Are you sure you want to delete this image?"
          confirm-button-text="Delete"
          cancel-button-text="Cancel"
          @confirm="handleDeleteEmit(image.id)"
        >
          <template #reference>
            <ElButton 
              type="danger" 
              size="small"
            >
              Delete
            </ElButton>
          </template>
        </ElPopconfirm>
      </div>
    </div>
  </ElCard>
</template>

<style scoped>
.image-thumbnail {
  transition: transform 0.2s;
  margin-bottom: 20px;
  height: 100%;
}

.image-thumbnail:hover {
  transform: translateY(-5px);
}

.thumbnail-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  cursor: pointer;
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

.image-tags {
  margin: 8px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag {
  margin-right: 4px;
}

.file-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.8em;
  color: #909399;
  margin: 8px 0;
}

.image-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  gap: 8px;
}
</style>