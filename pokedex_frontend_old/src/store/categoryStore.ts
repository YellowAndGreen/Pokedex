import { defineStore } from 'pinia';
import { ref } from 'vue';
import { CategoryRead, CategoryCreate, CategoryReadWithImages, CategoryUpdate, ImageRead } from '../types';
import apiService from '../services/apiService';

export const useCategoryStore = defineStore('category', () => {
  const categories = ref<CategoryRead[]>([]);
  const currentCategoryDetail = ref<CategoryReadWithImages | null>(null);
  const isLoadingCategories = ref(false);
  const isLoadingCategoryDetail = ref(false);
  const error = ref<string | null>(null);

  const fetchCategories = async () => {
    isLoadingCategories.value = true;
    error.value = null;
    
    try {
      categories.value = await apiService.getCategories();
    } catch (err: any) {
      error.value = err.message || 'Failed to load categories';
      console.error('Error fetching categories:', err);
    } finally {
      isLoadingCategories.value = false;
    }
  };

  const fetchCategoryWithImages = async (categoryId: string) => {
    console.log('[store] fetchCategoryWithImages called with ID:', categoryId);
    isLoadingCategoryDetail.value = true;
    error.value = null;
    
    try {
      currentCategoryDetail.value = await apiService.getCategoryWithImages(categoryId);
      console.log('[store] currentCategoryDetail updated:', JSON.parse(JSON.stringify(currentCategoryDetail.value))); // Deep copy for logging complex objects
    } catch (err: any) {
      console.error('[store] Error fetching category with images:', err);
      error.value = err.message || 'Failed to load category details';
    } finally {
      isLoadingCategoryDetail.value = false;
    }
  };

  const createCategory = async (categoryData: CategoryCreate) => {
    error.value = null;
    
    try {
      const newCategory = await apiService.postCategory(categoryData);
      categories.value.push(newCategory);
      return newCategory;
    } catch (err: any) {
      error.value = err.message || 'Failed to create category';
      console.error('Error creating category:', err);
      throw err;
    }
  };

  const updateCategory = async (categoryId: string, categoryData: CategoryUpdate) => {
    error.value = null;
    
    try {
      const updatedCategory = await apiService.putCategory(categoryId, categoryData);
      
      // Update in categories list
      const index = categories.value.findIndex(c => c.id === categoryId);
      if (index !== -1) {
        // Ensure all fields of CategoryRead are present after partial update
        categories.value[index] = { ...categories.value[index], ...updatedCategory }; 
      }
      
      // Update currentCategoryDetail if needed
      if (currentCategoryDetail.value && currentCategoryDetail.value.id === categoryId) {
        // Preserve images array, apply other updates from updatedCategory
        currentCategoryDetail.value = {
          ...currentCategoryDetail.value, // Keep existing fields like images
          ...updatedCategory // Apply changes from the PUT response
        };
      }
      
      return updatedCategory;
    } catch (err: any) {
      error.value = err.message || 'Failed to update category';
      console.error('Error updating category:', err);
      throw err;
    }
  };

  const deleteCategory = async (categoryId: string) => {
    error.value = null;
    
    try {
      await apiService.deleteCategoryById(categoryId);
      categories.value = categories.value.filter(c => c.id !== categoryId);
      
      if (currentCategoryDetail.value?.id === categoryId) {
        currentCategoryDetail.value = null;
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to delete category';
      console.error('Error deleting category:', err);
      throw err;
    }
  };

  const uploadImageAndUpdateCategoryThumbnailIfNeeded = async (
    formData: FormData, 
    categoryId: string, 
    setAsThumbnail: boolean
  ): Promise<ImageRead> => {
    error.value = null;
    try {
      const newImage = await apiService.uploadImageFile(formData);
      
      // Add the new image to the current category detail if it's loaded
      if (currentCategoryDetail.value && currentCategoryDetail.value.id === categoryId) {
        currentCategoryDetail.value.images.push(newImage);
      }

      if (setAsThumbnail) {
        await updateCategory(categoryId, { thumbnailUrl: newImage.imageUrl });
      }
      return newImage;
    } catch (err: any) {
      error.value = err.message || 'Failed to upload image or update thumbnail';
      console.error('Error in uploadImageAndUpdateCategoryThumbnailIfNeeded:', err);
      throw err;
    }
  };

  return {
    categories,
    currentCategoryDetail,
    isLoadingCategories,
    isLoadingCategoryDetail,
    error,
    fetchCategories,
    fetchCategoryWithImages,
    createCategory,
    updateCategory,
    deleteCategory,
    uploadImageAndUpdateCategoryThumbnailIfNeeded
  };
});