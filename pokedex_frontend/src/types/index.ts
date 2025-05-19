export interface CategoryRead {
  id: string;
  name: string;
  description?: string | null;
  thumbnail_url?: string | null;
  created_at?: string;
  updated_at?: string;
  thumbnail_path?: string | null;
}

export interface ImageRead {
  id: string;
  title?: string | null;
  description?: string | null;
  image_url: string;
  categoryId: string;
  thumbnail_url?: string | null;
  created_at?: string;
  updated_at?: string;
  original_filename?: string | null;
  mime_type?: string | null;
  size_bytes?: number | null;
  tags?: string | null;
}

export interface CategoryReadWithImages extends CategoryRead {
  images: ImageRead[];
}

export interface CategoryCreate {
  name: string;
  description?: string | null;
}

export interface CategoryUpdate {
  name?: string;
  description?: string | null;
  thumbnailUrl?: string | null;
}
