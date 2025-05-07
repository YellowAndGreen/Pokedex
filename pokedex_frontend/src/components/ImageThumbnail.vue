<script setup lang="ts">
import { computed } from 'vue';
import { 
  ElCard, 
  ElImage, 
  ElButton, 
  ElPopconfirm, 
  ElTag,
  ElTooltip
} from 'element-plus';
import type { ImageRead } from '../types';

const props = defineProps<{
  image: ImageRead;
}>();

const emit = defineEmits<{
  (e: 'view-detail', imageId: number): void;
  (e: 'edit-meta', imageId: number): void;
  (e: 'delete', imageId: number): void;
}>();

// Computed URLs for the image sources
const thumbnailUrl = computed(() => {
  // In a real app, this would be a properly constructed URL
  return `/static/uploads/thumbnails/${props.image.relative_thumbnail_path}`;
});

const imageUrl = computed(() => {
  // In a real app, this would be a properly constructed URL
  return `/static/uploads/images/${props.image.relative_file_path}`;
});

// Format the file size in a human-readable format
const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' bytes';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
};

// For demonstration purposes, use placeholder images
const placeholderUrl = computed(() => {
  // Using Pexels for bird images (in real app, we'd use actual uploaded images)
  const birdImages = [
    'https://images.pexels.com/photos/326900/pexels-photo-326900.jpeg',
    'https://images.pexels.com/photos/1545548/pexels-photo-1545548.jpeg',
    'https://images.pexels.com/photos/1133957/pexels-photo-1133957.jpeg',
    'https://images.pexels.com/photos/2662434/pexels-photo-2662434.jpeg'
  ];
  // Use image ID to select a consistent placeholder
  return birdImages[props.image.id % birdImages.length];
});
</script>

<template>
  <ElCard class="image-thumbnail" shadow="hover">
    <ElImage
      :src="placeholderUrl" 
      :preview-src-list="[placeholderUrl]"
      fit="cover"
      lazy
      class="thumbnail-image"
      @click="emit('view-detail', image.id)"
    />
    
    <div class="image-info">
      <div class="image-title">{{ image.original_filename }}</div>
      
      <!-- Show a snippet of description -->
      <ElTooltip v-if="image.description" :content="image.description" placement="top">
        <div class="image-description">
          {{ image.description.length > 50 
            ? image.description.substring(0, 50) + '...' 
            : image.description }}
        </div>
      </ElTooltip>
      
      <!-- Tags -->
      <div class="image-tags">
        <ElTag 
          v-for="tag in image.tags" 
          :key="tag" 
          size="small" 
          type="info" 
          class="tag"
        >
          {{ tag }}
        </ElTag>
      </div>
      
      <!-- File info -->
      <div class="file-info">
        <span>{{ formatFileSize(image.size_bytes) }}</span>
        <span class="upload-date">{{ new Date(image.upload_date).toLocaleDateString() }}</span>
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
          @confirm="emit('delete', image.id)"
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