import { setActivePinia, createPinia } from 'pinia';
import { useImageStore } from '@/store/imageStore';
import {
  // API service functions, aliased to avoid conflicts with store actions
  createCategory as apiCreateCategory,
  deleteCategory as apiDeleteCategory,
  deleteImage as apiDeleteImage, // For direct cleanup if needed
  getImages as apiGetImages, // For verification or direct checks
  getImageById as apiGetImageById, // For verification
  getCategories as apiGetCategories, // <<< IMPORT ADDED FOR HEALTH CHECK
  FULL_API_URL,
  uploadImage as apiUploadImage
} from '@/services/apiService';
import type {
  ImageCreateMetadata,
  ImageRead,
  ImageUpdate,
  CategoryRead,
  HTTPValidationError
} from '@/types';
import { describe, it, expect, beforeAll, afterAll, beforeEach, vi } from 'vitest';
import fs from 'fs';
import path from 'path';

// --- Test Configuration & Setup ---
vi.setConfig({ testTimeout: 30000 }); // 降低超时时间从45000到30000

let testCategory: CategoryRead | null = null; // Temporary category for image tests
let createdImageIdsInStoreTest: string[] = []; // Track image IDs for cleanup

const imageAssetPath = path.resolve(__dirname, '../assets/test_image.png'); // Adjusted path

beforeAll(async () => {
  setActivePinia(createPinia());
  console.log(`Starting Image Store integration tests against API: ${FULL_API_URL}`);

  // 1. Check API responsiveness (optional, good practice)
  try {
    // await apiGetImages(0, 1); // Try a light image-related or general API call
    await apiGetCategories(0, 1); // <<< CHANGED: Use a known valid endpoint for health check
    console.log('API is responsive for Image Store tests (checked via categories endpoint).');
  } catch (e) {
    console.error('API is not responsive for Image Store tests. Ensure backend is running.', e);
    throw new Error('API not responsive for Image Store tests'); // 取消注释，确保API不可用时测试失败
  }

  // 2. Create a temporary category for all image tests in this suite
  try {
    const uniqueCategoryName = `Test Category for Images ${Date.now()}`;
    // testCategory = await categoryStore.addCategory({ name: uniqueCategoryName, description: 'Temp category for image store tests' });
    // OR direct API call:
    testCategory = await apiCreateCategory({ name: uniqueCategoryName, description: 'Temp category for image store tests' });
    if (!testCategory) {
      throw new Error('Failed to create temporary category for image tests.');
    }
    console.log(`Temporary category created for image tests: ${testCategory.id} - ${testCategory.name}`);
  } catch (e) {
    console.error('Failed to create temporary category for Image Store tests:', e);
    throw new Error('Failed to create temporary category, aborting Image Store tests.');
  }
});

afterAll(async () => {
  console.log('Cleaning up resources from Image Store integration tests...');

  // 1. Delete all images created during these tests
  if (createdImageIdsInStoreTest.length > 0) {
    console.log(`Cleaning up ${createdImageIdsInStoreTest.length} images...`);
    for (const id of createdImageIdsInStoreTest.reverse()) {
      try {
        await apiDeleteImage(id);
        console.log(`Cleaned up image (from image store test) with ID: ${id}`);
      } catch (e: any) {
        if (e.status !== 404) {
          console.error(`Error cleaning up image (from image store test) ${id}:`, e.message || e);
        }
      }
    }
    createdImageIdsInStoreTest = [];
  }

  // 2. Delete the temporary category
  if (testCategory) {
    console.log(`Cleaning up temporary category: ${testCategory.id} - ${testCategory.name}`);
    try {
      // const categoryStore = useCategoryStore();
      // await categoryStore.removeCategory(testCategory.id);
      // OR direct API call:
      await apiDeleteCategory(testCategory.id);
      console.log(`Cleaned up temporary category (from image store test) with ID: ${testCategory.id}`);
    } catch (e: any) {
      if (e.status !== 404) {
        console.error(`Error cleaning up temporary category ${testCategory.id}:`, e.message || e);
      }
    }
    testCategory = null;
  }
  console.log('Image Store integration test cleanup finished.');
});


describe('Image Store (Integration with Live API)', () => {
  let store: ReturnType<typeof useImageStore>;

  beforeEach(() => {
    store = useImageStore();
    // Reset store state before each test
    store.images = [];
    store.currentImage = null;
    store.isLoading = false;
    store.error = null;
    store.validationErrors = null;
    store.totalImages = 0;
    store.currentPage = 1;
    // store.imagesPerPage remains as default
  });

  it('initial state is correct after setup', () => {
    expect(store.images).toEqual([]);
    expect(store.currentImage).toBeNull();
    expect(store.isLoading).toBe(false);
    expect(store.error).toBeNull();
    expect(store.validationErrors).toBeNull();
  });

  // --- Actions --- 
  describe('Actions', () => {
    describe('addNewImage and fetchImageDetails', () => {
      let uploadedImageViaStore: ImageRead | null = null;

      it('should upload an image via addNewImage and then fetch its details', async () => {
        expect(testCategory, 'Test category must exist for uploading image').not.toBeNull();
        if (!testCategory) return; // Type guard

        if (!fs.existsSync(imageAssetPath)) {
          throw new Error(`Test image not found at: ${imageAssetPath}`);
        }
        const imageBuffer = fs.readFileSync(imageAssetPath);
        const imageFile = new File([imageBuffer], 'store_test_image.png', { type: 'image/png' });

        const metadata: ImageCreateMetadata = {
          title: 'Store Upload Test Image',
          description: 'Uploaded via imageStore.addNewImage',
          category_id: testCategory.id,
          tags: 'store,test,integration'
        };

        // 1. Add new image
        uploadedImageViaStore = await store.addNewImage(imageFile, metadata);
        expect(uploadedImageViaStore).toBeDefined();
        expect(uploadedImageViaStore.id).toBeDefined();
        createdImageIdsInStoreTest.push(uploadedImageViaStore.id);

        expect(uploadedImageViaStore.title).toBe(metadata.title);
        expect(uploadedImageViaStore.category_id).toBe(testCategory.id);
        expect(store.isLoading).toBe(false);
        expect(store.images.find(img => img.id === uploadedImageViaStore?.id)).toEqual(uploadedImageViaStore);

        // 2. Fetch image details
        if (!uploadedImageViaStore) throw new Error("Uploaded image is unexpectedly null");
        
        await store.fetchImageDetails(uploadedImageViaStore.id);
        expect(store.isLoading).toBe(false);
        expect(store.currentImage).not.toBeNull();
        expect(store.currentImage?.id).toBe(uploadedImageViaStore.id);
        expect(store.currentImage?.title).toBe(metadata.title);
        expect(store.error).toBeNull();
      });

      it('fetchImageDetails should set error for non-existent image ID', async () => {
        const nonExistentId = '00000000-0000-0000-0000-000000000000';
        await store.fetchImageDetails(nonExistentId);
        expect(store.isLoading).toBe(false);
        expect(store.currentImage).toBeNull();
        expect(store.error).toContain('404');
      });
    });

    describe('fetchImages', () => {
      let img1: ImageRead, img2: ImageRead;

      beforeAll(async () => {
        expect(testCategory, 'Test category must exist for fetchImages test').not.toBeNull();
        if (!testCategory) throw new Error("Test category missing for fetchImages setup");

        const fileBuffer = fs.readFileSync(imageAssetPath);
        const file1 = new File([fileBuffer], 'fetch_img_1.png', { type: 'image/png' });
        const meta1: ImageCreateMetadata = { 
          title: 'Fetch Img 1', 
          category_id: testCategory.id,
          description: null, // 添加可选字段但设为null
          tags: null // 添加可选字段但设为null
        };
        // Use store to add for consistency, or direct API
        const tempStore = useImageStore(); // separate instance for setup to avoid state interference
        img1 = await tempStore.addNewImage(file1, meta1);
        createdImageIdsInStoreTest.push(img1.id);

        const file2 = new File([fileBuffer], 'fetch_img_2.png', { type: 'image/png' });
        const meta2: ImageCreateMetadata = { 
          title: 'Fetch Img 2', 
          category_id: testCategory.id,
          description: null, 
          tags: null 
        };
        img2 = await tempStore.addNewImage(file2, meta2);
        createdImageIdsInStoreTest.push(img2.id);
      });

      it('should fetch images for the test category', async () => {
        expect(testCategory).not.toBeNull();
        await store.fetchImages(0, 10, testCategory!.id);

        expect(store.isLoading).toBe(false);
        expect(store.error).toBeNull();
        expect(store.images.length).toBeGreaterThanOrEqual(2);
        
        const fetchedImg1 = store.images.find(i => i.id === img1.id);
        const fetchedImg2 = store.images.find(i => i.id === img2.id);
        expect(fetchedImg1).toBeDefined();
        expect(fetchedImg1?.title).toBe(img1.title);
        expect(fetchedImg2).toBeDefined();
        expect(fetchedImg2?.title).toBe(img2.title);
      });
      
      // Test for fetching images without categoryId (all images) can be added if API supports it and it's desired
      // Note: GET /api/images/ is not in openapi.json, so this might not be a valid test.
      // it('should fetch all images if categoryId is not provided', async () => { ... });
    });

    describe('editImage', () => {
      let imageToEdit: ImageRead;
      const originalTitle = `Original Image Title ${Date.now()}`;
      const updatedTitle = `Updated Image Title ${Date.now()}`;

      beforeEach(async () => { // Create a fresh image for each edit test
        expect(testCategory).not.toBeNull();
        const fileBuffer = fs.readFileSync(imageAssetPath);
        const file = new File([fileBuffer], 'edit_test.png', { type: 'image/png' });
        const meta: ImageCreateMetadata = { 
          title: originalTitle, 
          category_id: testCategory!.id,
          description: null,
          tags: null
        };
        // Use a temp store or direct API call for setup to avoid interference with main 'store' instance
        imageToEdit = await apiUploadImage(file, meta);
        createdImageIdsInStoreTest.push(imageToEdit.id);
        
        // Ensure main store has this image if we want to test currentImage update
        store.images = [imageToEdit];
        store.currentImage = imageToEdit;
      });

      it('should update image metadata via editImage and reflect in state', async () => {
        const updateData: ImageUpdate = { title: updatedTitle, description: 'Updated Desc' };
        const result = await store.editImage(imageToEdit.id, updateData);

        expect(result).toBeDefined();
        expect(result.id).toBe(imageToEdit.id);
        expect(result.title).toBe(updatedTitle);
        expect(result.description).toBe('Updated Desc');

        expect(store.isLoading).toBe(false);
        const imageInList = store.images.find(img => img.id === imageToEdit.id);
        expect(imageInList).toEqual(result);
        expect(store.currentImage).toEqual(result); // If it was the current image
        expect(store.error).toBeNull();
      });

      it('should fail to update a non-existent image ID', async () => {
        const nonExistentId = '00000000-0000-0000-0000-000000000000';
        const updateData: ImageUpdate = { title: 'Non-existent update' };
        try {
          await store.editImage(nonExistentId, updateData);
        } catch (e: any) {
          expect(e).toBeDefined();
          expect(store.isLoading).toBe(false);
          expect(store.error).toContain('404');
        }
      });
    });

    describe('removeImage', () => {
      let imageToRemove: ImageRead;

      beforeEach(async () => {
        expect(testCategory).not.toBeNull();
        const fileBuffer = fs.readFileSync(imageAssetPath);
        const file = new File([fileBuffer], 'remove_test.png', { type: 'image/png' });
        const meta: ImageCreateMetadata = { 
          title: `Remove Me ${Date.now()}`, 
          category_id: testCategory!.id,
          description: null,
          tags: null
        };
        imageToRemove = await apiUploadImage(file, meta);
        // Don't add to createdImageIdsInStoreTest immediately, this test should handle its deletion.
        store.images = [imageToRemove];
        store.currentImage = imageToRemove;
      });

      it('should remove image via removeImage and from state', async () => {
        await store.removeImage(imageToRemove.id);

        expect(store.isLoading).toBe(false);
        expect(store.images.find(img => img.id === imageToRemove.id)).toBeUndefined();
        expect(store.currentImage).toBeNull(); // If it was the current image
        expect(store.error).toBeNull();

        // Verify it's gone from the backend
        try {
          await apiGetImageById(imageToRemove.id); // getImageById will throw 404 if not found
          throw new Error('Image should have been deleted from backend');
        } catch (e: any) {
          expect(e.status === 404 || e.message.includes('404')).toBe(true);
        }
      });
      
      // Ensure image created in beforeEach is cleaned up if test fails before removeImage call
      afterEach(async () => {
        if (imageToRemove && imageToRemove.id) {
          try {
            await apiGetImageById(imageToRemove.id); // 检查图片是否仍然存在
            if (!createdImageIdsInStoreTest.includes(imageToRemove.id)) {
              createdImageIdsInStoreTest.push(imageToRemove.id);
              console.log(`Added image to cleanup list: ${imageToRemove.id}`);
            }
          } catch (e: any) {
            // 如果是404错误，说明图片已被成功删除或从未被正确创建
            if (e.status !== 404 && !e.message?.includes('404')) {
              console.error(`Error checking image existence: ${e.message || e}`);
            }
          }
        }
      });
    });

    // Tests for clearValidationErrors and clearError are simple and don't involve API
    describe('clearValidationErrors', () => {
      it('should set validationErrors to null', () => {
        const mockValidation: HTTPValidationError = { detail: [{ loc: ['file'], msg: 'error', type: 'type_error' }] };
        store.validationErrors = mockValidation;
        store.clearValidationErrors();
        expect(store.validationErrors).toBeNull();
      });
    });

    describe('clearError', () => {
      it('should set error to null', () => {
        store.error = 'An API error occurred';
        store.clearError();
        expect(store.error).toBeNull();
      });
    });
  });
}); 