export interface CategoryBase {
  name: string;
  description?: string;
}

export interface CategoryCreate extends CategoryBase {
  thumbnail?: File;
}

export interface CategoryRead extends CategoryBase {
  id: string;
  thumbnailUrl: string;
  createdDate: string;
  updatedDate: string;
}

export interface CategoryUpdate {
  name?: string;
  description?: string;
  thumbnailUrl?: string;
}

export interface ImageBase {
  title: string;
  description?: string;
}

export interface ImageCreate {
  categoryId: string;
  imageFile: File;
}

export interface ImageUpdate {
  title?: string;
  description?: string;
  categoryId?: string;
}

export interface ImageRead extends ImageBase {
  id: string;
  categoryId: string;
  imageUrl: string;
  createdDate: string;
  metadata: {
    width: number;
    height: number;
    fileSize: string;
    format: string;
    cameraModel?: string;
    location?: string;
  };
}

export interface CategoryReadWithImages extends CategoryRead {
  images: ImageRead[];
}
