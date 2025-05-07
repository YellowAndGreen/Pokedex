import axios from 'axios';
import { CategoryRead, CategoryReadWithImages, ImageRead } from '../types';

const mockCategories: CategoryRead[] = [
  {
    id: 1,
    name: 'Hummingbirds',
    description: 'Family of small, colorful birds known for their hovering flight and rapid wing beats.',
    created_at: '2025-01-05T10:30:00Z',
    updated_at: '2025-01-05T10:30:00Z'
  },
  {
    id: 2,
    name: 'Eagles',
    description: 'Large birds of prey with powerful vision and impressive wingspans.',
    created_at: '2025-01-08T14:20:00Z',
    updated_at: '2025-01-10T09:15:00Z'
  },
  {
    id: 3,
    name: 'Penguins',
    description: 'Flightless aquatic birds primarily found in the Southern Hemisphere.',
    created_at: '2025-01-12T16:45:00Z',
    updated_at: '2025-01-12T16:45:00Z'
  },
  {
    id: 4,
    name: 'Parrots',
    description: 'Colorful birds with curved bills, known for their intelligence and ability to mimic sounds.',
    created_at: '2025-01-15T11:10:00Z',
    updated_at: '2025-01-16T14:30:00Z'
  }
];

// Generate mock images for each category
const generateMockImages = (categoryId: number, count: number): ImageRead[] => {
  const images: ImageRead[] = [];
  
  for (let i = 1; i <= count; i++) {
    images.push({
      id: categoryId * 100 + i,
      category_id: categoryId,
      original_filename: `bird_photo_${categoryId}_${i}.jpg`,
      relative_file_path: `cat${categoryId}/bird_photo_${i}.jpg`,
      relative_thumbnail_path: `cat${categoryId}/thumbnails/bird_photo_${i}.jpg`,
      mime_type: 'image/jpeg',
      size_bytes: Math.floor(Math.random() * 5000000) + 500000, // Random size between 500KB and 5MB
      upload_date: new Date(Date.now() - Math.floor(Math.random() * 30) * 86400000).toISOString(), // Random date within last 30 days
      description: `Beautiful bird photo #${i} in the ${mockCategories.find(c => c.id === categoryId)?.name} category`,
      tags: ['bird', 'nature', `photo${i}`, categoryId === 1 ? 'hummingbird' : 
             categoryId === 2 ? 'eagle' : 
             categoryId === 3 ? 'penguin' : 'parrot']
    });
  }
  
  return images;
};

// Generate mock data for categories with images
let mockCategoriesWithImages: CategoryReadWithImages[] = mockCategories.map(category => ({
  ...category,
  images: generateMockImages(category.id, category.id === 1 ? 8 : 
                                         category.id === 2 ? 5 : 
                                         category.id === 3 ? 6 : 4)
}));

// Setup mock handlers for API requests
export const setupMocks = () => {
  // Mock API adapter
  const mockAdapter = {
    // GET /api/categories
    getCategories: () => {
      return Promise.resolve([...mockCategories]);
    },
    
    // GET /api/categories/:id
    getCategoryWithImages: (categoryId: number) => {
      const category = mockCategoriesWithImages.find(c => c.id === categoryId);
      if (!category) {
        return Promise.reject(new Error('Category not found'));
      }
      return Promise.resolve({...category, images: [...category.images]});
    },
    
    // POST /api/categories
    createCategory: (data: any) => {
      const newCategory: CategoryRead = {
        id: Math.max(...mockCategories.map(c => c.id), 0) + 1,
        name: data.name,
        description: data.description,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      mockCategories.push(newCategory);
      mockCategoriesWithImages.push({
        ...newCategory,
        images: []
      });
      
      return Promise.resolve({...newCategory});
    },
    
    // PUT /api/categories/:id
    updateCategory: (categoryId: number, data: any) => {
      const index = mockCategories.findIndex(c => c.id === categoryId);
      if (index === -1) {
        return Promise.reject(new Error('Category not found'));
      }
      
      const updatedCategory = {
        ...mockCategories[index],
        name: data.name,
        description: data.description,
        updated_at: new Date().toISOString()
      };
      
      mockCategories[index] = updatedCategory;
      
      const categoryWithImagesIndex = mockCategoriesWithImages.findIndex(c => c.id === categoryId);
      if (categoryWithImagesIndex !== -1) {
        mockCategoriesWithImages[categoryWithImagesIndex] = {
          ...updatedCategory,
          images: mockCategoriesWithImages[categoryWithImagesIndex].images
        };
      }
      
      return Promise.resolve({...updatedCategory});
    },
    
    // DELETE /api/categories/:id
    deleteCategory: (categoryId: number) => {
      const index = mockCategories.findIndex(c => c.id === categoryId);
      if (index === -1) {
        return Promise.reject(new Error('Category not found'));
      }
      
      mockCategories.splice(index, 1);
      mockCategoriesWithImages = mockCategoriesWithImages.filter(c => c.id !== categoryId);
      
      return Promise.resolve();
    },
    
    // POST /api/images/upload
    uploadImage: (formData: FormData) => {
      const categoryId = Number(formData.get('category_id'));
      const description = formData.get('description') as string || '';
      const tags = (formData.get('tags') as string || '').split(',').map(t => t.trim()).filter(Boolean);
      
      // Create new image
      const newImageId = Math.max(...mockCategoriesWithImages.flatMap(c => c.images.map(i => i.id)), 0) + 1;
      const newImage: ImageRead = {
        id: newImageId,
        category_id: categoryId,
        original_filename: `uploaded_image_${Date.now()}.jpg`,
        relative_file_path: `cat${categoryId}/uploaded_image_${Date.now()}.jpg`,
        relative_thumbnail_path: `cat${categoryId}/thumbnails/uploaded_image_${Date.now()}.jpg`,
        mime_type: 'image/jpeg',
        size_bytes: Math.floor(Math.random() * 2000000) + 100000,
        upload_date: new Date().toISOString(),
        description,
        tags
      };
      
      // Add to category
      const categoryIndex = mockCategoriesWithImages.findIndex(c => c.id === categoryId);
      if (categoryIndex === -1) {
        return Promise.reject(new Error('Category not found'));
      }
      
      mockCategoriesWithImages[categoryIndex].images.push(newImage);
      
      return Promise.resolve({...newImage});
    },
    
    // PUT /api/images/:id
    updateImage: (imageId: number, data: any) => {
      let updatedImage: ImageRead | null = null;
      
      mockCategoriesWithImages = mockCategoriesWithImages.map(category => {
        const imageIndex = category.images.findIndex(img => img.id === imageId);
        if (imageIndex !== -1) {
          const originalImage = category.images[imageIndex];
          
          // If category_id changed, need to move the image
          if (data.category_id && data.category_id !== originalImage.category_id) {
            // Remove from current category
            const updatedImages = category.images.filter(img => img.id !== imageId);
            
            // Find new category and add image there
            const newCategoryIndex = mockCategoriesWithImages.findIndex(c => c.id === data.category_id);
            if (newCategoryIndex !== -1) {
              updatedImage = {
                ...originalImage,
                category_id: data.category_id,
                description: data.description ?? originalImage.description,
                tags: data.tags ?? originalImage.tags
              };
              
              mockCategoriesWithImages[newCategoryIndex].images.push(updatedImage);
            }
            
            return {
              ...category,
              images: updatedImages
            };
          } else {
            // Just update in place
            updatedImage = {
              ...originalImage,
              description: data.description ?? originalImage.description,
              tags: data.tags ?? originalImage.tags
            };
            
            return {
              ...category,
              images: category.images.map(img => 
                img.id === imageId ? updatedImage! : img
              )
            };
          }
        }
        
        return category;
      });
      
      if (!updatedImage) {
        return Promise.reject(new Error('Image not found'));
      }
      
      return Promise.resolve({...updatedImage});
    },
    
    // DELETE /api/images/:id
    deleteImage: (imageId: number) => {
      let deleted = false;
      
      mockCategoriesWithImages = mockCategoriesWithImages.map(category => {
        const imageIndex = category.images.findIndex(img => img.id === imageId);
        if (imageIndex !== -1) {
          deleted = true;
          return {
            ...category,
            images: category.images.filter(img => img.id !== imageId)
          };
        }
        return category;
      });
      
      if (!deleted) {
        return Promise.reject(new Error('Image not found'));
      }
      
      return Promise.resolve();
    }
  };
  
  // Mock interceptors for API requests
  axios.interceptors.request.use(config => {
    // Return config to continue
    return config;
  });
  
  axios.interceptors.response.use(
    async response => {
      // Mock the API responses based on the request
      const url = response.config.url || '';
      const method = response.config.method?.toLowerCase() || '';
      const data = response.config.data ? JSON.parse(response.config.data) : {};
      
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // Categories endpoint
      if (url.match(/^\/api\/categories\/?$/)) {
        if (method === 'get') {
          response.data = await mockAdapter.getCategories();
          return response;
        }
        
        if (method === 'post') {
          response.data = await mockAdapter.createCategory(data);
          return response;
        }
      }
      
      const categoryDetailMatch = url.match(/^\/api\/categories\/(\d+)\/?$/);
      if (categoryDetailMatch) {
        const categoryId = parseInt(categoryDetailMatch[1], 10);
        
        if (method === 'get') {
          response.data = await mockAdapter.getCategoryWithImages(categoryId);
          return response;
        }
        
        if (method === 'put') {
          response.data = await mockAdapter.updateCategory(categoryId, data);
          return response;
        }
        
        if (method === 'delete') {
          await mockAdapter.deleteCategory(categoryId);
          response.data = null;
          return response;
        }
      }
      
      // Images endpoints
      if (url.includes('/api/images/upload') && method === 'post') {
        response.data = await mockAdapter.uploadImage(response.config.data);
        return response;
      }
      
      const imageMatch = url.match(/^\/api\/images\/(\d+)\/?$/);
      if (imageMatch) {
        const imageId = parseInt(imageMatch[1], 10);
        
        if (method === 'put') {
          response.data = await mockAdapter.updateImage(imageId, data);
          return response;
        }
        
        if (method === 'delete') {
          await mockAdapter.deleteImage(imageId);
          response.data = null;
          return response;
        }
      }
      
      // If not handled, reject with 404
      return Promise.reject(new Error('Not Found'));
    },
    error => {
      console.error('Mock API error:', error);
      return Promise.reject(error);
    }
  );
  
  console.log('Mock data service initialized');
};