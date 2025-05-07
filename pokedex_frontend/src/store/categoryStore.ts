import { defineStore } from 'pinia';
import { ref } from 'vue';
import { CategoryRead, CategoryCreate, CategoryReadWithImages } from '../types';
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

  const fetchCategoryWithImages = async (categoryId: number) => {
    isLoadingCategoryDetail.value = true;
    error.value = null;
    
    try {
      currentCategoryDetail.value = await apiService.getCategoryWithImages(categoryId);
    } catch (err: any) {
      error.value = err.message || 'Failed to load category details';
      console.error('Error fetching category with images:', err);
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

  const updateCategory = async (categoryId: number, categoryData: CategoryCreate) => {
    error.value = null;
    
    try {
      const updatedCategory = await apiService.putCategory(categoryId, categoryData);
      
      // Update in categories list
      const index = categories.value.findIndex(c => c.id === categoryId);
      if (index !== -1) {
        categories.value[index] = updatedCategory;
      }
      
      // Update currentCategoryDetail if needed
      if (currentCategoryDetail.value && currentCategoryDetail.value.id === categoryId) {
        currentCategoryDetail.value = {
          ...updatedCategory,
          images: currentCategoryDetail.value.images
        };
      }
      
      return updatedCategory;
    } catch (err: any) {
      error.value = err.message || 'Failed to update category';
      console.error('Error updating category:', err);
      throw err;
    }
  };

  const deleteCategory = async (categoryId: number) => {
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
    deleteCategory
  };
});