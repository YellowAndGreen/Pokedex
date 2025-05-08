import axios from 'axios';
import { setupMocks } from './mockData';
import type { 
  CategoryRead, 
  CategoryCreate, 
  CategoryReadWithImages,
  ImageRead,
  ImageUpdate
} from '../types';

// Create axios instance
const api = axios.create({
  baseURL: '/api', // This would be replaced with actual API URL in a real environment
  headers: {
    'Content-Type': 'application/json'
  }
});

export const apiInstance = api; // Export the instance

// API service functions
const apiService = {
  // Category endpoints
  getCategories: async (skip = 0, limit = 100): Promise<CategoryRead[]> => {
    const response = await api.get(`/categories/?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getCategoryWithImages: async (categoryId: string): Promise<CategoryReadWithImages> => {
    const response = await api.get(`/categories/${categoryId}/`);
    console.log('[apiService] getCategoryWithImages response.data:', JSON.parse(JSON.stringify(response.data)));
    console.log('[apiService] getCategoryWithImages typeof response.data:', typeof response.data, 'isArray:', Array.isArray(response.data));
    return response.data;
  },

  postCategory: async (data: CategoryCreate): Promise<CategoryRead> => {
    const response = await api.post('/categories/', data);
    return response.data;
  },

  putCategory: async (categoryId: string, data: CategoryCreate): Promise<CategoryRead> => {
    const response = await api.put(`/categories/${categoryId}/`, data);
    return response.data;
  },

  deleteCategoryById: async (categoryId: string): Promise<void> => {
    await api.delete(`/categories/${categoryId}/`);
  },

  // Image endpoints
  uploadImageFile: async (formData: FormData): Promise<ImageRead> => {
    const response = await api.post('/images/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  getImage: async (imageId: string): Promise<ImageRead> => {
    const response = await api.get(`/images/${imageId}/`);
    return response.data;
  },

  updateImage: async (imageId: string, data: ImageUpdate): Promise<ImageRead> => {
    const response = await api.put(`/images/${imageId}/`, data);
    return response.data;
  },

  deleteImageById: async (imageId: string): Promise<void> => {
    console.log('[apiService] deleteImageById called with imageId:', imageId);
    await api.delete(`/images/${imageId}/`);
    console.log('[apiService] api.delete /images/:id finished for imageId:', imageId);
  }
};

// Initialize mock data for development
if (import.meta.env.DEV) {
  setupMocks();
}

export default apiService;