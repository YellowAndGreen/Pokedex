import MockAdapter from 'axios-mock-adapter';
import { CategoryRead, CategoryReadWithImages, ImageRead, CategoryCreate, ImageUpdate } from '../types';
import { apiInstance } from './apiService';

let mockCategories: CategoryRead[] = [
  {
    id: '03e9d0a1-5b5a-4b7d-9e9a-3a1b3b4b5b6b',
    name: 'Hummingbirds',
    description: 'Family of small, colorful birds known for their hovering flight and rapid wing beats.',
    thumbnailUrl: 'https://cdn.example.com/uploads/03e9d0a1/thumbnail.jpg',
    createdDate: '2025-01-05T10:30:00Z',
    updatedDate: '2025-01-05T10:30:00Z'
  },
  {
    id: '7b8c9d0e-1f2g-3h4i-5j6k-7l8m9n0o1p2',
    name: 'Eagles',
    description: 'Large birds of prey with powerful vision and impressive wingspans.',
    thumbnailUrl: 'https://cdn.example.com/uploads/7b8c9d0e/thumbnail.jpg',
    createdDate: '2025-01-08T14:20:00Z',
    updatedDate: '2025-01-10T09:15:00Z'
  },
  {
    id: 'a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p',
    name: 'Penguins',
    description: 'Flightless aquatic birds primarily found in the Southern Hemisphere.',
    thumbnailUrl: 'https://cdn.example.com/uploads/a1b2c3d4/thumbnail.jpg',
    createdDate: '2025-01-12T16:45:00Z',
    updatedDate: '2025-01-12T16:45:00Z'
  },
  {
    id: 'q1w2e3r4-t5y6-u7i8-o9p0-a1s2d3f4g5h',
    name: 'Parrots',
    description: 'Colorful birds with curved bills, known for their intelligence and ability to mimic sounds.',
    thumbnailUrl: 'https://cdn.example.com/uploads/q1w2e3r4/thumbnail.jpg',
    createdDate: '2025-01-15T11:10:00Z',
    updatedDate: '2025-01-16T14:30:00Z'
  }
];

const generateMockImages = (categoryId: string, count: number): ImageRead[] => {
  return Array.from({ length: count }, (_, i) => {
    const imageIndex = i + 1;
    const category = mockCategories.find(c => c.id === categoryId);
    const categoryName = category ? category.name : 'Category';
    const imageTitle = `Sample Image ${imageIndex} for ${categoryName}`;

    return {
      id: `${categoryId}_image_${imageIndex.toString().padStart(3, '0')}`,
      title: imageTitle,
      description: `Photo #${imageIndex} in ${categoryName}`,
      imageUrl: `https://via.placeholder.com/400x300/CCCCCC/000000?text=${encodeURIComponent(imageTitle.replace(/ /g, '+'))}`,
      categoryId,
      createdDate: new Date().toISOString(),
      metadata: {
        width: 400,
        height: 300,
        fileSize: '10KB', // Example, actual size will vary
        format: 'PNG' // Placeholder images are typically PNG or JPEG
      }
    };
  });
};

let mockCategoriesWithImages: CategoryReadWithImages[] = mockCategories.map(category => ({
  ...category,
  images: generateMockImages(category.id, Math.floor(Math.random() * 5) + 3)
}));

export const setupMocks = () => {
  const mock = new MockAdapter(apiInstance, { delayResponse: 500 });

  // Categories endpoints
  mock.onGet(/^\/api\/categories\/?(\?.*)?$/).reply(config => {
    // Log the actual URL called to help with debugging
    console.log('[MockAdapter] GET /api/categories called with URL:', config.url);
    // We ignore skip and limit for now in the mock, always return all categories
    return [200, [...mockCategories]];
  });

  mock.onGet(/\/api\/categories\/([a-f0-9-]+)\/?/).reply(config => {
    console.log('[MockAdapter] config received for /api/categories/:id/:', JSON.parse(JSON.stringify(config, null, 2)));

    let categoryIdFromUrl = '';
    const urlToParse = config.url || ''; 

    // Check if the URL path matches the expected pattern for extracting the ID
    // The regex used in onGet is /\/api\/categories\/([a-f0-9-]+)\/?/
    // match[0] would be the full matched part of the URL (e.g., /api/categories/some-id/)
    // match[1] would be the captured ID (e.g., some-id)
    const idMatcher = /\/api\/categories\/([a-f0-9-]+)\/?/;
    const match = urlToParse.match(idMatcher);

    if (match && match[1]) {
      categoryIdFromUrl = match[1];
      console.log(`[MockAdapter] Extracted ID using regex match on urlToParse ('${urlToParse}'): "${categoryIdFromUrl}"`);
    } else {
      // Fallback or more verbose splitting if direct regex match on config.url fails
      console.log(`[MockAdapter] Could not extract ID using direct regex match on urlToParse: "${urlToParse}". Attempting split based logic...`);
      if (config.baseURL && urlToParse.startsWith(config.baseURL)) {
        const pathAfterBase = urlToParse.substring(config.baseURL.length);
        const parts = pathAfterBase.split('/').filter(p => p); // filter out empty strings
        if (parts.length > 1 && parts[0] === 'categories') { //e.g. /categories/id -> parts = [categories, id]
            categoryIdFromUrl = parts[1];
        }
        console.log(`[MockAdapter] Attempting to parse ID from pathAfterBase: "${pathAfterBase}", categoryIdFromUrl: "${categoryIdFromUrl}"`);
      } else if (urlToParse.startsWith('/api/categories/')) {
        categoryIdFromUrl = urlToParse.split('/')[3] || '';
        console.log(`[MockAdapter] Attempting to parse ID from absolute path: "${urlToParse}", split[3]: "${categoryIdFromUrl}"`);
      } else {
        const parts = urlToParse.split('/').filter(p => p); // filter out empty strings
        if (parts.length > 1 && parts[0] === 'categories') { //e.g. categories/id -> parts = [categories, id]
            categoryIdFromUrl = parts[1];
        }
        console.log(`[MockAdapter] Attempting to parse ID from relative path: "${urlToParse}", categoryIdFromUrl: "${categoryIdFromUrl}"`);
      }
    }

    console.log('[MockAdapter] Final determined categoryIdFromUrl:', categoryIdFromUrl);

    const category = mockCategoriesWithImages.find(c => c.id === categoryIdFromUrl);
    if (category) {
      console.log('[MockAdapter] onGet /api/categories/:id - found category:', JSON.parse(JSON.stringify(category)));
      return [200, category];
    } else {
      console.log('[MockAdapter] onGet /api/categories/:id - category NOT FOUND for ID:', categoryIdFromUrl);
      return [404, { detail: 'Category not found' }];
    }
  });

  mock.onPost('/api/categories/').reply(config => {
    const data = JSON.parse(config.data) as CategoryCreate;
    const newCategory: CategoryRead = {
      id: crypto.randomUUID(),
      ...data,
      thumbnailUrl: '',
      createdDate: new Date().toISOString(),
      updatedDate: new Date().toISOString()
    };
    mockCategories.push(newCategory);
    mockCategoriesWithImages.push({ ...newCategory, images: [] });
    return [201, newCategory];
  });

  mock.onPut(/\/api\/categories\/([a-f0-9-]+)\/?$|\/categories\/([a-f0-9-]+)\/?$/).reply(config => {
    let categoryId = '';
    const urlToParse = config.url || '';

    // Try matching /api/categories/some-id/
    let match = urlToParse.match(/\/api\/categories\/([a-f0-9-]+)\/?$/);
    if (match && match[1]) {
      categoryId = match[1];
      console.log(`[MockAdapter] PUT Extracted ID (api path) from URL ('${urlToParse}'): "${categoryId}"`);
    } else {
      // Try matching /categories/some-id/
      match = urlToParse.match(/\/categories\/([a-f0-9-]+)\/?$/);
      if (match && match[1]) {
        categoryId = match[1];
        console.log(`[MockAdapter] PUT Extracted ID (relative path) from URL ('${urlToParse}'): "${categoryId}"`);
      }
    }

    if (!categoryId) {
      console.error('[MockAdapter] PUT /api/categories/:id - Could not determine Category ID from URL:', urlToParse);
      return [400, { detail: 'Category ID missing or invalid in URL' }];
    }

    const updateData = JSON.parse(config.data) as Partial<CategoryRead>; 

    const categoryIndex = mockCategories.findIndex(c => c.id === categoryId);
    if (categoryIndex === -1) {
      console.warn('[MockAdapter] PUT /api/categories/:id - Category not found for ID:', categoryId);
      return [404, { detail: 'Category not found' }];
    }

    // Merge existing data with updateData and update timestamp
    const originalCategory = mockCategories[categoryIndex];
    mockCategories[categoryIndex] = {
      ...originalCategory,
      ...updateData, // Apply partial updates (name, description, thumbnailUrl)
      updatedDate: new Date().toISOString()
    };

    // Also update the category in mockCategoriesWithImages array
    const detailCategoryIndex = mockCategoriesWithImages.findIndex(c => c.id === categoryId);
    if (detailCategoryIndex !== -1) {
      mockCategoriesWithImages[detailCategoryIndex] = {
        ...mockCategoriesWithImages[detailCategoryIndex],
        ...updateData, // Apply partial updates here as well
        updatedDate: new Date().toISOString()
      };
    } else {
      // This case should ideally not happen if mockCategories and mockCategoriesWithImages are in sync
      console.warn("[MockAdapter] PUT /api/categories/:id - Category found in mockCategories but NOT in mockCategoriesWithImages. ID:", categoryId);
    }
    
    console.log('[MockAdapter] PUT /api/categories/:id - Updated category:', mockCategories[categoryIndex]);
    return [200, { ...mockCategories[categoryIndex] }];
  });

  mock.onDelete(/\/api\/categories\/([a-f0-9-]+)\/?/).reply(config => {
    const categoryId = config.url?.split('/')[3] || '';
    mockCategories = mockCategories.filter(c => c.id !== categoryId);
    mockCategoriesWithImages = mockCategoriesWithImages.filter(c => c.id !== categoryId);
    return [204];
  });

  // Images endpoints
  mock.onPost('/api/images/upload/').reply(config => {
    const formData = config.data as FormData;
    const categoryId = formData.get('category_id') as string; // 保持与后端字段名一致
    const file = formData.get('file') as File;

    if (!mockCategories.find(c => c.id === categoryId)) {
      return [400, { detail: 'Invalid categoryId' }];
    }

    const newImage: ImageRead = {
    id: crypto.randomUUID(),
    title: file.name,
    description: formData.get('description') as string || undefined,
    imageUrl: URL.createObjectURL(file),
    categoryId,
    createdDate: new Date().toISOString(),
    metadata: {
      width: 1920,
      height: 1080,
      fileSize: `${(file.size / 1024 / 1024).toFixed(1)}MB`,
      format: file.type.split('/')[1].toUpperCase(),
      cameraModel: 'Unknown',
      location: 'Unspecified'
    }
  };

    const categoryIndex = mockCategoriesWithImages.findIndex(c => c.id === categoryId);
    mockCategoriesWithImages[categoryIndex].images.push(newImage);
    return [201, newImage];
  });

  mock.onPut(/\/api\/images\/([a-f0-9-]+)\/?/).reply(config => {
    const imageId = config.url?.split('/')[3] || '';
    const data = JSON.parse(config.data) as ImageUpdate;
    
    let updatedImage: ImageRead | null = null;
    mockCategoriesWithImages = mockCategoriesWithImages.map(category => ({
      ...category,
      images: category.images.map(img => 
        img.id === imageId ? { ...img, ...data } : img
      )
    }));
    
    return updatedImage ? [200, updatedImage] : [404, { detail: 'Image not found' }];
  });

  mock.onDelete(/\/api\/images\/([a-f0-9-]+_image_\d+)\/?/).reply(config => {
    console.log('[MockAdapter] onDelete /api/images/:id - config:', JSON.parse(JSON.stringify(config, null, 2)));

    let imageIdFromUrl = '';
    const urlToParse = config.url || '';
    const idMatcher = /\/images\/([a-f0-9-]+_image_\d+)\/?/;
    const match = urlToParse.match(idMatcher);

    if (match && match[1]) {
      imageIdFromUrl = match[1];
      console.log(`[MockAdapter] onDelete - Extracted ID using regex match on urlToParse ('${urlToParse}'): "${imageIdFromUrl}"`);
    } else {
      console.log(`[MockAdapter] onDelete - Could not extract image ID using direct regex match on urlToParse: "${urlToParse}" (is it absolute /api/images/id?)`);
      const absIdMatcher = /\/api\/images\/([a-f0-9-]+_image_\d+)\/?/;
      const absMatch = urlToParse.match(absIdMatcher);
      if (absMatch && absMatch[1]) {
        imageIdFromUrl = absMatch[1];
        console.log(`[MockAdapter] onDelete - Extracted ID using regex match for absolute path on urlToParse ('${urlToParse}'): "${imageIdFromUrl}"`);
      }
    }
    console.log('[MockAdapter] onDelete - Final determined imageIdFromUrl:', imageIdFromUrl);

    let imageFoundAndRemoved = false;
    if (imageIdFromUrl) { 
      mockCategoriesWithImages = mockCategoriesWithImages.map(category => {
        const initialImageCount = category.images.length;
        const newImages = category.images.filter(img => img.id !== imageIdFromUrl);
        if (newImages.length < initialImageCount) {
          imageFoundAndRemoved = true;
        }
        return { ...category, images: newImages };
      });
    }

    if (imageFoundAndRemoved) {
      console.log('[MockAdapter] Image removed from mockCategoriesWithImages, id:', imageIdFromUrl);
      return [204]; 
    } else {
      console.log('[MockAdapter] Image NOT FOUND for deletion or invalid ID, id:', imageIdFromUrl);
      return [404, { detail: 'Image not found for deletion' }];
    }
  });

  console.log('Mock adapter setup complete');
};
