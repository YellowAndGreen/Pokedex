export interface CategoryBase {
  name: string;
  description: string | null;
}

export interface CategoryCreate extends CategoryBase {}

export interface CategoryRead extends CategoryBase {
  id: number;
  created_at?: string;
  updated_at?: string;
}

export interface ImageBase {
  description: string | null;
  tags: string[] | null;
}

export interface ImageCreate {
  category_id: number;
  file: File;
  description?: string | null;
  tags?: string[] | null;
}

export interface ImageUpdate {
  category_id?: number;
  description?: string | null;
  tags?: string[] | null;
}

export interface ImageRead extends ImageBase {
  id: number;
  category_id: number;
  original_filename: string;
  stored_filename: string;
  relative_file_path: string;
  relative_thumbnail_path: string | null;
  mime_type: string;
  size_bytes: number;
  upload_date: string;
}

export interface CategoryReadWithImages extends CategoryRead {
  images: ImageRead[];
}