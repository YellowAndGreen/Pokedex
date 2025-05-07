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
    const categoryId = Number(formData.get('category_id'));
    
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

  const updateImageMetadata = async (imageId: number, imageData: ImageUpdate) => {
    isUpdating.value = true;
    error.value = null;
    const categoryStore = useCategoryStore();
    
    try {
      const updatedImage = await apiService.updateImage(imageId, imageData);
      
      // Refresh the category images if we have the current category loaded
      if (categoryStore.currentCategoryDetail && updatedImage.category_id) {
        await categoryStore.fetchCategoryWithImages(updatedImage.category_id);
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

  const deleteImage = async (imageId: number, categoryId: number) => {
    isDeleting.value = true;
    error.value = null;
    const categoryStore = useCategoryStore();
    
    try {
      await apiService.deleteImageById(imageId);
      
      // Refresh the category images
      if (categoryId) {
        await categoryStore.fetchCategoryWithImages(categoryId);
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to delete image';
      console.error('Error deleting image:', err);
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