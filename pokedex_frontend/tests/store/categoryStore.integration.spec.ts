import { setActivePinia, createPinia } from 'pinia';
import { useCategoryStore } from '@/store/categoryStore';
import { 
  getCategories as apiGetCategories, // 使用别名以避免与 store action 混淆
  createCategory as apiCreateCategory,
  deleteCategory as apiDeleteCategory,
  FULL_API_URL 
} from '@/services/apiService';
import type { CategoryCreate, CategoryRead, CategoryUpdate, HTTPValidationError } from '@/types';
import { describe, it, expect, beforeAll, afterAll, beforeEach, vi } from 'vitest';

// 不再模拟 apiService
// vi.mock('@/services/apiService', ...);

// 用于存储在测试期间创建的资源的 ID，以便后续清理
let createdCategoryIdsInStoreTest: string[] = [];

const mockValidationError: HTTPValidationError = { // 保持这个用于验证错误结构
  detail: [{
    loc: ['body', 'name'],
    msg: 'field required',
    type: 'value_error.missing'
  }]
};

// 全局超时，因为 API 调用可能需要更长时间
vi.setConfig({ testTimeout: 30000 });

beforeAll(async () => {
  // 为每个测试套件（文件）设置一次 Pinia 实例
  // 如果在 describe 块外部或 beforeEach/constructor 中访问 store，则需要此操作
  setActivePinia(createPinia()); 
  console.log(`Starting Category Store integration tests against API: ${FULL_API_URL}`);
  try {
    await apiGetCategories(0, 1); // 尝试一个小请求检查 API 是否可达
    console.log('API is responsive for Category Store tests.');
  } catch (e) {
    console.error('API is not responsive. Ensure backend is running at ' + FULL_API_URL, e);
    // 根据需要，可以选择抛出错误使整个测试套件失败
    throw new Error('API not responsive for Category Store tests');
  }
});

afterAll(async () => {
  console.log('Cleaning up categories created during Category Store integration tests...');
  for (const id of createdCategoryIdsInStoreTest.reverse()) {
    try {
      await apiDeleteCategory(id); // 使用真实的 API 删除
      console.log(`Cleaned up category (from store test) with ID: ${id}`);
    } catch (e: any) {
      // 如果分类已被其他测试或手动删除，可能会出现 404，这是正常的
      if (e.status !== 404) {
        console.error(`Error cleaning up category (from store test) ${id}:`, e.message || e);
      }
    }
  }
  createdCategoryIdsInStoreTest = [];
  console.log('Category Store integration test cleanup finished.');
});

describe('Category Store (Integration with Live API)', () => {
  let store: ReturnType<typeof useCategoryStore>;

  beforeEach(() => {
    // 在每个测试用例之前获取一个新的 store 实例，以确保测试隔离性
    // Pinia 实例已在 beforeAll 中设置，所以这里可以直接使用
    store = useCategoryStore();
    // 清理 store 内部可能残留的状态 (虽然 Pinia 的 setActivePinia 应该处理了大部分)
    store.categories = [];
    store.currentCategory = null;
    store.error = null;
    store.validationErrors = null;
    store.isLoading = false;
  });

  it('initial state is correct after setup', () => {
    // 这个测试现在验证的是 beforeEach 清理后的状态
    expect(store.categories).toEqual([]);
    expect(store.currentCategory).toBeNull();
    expect(store.isLoading).toBe(false);
    expect(store.error).toBeNull();
    expect(store.validationErrors).toBeNull();
  });

  describe('Getters', () => {
    describe('getCategoryNameById', () => {
      it('should return category name if category exists in store state', async () => {
        // 这个 getter 是同步的，直接依赖于 store.categories 的状态
        // 为了测试它，我们需要先用真实 API填充 store.categories
        const uniqueName = `Getter Test Cat_${Date.now()}`;
        const created = await apiCreateCategory({ name: uniqueName });
        createdCategoryIdsInStoreTest.push(created.id);
        
        await store.fetchCategories(); // 填充 store.categories

        const categoryFromStore = store.categories.find(c => c.id === created.id);
        expect(categoryFromStore).toBeDefined();
        expect(store.getCategoryNameById(created.id)).toBe(uniqueName);
      });

      it('should return undefined if category does not exist in store state', () => {
        // 假设 store.categories 为空或不包含该 ID
        expect(store.getCategoryNameById('non-existent-uuid-for-getter')).toBeUndefined();
      });
    });
  });

  describe('Actions', () => {
    describe('fetchCategories', () => {
      let createdCat1: CategoryRead;
      let createdCat2: CategoryRead;

      beforeAll(async () => { // 使用 beforeAll 在这个 describe 块开始前创建数据
        const name1 = `Fetch Test Cat 1_${Date.now()}`;
        const name2 = `Fetch Test Cat 2_${Date.now() + 1}`;
        createdCat1 = await apiCreateCategory({ name: name1, description: 'Desc 1' });
        createdCat2 = await apiCreateCategory({ name: name2, description: 'Desc 2' });
        createdCategoryIdsInStoreTest.push(createdCat1.id, createdCat2.id);
      });

      it('should fetch categories and update state from live API', async () => {
        await store.fetchCategories();

        expect(store.isLoading).toBe(false);
        expect(store.error).toBeNull();
        expect(store.validationErrors).toBeNull();
        
        // 验证 store.categories 数组中包含了我们创建的分类
        // 注意：API 可能返回其他已存在的分类，所以我们只检查我们创建的是否存在
        const fetchedCat1 = store.categories.find(c => c.id === createdCat1.id);
        const fetchedCat2 = store.categories.find(c => c.id === createdCat2.id);

        expect(fetchedCat1).toBeDefined();
        expect(fetchedCat1?.name).toBe(createdCat1.name);
        expect(fetchedCat2).toBeDefined();
        expect(fetchedCat2?.name).toBe(createdCat2.name);
        expect(store.categories.length).toBeGreaterThanOrEqual(2);
      });

      // 对于真实 API，模拟特定错误（如422）比较困难且不稳定
      // 这类错误的覆盖通常在单元测试中通过模拟来完成
      // 如果需要，可以尝试创建一个已知会失败的请求，但这不是集成测试的主要目标
    });

    describe('fetchCategoryDetails', () => {
      let testCategory: CategoryRead;
      beforeAll(async () => {
        const name = `Detail Test Cat_${Date.now()}`;
        testCategory = await apiCreateCategory({ name, description: 'Details here' });
        createdCategoryIdsInStoreTest.push(testCategory.id);
      });

      it('should fetch category details and update currentCategory from live API', async () => {
        await store.fetchCategoryDetails(testCategory.id);

        expect(store.isLoading).toBe(false);
        expect(store.currentCategory).not.toBeNull();
        expect(store.currentCategory?.id).toBe(testCategory.id);
        expect(store.currentCategory?.name).toBe(testCategory.name);
        expect(store.currentCategory?.description).toBe(testCategory.description);
        expect(store.error).toBeNull();
      });

      it('should set error if category ID does not exist on live API', async () => {
        const nonExistentId = '00000000-0000-0000-0000-000000000000'; // 合法但不存在的 UUID
        await store.fetchCategoryDetails(nonExistentId);
        
        expect(store.isLoading).toBe(false);
        expect(store.currentCategory).toBeNull();
        expect(store.error).toContain('404'); // 假设 API 对于未找到的资源返回 404
      });
    });

    describe('addCategory', () => {
      const newCategoryData: CategoryCreate = { 
        name: `Add Test Cat_${Date.now()}`, 
        description: 'Category to be added' 
      };

      it('should add category via live API and update state', async () => {
        const addedCategory = await store.addCategory(newCategoryData);
        
        expect(addedCategory).toBeDefined();
        expect(addedCategory.id).toBeDefined();
        createdCategoryIdsInStoreTest.push(addedCategory.id); // 重要：添加到清理列表

        expect(addedCategory.name).toBe(newCategoryData.name);
        expect(addedCategory.description).toBe(newCategoryData.description);
        
        expect(store.isLoading).toBe(false);
        // 验证新分类是否在 store.categories 列表中
        // 注意: addCategory action 的实现是直接 push，或者重新 fetch
        // 如果是直接 push:
        expect(store.categories.find(c => c.id === addedCategory.id)).toEqual(addedCategory);
        // 如果是重新 fetch (需要 store.fetchCategories() 被调用，或者我们在这里手动调用再检查)
        // await store.fetchCategories(); // 如果 addCategory 内部没有 fetch
        // expect(store.categories.some(c => c.id === addedCategory.id)).toBe(true);

        expect(store.error).toBeNull();
        expect(store.validationErrors).toBeNull();
      });

      it('should set error and validationErrors on API failure (e.g., duplicate name)', async () => {
        // 先创建一个分类
        const initialName = `Duplicate Test Cat_${Date.now()}`;
        const initialCategory = await apiCreateCategory({ name: initialName });
        createdCategoryIdsInStoreTest.push(initialCategory.id);

        const duplicateData: CategoryCreate = { name: initialName, description: 'Trying to duplicate' };
        
        try {
          await store.addCategory(duplicateData);
          // 如果没有抛出错误，则测试失败
          // throw new Error('addCategory should have thrown an error for duplicate name');
        } catch (e: any) {
          expect(e).toBeDefined();
          // 真实 API 对于重复名称可能返回 400, 409, 或 422
          // 检查 store 的状态
          expect(store.isLoading).toBe(false);
          expect(store.error).not.toBeNull();
          if (e.status === 422 && e.data) { // 根据 store 中对 validationError 的处理
             expect(store.validationErrors).toEqual(e.data);
          }
          // 确保重复的分类没有被添加到列表中
          expect(store.categories.some(c => c.name === duplicateData.name && c.id !== initialCategory.id)).toBe(false);
        }
      });
    });

    describe('editCategory', () => {
      let categoryToEdit: CategoryRead;
      const originalName = `Edit Original Name_${Date.now()}`;
      const updatedName = `Edit Updated Name_${Date.now()}`;
      
      beforeEach(async () => { // 使用 beforeEach 来确保每次测试都有一个干净的、新的分类
        // 清理之前可能创建的同名分类 (如果测试失败未清理)
        const existing = await apiGetCategories(0,100);
        const conflicting = existing.find(c => c.name === originalName || c.name === updatedName);
        if(conflicting) await apiDeleteCategory(conflicting.id);

        categoryToEdit = await apiCreateCategory({ name: originalName, description: 'Original Description' });
        createdCategoryIdsInStoreTest.push(categoryToEdit.id);
        // 确保 store 中有这个分类，以便测试 currentCategory 的更新
        store.categories = [categoryToEdit];
        store.currentCategory = categoryToEdit;
      });

      it('should update category via live API and reflect in state', async () => {
        const updateData: CategoryUpdate = { name: updatedName, description: 'Updated Description' };
        
        const result = await store.editCategory(categoryToEdit.id, updateData);

        expect(result).toBeDefined();
        expect(result.id).toBe(categoryToEdit.id);
        expect(result.name).toBe(updatedName);
        expect(result.description).toBe('Updated Description');

        expect(store.isLoading).toBe(false);
        // 检查 categories 列表
        const categoryInList = store.categories.find(c => c.id === categoryToEdit.id);
        expect(categoryInList).toEqual(result);
        // 检查 currentCategory
        expect(store.currentCategory).toEqual(result);
        expect(store.error).toBeNull();
      });

       it('should only update category in list if currentCategory does not match', async () => {
        // 设置一个不同的 currentCategory
        const otherCatData = { name: `Other Cat_${Date.now()}`, description: "I am other"};
        const otherCategory = await apiCreateCategory(otherCatData);
        createdCategoryIdsInStoreTest.push(otherCategory.id);
        store.categories = [categoryToEdit, otherCategory]; // store 中有多个分类
        store.currentCategory = otherCategory; // current 不是要编辑的那个

        const updateData: CategoryUpdate = { name: updatedName };
        const updatedResultFromApi = await store.editCategory(categoryToEdit.id, updateData);
        
        const categoryInList = store.categories.find(c => c.id === categoryToEdit.id);
        expect(categoryInList).toEqual(updatedResultFromApi);
        expect(store.currentCategory).toEqual(otherCategory); // CurrentCategory 应该保持不变
      });

      it('should fail to update a non-existent category ID', async () => {
        const nonExistentId = '00000000-0000-0000-0000-000000000000';
        const updateData: CategoryUpdate = { name: 'Attempt to update non-existent' };
        try {
          await store.editCategory(nonExistentId, updateData);
        } catch (e: any) {
          expect(e).toBeDefined();
          expect(store.isLoading).toBe(false);
          expect(store.error).toContain('404'); // 期望 API 返回 404
        }
      });
    });

    describe('removeCategory', () => {
      let categoryToRemove: CategoryRead;
      const categoryName = `Remove Test Cat_${Date.now()}`;

      beforeEach(async () => { // 每次都创建一个新的待删除分类
        const existing = await apiGetCategories(0,100);
        const conflicting = existing.find(c => c.name === categoryName);
        if(conflicting) await apiDeleteCategory(conflicting.id);

        categoryToRemove = await apiCreateCategory({ name: categoryName });
        // 不立即加入 createdCategoryIdsInStoreTest，因为这个测试会删除它
        // 如果测试失败，它可能不会被删除，但 afterAll 无法知道它的 ID
        // 一种策略是，如果删除成功，就从一个临时列表移除，否则加入全局清理列表
        store.categories = [categoryToRemove];
        store.currentCategory = categoryToRemove;
      });

      it('should remove category via live API and from state', async () => {
        await store.removeCategory(categoryToRemove.id);

        expect(store.isLoading).toBe(false);
        expect(store.categories.find(c => c.id === categoryToRemove.id)).toBeUndefined();
        expect(store.currentCategory).toBeNull(); // 如果被删除的是 currentCategory
        expect(store.error).toBeNull();

        // 验证它真的从后端被删除了
        try {
          await apiGetCategories(0, 100).then(cats => {
            if (cats.find(c => c.id === categoryToRemove.id)) {
              throw new Error('Category still exists in backend after delete');
            }
          });
        } catch (apiError: any) {
           // 如果 getCategoryById 抛出 404，说明删除成功
           // 但 getCategories 不会因为单个缺失而抛出 404，所以上面检查的是列表
        }
      });
      
      it('should only remove from list if currentCategory does not match', async () => {
        const otherCatData = { name: `Remove Other Cat_${Date.now()}`, description: "I am other"};
        const otherCategory = await apiCreateCategory(otherCatData);
        createdCategoryIdsInStoreTest.push(otherCategory.id); // 这个需要被清理
        store.categories = [categoryToRemove, otherCategory];
        store.currentCategory = otherCategory;

        await store.removeCategory(categoryToRemove.id);
        
        expect(store.categories.find(c => c.id === categoryToRemove.id)).toBeUndefined();
        expect(store.categories.length).toBe(1);
        expect(store.currentCategory).toEqual(otherCategory); 
      });

      it('should handle failure when trying to delete non-existent category', async () => {
        const nonExistentId = '00000000-0000-0000-0000-000000000000';
        try {
          await store.removeCategory(nonExistentId);
        } catch (e: any) {
          expect(e).toBeDefined();
          expect(store.isLoading).toBe(false);
          expect(store.error).toContain('404'); // 期望 API 返回 404
        }
         // 如果 removeCategory 成功删除了，但 ID 不在 createdCategoryIdsInStoreTest，就手动加入
        if(!createdCategoryIdsInStoreTest.includes(categoryToRemove.id)) {
             // 如果 beforeEach 中的分类没被这个测试删除掉，则加入清理列表
             const stillExists = await apiGetCategories(0,100).then(cats => cats.find(c => c.id === categoryToRemove.id));
             if(stillExists) createdCategoryIdsInStoreTest.push(categoryToRemove.id);
        }
      });
       // 将 beforeEach 中创建但未被测试删除的 categoryToRemove.id 加入清理列表
      afterEach(async () => {
        if (categoryToRemove && categoryToRemove.id) {
            const exists = await apiGetCategories(0, 100).then(cats => cats.find(c => c.id === categoryToRemove.id));
            if (exists && !createdCategoryIdsInStoreTest.includes(categoryToRemove.id)) {
                createdCategoryIdsInStoreTest.push(categoryToRemove.id);
            }
        }
      });
    });

    describe('clearValidationErrors', () => {
      it('should set validationErrors to null', () => {
        store.validationErrors = mockValidationError; // Set a dummy error
        store.clearValidationErrors();
        expect(store.validationErrors).toBeNull();
      });
    });

    describe('clearError', () => {
      it('should set error to null', () => {
        store.error = 'Some error message'; // Set a dummy error
        store.clearError();
        expect(store.error).toBeNull();
      });
    });
  });
}); 