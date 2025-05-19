import axios from 'axios';
import type { 
  CategoryRead, 
  CategoryReadWithImages, 
  CategoryCreate,
  ImageRead
} from '../types';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

export const apiInstance = api;

const apiService = {
  getCategories: async (skip: number = 0, limit: number = 100): Promise<CategoryRead[]> => {
    const response = await api.get<CategoryRead[]>(`/categories/?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getCategoryWithImages: async (categoryId: number | string): Promise<CategoryReadWithImages> => {
    const response = await api.get<CategoryReadWithImages>(`/categories/${categoryId}/`);
    return response.data;
  },

  uploadImageFile: async (formData: FormData): Promise<ImageRead> => {
    const response = await api.post<ImageRead>('/images/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  createCategory: async (categoryData: CategoryCreate): Promise<CategoryRead> => {
    const response = await api.post<CategoryRead>('/categories/', categoryData);
    return response.data;
  }
};

export default apiService;
