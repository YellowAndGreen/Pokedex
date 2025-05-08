import axios, { AxiosRequestConfig } from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { CategoryRead, CategoryReadWithImages, ImageRead, CategoryCreate, ImageUpdate } from '../types';
import { apiInstance } from './apiService';

const mockCategories: CategoryRead[] = [
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
  return Array.from({ length: count }, (_, i) => ({
    id: `${categoryId}_image_${(i + 1).toString().padStart(3, '0')}`,
    title: `Sample Image ${i + 1}`,
    description: `Photo #${i + 1} in ${mockCategories.find(c => c.id === categoryId)?.name}`,
    imageUrl: `https://cdn.example.com/images/${categoryId}/image-${i + 1}.jpg`,
    categoryId,
    createdDate: new Date().toISOString(),
    metadata: {
      width: 1920,
      height: 1080,
      fileSize: '2.4MB',
      format: 'JPEG'
    }
  }));
};

let mockCategoriesWithImages: CategoryReadWithImages[] = mockCategories.map(category => ({
  ...category,
  images: generateMockImages(category.id, Math.floor(Math.random() * 5) + 3)
}));

export const setupMocks = () => {
  const mock = new MockAdapter(apiInstance, { delayResponse: 500 });

  // Categories endpoints
  mock.onGet(/\/api\/categories\/?/).reply(200, [...mockCategories]);
  mock.onGet(/\/api\/categories\/([a-f0-9-]+)\/?/).reply(config => {
    const categoryId = config.url?.split('/')[3] || '';
    const category = mockCategoriesWithImages.find(c => c.id === categoryId);
    return category ? [200, category] : [404, { detail: 'Category not found' }];
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

  mock.onPut(/\/api\/categories\/([a-f0-9-]+)\/?/).reply(config => {
    const categoryId = config.url?.split('/')[3] || '';
    const data = JSON.parse(config.data) as CategoryCreate;
    const index = mockCategories.findIndex(c => c.id === categoryId);
    
    if (index === -1) return [404, { detail: 'Category not found' }];
    
    const updated = { ...mockCategories[index], ...data };
    mockCategories[index] = updated;
    return [200, updated];
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

  mock.onDelete(/\/api\/images\/([a-f0-9-]+)\/?/).reply(config => {
    const imageId = config.url?.split('/')[3] || '';
    mockCategoriesWithImages = mockCategoriesWithImages.map(category => ({
      ...category,
      images: category.images.filter(img => img.id !== imageId)
    }));
    return [204];
  });

  console.log('Mock adapter setup complete');
};
