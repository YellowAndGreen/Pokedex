import { defineStore } from 'pinia';
import apiService from '../services/apiService';
import type { CategoryRead, CategoryReadWithImages, CategoryCreate } from '../types';

export const useCategoryStore = defineStore('category', {
  state: () => ({
    categories: [] as CategoryRead[],
    currentCategoryDetail: null as CategoryReadWithImages | null,
    isLoadingList: false,
    isLoadingDetail: false,
    error: null as Error | string | null,
  }),
  actions: {
    async fetchCategories() {
      this.isLoadingList = true;
      this.error = null;
      try {
        this.categories = await apiService.getCategories();
      } catch (err) {
        this.error = err instanceof Error ? err : new Error(String(err));
        console.error('Pinia: fetchCategories error', this.error);
      } finally {
        this.isLoadingList = false;
      }
    },
    async fetchCategoryWithImages(id: string | number) {
      this.isLoadingDetail = true;
      this.error = null;
      this.currentCategoryDetail = null;
      try {
        this.currentCategoryDetail = await apiService.getCategoryWithImages(id);
      } catch (err) {
        this.error = err instanceof Error ? err : new Error(String(err));
        console.error('Pinia: fetchCategoryWithImages error', this.error);
      } finally {
        this.isLoadingDetail = false;
      }
    },
    async addCategory(categoryData: CategoryCreate) {
      try {
        const newCategory = await apiService.createCategory(categoryData);
        await this.fetchCategories();
        return newCategory;
      } catch (err) {
        this.error = err instanceof Error ? err : new Error(String(err));
        console.error('Pinia: addCategory error', this.error);
        throw err;
      }
    },
  },
});
