export interface CategoryBase {
  name: string;
  description: string;
}

export interface CategoryCreate extends CategoryBase {}

export interface CategoryRead extends CategoryBase {
  id: number;
  created_at: string;
  updated_at: string;
}

export interface ImageBase {
  description: string;
  tags: string[];
}

export interface ImageCreate extends ImageBase {
  category_id: number;
  file: File;
}

export interface ImageUpdate extends ImageBase {
  category_id?: number;
}

export interface ImageRead extends ImageBase {
  id: number;
  category_id: number;
  original_filename: string;
  relative_file_path: string;
  relative_thumbnail_path: string;
  mime_type: string;
  size_bytes: number;
  upload_date: string;
}

export interface CategoryReadWithImages extends CategoryRead {
  images: ImageRead[];
}