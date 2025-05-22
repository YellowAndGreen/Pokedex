// src/services/apiService.ts
import axios, { type AxiosError, type AxiosResponse } from 'axios';
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
  HTTPValidationError
} from '@/types'; // 使用路径别名 @

// 如果未设置 VITE_API_URL，则默认为 'http://localhost:8000'。
// 请确保您的 .env 文件中的 VITE_API_URL 设置为协议和主机，例如 http://localhost:8000
const API_BASE_URL_INTERNAL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const API_BASE_URL = API_BASE_URL_INTERNAL; // 导出
const API_PREFIX = '/api'; // API 端点的前缀
export const FULL_API_URL = `${API_BASE_URL}${API_PREFIX}`;

// 创建用于 API 调用的 Axios 实例。
const apiClient = axios.create({
  baseURL: FULL_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 辅助函数：处理 API 错误
const handleApiError = (error: AxiosError) => {
  if (error.response) {
    // 请求已发出，服务器以状态码响应
    // 但不在 2xx 范围内
    console.error('API Error Response:', error.response.data);
    console.error('Status:', error.response.status);
    console.error('Headers:', error.response.headers);
    // 可以抛出更具体的错误或包含错误数据的错误对象
    const apiError = new Error(
      `API request failed with status ${error.response.status}`
    ) as any;
    apiError.data = error.response.data as HTTPValidationError; // 假设错误响应体是 HTTPValidationError
    apiError.status = error.response.status;
    throw apiError;
  } else if (error.request) {
    // 请求已发出但未收到响应
    console.error('API No Response:', error.request);
    throw new Error('API request made but no response received.');
  } else {
    // 设置请求时发生了一些事情，触发了错误
    console.error('API Request Setup Error:', error.message);
    throw new Error(`API request setup error: ${error.message}`);
  }
};


// --- Category Service Functions (类别服务函数) ---

/**
 * 创建一个新类别。
 * 对应: POST /api/categories/
 * @param categoryData - 新类别的数据。
 * @returns 一个解析为已创建类别数据的 Promise。
 */
export const createCategory = async (categoryData: CategoryCreate): Promise<CategoryRead> => {
  try {
    const response: AxiosResponse<CategoryRead> = await apiClient.post('/categories/', categoryData);
    return response.data;
  } catch (error) {
    handleApiError(error as AxiosError);
    throw error; // 重新抛出，以便调用者可以处理
  }
};

/**
 * 检索所有类别的列表。支持分页。
 * 对应: GET /api/categories/
 * @param skip - 要跳过的记录数（用于分页）。
 * @param limit - 要返回的最大记录数（用于分页）。
 * @returns 一个解析为类别数据数组的 Promise。
 */
export const getCategories = async (skip: number = 0, limit: number = 100): Promise<CategoryRead[]> => {
  try {
    const response: AxiosResponse<CategoryRead[]> = await apiClient.get('/categories/', {
      params: { skip, limit },
    });
    return response.data;
  } catch (error) {
    handleApiError(error as AxiosError);
    throw error;
  }
};

/**
 * 通过 ID 检索特定类别。
 * 对应: GET /api/categories/{category_id}/
 * @param categoryId - 要检索的类别的 ID（UUID字符串）。
 * @returns 一个解析为类别数据的 Promise。
 */
export const getCategoryById = async (categoryId: string): Promise<CategoryRead> => {
  try {
    const response: AxiosResponse<CategoryRead> = await apiClient.get(`/categories/${categoryId}/`);
    return response.data;
  } catch (error) {
    handleApiError(error as AxiosError);
    throw error;
  }
};

/**
 * 更新现有类别。
 * 对应: PUT /api/categories/{category_id}/
 * @param categoryId - 要更新的类别的 ID（UUID字符串）。
 * @param categoryData - 用于更新类别的数据。
 * @returns 一个解析为已更新类别数据的 Promise。
 */
export const updateCategory = async (categoryId: string, categoryData: CategoryUpdate): Promise<CategoryRead> => {
  try {
    const response: AxiosResponse<CategoryRead> = await apiClient.put(`/categories/${categoryId}/`, categoryData);
    return response.data;
  } catch (error) {
    handleApiError(error as AxiosError);
    throw error;
  }
};

/**
 * 通过 ID 删除类别。
 * 对应: DELETE /api/categories/{category_id}/
 * @param categoryId - 要删除的类别的 ID（UUID字符串）。
 * @returns 一个解析为已删除类别数据（或确认信息）的 Promise。
 */
export const deleteCategory = async (categoryId: string): Promise<CategoryRead> => {
  try {
    const response: AxiosResponse<CategoryRead> = await apiClient.delete(`/categories/${categoryId}/`);
    return response.data;
  } catch (error) {
    handleApiError(error as AxiosError);
    throw error;
  }
};

// --- Image Service Functions (图片服务函数) ---

/**
 * 获取图片的缩略图 URL。
 * 注意：此函数返回 URL 字符串。实际图片由浏览器的 <img> src 加载。
 * 对应: GET /api/images/{image_id}/thumbnail
 * @param imageId - 图片的 ID（UUID字符串）。
 * @returns 图片缩略图的 URL 字符串。
 */
export const getImageThumbnailUrl = (imageId: string): string => {
  return `${FULL_API_URL}/images/${imageId}/thumbnail`;
};

/**
 * 获取用于查看图片的 URL。
 * 注意：此函数返回 URL 字符串。实际图片由浏览器的 <img> src 加载。
 * 对应: GET /api/images/{image_id}/view
 * @param imageId - 图片的 ID（UUID字符串）。
 * @returns 查看图片的 URL 字符串。
 */
export const getViewImageUrl = (imageId: string): string => {
  return `${FULL_API_URL}/images/${imageId}/view`;
};

/**
 * 上传新图片及其元数据。
 * 对应: POST /api/images/upload/
 * @param imageFile - 图片文件 (File 对象)。
 * @param metadata - 图片的元数据 (标题、category_id 等)。
 * @returns 一个解析为已创建图片数据的 Promise。
 */
export const uploadImage = async (imageFile: File, metadata: ImageCreateMetadata): Promise<ImageRead> => {
  const formData = new FormData();
  formData.append('file', imageFile);
  formData.append('category_id', metadata.category_id); // Required

  // For fields that are string | null in openapi, send empty string if null to ensure field presence.
  formData.append('title', metadata.title ?? ''); 
  formData.append('description', metadata.description ?? '');
  formData.append('tags', metadata.tags ?? '');
  
  // For set_as_category_thumbnail (boolean | null, default: false)
  // Send its string representation. Backend should handle 'false' string or default if not sent.
  // Sending explicitly based on frontend type, converting boolean to string.
  formData.append('set_as_category_thumbnail', (metadata.set_as_category_thumbnail === true).toString());

  try {
    const response: AxiosResponse<ImageRead> = await apiClient.post('/images/upload/', formData, {
      headers: { 
        'Content-Type': undefined // Allow Axios to set Content-Type for FormData
      }
    });
    return response.data;
  } catch (error) {
    handleApiError(error as AxiosError);
    throw error;
  }
};

/**
 * 检索图片列表。支持分页和过滤。
 * 对应: GET /api/images/
 * @param skip - 要跳过的记录数。
 * @param limit - 要返回的最大记录数。
 * @param categoryId - 按类别 ID 可选过滤（UUID字符串）。
 * @returns 一个解析为图片数据数组的 Promise。
 */
export const getImages = async (
  skip: number = 0,
  limit: number = 50,
  categoryId?: string
): Promise<ImageRead[]> => {
  try {
    const params: any = { skip, limit };
    if (categoryId) {
      params.category_id = categoryId;
    }

    // WARNING: The endpoint GET /api/images/ is NOT defined in the provided openapi.json.
    // This function will likely cause a 404 if the backend strictly follows the openapi.json.
    // If images are meant to be fetched via categories, this function might need to be removed or re-designed.
    const response: AxiosResponse<ImageRead[]> = await apiClient.get('/images/', { params });
    
    // Assuming backend returns ImageRead[] where each ImageRead already contains image_url and thumbnail_url
    return response.data;
  } catch (error) {
    handleApiError(error as AxiosError);
    throw error;
  }
};

/**
 * 通过 ID 检索特定图片。
 * 对应: GET /api/images/{image_id}/
 * @param imageId - 要检索的图片的 ID（UUID字符串）。
 * @returns 一个解析为图片数据的 Promise。
 */
export const getImageById = async (imageId: string): Promise<ImageRead> => {
  try {
    const response: AxiosResponse<ImageRead> = await apiClient.get(`/images/${imageId}/`);
    return response.data;
  } catch (error) {
    handleApiError(error as AxiosError);
    throw error;
  }
};

/**
 * 更新现有图片的元数据。
 * 对应: PUT /api/images/{image_id}/
 * @param imageId - 要更新的图片的 ID（UUID字符串）。
 * @param imageData - 用于更新图片的数据。
 * @returns 一个解析为已更新图片数据的 Promise。
 */
export const updateImage = async (imageId: string, imageData: ImageUpdate): Promise<ImageRead> => {
  try {
    const response: AxiosResponse<ImageRead> = await apiClient.put(`/images/${imageId}/`, imageData);
    return response.data;
  } catch (error) {
    handleApiError(error as AxiosError);
    throw error;
  }
};

/**
 * 通过 ID 删除图片。
 * 对应: DELETE /api/images/{image_id}/
 * @param imageId - 要删除的图片的 ID（UUID字符串）。
 * @returns 一个解析为已删除图片数据（或确认信息）的 Promise。
 */
export const deleteImage = async (imageId: string): Promise<ImageRead> => { // OpenAPI 指定返回 ImageRead
  try {
    const response: AxiosResponse<ImageRead> = await apiClient.delete(`/images/${imageId}/`);
    return response.data;
  } catch (error) {
    handleApiError(error as AxiosError);
    throw error;
  }
};

// --- Species Service Functions (物种服务函数) ---

/**
 * 创建一个新物种条目。
 * 对应: POST /api/species/
 * @param speciesData - 新物种的数据。
 * @returns 一个解析为已创建物种数据的 Promise。
 */
export const createSpecies = async (speciesData: SpeciesCreate): Promise<SpeciesRead> => {
  try {
    const response: AxiosResponse<SpeciesRead> = await apiClient.post('/species/', speciesData);
    return response.data;
  } catch (error) {
    handleApiError(error as AxiosError);
    throw error;
  }
};

/**
 * 检索所有物种的列表。支持分页。
 * 对应: GET /api/species/
 * @param skip - 要跳过的记录数。
 * @param limit - 要返回的最大记录数。
 * @returns 一个解析为物种数据数组的 Promise。
 */
export const getAllSpecies = async (skip: number = 0, limit: number = 100): Promise<SpeciesRead[]> => {
  try {
    const response: AxiosResponse<SpeciesRead[]> = await apiClient.get('/species/', {
      params: { skip, limit },
    });
    return response.data;
  } catch (error) {
    handleApiError(error as AxiosError);
    throw error;
  }
};

/**
 * 根据查询字符串搜索物种。支持分页。
 * 对应: GET /api/species/search/
 * @param query - 搜索查询字符串。
 * @param skip - 要跳过的记录数。
 * @param limit - 要返回的最大记录数。
 * @returns 一个解析为匹配物种数据数组的 Promise。
 */
export const searchSpecies = async (query: string, skip: number = 0, limit: number = 20): Promise<SpeciesRead[]> => {
  try {
    const response: AxiosResponse<SpeciesRead[]> = await apiClient.get('/species/search/', {
      params: { query, skip, limit },
    });
    return response.data;
  } catch (error) {
    handleApiError(error as AxiosError);
    throw error;
  }
};

/**
 * 通过 ID 检索特定物种。
 * 对应: GET /api/species/{species_id}
 * @param speciesId - 要检索的物种的 ID。
 * @returns 一个解析为物种数据的 Promise。
 */
export const getSpeciesById = async (speciesId: number): Promise<SpeciesRead> => {
  try {
    const response: AxiosResponse<SpeciesRead> = await apiClient.get(`/species/${speciesId}`);
    return response.data;
  } catch (error) {
    handleApiError(error as AxiosError);
    throw error;
  }
};

/**
 * 更新现有物种条目。
 * 对应: PUT /api/species/{species_id}
 * @param speciesId - 要更新的物种的 ID。
 * @param speciesData - 用于更新物种的数据。
 * @returns 一个解析为已更新物种数据的 Promise。
 */
export const updateSpecies = async (speciesId: number, speciesData: SpeciesUpdate): Promise<SpeciesRead> => {
  try {
    const response: AxiosResponse<SpeciesRead> = await apiClient.put(`/species/${speciesId}`, speciesData);
    return response.data;
  } catch (error) {
    handleApiError(error as AxiosError);
    throw error;
  }
};

/**
 * 通过 ID 删除物种。
 * 对应: DELETE /api/species/{species_id}
 * @param speciesId - 要删除的物种的 ID。
 * @returns 一个解析为已删除物种数据（或确认信息）的 Promise。
 */
export const deleteSpecies = async (speciesId: number): Promise<SpeciesRead> => { // OpenAPI 指定返回 SpeciesRead
  try {
    const response: AxiosResponse<SpeciesRead> = await apiClient.delete(`/species/${speciesId}`);
    return response.data;
  } catch (error) {
    handleApiError(error as AxiosError);
    throw error;
  }
};
