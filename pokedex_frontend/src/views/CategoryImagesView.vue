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
import type { ImageRead, ImageUpdate } from '../types';

const route = useRoute();
const router = useRouter();
const categoryStore = useCategoryStore();
const imageStore = useImageStore();
const uploadDialogVisible = ref(false);
const detailDialogVisible = ref(false);
const metaDialogVisible = ref(false);
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
</script>

<template>
  <div class="category-images-container">
    <ElPageHeader @back="goBack" class="page-header">
      <template #content>
        <div class="page-title">
          <template v-if="categoryStore.currentCategoryDetail">
            <span class="page-title-text">{{ categoryStore.currentCategoryDetail.name }}</span>
            <span v-if="filteredImages.length" class="image-count">
              {{ filteredImages.length }} {{ filteredImages.length === 1 ? 'image' : 'images' }}
            </span>
          </template>
          <span v-else>Bird Species Images</span>
        </div>
      </template>
      
      <template #extra>
        <ElButton type="primary" @click="openUploadDialog">
          Upload Images
        </ElButton>
      </template>
    </ElPageHeader>
    
    <div v-if="categoryStore.isLoadingCategoryDetail || imageStore.isUploading" class="loading-message">
      Loading...
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
          placeholder="Search by title..."
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
        description="No images found in this category. Start by uploading an image!"
      >
        <ElButton type="primary" @click="openUploadDialog">Upload Image</ElButton>
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
              @edit-meta="editImageMeta"
              @delete="deleteImage"
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
    
    <!-- Image Upload Dialog -->
    <ElDialog
      v-model="uploadDialogVisible"
      title="Upload Image"
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
    
    <!-- Image Detail Dialog -->
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
              <ElDescriptionsItem label="Title">{{ selectedImage.title }}</ElDescriptionsItem>
              <ElDescriptionsItem label="Description">{{ selectedImage.description || 'N/A' }}</ElDescriptionsItem>
              <ElDescriptionsItem label="Category">{{ categoryStore.currentCategoryDetail?.name }}</ElDescriptionsItem>
              <ElDescriptionsItem label="Format">{{ selectedImage.metadata.format }}</ElDescriptionsItem>
              <ElDescriptionsItem label="Dimensions">
                {{ selectedImage.metadata.width }} x {{ selectedImage.metadata.height }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="File Size">{{ selectedImage.metadata.fileSize }}</ElDescriptionsItem>
              <ElDescriptionsItem label="Uploaded">{{ new Date(selectedImage.createdDate).toLocaleString() }}</ElDescriptionsItem>
            </ElDescriptions>
          </ElCol>
        </ElRow>
      </div>
      <template #footer>
        <ElButton @click="detailDialogVisible = false">Close</ElButton>
        <ElButton type="primary" @click="editImageMeta(String(selectedImage!.id))">
          Edit Metadata
        </ElButton>
        <ElPopconfirm
          title="Are you sure you want to delete this image?"
          @confirm="handleDeleteConfirm"
        >
          <template #reference>
            <ElButton type="danger">Delete Image</ElButton>
          </template>
        </ElPopconfirm>
      </template>
    </ElDialog>
    
    <!-- Image Metadata Edit Dialog -->
    <ElDialog
      v-model="metaDialogVisible"
      title="Edit Image Metadata"
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
</style>