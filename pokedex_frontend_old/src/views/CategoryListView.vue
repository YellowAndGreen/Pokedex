<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { 
  ElDialog, 
  ElRow, 
  ElCol, 
  ElButton, 
  ElEmpty, 
  ElSkeleton, 
  ElSkeletonItem,
  ElInput
} from 'element-plus';
import { useCategoryStore } from '../store/categoryStore';
import CategoryCard from '../components/CategoryCard.vue';
import CategoryForm from '../components/CategoryForm.vue';
import type { CategoryCreate, CategoryRead } from '../types';

const router = useRouter();
const categoryStore = useCategoryStore();
const dialogVisible = ref(false);
const isEditMode = ref(false);
const editingCategory = ref<CategoryRead | null>(null);
const searchQuery = ref('');

// Computed filtered categories based on search query
const filteredCategories = computed(() => {
  if (!searchQuery.value) return categoryStore.categories;
  
  const query = searchQuery.value.toLowerCase();
  return categoryStore.categories.filter(category => 
    category.name.toLowerCase().includes(query) || 
    (category.description?.toLowerCase().includes(query) || false)
  );
});

onMounted(async () => {
  await categoryStore.fetchCategories();
});

const openCreateDialog = () => {
  isEditMode.value = false;
  editingCategory.value = null;
  dialogVisible.value = true;
};

const openEditDialog = (category: CategoryRead) => {
  isEditMode.value = true;
  editingCategory.value = category;
  dialogVisible.value = true;
};

const handleViewCategory = (categoryId: string) => {
  router.push(`/categories/${categoryId}`);
};

const handleFormSubmit = async (formData: CategoryCreate) => {
  try {
    if (isEditMode.value && editingCategory.value) {
      await categoryStore.updateCategory(editingCategory.value.id, formData);
    } else {
      await categoryStore.createCategory(formData);
    }
    dialogVisible.value = false;
  } catch (error) {
    console.error('Form submission error:', error);
  }
};

const handleDeleteCategory = async (categoryId: string) => {
  try {
    await categoryStore.deleteCategory(categoryId);
  } catch (error) {
    console.error('Delete category error:', error);
  }
};

const closeDialog = () => {
  dialogVisible.value = false;
};
</script>

<template>
  <div class="category-list-container">
    <div class="category-list-header">
      <h1>鸟类物种图库</h1>
      <p>浏览和管理您的鸟类物种图像收藏</p>
      
      <div class="header-actions">
        <ElInput
          v-model="searchQuery"
          placeholder="搜索物种..."
          class="search-input"
          clearable
        >
          <template #prefix>
            <i class="el-icon-search"></i>
          </template>
        </ElInput>
        
        <ElButton type="primary" @click="openCreateDialog">
          添加新物种
        </ElButton>
      </div>
    </div>
    
    <div v-if="categoryStore.error" class="error-message">
      {{ categoryStore.error }}
    </div>
    
    <!-- 骨架屏加载状态 -->
    <div v-if="categoryStore.isLoadingCategories">
      <ElRow :gutter="20">
        <ElCol 
          v-for="i in 4" 
          :key="i" 
          :xs="24" 
          :sm="12" 
          :md="8" 
          :lg="6" 
          :xl="4"
          class="category-grid-item-wrapper"
        >
          <ElSkeleton animated>
            <template #template>
              <div class="category-skeleton">
                <ElSkeletonItem variant="image" style="height: 180px" />
                <div style="padding: 14px">
                  <ElSkeletonItem variant="h3" style="width: 50%" />
                  <div style="margin-top: 16px">
                    <ElSkeletonItem variant="text" style="width: 100%" />
                    <ElSkeletonItem variant="text" style="width: 100%" />
                  </div>
                  <div style="margin-top: 16px; display: flex; justify-content: space-between">
                    <ElSkeletonItem variant="button" style="width: 30%" />
                    <ElSkeletonItem variant="button" style="width: 30%" />
                    <ElSkeletonItem variant="button" style="width: 30%" />
                  </div>
                </div>
              </div>
            </template>
          </ElSkeleton>
        </ElCol>
      </ElRow>
    </div>
    
    <!-- 空状态 -->
    <ElEmpty 
      v-else-if="filteredCategories.length === 0" 
      description="未找到鸟类物种。开始添加您的第一个物种类别！"
    >
      <ElButton type="primary" @click="openCreateDialog">添加鸟类物种</ElButton>
    </ElEmpty>
    
    <!-- 类别卡片网格 -->
    <ElRow :gutter="20" class="category-grid">
      <ElCol 
        v-for="category in filteredCategories" 
        :key="category.id"
        :xs="24" 
        :sm="12" 
        :md="8" 
        :lg="6" 
        :xl="4"
        class="category-grid-item-wrapper"
      >
        <CategoryCard 
          :category="category" 
          @view="handleViewCategory"
          @edit="openEditDialog"
          @delete="handleDeleteCategory"
        />
      </ElCol>
    </ElRow>
    
    <!-- 类别创建/编辑对话框 -->
    <ElDialog
      v-model="dialogVisible"
      :title="isEditMode ? '编辑鸟类物种' : '添加新鸟类物种'"
      width="50%"
      destroy-on-close
    >
      <CategoryForm
        :is-edit-mode="isEditMode"
        :initial-data="editingCategory === null ? undefined : editingCategory"
        @submit="handleFormSubmit"
        @cancel="closeDialog"
      />
    </ElDialog>
  </div>
</template>

<style scoped>
.category-list-container {
  padding: 24px;
}

.category-list-header {
  margin-bottom: 32px;
  text-align: center;
}

.category-list-header h1 {
  margin-bottom: 8px;
  color: #303133;
}

.category-list-header p {
  color: #606266;
  margin-bottom: 24px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.search-input {
  max-width: 300px;
}

/* 卡片网格样式 */
.category-grid {
  margin-bottom: 24px;
}

.category-grid-item-wrapper {
  margin-bottom: 20px;
  display: flex;
}

.category-skeleton {
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
  width: 100%;
}

.error-message {
  background-color: #fef0f0;
  color: #f56c6c;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .header-actions {
    flex-direction: column;
    gap: 16px;
  }
  
  .search-input {
    max-width: 100%;
  }
}
</style>