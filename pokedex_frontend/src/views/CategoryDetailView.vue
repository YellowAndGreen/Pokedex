<template>
      <div class="category-detail-view">
        <el-breadcrumb separator-icon="ArrowRight" class="page-breadcrumb">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/categories' }">类别列表</el-breadcrumb-item>
          <el-breadcrumb-item>{{ currentCategoryDetail?.name || '加载中...' }}</el-breadcrumb-item>
        </el-breadcrumb>

        <div v-if="isLoadingDetail" class="loading-state">
          <el-skeleton :rows="3" animated /><el-divider />
          <el-row :gutter="20"><el-col :xs="12" :sm="8" :md="6" :lg="4" v-for="n in 12" :key="n"><el-skeleton style="width: 100%; margin-bottom: 20px;" animated><template #template><el-skeleton-item variant="image" style="width: 100%; height: 150px;" /><div style="padding: 10px;"><el-skeleton-item variant="p" style="width: 70%" /></div></template></el-skeleton></el-col></el-row>
        </div>
        <el-alert v-if="error && !isLoadingDetail" :title="'数据加载失败: ' + (error instanceof Error ? error.message : String(error))" type="error" show-icon closable @close="clearError" class="error-alert"/>

        <div v-if="currentCategoryDetail && !isLoadingDetail && !error">
          <el-descriptions :title="currentCategoryDetail.name" :column="2" border class="category-info">
            <el-descriptions-item label="ID">{{ currentCategoryDetail.id }}</el-descriptions-item>
            <el-descriptions-item label="名称">{{ currentCategoryDetail.name }}</el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">{{ currentCategoryDetail.description || '暂无描述' }}</el-descriptions-item>
            <el-descriptions-item label="图片数量">{{ currentCategoryDetail.images.length }} 张</el-descriptions-item>
          </el-descriptions>
          
          <div class="action-buttons" style="margin-top: 20px; margin-bottom: 20px; text-align: right;">
            <el-button type="primary" :icon="UploadFilled" @click="openUploadDialog">上传图片到此类别</el-button>
          </div>
          <el-divider content-position="left">类别下的图片</el-divider>
          
          <div v-if="currentCategoryDetail.images && currentCategoryDetail.images.length > 0" class="image-grid-container">
            <el-row :gutter="16"><el-col v-for="image in currentCategoryDetail.images" :key="image.id" :xs="12" :sm="8" :md="6" :lg="4" :xl="3" class="image-grid-item-wrapper"><ImageCard :image="image" /></el-col></el-row>
          </div>
          <el-empty v-else description="该类别下暂无图片。" />
        </div>
        <ImageUploadForm :visible="isUploadDialogVisible" :category-id="categoryId" :category-name="currentCategoryDetail?.name || ''" @update:visible="isUploadDialogVisible = $event" @upload-success="handleUploadSuccess"/>
      </div>
    </template>
    <script setup lang="ts">
    import { ref, onMounted, computed, watch } from 'vue';
    import { useRoute } from 'vue-router';
    import { storeToRefs } from 'pinia';
    import { useCategoryStore } from '../store/categoryStore';
    import ImageCard from '../components/ImageCard.vue';
    import ImageUploadForm from '../components/ImageUploadForm.vue'; //将在Phase3创建
    import { ElMessage, ElAlert, ElRow, ElCol, ElEmpty, ElSkeleton, ElSkeletonItem, ElBreadcrumb, ElBreadcrumbItem, ElDescriptions, ElDescriptionsItem, ElDivider, ElButton } from 'element-plus';
    import { ArrowRight, UploadFilled } from '@element-plus/icons-vue';

    const route = useRoute();
    const categoryStore = useCategoryStore();
    const { currentCategoryDetail, isLoadingDetail, error } = storeToRefs(categoryStore);

    const categoryId = computed(() => route.params.id as string);
    const isUploadDialogVisible = ref(false); //用于控制ImageUploadForm的显示

    const fetchDetails = (id: string) => {
      if (id) categoryStore.fetchCategoryWithImages(id);
    };
    
    const clearError = () => {
        categoryStore.error = null;
    };

    onMounted(() => { fetchDetails(categoryId.value); });
    watch(categoryId, (newId, oldId) => { 
      // 仅当路由ID实际变化且与当前加载的详情ID不同时才重新加载
      if (newId && newId !== oldId && newId !== currentCategoryDetail.value?.id.toString()) {
        fetchDetails(newId); 
      }
    });

    const openUploadDialog = () => { isUploadDialogVisible.value = true; };
    const handleUploadSuccess = async () => {
      // 图片上传成功后，刷新当前类别的详情 (从而更新图片列表)
      if (categoryId.value) await categoryStore.fetchCategoryWithImages(categoryId.value); 
      isUploadDialogVisible.value = false;
    };
    </script>
    <style scoped>
    /* 样式应与原有UI风格一致或基于Element Plus统一设计 */
    .category-detail-view { padding: 20px; }
    .page-breadcrumb { margin-bottom: 20px; }
    .loading-state, .error-alert { margin-top: 20px; }
    .category-info { margin-bottom: 20px; } 
    .el-divider { margin: 30px 0; }
    .image-grid-item-wrapper { margin-bottom: 16px; display: flex; }
    </style> 