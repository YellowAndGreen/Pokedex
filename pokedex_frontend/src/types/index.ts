export interface CategoryRead {
  id: number;
  name: string;
  description?: string | null;
  thumbnailUrl?: string | null;
}

export interface ImageRead {
  id: number;
  title?: string | null;
  description?: string | null;
  imageUrl: string;
  categoryId: number;
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
