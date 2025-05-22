// src/store/categoryStore.ts
import { defineStore } from 'pinia';
import type { CategoryRead, CategoryCreate, CategoryUpdate, HTTPValidationError } from '@/types';
import {
  getCategories,
  getCategoryById,
  createCategory,
  updateCategory,
  deleteCategory
} from '@/services/apiService';

interface CategoryState {
  categories: CategoryRead[];
  currentCategory: CategoryRead | null;
  isLoading: boolean;
  error: string | null;
  validationErrors: HTTPValidationError | null;
}

export const useCategoryStore = defineStore('category', {
  state: (): CategoryState => ({
    categories: [],
    currentCategory: null,
    isLoading: false,
    error: null,
    validationErrors: null,
  }),
  getters: {
    getCategoryNameById: (state) => (id: string): string | undefined => {
      const category = state.categories.find(cat => cat.id === id);
      return category?.name;
    },
  },
  actions: {
    async fetchCategories(skip: number = 0, limit: number = 100) {
      this.isLoading = true;
      this.error = null;
      this.validationErrors = null;
      try {
        this.categories = await getCategories(skip, limit);
      } catch (err: any) {
        this.error = err.message || '获取分类列表失败';
        if (err.data && err.status === 422) {
          this.validationErrors = err.data;
        }
        console.error('Error fetching categories:', err);
      } finally {
        this.isLoading = false;
      }
    },

    async fetchCategoryDetails(id: string) {
      this.isLoading = true;
      this.error = null;
      this.currentCategory = null;
      this.validationErrors = null;
      try {
        this.currentCategory = await getCategoryById(id);
      } catch (err: any) {
        this.error = err.message || `获取分类 ${id} 详情失败`;
        if (err.data && err.status === 422) { // Though unlikely for GET by ID
          this.validationErrors = err.data;
        }
        console.error(`Error fetching category ${id}:`, err);
      } finally {
        this.isLoading = false;
      }
    },

    async addCategory(categoryData: CategoryCreate) {
      this.isLoading = true;
      this.error = null;
      this.validationErrors = null;
      try {
        const newCategory = await createCategory(categoryData);
        this.categories.push(newCategory); // 也可以重新拉取整个列表 this.fetchCategories();
        return newCategory;
      } catch (err: any) {
        this.error = err.message || '创建分类失败';
         if (err.data && err.status === 422) {
          this.validationErrors = err.data;
        }
        console.error('Error creating category:', err);
        throw err; // 重新抛出以便组件可以处理
      } finally {
        this.isLoading = false;
      }
    },

    async editCategory(id: string, categoryData: CategoryUpdate) {
      this.isLoading = true;
      this.error = null;
      this.validationErrors = null;
      try {
        const updated = await updateCategory(id, categoryData);
        const index = this.categories.findIndex(cat => cat.id === id);
        if (index !== -1) {
          this.categories[index] = updated;
        }
        if (this.currentCategory?.id === id) {
          this.currentCategory = updated;
        }
        return updated;
      } catch (err: any) {
        this.error = err.message || `更新分类 ${id} 失败`;
        if (err.data && err.status === 422) {
          this.validationErrors = err.data;
        }
        console.error(`Error updating category ${id}:`, err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async removeCategory(id: string) {
      this.isLoading = true;
      this.error = null;
      this.validationErrors = null;
      try {
        await deleteCategory(id);
        this.categories = this.categories.filter(cat => cat.id !== id);
        if (this.currentCategory?.id === id) {
          this.currentCategory = null;
        }
      } catch (err: any) {
        this.error = err.message || `删除分类 ${id} 失败`;
        // 通常 DELETE 不太会有 422，但以防万一
        if (err.data && err.status === 422) {
          this.validationErrors = err.data;
        }
        console.error(`Error deleting category ${id}:`, err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    // 清除验证错误
    clearValidationErrors() {
      this.validationErrors = null;
    },
    // 清除一般错误
    clearError() {
      this.error = null;
    }
  }
});
