<template>
  <div class="category-list-view">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator-icon="ArrowRight" class="page-breadcrumb">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item>类别列表</el-breadcrumb-item>
    </el-breadcrumb>

    <h1 class="page-title">宝可梦类别</h1>

    <!-- 加载状态 -->
    <div v-if="isLoadingList" class="loading-state">
      <el-row :gutter="20">
        <el-col 
          v-for="n in 8" 
          :key="n"
          :xs="24" :sm="12" :md="8" :lg="6"
        >
          <el-skeleton style="width: 100%; margin-bottom: 20px;" animated>
            <template #template>
              <el-skeleton-item variant="image" style="width: 100%; height: 180px;" />
              <div style="padding: 14px;">
                <el-skeleton-item variant="p" style="width: 50%" />
                <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 10px;">
                  <el-skeleton-item variant="text" style="margin-right: 16px;" />
                  <el-skeleton-item variant="text" style="width: 30%;" />
                </div>
              </div>
            </template>
          </el-skeleton>
        </el-col>
      </el-row>
    </div>

    <!-- 错误提示 -->
    <el-alert 
      v-if="error"
      :title="'数据加载失败: ' + (error instanceof Error ? error.message : String(error))"
      type="error"
      show-icon
      closable
      @close="clearError"
      class="error-alert"
    />

    <!-- 类别网格 -->
    <div v-if="!isLoadingList && !error && categories.length > 0" class="category-grid-container">
      <el-row :gutter="20">
        <el-col 
          v-for="category in categories"
          :key="category.id"
          :xs="24" :sm="12" :md="8" :lg="6" :xl="4"
          class="category-grid-item-wrapper"
        >
          <CategoryCard :category="category" />
        </el-col>
      </el-row>
    </div>

    <!-- 空状态 -->
    <el-empty 
      v-if="!isLoadingList && !error && categories.length === 0"
      description="暂无任何类别数据。"
      class="empty-state"
    />

    <!-- 浮动操作按钮 -->
    <div class="fab-container">
      <el-tooltip content="创建新类别" placement="left">
        <el-button 
          type="primary"
          :icon="Plus"
          circle
          size="large"
          @click="openCreateCategoryDialog"
        />
      </el-tooltip>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useCategoryStore } from '../store/categoryStore';
import CategoryCard from '../components/CategoryCard.vue';
import { ElMessage } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';

const categoryStore = useCategoryStore();
const { categories, isLoadingList, error } = storeToRefs(categoryStore);
const isCategoryFormVisible = ref(false);

onMounted(() => {
  if (categories.value.length === 0) {
    categoryStore.fetchCategories();
  }
});

const clearError = () => {
  categoryStore.error = null;
};

const openCreateCategoryDialog = () => {
  isCategoryFormVisible.value = true;
};
</script>

<style scoped>
.category-list-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-breadcrumb {
  margin-bottom: 20px;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #303133;
  margin-bottom: 25px;
  text-align: center;
}

.loading-state,
.error-alert,
.empty-state {
  margin-top: 20px;
}

.category-grid-item-wrapper {
  margin-bottom: 20px;
  display: flex;
}

.fab-container {
  position: fixed;
  right: 40px;
  bottom: 40px;
  z-index: 1000;
}
</style>
