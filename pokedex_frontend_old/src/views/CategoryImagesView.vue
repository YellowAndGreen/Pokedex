<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { 
  ElDialog, 
  ElRow, 
  ElCol, 
  ElButton, 
  ElEmpty, 
  ElPagination,
  ElPageHeader,
  ElImage,
  ElDescriptions,
  ElDescriptionsItem,
  ElInput,
  ElPopconfirm
} from 'element-plus';
import { useCategoryStore } from '../store/categoryStore';
import { useImageStore } from '../store/imageStore';
import ImageThumbnail from '../components/ImageThumbnail.vue';
import ImageUploadForm from '../components/ImageUploadForm.vue';
import ImageMetaForm from '../components/ImageMetaForm.vue';
import CategoryForm from '../components/CategoryForm.vue';
import type { ImageRead, ImageUpdate, CategoryCreate } from '../types';

const route = useRoute();
const router = useRouter();
const categoryStore = useCategoryStore();
const imageStore = useImageStore();
const uploadDialogVisible = ref(false);
const detailDialogVisible = ref(false);
const metaDialogVisible = ref(false);
const editCategoryDialogVisible = ref(false);
const selectedImage = ref<ImageRead | null>(null);
const searchQuery = ref('');

const pageSize = ref(12);
const currentPage = ref(1);

// Get category ID from route params
const categoryId = computed(() => {
  const idParam = route.params.id;
  if (Array.isArray(idParam)) {
    return String(idParam[0]);
  }
  return String(idParam);
});

// Filtered images based on search
const filteredImages = computed(() => {
  console.log('[View] filteredImages computed. currentCategoryDetail:', JSON.parse(JSON.stringify(categoryStore.currentCategoryDetail))); // Deep copy
  if (!categoryStore.currentCategoryDetail?.images) {
    console.log('[View] filteredImages: currentCategoryDetail or images is null/undefined. Returning [].');
    return [];
  }
  
  if (!searchQuery.value) {
    console.log('[View] filteredImages - no search query, returning all images from currentCategoryDetail. Count:', categoryStore.currentCategoryDetail.images.length);
    return categoryStore.currentCategoryDetail.images;
  }
  
  const query = searchQuery.value.toLowerCase();
  const result = categoryStore.currentCategoryDetail.images.filter(image => 
    (image.title.toLowerCase().includes(query)) ||
    (image.description?.toLowerCase().includes(query) || false)
  );
  console.log('[View] filteredImages - with search query, result count:', result.length);
  return result;
});

// Paginated images
const paginatedImages = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value;
  return filteredImages.value.slice(startIndex, startIndex + pageSize.value);
});

onMounted(async () => {
  const currentId = categoryId.value;
  console.log('[View] onMounted - categoryId from route:', currentId);
  if (currentId) {
    await categoryStore.fetchCategoryWithImages(currentId);
  } else {
    console.error('Invalid category ID in onMounted:', route.params.id);
  }
});

// Watch for route changes
watch(() => route.params.id, async (newIdParam) => {
  let newId: string;
  if (Array.isArray(newIdParam)) {
    newId = String(newIdParam[0]);
  } else {
    newId = String(newIdParam);
  }
  console.log('[View] watch route.params.id - newId:', newId);

  if (newId) {
    if (categoryStore.currentCategoryDetail?.id !== newId) {
        console.log('[View] watch - fetching new category data for ID:', newId);
        await categoryStore.fetchCategoryWithImages(newId);
        currentPage.value = 1;
    } else {
        console.log('[View] watch - ID is the same as currentCategoryDetail, not fetching.');
    }
  } else {
    console.error('Invalid category ID in watch:', newIdParam);
  }
}, { immediate: false });

const openUploadDialog = () => {
  uploadDialogVisible.value = true;
};

const closeUploadDialog = () => {
  uploadDialogVisible.value = false;
};

const handleUploadSuccess = async () => {
  uploadDialogVisible.value = false;
  const currentId = categoryId.value;
  if (currentId) {
    await categoryStore.fetchCategoryWithImages(currentId);
  } else {
    console.error('Upload success but category ID is invalid, cannot refresh category images. ID was:', currentId, 'From route params:', route.params.id);
  }
};

const handleUploadError = (error: Error) => {
  console.error('Upload error:', error);
};

const viewImageDetail = (imageId: string) => {
  if (categoryStore.currentCategoryDetail?.images) {
    const image = categoryStore.currentCategoryDetail.images.find(img => img.id === imageId);
    if (image) {
      selectedImage.value = image;
      detailDialogVisible.value = true;
    }
  }
};

const editImageMeta = (imageId: string) => {
  if (categoryStore.currentCategoryDetail?.images) {
    const image = categoryStore.currentCategoryDetail.images.find(img => img.id === imageId);
    if (image) {
      selectedImage.value = image;
      metaDialogVisible.value = true;
    }
  }
};

const deleteImage = async (imageId: string) => {
  console.log('[View] deleteImage called with imageId:', imageId, 'and current categoryId:', categoryId.value);
  try {
    await imageStore.deleteImage(imageId, categoryId.value);
    console.log('[View] imageStore.deleteImage finished for imageId:', imageId);
    if (selectedImage.value && selectedImage.value.id === imageId) {
      detailDialogVisible.value = false;
      selectedImage.value = null;
    }
    const currentCatId = categoryId.value;
    if (currentCatId) {
      console.log('[View] Refreshing category after delete for categoryId:', currentCatId);
      await categoryStore.fetchCategoryWithImages(currentCatId);
    }
  } catch (error) {
    console.error('[View] Delete image error in view for imageId:', imageId, error);
  }
};

const handleDeleteConfirm = () => {
  if (selectedImage.value) {
    console.log('[View] handleDeleteConfirm called for selectedImage.id:', selectedImage.value.id);
    deleteImage(selectedImage.value.id);
  } else {
    console.warn('[View] handleDeleteConfirm called but no selectedImage.');
  }
};

const handleMetaFormSubmit = async (updateData: ImageUpdate, imageId: string) => {
  try {
    await imageStore.updateImageMetadata(imageId, updateData);
    metaDialogVisible.value = false;
    const currentCatId = categoryId.value;
    if (currentCatId) {
      await categoryStore.fetchCategoryWithImages(currentCatId);
      if (selectedImage.value && selectedImage.value.id === imageId) {
        const updatedImg = categoryStore.currentCategoryDetail?.images.find(i => i.id === imageId);
        if (updatedImg) selectedImage.value = updatedImg;
        else detailDialogVisible.value = false;
      }
    }
  } catch (error) {
    console.error('Update metadata error:', error);
  }
};

const goBack = () => {
  router.push('/');
};

const openEditCategoryDialog = () => {
  editCategoryDialogVisible.value = true;
};

const handleCategoryFormSubmit = async (formData: CategoryCreate) => {
  try {
    const currentId = categoryId.value;
    if (currentId && categoryStore.currentCategoryDetail) {
      await categoryStore.updateCategory(currentId, formData);
      await categoryStore.fetchCategoryWithImages(currentId);
      editCategoryDialogVisible.value = false;
    }
  } catch (error) {
    console.error('编辑物种信息失败:', error);
  }
};

const closeEditCategoryDialog = () => {
  editCategoryDialogVisible.value = false;
};

const deleteCategory = async () => {
  try {
    const currentId = categoryId.value;
    if (currentId) {
      await categoryStore.deleteCategory(currentId);
      router.push('/');
    }
  } catch (error) {
    console.error('删除物种失败:', error);
  }
};
</script>

<template>
  <div class="category-images-container">
    <ElPageHeader @back="goBack" class="page-header">
      <template #content>
        <div class="page-title">
          <template v-if="categoryStore.currentCategoryDetail">
            <span class="page-title-text">{{ categoryStore.currentCategoryDetail.name }}</span>
            <span v-if="filteredImages.length" class="image-count">
              {{ filteredImages.length }} {{ filteredImages.length === 1 ? '张图片' : '张图片' }}
            </span>
          </template>
          <span v-else>鸟类物种图片</span>
        </div>
      </template>
      
      <template #extra>
        <div class="header-actions">
          <ElButton type="warning" @click="openEditCategoryDialog" class="mr-2">
            编辑物种信息
          </ElButton>
          <ElPopconfirm
            title="确定要删除此物种及其所有图片吗？此操作无法撤销！"
            confirm-button-text="删除"
            cancel-button-text="取消"
            @confirm="deleteCategory"
          >
            <template #reference>
              <ElButton type="danger" class="mr-2">
                删除物种
              </ElButton>
            </template>
          </ElPopconfirm>
          <ElButton type="primary" @click="openUploadDialog">
            上传图片
          </ElButton>
        </div>
      </template>
    </ElPageHeader>
    
    <div v-if="categoryStore.isLoadingCategoryDetail || imageStore.isUploading" class="loading-message">
      加载中...
    </div>
    
    <div v-if="categoryStore.error || imageStore.error" class="error-message">
      {{ categoryStore.error || imageStore.error }}
    </div>
    
    <template v-else-if="categoryStore.currentCategoryDetail">
      <div class="category-description" v-if="categoryStore.currentCategoryDetail.description">
        {{ categoryStore.currentCategoryDetail.description }}
      </div>
      
      <div class="search-filters">
        <ElInput
          v-model="searchQuery"
          placeholder="搜索图片标题..."
          clearable
          class="search-input"
        >
          <template #prefix>
            <i class="el-icon-search"></i>
          </template>
        </ElInput>
      </div>
      
      <ElEmpty 
        v-if="filteredImages.length === 0" 
        description="此类别中没有找到图片。开始上传第一张图片！"
      >
        <ElButton type="primary" @click="openUploadDialog">上传图片</ElButton>
      </ElEmpty>
      
      <template v-else>
        <ElRow :gutter="20">
          <ElCol 
            v-for="image in paginatedImages" 
            :key="image.id"
            :xs="24" 
            :sm="12" 
            :md="8" 
            :lg="6" 
            class="mb-4"
          >
            <ImageThumbnail 
              :image="image" 
              @view-detail="viewImageDetail"
            />
          </ElCol>
        </ElRow>
        
        <ElPagination
          v-if="filteredImages.length > pageSize"
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="filteredImages.length"
          layout="prev, pager, next, jumper"
          class="pagination"
          @current-change="currentPage = $event"
        />
      </template>
    </template>
    
    <!-- 物种编辑对话框 -->
    <ElDialog
      v-model="editCategoryDialogVisible"
      title="编辑物种信息"
      width="50%"
      destroy-on-close
    >
      <CategoryForm
        v-if="categoryStore.currentCategoryDetail"
        :is-edit-mode="true"
        :initial-data="categoryStore.currentCategoryDetail"
        @submit="handleCategoryFormSubmit"
        @cancel="closeEditCategoryDialog"
      />
    </ElDialog>
    
    <!-- Image Upload Dialog -->
    <ElDialog
      v-model="uploadDialogVisible"
      title="上传图片"
      width="50%"
      destroy-on-close
    >
      <ImageUploadForm
        :category-id="categoryId"
        @upload-success="handleUploadSuccess"
        @upload-error="handleUploadError"
        @cancel="closeUploadDialog"
      />
    </ElDialog>
    
    <!-- 图片详情对话框 -->
    <ElDialog 
      v-if="selectedImage"
      v-model="detailDialogVisible"
      :title="selectedImage.title" 
      width="60%"
      @closed="selectedImage = null"
    >
      <div class="image-detail-content">
        <ElRow :gutter="20">
          <ElCol :span="12">
            <ElImage 
              class="detail-image"
              :src="selectedImage.imageUrl" 
              :preview-src-list="[selectedImage.imageUrl]"
              fit="contain"
            />
          </ElCol>
          <ElCol :span="12">
            <ElDescriptions :column="1" border>
              <ElDescriptionsItem label="标题">{{ selectedImage.title }}</ElDescriptionsItem>
              <ElDescriptionsItem label="描述">{{ selectedImage.description || '无' }}</ElDescriptionsItem>
              <ElDescriptionsItem label="物种">{{ categoryStore.currentCategoryDetail?.name }}</ElDescriptionsItem>
              <ElDescriptionsItem label="格式">{{ selectedImage.metadata.format }}</ElDescriptionsItem>
              <ElDescriptionsItem label="尺寸">
                {{ selectedImage.metadata.width }} x {{ selectedImage.metadata.height }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="文件大小">{{ selectedImage.metadata.fileSize }}</ElDescriptionsItem>
              <ElDescriptionsItem label="上传时间">{{ new Date(selectedImage.createdDate).toLocaleString() }}</ElDescriptionsItem>
            </ElDescriptions>
          </ElCol>
        </ElRow>
      </div>
      <template #footer>
        <div class="detail-footer-actions">
          <ElButton @click="detailDialogVisible = false">关闭</ElButton>
          <div>
            <ElButton type="warning" @click="editImageMeta(String(selectedImage!.id))" class="mr-2">
              编辑
            </ElButton>
            <ElPopconfirm
              title="确定要删除这张图片吗？"
              confirm-button-text="删除"
              cancel-button-text="取消"
              @confirm="handleDeleteConfirm"
            >
              <template #reference>
                <ElButton type="danger">删除</ElButton>
              </template>
            </ElPopconfirm>
          </div>
        </div>
      </template>
    </ElDialog>
    
    <!-- 图片元数据编辑对话框 -->
    <ElDialog
      v-model="metaDialogVisible"
      title="编辑图片元数据"
      width="50%"
      @closed="selectedImage = null" 
    >
      <ImageMetaForm 
        v-if="selectedImage" 
        :initial-data="selectedImage" 
        :categories="categoryStore.categories"
        @submit="handleMetaFormSubmit" 
        @cancel="metaDialogVisible = false"
      />
    </ElDialog>
  </div>
</template>

<style scoped>
.category-images-container {
  padding: 0 24px 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title-text {
  font-size: 1.5rem;
  font-weight: 600;
}

.image-count {
  color: #909399;
  font-size: 0.9rem;
  font-weight: normal;
}

.category-description {
  color: #606266;
  margin-bottom: 24px;
  padding: 0 12px;
}

.search-filters {
  margin-bottom: 24px;
}

.search-input {
  max-width: 400px;
}

.mb-4 {
  margin-bottom: 16px;
}

.loading-message {
  padding: 20px;
  color: #909399;
  text-align: center;
}

.error-message {
  background-color: #fef0f0;
  color: #f56c6c;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.pagination {
  margin-top: 24px;
  text-align: center;
}

.image-detail {
  display: flex;
  flex-direction: column;
}

.image-detail-content {
  display: flex;
  flex-direction: column;
}

.detail-image-container {
  max-height: 400px;
  overflow: hidden;
  margin-bottom: 24px;
  display: flex;
  justify-content: center;
}

.detail-image {
  max-width: 100%;
  max-height: 400px;
}

.image-metadata {
  flex: 1;
}

.meta-descriptions {
  margin-bottom: 24px;
}

.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.detail-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.detail-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

@media (min-width: 992px) {
  .image-detail-content {
    flex-direction: row;
    gap: 24px;
  }
  
  .detail-image-container {
    flex: 1;
    margin-bottom: 0;
    max-width: 50%;
  }
  
  .image-metadata {
    flex: 1;
  }
}

@media (max-width: 768px) {
  .search-filters {
    flex-direction: column;
  }
  
  .search-input {
    max-width: 100%;
    margin-bottom: 12px;
  }
}

.header-actions {
  display: flex;
  gap: 12px;
}

.mr-2 {
  margin-right: 8px;
}

.detail-footer-actions {
  display: flex;
  justify-content: space-between;
  width: 100%;
}
</style>