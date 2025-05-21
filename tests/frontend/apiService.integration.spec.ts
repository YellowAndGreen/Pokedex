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
  // Species functions
  createSpecies,
  getAllSpecies,
  searchSpecies,
  getSpeciesById,
  updateSpecies,
  deleteSpecies,
  FULL_API_URL,
} from '@/services/apiService'; // 假设 @ 指向 src
import type {
  CategoryCreate,
  CategoryRead,
  CategoryUpdate,
  ImageCreateMetadata,
  ImageRead,
  ImageUpdate,
  SpeciesCreate,
  SpeciesRead,
  SpeciesUpdate,
} from '@/types';

// 注意：这些是集成测试，它们会向 http://localhost:8000/api 发送真实的 HTTP 请求。
// 请确保您的后端服务正在运行，并且数据库处于可测试状态。

// 用于存储在测试期间创建的资源的 ID，以便后续清理
let createdCategoryIds: number[] = [];
let createdImageIds: number[] = [];
let createdSpeciesIds: number[] = [];

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
  for (const id of createdSpeciesIds.reverse()) { // 最后删除物种
    try {
      await deleteSpecies(id);
      console.log(`Cleaned up species with ID: ${id}`);
    } catch (e: any) {
      if (e.status !== 404) console.error(`Error cleaning up species ${id}:`, e.message);
    }
  }
  createdCategoryIds = [];
  createdImageIds = [];
  createdSpeciesIds = [];
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
      expect(created.image_count).toBe(0);
      createdCategoryIds.push(created.id); // 保存 ID 以便清理
      testCategory = created; // 保存用于后续测试
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
        await getCategoryById(9999999); // 一个极不可能存在的 ID
      } catch (error: any) {
        expect(error).toBeDefined();
        expect(error.status).toBe(404);
      }
    });

    it('should update an existing category', async () => {
      expect(testCategory).not.toBeNull();
      const updatedName = `更新的测试分类_${Date.now()}`;
      const updateData: CategoryUpdate = { name: updatedName, description: '描述已更新' };
      const updated = await updateCategory(testCategory!.id, updateData);
      expect(updated.id).toBe(testCategory!.id);
      expect(updated.name).toBe(updatedName);
      expect(updated.description).toBe('描述已更新');
      testCategory = updated; // 更新 testCategory 以反映更改
    });

    it('should delete a category', async () => {
      // 为了不影响其他测试，我们创建一个新的分类来删除
      const tempCategoryData: CategoryCreate = { name: `待删除分类_${Date.now()}` };
      const tempCategory = await createCategory(tempCategoryData);
      createdCategoryIds.push(tempCategory.id); // 也加入清理列表

      const deleted = await deleteCategory(tempCategory.id);
      expect(deleted.id).toBe(tempCategory.id);

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
    let tempCategoryIdForImage: number;
    let tempSpeciesIdForImage: number | null = null;

    beforeAll(async () => {
      // 为图片测试创建一个临时的分类和物种
      const cat = await createCategory({ name: `图片测试分类_${Date.now()}` });
      tempCategoryIdForImage = cat.id;
      createdCategoryIds.push(tempCategoryIdForImage);

      const spec = await createSpecies({
        order_details: "测试目", family_details: "测试科", genus_details: "测试属",
        name_chinese: `图片测试物种_${Date.now()}`
      });
      tempSpeciesIdForImage = spec.id;
      createdSpeciesIds.push(tempSpeciesIdForImage);
    });

    it('getImageThumbnailUrl should construct correct thumbnail URL', () => {
      const imageId = 123;
      const expectedUrl = `${FULL_API_URL}/images/${imageId}/thumbnail`;
      expect(getImageThumbnailUrl(imageId)).toBe(expectedUrl);
    });

    it('getViewImageUrl should construct correct view URL', () => {
      const imageId = 456;
      const expectedUrl = `${FULL_API_URL}/images/${imageId}/view`;
      expect(getViewImageUrl(imageId)).toBe(expectedUrl);
    });

    it('should upload an image', async () => {
      const metadata: ImageCreateMetadata = {
        title: `测试图片_${Date.now()}`,
        description: '这是一个集成测试图片',
        category_id: tempCategoryIdForImage,
        species_id: tempSpeciesIdForImage,
      };
      // 创建一个模拟的 File 对象
      const blob = new Blob(['这是一个模拟图片内容'], { type: 'image/png' });
      const imageFile = new File([blob], 'test-image.png', { type: 'image/png' });

      const uploadedImage = await uploadImage(imageFile, metadata);
      expect(uploadedImage).toHaveProperty('id');
      expect(uploadedImage.title).toBe(metadata.title);
      expect(uploadedImage.category_id).toBe(metadata.category_id);
      expect(uploadedImage.species_id).toBe(metadata.species_id);
      expect(uploadedImage.view_url).toContain(`/images/${uploadedImage.id}/view`);
      expect(uploadedImage.thumbnail_url).toContain(`/images/${uploadedImage.id}/thumbnail`);
      createdImageIds.push(uploadedImage.id);
    });

    it('should get all images (possibly filtered)', async () => {
      const images = await getImages(0, 10, tempCategoryIdForImage);
      expect(images).toBeInstanceOf(Array);
      // 期望至少有一个我们上传的图片
      const uploadedImageExists = images.some(img => createdImageIds.includes(img.id));
      if (createdImageIds.length > 0) {
         expect(uploadedImageExists).toBe(true);
      }
    });

    it('should get an image by ID', async () => {
      if (createdImageIds.length === 0) {
        console.warn('Skipping getImageById test as no image was created in previous tests.');
        return;
      }
      const imageIdToFetch = createdImageIds[0];
      const image = await getImageById(imageIdToFetch);
      expect(image).toBeDefined();
      expect(image.id).toBe(imageIdToFetch);
    });

    it('should update an image', async () => {
       if (createdImageIds.length === 0) {
        console.warn('Skipping updateImage test as no image was created.');
        return;
      }
      const imageToUpdateId = createdImageIds[0];
      const newTitle = `更新的图片标题_${Date.now()}`;
      const updateData: ImageUpdate = { title: newTitle };
      const updatedImage = await updateImage(imageToUpdateId, updateData);
      expect(updatedImage.id).toBe(imageToUpdateId);
      expect(updatedImage.title).toBe(newTitle);
    });

    // deleteImage 测试已包含在 afterAll 清理中，也可以单独写一个测试用例
  });


  // --- Species ---
  describe('Species API', () => {
    let testSpecies: SpeciesRead | null = null;

    it('should create a new species', async () => {
      const newSpeciesData: SpeciesCreate = {
        order_details: "雀形目",
        family_details: "鸦科",
        genus_details: "鸦属",
        name_chinese: `测试乌鸦_${Date.now()}`,
        name_english: "Test Crow",
        name_latin: "Corvus testus"
      };
      const created = await createSpecies(newSpeciesData);
      expect(created).toHaveProperty('id');
      expect(created.name_chinese).toBe(newSpeciesData.name_chinese);
      createdSpeciesIds.push(created.id);
      testSpecies = created;
    });

    it('should get all species', async () => {
      const speciesList = await getAllSpecies(0, 10);
      expect(speciesList).toBeInstanceOf(Array);
      expect(speciesList.length).toBeGreaterThanOrEqual(createdSpeciesIds.length > 0 ? 1 : 0);
    });

    it('should get a species by ID', async () => {
      expect(testSpecies).not.toBeNull();
      const fetched = await getSpeciesById(testSpecies!.id);
      expect(fetched.id).toBe(testSpecies!.id);
      expect(fetched.name_chinese).toBe(testSpecies!.name_chinese);
    });

    it('should search species', async () => {
      expect(testSpecies).not.toBeNull();
      // 使用一个独特的词进行搜索，确保能找到我们创建的物种
      const queryPart = testSpecies!.name_chinese.substring(0, 5); // 取部分中文名
      const results = await searchSpecies(queryPart, 0, 5);
      expect(results).toBeInstanceOf(Array);
      const found = results.some(s => s.id === testSpecies!.id);
      expect(found).toBe(true);
    });

    it('should update a species', async () => {
      expect(testSpecies).not.toBeNull();
      const updatedLatinName = `Corvus testus updatedus_${Date.now()}`;
      const updateData: SpeciesUpdate = { name_latin: updatedLatinName };
      const updated = await updateSpecies(testSpecies!.id, updateData);
      expect(updated.id).toBe(testSpecies!.id);
      expect(updated.name_latin).toBe(updatedLatinName);
      testSpecies = updated;
    });

    // deleteSpecies 测试已包含在 afterAll 清理中
  });
}); 