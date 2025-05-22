// src/store/imageStore.ts
import { defineStore } from 'pinia';
import type { ImageRead, ImageCreateMetadata, ImageUpdate, HTTPValidationError } from '@/types';
import {
  getImages,
  getImageById,
  uploadImage,
  updateImage,
  deleteImage
} from '@/services/apiService';

interface ImageState {
  images: ImageRead[];
  currentImage: ImageRead | null;
  isLoading: boolean;
  error: string | null;
  validationErrors: HTTPValidationError | null;
  // 可以考虑添加分页信息
  totalImages: number;
  currentPage: number;
  imagesPerPage: number;
}

export const useImageStore = defineStore('image', {
  state: (): ImageState => ({
    images: [],
    currentImage: null,
    isLoading: false,
    error: null,
    validationErrors: null,
    totalImages: 0,
    currentPage: 1,
    imagesPerPage: 50, // 默认值，可以从 API 或配置中获取
  }),
  actions: {
    async fetchImages(
        skip: number = 0,
        limit: number = 50,
        categoryId?: string
      ) {
      this.isLoading = true;
      this.error = null;
      this.validationErrors = null;
      try {
        // 注意：OpenAPI 直接返回数组，没有分页元数据。
        // 如果后端支持返回总数，这里可以更新 totalImages。
        // 目前，我们只能获取当前页的图片。
        const fetchedImages = await getImages(skip, limit, categoryId);
        this.images = fetchedImages;
        // 假设 totalImages 和 currentPage 需要另外管理或通过其他方式获取
        // this.totalImages = ... ;
        // this.currentPage = (skip / limit) + 1;
        // this.imagesPerPage = limit;

      } catch (err: any) {
        this.error = err.message || '获取图片列表失败';
        if (err.data && err.status === 422) {
          this.validationErrors = err.data;
        }
        console.error('Error fetching images:', err);
      } finally {
        this.isLoading = false;
      }
    },

    async fetchImageDetails(id: string) {
      this.isLoading = true;
      this.error = null;
      this.currentImage = null;
      this.validationErrors = null;
      try {
        this.currentImage = await getImageById(id);
      } catch (err: any) {
        this.error = err.message || `获取图片 ${id} 详情失败`;
        if (err.data && err.status === 422) {
          this.validationErrors = err.data;
        }
        console.error(`Error fetching image ${id}:`, err);
      } finally {
        this.isLoading = false;
      }
    },

    async addNewImage(imageFile: File, metadata: ImageCreateMetadata) {
      this.isLoading = true;
      this.error = null;
      this.validationErrors = null;
      try {
        const newImage = await uploadImage(imageFile, metadata);
        this.images.unshift(newImage); // 添加到列表开头，或重新拉取
        return newImage;
      } catch (err: any) {
        this.error = err.message || '上传图片失败';
        if (err.data && err.status === 422) {
          this.validationErrors = err.data;
        }
        console.error('Error uploading image:', err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async editImage(id: string, imageData: ImageUpdate) {
      this.isLoading = true;
      this.error = null;
      this.validationErrors = null;
      try {
        const updated = await updateImage(id, imageData);
        const index = this.images.findIndex(img => img.id === id);
        if (index !== -1) {
          this.images[index] = updated;
        }
        if (this.currentImage?.id === id) {
          this.currentImage = updated;
        }
        return updated;
      } catch (err: any) {
        this.error = err.message || `更新图片 ${id} 失败`;
         if (err.data && err.status === 422) {
          this.validationErrors = err.data;
        }
        console.error(`Error updating image ${id}:`, err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async removeImage(id: string) {
      this.isLoading = true;
      this.error = null;
      this.validationErrors = null;
      try {
        await deleteImage(id);
        this.images = this.images.filter(img => img.id !== id);
        if (this.currentImage?.id === id) {
          this.currentImage = null;
        }
      } catch (err: any) {
        this.error = err.message || `删除图片 ${id} 失败`;
        if (err.data && err.status === 422) {
          this.validationErrors = err.data;
        }
        console.error(`Error deleting image ${id}:`, err);
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
