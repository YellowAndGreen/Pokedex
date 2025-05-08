<script setup lang="ts">
import { computed } from 'vue';
import { 
  ElCard, 
  ElButton, 
  ElPopconfirm, 
  ElImage 
} from 'element-plus';
import type { CategoryRead } from '../types';

const props = defineProps<{
  category: CategoryRead;
  imageCount?: number;
}>();

const emit = defineEmits<{
  (e: 'view', categoryId: string): void;
  (e: 'edit', category: CategoryRead): void;
  (e: 'delete', categoryId: string): void;
}>();

// For demonstration, use placeholder images
const getBirdImageUrl = computed(() => {
  // Using Pexels for bird species images (in real app, we'd use actual category thumbnails)
  const birdImages = [
    'https://images.pexels.com/photos/349758/hummingbird-bird-birds-349758.jpeg',
    'https://images.pexels.com/photos/37833/rainbow-lorikeet-parrots-australia-rainbow-37833.jpeg',
    'https://images.pexels.com/photos/45851/bird-blue-cristata-cyanocitta-45851.jpeg',
    'https://images.pexels.com/photos/1618606/pexels-photo-1618606.jpeg'
  ];
  // Use category ID to select a consistent placeholder
  // Convert first char of string ID to a number for modulo
  const charCode = props.category.id.charCodeAt(0) || 0;
  return birdImages[charCode % birdImages.length];
});
</script>

<template>
  <ElCard shadow="hover" class="category-card">
    <div class="image-container">
      <ElImage 
        :src="getBirdImageUrl" 
        fit="cover" 
        class="category-image"
        @click="emit('view', category.id)"
      />
    </div>
    
    <h3 class="category-name" @click="emit('view', category.id)">
      {{ category.name }}
    </h3>
    
    <p class="category-description">
      {{ category.description }}
    </p>
    
    <div class="category-meta">
      <span class="image-count" v-if="imageCount !== undefined">
        {{ imageCount }} {{ imageCount === 1 ? 'image' : 'images' }}
      </span>
      <span class="creation-date" v-if="category.createdDate">
        Added: {{ new Date(category.createdDate).toLocaleDateString() }}
      </span>
      <span class="creation-date" v-else>
        Added: N/A
      </span>
    </div>
    
    <div class="category-actions">
      <ElButton 
        type="primary" 
        @click="emit('view', category.id)"
      >
        View Images
      </ElButton>
      
      <ElButton 
        type="warning" 
        @click="emit('edit', category)"
      >
        Edit
      </ElButton>
      
      <ElPopconfirm
        title="Are you sure you want to delete this category?"
        confirm-button-text="Delete"
        cancel-button-text="Cancel"
        @confirm="emit('delete', category.id)"
      >
        <template #reference>
          <ElButton type="danger">
            Delete
          </ElButton>
        </template>
      </ElPopconfirm>
    </div>
  </ElCard>
</template>

<style scoped>
.category-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
}

.image-container {
  overflow: hidden;
  border-radius: 4px;
  height: 180px;
  margin-bottom: 16px;
}

.category-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
  cursor: pointer;
}

.category-image:hover {
  transform: scale(1.05);
}

.category-name {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 8px;
  cursor: pointer;
  color: #303133;
}

.category-name:hover {
  color: #409EFF;
}

.category-description {
  flex-grow: 1;
  color: #606266;
  font-size: 0.9rem;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.category-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #909399;
  margin-bottom: 16px;
}

.category-actions {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

@media (max-width: 768px) {
  .category-actions {
    flex-direction: column;
  }
}
</style>