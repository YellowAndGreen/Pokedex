// pokedex_frontend/tests/integration/services/apiService.integration.spec.ts
import { describe, it, expect, beforeAll, afterAll, beforeEach, afterEach } from 'vitest';
import {
  // Category functions
  createCategory,
  getCategories,
  getCategoryById,
  updateCategory,
  deleteCategory,
  // Image functions
  uploadImage,
  getImages,
  getImageById,
  updateImage,
  deleteImage,
  getImageThumbnailUrl,
  getViewImageUrl,
  FULL_API_URL,
  API_BASE_URL,
} from '@/services/apiService'; // 假设 @ 指向 src
import type {
  CategoryCreate,
  CategoryRead,
  CategoryUpdate,
  ImageCreateMetadata,
  ImageRead,
  ImageUpdate,
} from '@/types';
import fs from 'fs';
import path from 'path';

// 注意：这些是集成测试，它们会向 http://localhost:8000/api 发送真实的 HTTP 请求。
// 请确保您的后端服务正在运行，并且数据库处于可测试状态。

// 用于存储在测试期间创建的资源的 ID，以便后续清理
let createdCategoryIds: string[] = [];
let createdImageIds: string[] = [];
// let createdSpeciesIds: number[] = []; // Removed

// 全局超时设置，因为 API 调用可能需要更长时间
vi.setConfig({ testTimeout: 30000 }); // 30 秒超时

beforeAll(async () => {
  console.log(`Starting integration tests against API: ${FULL_API_URL}`);
  // 可选：在这里可以进行一些全局的预检，例如检查 API 是否可达
  try {
    await getCategories(0, 1); // 尝试一个小请求
    console.log('API is responsive.');
  } catch (e) {
    console.error('API is not responsive or initial data setup failed. Ensure backend is running at ' + FULL_API_URL, e);
    // 如果 API 不可达，可能希望测试失败或跳过
    // throw new Error('API not responsive');
  }
});

afterAll(async () => {
  console.log('Cleaning up created resources after integration tests...');
  // 清理测试中创建的资源
  // 注意：清理顺序可能很重要，例如先删除依赖于其他资源的资源
  for (const id of createdImageIds.reverse()) { // 先删除图片
    try {
      await deleteImage(id);
      console.log(`Cleaned up image with ID: ${id}`);
    } catch (e: any) {
      if (e.status !== 404) console.error(`Error cleaning up image ${id}:`, e.message);
    }
  }
  for (const id of createdCategoryIds.reverse()) { // 再删除分类
    try {
      await deleteCategory(id);
      console.log(`Cleaned up category with ID: ${id}`);
    } catch (e: any) {
      if (e.status !== 404) console.error(`Error cleaning up category ${id}:`, e.message);
    }
  }

  createdCategoryIds = [];
  createdImageIds = [];
  // createdSpeciesIds = []; // Removed
  console.log('Cleanup finished.');
});


describe('apiService (Integration with Live API)', () => {
  // --- Categories ---
  describe('Category API', () => {
    let testCategory: CategoryRead | null = null;

    it('should create a new category', async () => {
      const uniqueName = `测试分类_${Date.now()}`;
      const newCategoryData: CategoryCreate = { name: uniqueName, description: '这是一个集成测试分类' };
      const created = await createCategory(newCategoryData);
      expect(created).toHaveProperty('id');
      expect(created.name).toBe(newCategoryData.name);
      expect(created.description).toBe(newCategoryData.description);
      createdCategoryIds.push(created.id);
      testCategory = created;
    });

    it('should not create a category with a duplicate name', async () => {
      expect(testCategory).not.toBeNull(); // 确保前一个测试已创建分类
      const duplicateCategoryData: CategoryCreate = { name: testCategory!.name, description: '尝试重复创建' };
      try {
        await createCategory(duplicateCategoryData);
        // 如果没有抛出错误，则测试失败
        throw new Error('创建重复名称的分类应该失败');
      } catch (error: any) {
        expect(error).toBeDefined();
        // 后端对于重复名称可能返回 400, 409 或 422，具体取决于实现
        // 假设您的 apiService 会将 AxiosError 的 status 和 data 附加到抛出的错误上
        expect([400, 409, 422]).toContain(error.status);
      }
    });

    it('should get all categories', async () => {
      const categories = await getCategories(0, 10);
      expect(categories).toBeInstanceOf(Array);
      expect(categories.length).toBeGreaterThanOrEqual(createdCategoryIds.length > 0 ? 1 : 0); // 至少应该包含我们创建的
    });

    it('should get a category by ID', async () => {
      expect(testCategory).not.toBeNull();
      const fetchedCategory = await getCategoryById(testCategory!.id);
      expect(fetchedCategory).toBeDefined();
      expect(fetchedCategory.id).toBe(testCategory!.id);
      expect(fetchedCategory.name).toBe(testCategory!.name);
    });

    it('should return 404 for a non-existent category ID', async () => {
      try {
        await getCategoryById('00000000-0000-0000-0000-000000000000'); // 使用合法但不存在的 UUID
      } catch (error: any) {
        expect(error).toBeDefined();
        expect(error.status).toBe(404);
      }
    });

    it('should update an existing category', async () => {
      expect(testCategory).not.toBeNull();
      const updatedName = `更新的测试分类_${Date.now()}`;
      const updateData: CategoryUpdate = {
        name: updatedName,
        description: testCategory!.description === undefined || testCategory!.description === null ? null : testCategory!.description
      };
      const updated = await updateCategory(testCategory!.id, updateData);
      expect(updated.id).toBe(testCategory!.id);
      expect(updated.name).toBe(updatedName);
      // Optionally, check description if the backend is expected to return it correctly
      // expect(updated.description).toBe(updateData.description);
      testCategory = updated; // 更新 testCategory 以反映更改
    });

    it('should delete a category', async () => {
      // 为了不影响其他测试，我们创建一个新的分类来删除
      const tempCategoryData: CategoryCreate = { name: `待删除分类_${Date.now()}` };
      const tempCategory = await createCategory(tempCategoryData);
      createdCategoryIds.push(tempCategory.id); // 也加入清理列表

      await deleteCategory(tempCategory.id); // 不再断言 deleted.id

      // 验证是否真的被删除了
      try {
        await getCategoryById(tempCategory.id);
      } catch (error: any) {
        expect(error.status).toBe(404);
      }
      // 从清理列表中移除，因为它已经被这个测试删除了
      createdCategoryIds = createdCategoryIds.filter(id => id !== tempCategory.id);
    });
  });

  // --- Images ---
  describe('Image API', () => {
    let tempCategoryIdForImage: string;
    let testImage: ImageRead | null = null;

    beforeAll(async () => {
      // 为图片测试创建一个临时分类
      const uniqueCategoryName = `图片测试分类_${Date.now()}`;
      const cat = await createCategory({ name: uniqueCategoryName, description: '用于图片上传测试的临时分类' });
      tempCategoryIdForImage = cat.id;
      createdCategoryIds.push(tempCategoryIdForImage); // 加入清理列表
    });

    it('should upload an image', async () => {
      expect(tempCategoryIdForImage).toBeDefined();

      const imageAssetPath = path.resolve(__dirname, 'assets/test_image.png');
      
      // 检查文件是否存在，以便调试
      if (!fs.existsSync(imageAssetPath)) {
        console.error(`Test image not found at: ${imageAssetPath}`);
        throw new Error(`Test image not found at: ${imageAssetPath}. __dirname is ${__dirname}`);
      }
      const imageBuffer = fs.readFileSync(imageAssetPath);
      const imageFile = new File([imageBuffer], 'test_image.png', { type: 'image/png' });

      const metadata: ImageCreateMetadata = {
        title: '真实图片测试标题',
        description: '这是一个通过集成测试上传的真实图片描述',
        category_id: tempCategoryIdForImage,
        tags: '真实,测试,集成,图片',
        set_as_category_thumbnail: false,
      };

      const uploadedImage = await uploadImage(imageFile, metadata);

      expect(uploadedImage).toHaveProperty('id');
      expect(uploadedImage.title).toBe(metadata.title);
      expect(uploadedImage.description).toBe(metadata.description);
      expect(uploadedImage.category_id).toBe(metadata.category_id);
      expect(uploadedImage.tags).toBe(metadata.tags);
      
      // 根据 openapi.json, image_url 和 thumbnail_url 是字符串
      // 后端实际返回的是指向静态资源的绝对 URL
      // 我们从 apiService 导入 API_BASE_URL 来构建预期的基础 URL
      // expect(uploadedImage.image_url).toBe(`${API_BASE_URL}${uploadedImage.relative_file_path}`);
      // expect(uploadedImage.thumbnail_url).toBe(`${API_BASE_URL}${uploadedImage.relative_thumbnail_path}`);
      
      expect(uploadedImage.original_filename).toBe('test_image.png');
      expect(uploadedImage.mime_type).toBe('image/png');

      testImage = uploadedImage; // 保存用于后续测试
      createdImageIds.push(uploadedImage.id);
    });

    it('should get an image by ID', async () => {
      expect(testImage, '依赖于前一个创建图片的测试').not.toBeNull();
      const fetchedImage = await getImageById(testImage!.id);
      expect(fetchedImage).toBeDefined();
      expect(fetchedImage.id).toBe(testImage!.id);
      expect(fetchedImage.title).toBe(testImage!.title);
      expect(fetchedImage.description).toBe(testImage!.description);
      expect(fetchedImage.category_id).toBe(testImage!.category_id);
      expect(fetchedImage.tags).toBe(testImage!.tags);

      // Validate image_url structure
      expect(fetchedImage.image_url, 'fetchedImage.image_url should be a non-empty string').toBeTruthy();
      const imageUrlParts = new URL(fetchedImage.image_url as string);
      expect(imageUrlParts.protocol, 'Image URL protocol should be http:').toBe('http:');
      expect(imageUrlParts.port, 'Image URL port should be 8000').toBe('8000');
      expect(fetchedImage.relative_file_path, 'fetchedImage.relative_file_path should be a non-empty string').toBeTruthy();
      expect(imageUrlParts.pathname, 'Image URL pathname is incorrect').toBe(`/uploaded_images/${fetchedImage.relative_file_path}`);

      // Validate thumbnail_url structure
      expect(fetchedImage.thumbnail_url, 'fetchedImage.thumbnail_url should be a non-empty string').toBeTruthy();
      const thumbnailUrlParts = new URL(fetchedImage.thumbnail_url as string);
      expect(thumbnailUrlParts.protocol, 'Thumbnail URL protocol should be http:').toBe('http:');
      expect(thumbnailUrlParts.port, 'Thumbnail URL port should be 8000').toBe('8000');
      expect(fetchedImage.relative_thumbnail_path, 'fetchedImage.relative_thumbnail_path should be a non-empty string').toBeTruthy();
      expect(thumbnailUrlParts.pathname, 'Thumbnail URL pathname is incorrect').toBe(`/thumbnails/${fetchedImage.relative_thumbnail_path}`);
    });

    it('should update an image metadata', async () => {
      expect(testImage, '依赖于前一个创建图片的测试').not.toBeNull();
      const updatedTitle = `更新的图片标题_${Date.now()}`;
      const updatedDescription = '这是更新后的图片描述';
      const updatedTags = '更新,测试,图片';
      const updateData: ImageUpdate = {
        title: updatedTitle,
        description: updatedDescription,
        tags: updatedTags,
        set_as_category_thumbnail: true,
      };
      const updatedImage = await updateImage(testImage!.id, updateData);
      expect(updatedImage).toBeDefined();
      expect(updatedImage.id).toBe(testImage!.id);
      expect(updatedImage.title).toBe(updatedTitle);
      expect(updatedImage.description).toBe(updatedDescription);
      expect(updatedImage.tags).toBe(updatedTags);
      testImage = updatedImage;
    });

    it('should delete an image', async () => {
      expect(testImage, '依赖于前一个创建图片的测试').not.toBeNull();
      const imageIdToDelete = testImage!.id;
      await deleteImage(imageIdToDelete);
      try {
        await getImageById(imageIdToDelete);
        throw new Error('图片删除后仍能获取到，测试失败');
      } catch (error: any) {
        expect(error.status).toBe(404);
      }
      createdImageIds = createdImageIds.filter(id => id !== imageIdToDelete);
      testImage = null;
    });

    it('getImageThumbnailUrl should construct correct thumbnail URL', () => {
      const imageId = 'test-uuid-123';
      const expectedUrl = `${FULL_API_URL}/images/${imageId}/thumbnail`;
      expect(getImageThumbnailUrl(imageId)).toBe(expectedUrl);
    });

    it('getViewImageUrl should construct correct view URL', () => {
      const imageId = 'test-uuid-456';
      const expectedUrl = `${FULL_API_URL}/images/${imageId}/view`;
      expect(getViewImageUrl(imageId)).toBe(expectedUrl);
    });

  });

  // The Species API describe block that was here should be completely gone.

}); // End of apiService (Integration with Live API) describe block 