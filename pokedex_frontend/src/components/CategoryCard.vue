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
  // Prioritize actual thumbnail URL if available
  if (props.category.thumbnailUrl) {
    return props.category.thumbnailUrl;
  }
  // Return empty string to trigger error slot for placeholder
  return ''; 
});
</script>

<template>
  <ElCard shadow="hover" class="category-card" @click="emit('view', category.id)">
    <div class="image-container">
      <ElImage 
        :src="getBirdImageUrl" 
        fit="cover" 
        class="category-image"
        :preview="false"
      >
        <template #error>
          <div class="image-slot-error">
            <span>暂无图片</span>
          </div>
        </template>
      </ElImage>
    </div>
    
    <div class="card-content">
      <h3 class="category-name">
        {{ category.name }}
      </h3>
      
      <p class="category-description">
        {{ category.description }}
      </p>
      
      <div class="category-meta">
        <span class="image-count" v-if="imageCount !== undefined">
          {{ imageCount }} {{ imageCount === 1 ? '张图片' : '张图片' }}
        </span>
        <span class="creation-date" v-if="category.createdDate">
          添加于: {{ new Date(category.createdDate).toLocaleDateString() }}
        </span>
        <span class="creation-date" v-else>
          添加于: 未知
        </span>
      </div>
    </div>
    
    <div class="category-actions" @click.stop>
      <ElButton 
        type="primary" 
        @click.stop="emit('view', category.id)"
      >
        查看图片
      </ElButton>
      
      <ElButton 
        type="warning" 
        @click.stop="emit('edit', category)"
      >
        编辑
      </ElButton>
      
      <ElPopconfirm
        title="确定要删除这个物种类别吗？"
        confirm-button-text="删除"
        cancel-button-text="取消"
        @confirm="emit('delete', category.id)"
      >
        <template #reference>
          <ElButton type="danger" @click.stop>
            删除
          </ElButton>
        </template>
      </ElPopconfirm>
    </div>
  </ElCard>
</template>

<style scoped>
.category-card {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
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
  background-color: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
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

.image-slot-error {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background-color: #f5f7fa;
  color: #c0c4cc;
  font-size: 14px;
}

.card-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.category-name {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 8px;
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
  margin-top: auto;
}

/* 响应式断点调整 */
@media (max-width: 1200px) and (min-width: 992px) {
  .category-actions {
    flex-wrap: wrap;
  }
  
  .category-actions .el-button {
    margin-bottom: 8px;
    flex: 1 0 45%;
  }
}

@media (max-width: 768px) {
  .category-actions {
    flex-direction: column;
  }
}
</style>