import { defineStore } from 'pinia';
import { ref } from 'vue';
import { ImageUpdate } from '../types';
import apiService from '../services/apiService';
import { useCategoryStore } from './categoryStore';

export const useImageStore = defineStore('image', () => {
  const isUploading = ref(false);
  const isUpdating = ref(false);
  const isDeleting = ref(false);
  const error = ref<string | null>(null);

  const uploadImage = async (formData: FormData) => {
    isUploading.value = true;
    error.value = null;
    const categoryStore = useCategoryStore();
    const categoryId = formData.get('category_id') as string;
    
    try {
      const newImage = await apiService.uploadImageFile(formData);
      
      // Refresh the category images
      if (categoryId) {
        await categoryStore.fetchCategoryWithImages(categoryId);
      }
      
      return newImage;
    } catch (err: any) {
      error.value = err.message || 'Failed to upload image';
      console.error('Error uploading image:', err);
      throw err;
    } finally {
      isUploading.value = false;
    }
  };

  const updateImageMetadata = async (imageId: string, imageData: ImageUpdate) => {
    isUpdating.value = true;
    error.value = null;
    const categoryStore = useCategoryStore();
    
    try {
      const updatedImage = await apiService.updateImage(imageId, imageData);
      
      // Refresh the category images if we have the current category loaded
      if (categoryStore.currentCategoryDetail && updatedImage.categoryId) {
        await categoryStore.fetchCategoryWithImages(updatedImage.categoryId);
      }
      
      return updatedImage;
    } catch (err: any) {
      error.value = err.message || 'Failed to update image metadata';
      console.error('Error updating image metadata:', err);
      throw err;
    } finally {
      isUpdating.value = false;
    }
  };

  const deleteImage = async (imageId: string, categoryId: string) => {
    console.log('[store] imageStore.deleteImage called with imageId:', imageId, 'categoryId:', categoryId);
    isDeleting.value = true;
    error.value = null;
    const categoryStore = useCategoryStore();
    
    try {
      await apiService.deleteImageById(imageId);
      console.log('[store] apiService.deleteImageById finished for imageId:', imageId);
      
      if (categoryId) {
        console.log('[store] Refreshing category after delete for categoryId:', categoryId);
        await categoryStore.fetchCategoryWithImages(categoryId);
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to delete image';
      console.error('[store] Error deleting image in store for imageId:', imageId, err);
      throw err;
    } finally {
      isDeleting.value = false;
    }
  };

  return {
    isUploading,
    isUpdating,
    isDeleting,
    error,
    uploadImage,
    updateImageMetadata,
    deleteImage
  };
});