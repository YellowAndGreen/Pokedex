import axios, { AxiosRequestConfig } from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { CategoryRead, CategoryReadWithImages, ImageRead, CategoryCreate, ImageUpdate } from '../types';
import { apiInstance } from './apiService';

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
  const baseSeed = categoryId * 1000; // Base seed for deterministic but unique images per category

  for (let i = 1; i <= count; i++) {
    const imageSeed = baseSeed + i;
    images.push({
      id: categoryId * 100 + i,
      category_id: categoryId,
      original_filename: `bird_photo_${categoryId}_${i}.jpg`,
      stored_filename: `uuid_${categoryId}_${i}.jpg`, // This would be a UUID in a real scenario
      // Using picsum.photos for visible placeholder images
      relative_file_path: `https://picsum.photos/seed/${imageSeed}/600/400`,
      relative_thumbnail_path: `https://picsum.photos/seed/${imageSeed}/150/150`,
      mime_type: 'image/jpeg',
      size_bytes: Math.floor(Math.random() * 5000000) + 500000, // Random size between 500KB and 5MB
      upload_date: new Date(Date.now() - Math.floor(Math.random() * 30) * 86400000).toISOString(), // Random date within last 30 days
      description: `Beautiful bird photo #${i} in the ${mockCategories.find(c => c.id === categoryId)?.name} category`,
      tags: ['bird', 'nature', `photo${i}`]
    });
  }
  
  return images;
};

// Generate mock data for categories with images
let mockCategoriesWithImages: CategoryReadWithImages[] = mockCategories.map(category => ({
  ...category,
  images: generateMockImages(category.id, Math.floor(Math.random() * 5) + 3)
}));

// Setup mock handlers for API requests
export const setupMocks = () => {
  const mock = new MockAdapter(apiInstance, { delayResponse: 500 });

  // GET /api/categories/
  mock.onGet(/\/api\/categories\/?(\?.*)?$/).reply((config: AxiosRequestConfig) => {
    console.log('MOCK GET /api/categories/', config.params);
    // const skip = config.params?.skip ? parseInt(config.params.skip) : 0;
    // const limit = config.params?.limit ? parseInt(config.params.limit) : mockCategories.length;
    // const paginatedCategories = mockCategories.slice(skip, skip + limit);
    return [200, [...mockCategories]]; // Simpler: return all for now
  });

  // GET /api/categories/:id/
  mock.onGet(/\/api\/categories\/(\d+)\/?$/).reply((config: AxiosRequestConfig) => {
    console.log('[MockAdapter] Handler for specific category. Received config.url (relative to baseURL):', config.url);
    
    let categoryIdString: string | undefined;
    const pathParts = config.url?.split('/');

    // Example config.url: "/categories/1/" -> pathParts: ["", "categories", "1", ""]
    // Example config.url: "/categories/1" -> pathParts: ["", "categories", "1"]
    if (pathParts && pathParts.length >= 3 && pathParts[1] === 'categories') {
        categoryIdString = pathParts[2];
    }

    console.log('[MockAdapter] Extracted categoryIdString:', categoryIdString);
    const categoryId = parseInt(categoryIdString as string);
    console.log('[MockAdapter] Attempting to get category. Parsed ID:', categoryId);

    // Diagnostic: Log the state of mockCategoriesWithImages
    console.log('[MockAdapter] Current mockCategoriesWithImages count:', mockCategoriesWithImages.length);
    console.log('[MockAdapter] IDs in mockCategoriesWithImages:', mockCategoriesWithImages.map(c => c.id));
    
    const category = mockCategoriesWithImages.find(c => c.id === categoryId);
    console.log('[MockAdapter] Category found in mock data:', category ? category.name : 'Not Found');

    if (!category) {
      console.error('[MockAdapter] Category with ID', categoryId, 'not found. Returning 404.');
      return [404, { detail: 'Category not found' }];
    }
    console.log('[MockAdapter] Category with ID', categoryId, 'found. Returning 200.');
    return [200, {...category, images: [...category.images]}];
  });

  // POST /api/categories/
  mock.onPost('/api/categories/').reply((config: AxiosRequestConfig) => {
    const data = JSON.parse(config.data) as CategoryCreate;
    console.log('MOCK POST /api/categories/', data);
    const newCategory: CategoryRead = {
      id: Math.max(...mockCategories.map(c => c.id), 0) + 1,
      name: data.name,
      description: data.description,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    mockCategories.push(newCategory);
    mockCategoriesWithImages.push({ ...newCategory, images: [] });
    return [201, {...newCategory}];
  });

  // PUT /api/categories/:id/
  mock.onPut(/\/api\/categories\/(\d+)\/?$/).reply((config: AxiosRequestConfig) => {
    const categoryId = parseInt(config.url!.split('/')[3]);
    const data = JSON.parse(config.data) as CategoryCreate;
    console.log('MOCK PUT /api/categories/' + categoryId + '/', data);
    const index = mockCategories.findIndex(c => c.id === categoryId);
    if (index === -1) {
      return [404, { detail: 'Category not found' }];
    }
    const updatedCategoryData = {
      ...mockCategories[index],
      name: data.name,
      description: data.description,
      updated_at: new Date().toISOString(),
    };
    mockCategories[index] = updatedCategoryData;
    const catWithImagesIndex = mockCategoriesWithImages.findIndex(c => c.id === categoryId);
    if (catWithImagesIndex !== -1) {
      mockCategoriesWithImages[catWithImagesIndex] = {
         ...updatedCategoryData,
         images: mockCategoriesWithImages[catWithImagesIndex].images 
        };
    }
    return [200, {...updatedCategoryData}];
  });

  // DELETE /api/categories/:id/
  mock.onDelete(/\/api\/categories\/(\d+)\/?$/).reply((config: AxiosRequestConfig) => {
    const categoryId = parseInt(config.url!.split('/')[3]);
    console.log('MOCK DELETE /api/categories/' + categoryId + '/');
    const index = mockCategories.findIndex(c => c.id === categoryId);
    if (index === -1) {
      return [404, { detail: 'Category not found' }];
    }
    mockCategories.splice(index, 1);
    mockCategoriesWithImages = mockCategoriesWithImages.filter(c => c.id !== categoryId);
    return [204];
  });

  // POST /api/images/upload/
  mock.onPost('/api/images/upload/').reply((config: AxiosRequestConfig) => {
    // FormData is harder to inspect directly with JSON.parse, access fields directly
    const formData = config.data as FormData;
    const categoryId = Number(formData.get('category_id'));
    const description = formData.get('description') as string | null;
    const tagsRaw = formData.get('tags'); // Assuming tags are sent as JSON stringified array
    let tags: string[] | null = null;
    if (typeof tagsRaw === 'string' && tagsRaw.length > 0) {
        try {
            tags = JSON.parse(tagsRaw);
        } catch (e) {
            console.error('Failed to parse tags from FormData as JSON', tagsRaw);
            // Fallback or error handling if backend expects JSON array for tags
            // If backend expects comma-separated, then: tags = tagsRaw.split(',').map(t => t.trim()).filter(Boolean);
        }
    }

    console.log('MOCK POST /api/images/upload/', { categoryId, description, tags });

    if (isNaN(categoryId) || !mockCategories.find(c => c.id === categoryId)) {
        return [400, { detail: 'Invalid category_id' }];
    }

    const file = formData.get('file') as File;
    const original_filename = file ? file.name : `uploaded_image_${Date.now()}.jpg`;

    const newImageId = Math.max(0, ...mockCategoriesWithImages.flatMap(c => c.images.map(i => i.id))) + 1;
    const newImage: ImageRead = {
      id: newImageId,
      category_id: categoryId,
      original_filename: original_filename,
      stored_filename: `uuid_mock_${newImageId}.jpg`,
      relative_file_path: `images/mock_cat${categoryId}/uuid_mock_${newImageId}.jpg`,
      relative_thumbnail_path: `thumbnails/mock_cat${categoryId}/uuid_mock_${newImageId}_thumb.jpg`,
      mime_type: file ? file.type : 'image/jpeg',
      size_bytes: file ? file.size : Math.floor(Math.random() * 2000000) + 100000,
      upload_date: new Date().toISOString(),
      description: description,
      tags: tags,
    };

    const categoryIndex = mockCategoriesWithImages.findIndex(c => c.id === categoryId);
    mockCategoriesWithImages[categoryIndex].images.push(newImage);
    return [201, {...newImage}];
  });

  // PUT /api/images/:id/
  mock.onPut(/\/api\/images\/(\d+)\/?$/).reply((config: AxiosRequestConfig) => {
    const imageId = parseInt(config.url!.split('/')[3]);
    const data = JSON.parse(config.data) as ImageUpdate;
    console.log('MOCK PUT /api/images/' + imageId + '/', data);
    let updatedImageRef: ImageRead | null = null;
    let found = false;
    mockCategoriesWithImages = mockCategoriesWithImages.map(category => {
      let imagesInCategory = category.images;
      const imageIndex = imagesInCategory.findIndex(img => img.id === imageId);
      if (imageIndex !== -1) {
        found = true;
        const originalImage = imagesInCategory[imageIndex];
        const updatedImage: ImageRead = {
          ...originalImage,
          description: data.description !== undefined ? data.description : originalImage.description,
          tags: data.tags !== undefined ? data.tags : originalImage.tags,
        };
        if (data.category_id !== undefined && data.category_id !== originalImage.category_id) {
          imagesInCategory = imagesInCategory.filter(img => img.id !== imageId);
          const newCategoryIndex = mockCategoriesWithImages.findIndex(c => c.id === data.category_id);
          if (newCategoryIndex !== -1) {
            updatedImage.category_id = data.category_id;
            mockCategoriesWithImages[newCategoryIndex].images.push(updatedImage);
            updatedImageRef = updatedImage;
          }
        } else {
          imagesInCategory[imageIndex] = updatedImage;
          updatedImageRef = updatedImage;
        }
      }
      return { ...category, images: imagesInCategory };
    });
    if (!found || !updatedImageRef) {
      return [404, { detail: 'Image not found or error in update' }];
    }
    return [200, Object.assign({}, updatedImageRef)];
  });

  // DELETE /api/images/:id/
  mock.onDelete(/\/api\/images\/(\d+)\/?$/).reply((config: AxiosRequestConfig) => {
    const imageId = parseInt(config.url!.split('/')[3]);
    console.log('MOCK DELETE /api/images/' + imageId + '/');
    let deleted = false;
    mockCategoriesWithImages = mockCategoriesWithImages.map(category => {
      const initialLength = category.images.length;
      const newImages = category.images.filter(img => img.id !== imageId);
      if (newImages.length < initialLength) {
        deleted = true;
      }
      return { ...category, images: newImages };
    });

    if (!deleted) {
      return [404, { detail: 'Image not found' }];
    }
    return [204];
  });

  // GET /api/images/:id/  (This was missing from the original mock logic)
  mock.onGet(/\/api\/images\/(\d+)\/?$/).reply((config: AxiosRequestConfig) => {
    const imageId = parseInt(config.url!.split('/')[3]);
    console.log('MOCK GET /api/images/' + imageId + '/');
    for (const category of mockCategoriesWithImages) {
      const image = category.images.find(img => img.id === imageId);
      if (image) {
        return [200, {...image}];
      }
    }
    return [404, { detail: 'Image not found' }];
  });

  console.log('Mock adapter setup complete.');
};