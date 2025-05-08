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
      <h1>Bird Species Gallery</h1>
      <p>Browse and manage your bird species image collections</p>
      
      <div class="header-actions">
        <ElInput
          v-model="searchQuery"
          placeholder="Search categories..."
          class="search-input"
          clearable
        >
          <template #prefix>
            <i class="el-icon-search"></i>
          </template>
        </ElInput>
        
        <ElButton type="primary" @click="openCreateDialog">
          Add New Bird Species
        </ElButton>
      </div>
    </div>
    
    <div v-if="categoryStore.error" class="error-message">
      {{ categoryStore.error }}
    </div>
    
    <!-- Skeleton loading state -->
    <div v-if="categoryStore.isLoadingCategories">
      <ElRow :gutter="20">
        <ElCol v-for="i in 4" :key="i" :xs="24" :sm="12" :md="8" :lg="6" class="mb-4">
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
    
    <!-- Empty state when no categories -->
    <ElEmpty 
      v-else-if="filteredCategories.length === 0" 
      description="No bird species found. Start by adding your first species category!"
    >
      <ElButton type="primary" @click="openCreateDialog">Add Bird Species</ElButton>
    </ElEmpty>
    
    <!-- Category grid -->
    <ElRow v-else :gutter="20">
      <ElCol 
        v-for="category in filteredCategories" 
        :key="category.id"
        :xs="24" 
        :sm="12" 
        :md="8" 
        :lg="6" 
        class="mb-4"
      >
        <CategoryCard 
          :category="category" 
          @view="handleViewCategory"
          @edit="openEditDialog"
          @delete="handleDeleteCategory"
        />
      </ElCol>
    </ElRow>
    
    <!-- Category create/edit dialog -->
    <ElDialog
      v-model="dialogVisible"
      :title="isEditMode ? 'Edit Bird Species' : 'Add New Bird Species'"
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

.mb-4 {
  margin-bottom: 16px;
}

.error-message {
  background-color: #fef0f0;
  color: #f56c6c;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.category-skeleton {
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
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