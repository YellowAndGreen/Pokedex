// src/types/index.ts

/**
 * 表示验证错误项。
 * 对应 OpenAPI schema: ValidationError
 */
export interface ValidationError {
  loc: (string | number)[]; // 错误位置
  msg: string; // 错误信息
  type: string; // 错误类型
}

/**
 * 表示来自 API 的 HTTP 验证错误响应。
 * 对应 OpenAPI schema: HTTPValidationError
 */
export interface HTTPValidationError {
  detail?: ValidationError[]; // 验证错误数组
}

// --- Category Types (类别类型) ---

/**
 * 创建新类别时使用的数据模型。
 * 对应 OpenAPI schema: CategoryCreate
 */
export interface CategoryCreate {
  name: string;        // 类别名称，必须唯一
  description?: string | null; // 类别的可选描述
}

/**
 * 从 API 读取/返回类别信息时使用的数据模型。
 * 对应 OpenAPI schema: CategoryRead
 */
export interface CategoryRead {
  id: number;          // 类别的唯一标识符
  name: string;        // 类别名称
  description?: string | null; // 可选描述
  image_count: number; // 此类别中的图片数量
}

/**
 * 更新现有类别时使用的数据模型。
 * 对应 OpenAPI schema: CategoryUpdate
 */
export interface CategoryUpdate {
  name?: string;        // 可选的新类别名称
  description?: string | null; // 可选的新描述
}

// --- Image Types (图片类型) ---

/**
 * 创建/上传新图片时元数据的数据模型。
 * 实际文件将作为 FormData 处理。
 * 对应 POST /api/images/ 的参数
 */
export interface ImageCreateMetadata {
  title: string;        // 图片标题
  description?: string | null; // 可选描述
  category_id: number;  // 图片所属类别的 ID
  species_id?: number | null;  // 图片关联物种的可选 ID
}

/**
 * 从 API 读取/返回图片信息时使用的数据模型。
 * 对应 OpenAPI schema: ImageRead
 */
export interface ImageRead {
  id: number;             // 图片的唯一标识符
  title: string;          // 图片标题
  description?: string | null;   // 可选描述
  category_id: number;    // 图片所属类别的 ID
  species_id?: number | null;    // 可选的物种 ID
  file_path: string;      // 服务器端原始图片文件的路径 (主要供后端使用)
  thumbnail_path: string; // 服务器端缩略图文件的路径 (主要供后端使用)
  created_at: string;     // 创建时间戳 (ISO 8601 格式)
  updated_at: string;     // 最后更新时间戳 (ISO 8601 格式)

  // 前端辅助属性，用于直接在模板中显示图片
  view_url?: string;      // 查看完整图片的 URL
  thumbnail_url?: string; // 缩略图的 URL
}

/**
 * 更新图片元数据时使用的数据模型。
 * 对应 OpenAPI schema: ImageUpdate
 */
export interface ImageUpdate {
  title?: string;       // 可选的新标题
  description?: string | null; // 可选的新描述
  category_id?: number; // 可选的新类别 ID
  species_id?: number | null;  // 可选的新物种 ID
}

// --- Species Types (物种类型) ---

/**
 * 创建新物种条目时使用的数据模型。
 * 对应 OpenAPI schema: SpeciesCreate
 */
export interface SpeciesCreate {
  order_details: string;    // 目信息 (例如: 雀形目 Passeriformes)
  family_details: string;   // 科信息 (例如: 裸鼻雀科 Thraupidae)
  genus_details: string;    // 属信息 (例如: 印加雀属 Incaspiza)
  name_chinese: string;     // 中文种名
  name_english?: string | null;    // 英文种名
  name_latin?: string | null;      // 学名 (拉丁文学名)
  href?: string | null;            // 相关链接
  pinyin_full?: string | null;     // 中文名全拼 (小写)
  pinyin_initials?: string | null; // 中文名拼音首字母 (小写)
}

/**
 * 从 API 读取/返回物种信息时使用的数据模型。
 * 对应 OpenAPI schema: SpeciesRead
 */
export interface SpeciesRead {
  id: number;               // 物种的唯一标识符
  order_details: string;
  family_details: string;
  genus_details: string;
  name_chinese: string;
  name_english?: string | null;
  name_latin?: string | null;
  href?: string | null;
  pinyin_full?: string | null;
  pinyin_initials?: string | null;
}

/**
 * 更新现有物种条目时使用的数据模型。
 * 对应 OpenAPI schema: SpeciesUpdate
 */
export interface SpeciesUpdate {
  order_details?: string;
  family_details?: string;
  genus_details?: string;
  name_chinese?: string;
  name_english?: string | null;
  name_latin?: string | null;
  href?: string | null;
  pinyin_full?: string | null;
  pinyin_initials?: string | null;
}

/**
 * 用于分页响应的通用接口（如果 API 支持）。
 * 注意：当前的 OpenAPI 规范直接为列表端点返回数组。
 * 如果后端开始提供分页元数据，则这是一个占位符。
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  // 可能还有其他字段，如 `pages`
}
