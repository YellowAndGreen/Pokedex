<template>
  <VDialog
    :model-value="isVisible"
    max-width="900px"
    @update:model-value="$emit('close')"
  >
    <VCard class="pa-sm-8 pa-5">


      <VCardText class="mt-5">
        <VRow v-if="images && images.length > 0">
          <VCol
            cols="12"
            md="8"
          >
            <VCarousel
              v-model="currentSlide"
              height="400"
              show-arrows="hover"
              cycle
              hide-delimiter-background
            >
              <VCarouselItem
                v-for="(image, index) in images"
                :key="image.id"
              >
                <VSheet
                  height="100%"
                  tile
                >
                  <VImg
                    :src="image.url"
                    height="100%"
                    cover
                  >
                    <div class="d-flex fill-height justify-center align-center">
                      <!-- Optionally, you can display image title or other info here -->
                      <!-- <div class="text-h2 white--text">{{ image.title || 'Slide' }}</div> -->
                    </div>
                  </VImg>
                </VSheet>
              </VCarouselItem>
            </VCarousel>
          </VCol>
          <VCol
            cols="12"
            md="4"
          >
            <div v-if="images && images.length > 0 && images[currentSlide]">
              <!-- <h5 class="text-h5 mb-2">
                {{ images[currentSlide].title || 'Image Details' }}
              </h5> -->
              <h6 class="text-h6 mb-1">
                Category: {{ categoryName }}
              </h6>
              <p v-if="images[currentSlide].description && typeof images[currentSlide].description === 'string' && images[currentSlide].description.trim() !== ''" class="text-body-1">
                {{ images[currentSlide].description }}
              </p>
              <VChip
                v-if="images[currentSlide].tags && images[currentSlide].tags!.length > 0"
                v-for="(tag, tagIndex) in images[currentSlide].tags"
                :key="tagIndex"
                small
                class="me-2 mb-2"
              >
                {{ tag }}
              </VChip>

              <!-- EXIF Data Display -->
              <div v-if="images[currentSlide].exif_info && typeof images[currentSlide].exif_info === 'object' && Object.keys(images[currentSlide].exif_info!).length > 0" class="mt-4">
                <div class="text-body-2 mb-4 text-disabled"> IMAGE METADATA </div>
                <div class="d-flex flex-column gap-y-3">
                  <div 
                    v-for="(value, key) in images[currentSlide].exif_info"
                    :key="key"
                    v-if="value !== null && value !== ''" 
                    class="d-flex align-center gap-x-2"
                  >
                    <VIcon icon="ri-information-line" size="20" />
                    <div class="font-weight-medium">{{ formatExifKey(key as string) }}: </div>
                    <div>{{ value }}</div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else-if="images && images.length > 0">
              <p>Select an image to see details.</p>
            </div>
            <div v-else>
              <p>No image details to display.</p>
            </div>
          </VCol>
        </VRow>
        <VRow v-else>
          <VCol cols="12" class="text-center">
            <p>No images available for this category.</p>
          </VCol>
        </VRow>
      </VCardText>

      <VCardActions class="mt-6">
        <VSpacer />
      </VCardActions>
    </VCard>
  </VDialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface ExifData {
  make?: string | null;
  model?: string | null;
  lens_make?: string | null;
  bits_per_sample?: string | null;
  date_time_original?: string | null;
  exposure_time?: string | null;
  f_number?: string | null;
  exposure_program?: string | null;
  iso_speed_rating?: string | null;
  focal_length?: string | null;
  lens_specification?: string | null;
  lens_model?: string | null;
  exposure_mode?: string | null;
  cfa_pattern?: string | null;
  color_space?: string | null;
  white_balance?: string | null;
}

interface Image {
  id: string
  url: string
  title?: string
  description?: string
  tags?: string[]
  exif_info?: ExifData | null
}

interface Props {
  isVisible: boolean
  categoryName: string
  images: Image[]
}

const props = defineProps<Props>()
const emit = defineEmits(['close'])

const currentSlide = ref(0)

// 辅助函数，用于格式化EXIF键名
const formatExifKey = (key: string): string => {
  if (!key) return '';
  // 将 snake_case 或 camelCase 转换为 Title Case
  return key
    .replace(/_/g, ' ')
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, (str) => str.toUpperCase())
    .trim();
};

watch(() => props.images, (newImages) => {
  if (newImages && newImages.length > 0) {
    currentSlide.value = 0
  }
}, { immediate: true, deep: true })

watch(() => props.isVisible, (newVal) => {
  if (newVal && props.images && props.images.length > 0) {
    currentSlide.value = 0
  }
})
</script>

<style scoped>
.v-dialog-close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
}
</style> 