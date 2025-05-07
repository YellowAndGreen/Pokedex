# 图鉴式图片管理工具 - 前端设计文档

**文档信息**

*   **文档名称：** 图鉴式图片管理工具 - 前端设计文档
*   **版本：** 1.0
*   **创建日期：** 2025年5月7日
*   **关联后端API版本：** 1.0 (基于 `/api/...` 路由)
*   **目标读者：** 前端开发人员, UI/UX 设计师, 项目经理

---

**1. 引言**

**1.1 文档目的**
本文档旨在详细规划图鉴式图片管理工具的前端界面设计、组件划分、状态管理策略以及与后端API的交互方式。它是前端开发的蓝图，确保实现的功能符合项目目标 (`README.md`) 并能有效利用已定义的后端服务。

**1.2 核心用户流程**

```mermaid
graph LR
    A[用户访问应用] --> B{类别列表视图};
    B -- 点击类别 --> C{分类图片视图};
    B -- 点击“创建类别” --> D[类别创建/编辑表单];
    D -- 提交 --> B;
    C -- 点击“上传图片” --> E[图片上传表单/组件];
    E -- 提交 --> C;
    C -- 点击图片缩略图 --> F[图片详情展示(模态框)];
    F -- 点击“编辑元数据” --> G[图片元数据编辑表单];
    G -- 提交 --> F;
    C -- 点击图片“删除” --> C;
    B -- 点击类别“删除” --> B;
```

---

**2. 技术选型与核心库**

遵循 `README.md` 的规划：

*   **核心框架:** Vue.js (Vue 3)
*   **构建工具:** Vite
*   **UI 组件库:** Element Plus (提供丰富的预构建组件，加速开发)
*   **状态管理:** Pinia (Vue 3 官方推荐，类型安全且直观)
*   **路由管理:** Vue Router
*   **HTTP 客户端:** Axios (用于与后端API通信)
*   **语言:** JavaScript (或 TypeScript, 根据团队决定)

---

**3. 状态管理 (Pinia)**

定义以下 Store 来管理应用状态：

*   **`categoryStore` (`src/store/categoryStore.js`)**
    *   **State:**
        *   `categories: CategoryRead[]` - 所有类别的列表。
        *   `currentCategoryDetail: CategoryReadWithImages | null` - 当前正在查看的类别及其图片详情。
        *   `isLoadingCategories: boolean` - 类别列表加载状态。
        *   `isLoadingCategoryDetail: boolean` - 特定类别详情加载状态。
        *   `error: string | null` - 存储类别相关的错误信息。
    *   **Actions:**
        *   `fetchCategories()`: 调用 API (`GET /api/categories/`) 获取所有类别，更新 `categories` 和 `isLoadingCategories`。处理错误。
        *   `fetchCategoryWithImages(categoryId: number)`: 调用 API (`GET /api/categories/{categoryId}/`) 获取特定类别及其图片，更新 `currentCategoryDetail` 和 `isLoadingCategoryDetail`。处理错误。
        *   `createCategory(categoryData: CategoryCreate)`: 调用 API (`POST /api/categories/`) 创建新类别，成功后刷新类别列表 (`fetchCategories`) 或直接将新类别添加到 `categories` 状态。处理错误和反馈。
        *   `updateCategory(categoryId: number, categoryData: CategoryCreate)`: 调用 API (`PUT /api/categories/{categoryId}/`) 更新类别，成功后更新 `categories` 列表和 `currentCategoryDetail` (如果正在查看该类别)。处理错误和反馈。
        *   `deleteCategory(categoryId: number)`: 调用 API (`DELETE /api/categories/{categoryId}/`) 删除类别，成功后从 `categories` 列表中移除。处理错误和反馈（需要注意后端关于删除非空类别的策略）。
*   **`imageStore` (`src/store/imageStore.js`)** (主要负责图片操作的 Actions)
    *   **State:**
        *   `isUploading: boolean` - 图片上传状态。
        *   `isUpdating: boolean` - 图片元数据更新状态。
        *   `isDeleting: boolean` - 图片删除状态。
        *   `error: string | null` - 存储图片操作相关的错误信息。
    *   **Actions:**
        *   `uploadImage(formData: FormData)`: 调用 API (`POST /api/images/upload/`) 上传图片。需要 `formData` 包含 `file`, `category_id`, `description`, `tags`。成功后触发 `categoryStore.fetchCategoryWithImages` 刷新当前分类的图片列表。处理错误和反馈。
        *   `updateImageMetadata(imageId: number, imageData: ImageUpdate)`: 调用 API (`PUT /api/images/{imageId}/`) 更新图片元数据。成功后触发 `categoryStore.fetchCategoryWithImages` 刷新当前分类的图片列表（或直接更新 `currentCategoryDetail` 中的对应图片）。处理错误和反馈。
        *   `deleteImage(imageId: number, categoryId: number)`: 调用 API (`DELETE /api/images/{imageId}/`) 删除图片。成功后触发 `categoryStore.fetchCategoryWithImages(categoryId)` 刷新当前分类的图片列表。处理错误和反馈。

---

**4. API 服务层 (`src/services/apiService.js`)**

*   封装 Axios 实例，配置 `baseURL` (例如，从 `.env` 文件读取 `VITE_API_BASE_URL`，指向 `http://localhost:8000`)。
*   提供与后端 API 端点对应的异步函数：
    *   `getCategories(skip: number, limit: number): Promise<CategoryRead[]>`
    *   `getCategoryWithImages(categoryId: number): Promise<CategoryReadWithImages>`
    *   `postCategory(data: CategoryCreate): Promise<CategoryRead>`
    *   `putCategory(categoryId: number, data: CategoryCreate): Promise<CategoryRead>`
    *   `deleteCategoryById(categoryId: number): Promise<void>`
    *   `uploadImageFile(formData: FormData): Promise<ImageRead>`
    *   `getImage(imageId: number): Promise<ImageRead>`
    *   `updateImage(imageId: number, data: ImageUpdate): Promise<ImageRead>`
    *   `deleteImageById(imageId: number): Promise<void>`
*   可以添加请求/响应拦截器，用于统一处理错误、添加认证头（未来）等。

---

**5. 页面设计与组件**

**5.1 整体布局 (`src/App.vue` 或 `src/layouts/MainLayout.vue`)**

*   **结构:** 使用 Element Plus 的 `ElContainer` 实现经典后台布局。
    *   `ElHeader`: 应用标题，可能包含全局操作按钮（如全局上传入口 - V1可选）。
    *   `ElContainer` (内部):
        *   `ElAside`: 侧边栏，宽度固定。
            *   使用 `ElScrollbar` 包裹 `ElMenu`，用于显示和导航类别列表。
            *   菜单项应动态从 `categoryStore.categories` 生成。
            *   提供一个 "创建新类别" 的按钮或菜单项。
        *   `ElMain`: 主要内容区域，填充 `<router-view>` 来展示不同页面的内容。
*   **交互:**
    *   点击侧边栏类别菜单项，通过 `Vue Router` 导航到对应的 `CategoryImagesView`。
    *   点击 "创建新类别" 按钮，弹出创建类别的对话框。

**5.2 类别列表视图 (`src/views/CategoryListView.vue`)**

*   **挂载路由:** `/` 或 `/categories`。
*   **目的:** 展示所有图片类别，提供管理入口。
*   **核心组件:**
    *   (如果作为首页，可能不需要独立视图，直接在主布局的 `ElMain` 中展示)。
    *   如果需要一个专门的列表页（例如，带有搜索/过滤功能 - V1范围外），可以使用 `ElTable` 或 `ElRow`/`ElCol` 结合 `CategoryCard` 组件。
    *   `ElButton` (标记 "创建新类别")：触发创建对话框。
    *   `ElDialog` (用于创建/编辑类别):
        *   包含 `CategoryForm` 组件。
        *   区分创建和编辑模式。
    *   列表项/卡片 (`CategoryCard`):
        *   显示类别名称 (`name`) 和描述 (`description`)。
        *   显示该类别下的图片数量（需要后端 API 支持或前端计算）。
        *   操作按钮：
            *   "查看图片" (`ElButton`): 导航到 `CategoryImagesView`。
            *   "编辑" (`ElButton`): 打开编辑类别的 `ElDialog`。
            *   "删除" (`ElButton` + `ElPopconfirm`): 触发删除操作 (`categoryStore.deleteCategory`)。
*   **数据交互:**
    *   `onMounted`: 调用 `categoryStore.fetchCategories()` 加载数据。
    *   使用 `v-loading` 指令或类似方式展示加载状态 (`categoryStore.isLoadingCategories`)。
    *   表单提交时调用 `categoryStore.createCategory()` 或 `categoryStore.updateCategory()`。
    *   删除时调用 `categoryStore.deleteCategory()`。
    *   显示错误信息（从 `categoryStore.error`）。

**5.3 分类图片视图 (`src/views/CategoryImagesView.vue`)**

*   **挂载路由:** `/categories/:id` (例如 `/categories/1`)。
*   **目的:** 展示选定类别下的所有图片，并提供图片管理功能。
*   **核心组件:**
    *   `ElPageHeader`: 显示当前类别名称和描述 (`currentCategoryDetail.name`, `currentCategoryDetail.description`)，提供返回按钮。
    *   `ElButton` (标记 "上传图片到此类别"): 触发上传对话框/组件。
    *   `ElDialog` (用于上传图片):
        *   包含 `ImageUploadForm` 组件。
        *   自动填充当前 `category_id`。
    *   图片展示区:
        *   使用 `ElRow` 和 `ElCol` 创建响应式网格布局。
        *   `v-for` 遍历 `currentCategoryDetail.images`。
        *   每个图片使用 `ImageThumbnail` 组件展示。
    *   `ElPagination` (如果图片数量多): 用于图片列表的分页（需要后端 API 支持分页获取图片，目前 `GET /api/categories/{id}/` 返回所有图片，V1可简化不分页或前端分页）。
    *   `ElDialog` (用于显示图片大图和元数据):
        *   包含 `ElImage` (显示大图)。
        *   `ElDescriptions` 显示图片元数据 (`original_filename`, `mime_type`, `size_bytes`, `upload_date`, `description`, `tags`)。
        *   "编辑元数据" 按钮 (`ElButton`)。
    *   `ElDialog` (用于编辑图片元数据):
        *   包含 `ImageMetaForm` 组件。
*   **数据交互:**
    *   `onMounted` / `watch` (监听路由参数 `$route.params.id`): 调用 `categoryStore.fetchCategoryWithImages(categoryId)` 加载数据。
    *   使用 `v-loading` 指令或类似方式展示加载状态 (`categoryStore.isLoadingCategoryDetail`)。
    *   图片上传表单提交时调用 `imageStore.uploadImage()`。
    *   点击图片缩略图时，打开图片详情对话框。
    *   编辑元数据表单提交时调用 `imageStore.updateImageMetadata()`。
    *   删除图片按钮点击时（通过 `ImageThumbnail` 组件触发），调用 `imageStore.deleteImage()`。
    *   显示错误信息（从 `categoryStore.error` 或 `imageStore.error`）。

**5.4 可复用组件 (`src/components/`)**

*   **`CategoryForm.vue`**:
    *   包含 `ElForm`, `ElFormItem`, `ElInput` (用于名称和描述)。
    *   处理表单验证。
    *   `props`: `initialData` (用于编辑模式), `isEditMode`。
    *   `emits`: `submit` (携带表单数据)。
*   **`ImageThumbnail.vue`**:
    *   `props`: `image: ImageRead` (包含图片信息)。
    *   核心是 `ElImage` 组件，`src` 指向缩略图 URL (`/static/uploads/thumbnails/...` + `image.relative_thumbnail_path`)，`preview-src-list` 可以包含大图 URL (`/static/uploads/images/...` + `image.relative_file_path`)，利用 Element Plus 的预览功能。启用 `lazy` 加载。
    *   在其上覆盖操作按钮（查看详情、编辑元数据、删除），或在鼠标悬停时显示。
    *   `emits`: `view-detail`, `edit-meta`, `delete` (携带图片 ID)。
*   **`ImageUploadForm.vue`**:
    *   包含 `ElUpload` (用于文件选择和预览，设置 `accept` 限制文件类型，可能需要自定义 `http-request` 来配合 `imageStore.uploadImage` 的 `FormData` 需求)。
    *   `ElInput` (描述), `ElInput` (标签)。
    *   `props`: `categoryId`。
    *   `emits`: `upload-success`, `upload-error`。
    *   处理上传状态 (`imageStore.isUploading`)。
*   **`ImageMetaForm.vue`**:
    *   包含 `ElForm`, `ElFormItem`, `ElInput` (描述, 标签), `ElSelect` (可选，用于更改类别 `category_id`)。
    *   `props`: `initialData: ImageRead`。
    *   `emits`: `submit` (携带 `ImageUpdate` 数据)。

---

**6. 路由管理 (`src/router/index.js`)**

*   配置路由规则：
    *   `{ path: '/', component: CategoryListView }` (或指向包含侧边栏和主区域的布局组件，默认显示某种视图)
    *   `{ path: '/categories', component: CategoryListView }` (如果需要明确路径)
    *   `{ path: '/categories/:id', component: CategoryImagesView, props: true }` (`props: true` 可以将路由参数 `:id` 作为 prop 传入组件)
    *   可能需要一个 404 页面。

---

**7. 错误处理与用户反馈**

*   **API 调用:** 在 `apiService.js` 或 Store 的 Actions 中统一处理 Axios 错误。捕获错误并更新 Store 中的 `error` 状态。
*   **UI 反馈:**
    *   使用 Element Plus 的 `ElLoading` (服务或指令) 或骨架屏 (`ElSkeleton`) 展示加载状态。
    *   操作成功时，使用 `ElMessage.success()` 给出提示。
    *   发生错误时，使用 `ElNotification` 或 `ElMessage.error()` 显示 Store 中的错误信息。
    *   表单验证失败时，利用 `ElForm` 的内置验证状态。

---

**8. 未来展望（V1 之后）**

*   用户认证与登录页面。
*   高级搜索/过滤栏。
*   图片批量操作界面。
*   更精细的权限控制。

---

此设计文档提供了前端开发的主要方向和结构。开发过程中可能需要根据实际情况进行微调。