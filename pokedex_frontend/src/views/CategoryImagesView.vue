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
  ElTag,
  ElDivider,
  ElInput
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
  const id = Number(route.params.id);
  return isNaN(id) ? 0 : id;
});

// Filtered images based on search
const filteredImages = computed(() => {
  if (!categoryStore.currentCategoryDetail?.images) return [];
  
  if (!searchQuery.value) return categoryStore.currentCategoryDetail.images;
  
  const query = searchQuery.value.toLowerCase();
  return categoryStore.currentCategoryDetail.images.filter(image => 
    image.description.toLowerCase().includes(query) || 
    image.tags.some(tag => tag.toLowerCase().includes(query)) ||
    image.original_filename.toLowerCase().includes(query)
  );
});

// Paginated images
const paginatedImages = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value;
  return filteredImages.value.slice(startIndex, startIndex + pageSize.value);
});

onMounted(async () => {
  if (categoryId.value) {
    await categoryStore.fetchCategoryWithImages(categoryId.value);
  }
});

// Watch for route changes
watch(() => route.params.id, async (newId) => {
  const id = Number(newId);
  if (!isNaN(id) && id !== categoryId.value) {
    await categoryStore.fetchCategoryWithImages(id);
    currentPage.value = 1; // Reset pagination when category changes
  }
});

const openUploadDialog = () => {
  uploadDialogVisible.value = true;
};

const closeUploadDialog = () => {
  uploadDialogVisible.value = false;
};

const handleUploadSuccess = () => {
  uploadDialogVisible.value = false;
  categoryStore.fetchCategoryWithImages(categoryId.value);
};

const handleUploadError = (error: Error) => {
  console.error('Upload error:', error);
};

const viewImageDetail = (imageId: number) => {
  if (categoryStore.currentCategoryDetail?.images) {
    const image = categoryStore.currentCategoryDetail.images.find(img => img.id === imageId);
    if (image) {
      selectedImage.value = image;
      detailDialogVisible.value = true;
    }
  }
};

const editImageMeta = (imageId: number) => {
  if (categoryStore.currentCategoryDetail?.images) {
    const image = categoryStore.currentCategoryDetail.images.find(img => img.id === imageId);
    if (image) {
      selectedImage.value = image;
      detailDialogVisible.value = false;
      metaDialogVisible.value = true;
    }
  }
};

const deleteImage = async (imageId: number) => {
  try {
    await imageStore.deleteImage(imageId, categoryId.value);
  } catch (error) {
    console.error('Delete image error:', error);
  }
};

const handleMetaFormSubmit = async (data: ImageUpdate & { id: number }) => {
  try {
    const { id, ...updateData } = data;
    await imageStore.updateImageMetadata(id, updateData);
    metaDialogVisible.value = false;
  } catch (error) {
    console.error('Update metadata error:', error);
  }
};

const closeMetaDialog = () => {
  metaDialogVisible.value = false;
};

const goBack = () => {
  router.push('/');
};

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' bytes';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
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
          placeholder="Search by description, tags, or filename..."
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
      v-model="detailDialogVisible"
      :title="selectedImage?.original_filename"
      width="70%"
      destroy-on-close
    >
      <div v-if="selectedImage" class="image-detail">
        <div class="image-detail-content">
          <div class="detail-image-container">
            <!-- For demo, using a placeholder image -->
            <ElImage 
              :src="`https://images.pexels.com/photos/${selectedImage.id % 10 + 1}/bird-photo.jpg`" 
              fit="contain"
              :preview-src-list="[`https://images.pexels.com/photos/${selectedImage.id % 10 + 1}/bird-photo.jpg`]"
              class="detail-image"
            />
          </div>
          
          <div class="image-metadata">
            <ElDescriptions border :column="1" class="meta-descriptions">
              <ElDescriptionsItem label="File Name">
                {{ selectedImage.original_filename }}
              </ElDescriptionsItem>
              
              <ElDescriptionsItem label="File Type">
                {{ selectedImage.mime_type }}
              </ElDescriptionsItem>
              
              <ElDescriptionsItem label="File Size">
                {{ formatFileSize(selectedImage.size_bytes) }}
              </ElDescriptionsItem>
              
              <ElDescriptionsItem label="Upload Date">
                {{ new Date(selectedImage.upload_date).toLocaleString() }}
              </ElDescriptionsItem>
              
              <ElDescriptionsItem label="Description">
                {{ selectedImage.description || 'No description provided' }}
              </ElDescriptionsItem>
              
              <ElDescriptionsItem label="Tags">
                <div v-if="selectedImage.tags.length" class="tag-container">
                  <ElTag 
                    v-for="tag in selectedImage.tags" 
                    :key="tag" 
                    type="info" 
                    size="small"
                    class="detail-tag"
                  >
                    {{ tag }}
                  </ElTag>
                </div>
                <span v-else>No tags</span>
              </ElDescriptionsItem>
            </ElDescriptions>
            
            <div class="detail-actions">
              <ElButton type="primary" @click="editImageMeta(selectedImage.id)">
                Edit Metadata
              </ElButton>
              
              <ElButton 
                type="danger" 
                @click="() => { 
                  deleteImage(selectedImage.id);
                  detailDialogVisible = false;
                }"
              >
                Delete Image
              </ElButton>
            </div>
          </div>
        </div>
      </div>
    </ElDialog>
    
    <!-- Image Metadata Edit Dialog -->
    <ElDialog
      v-model="metaDialogVisible"
      title="Edit Image Metadata"
      width="50%"
      destroy-on-close
    >
      <ImageMetaForm
        v-if="selectedImage"
        :initial-data="selectedImage"
        @submit="handleMetaFormSubmit"
        @cancel="closeMetaDialog"
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