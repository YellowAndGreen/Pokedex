<template>
  <VDialog
    :model-value="isVisible"
    max-width="900px"
    @update:model-value="$emit('close')"
  >
    <VCard class="pa-sm-8 pa-5">
      <VBtn
        icon
        class="v-dialog-close-btn"
        @click="$emit('close')"
      >
        <VIcon icon="ri-close-line" />
      </VBtn>

      <VCardTitle class="text-center text-h4 mb-2">
        {{ categoryName }} - Image Gallery
      </VCardTitle>

      <VCardText class="mt-5">
        <VRow v-if="images && images.length > 0">
          <VCol
            cols="12"
            md="8"
          >
            <VCarousel
              v-model="currentSlide"
              show-arrows="hover"
              hide-delimiters
              height="400"
            >
              <VCarouselItem
                v-for="(image, index) in images"
                :key="image.id"
                :src="image.url"
                cover
              />
            </VCarousel>
          </VCol>
          <VCol
            cols="12"
            md="4"
          >
            <div v-if="images && images.length > 0 && images[currentSlide]">
              <h5 class="text-h5 mb-2">
                {{ images[currentSlide].title || 'Image Details' }}
              </h5>
              <p class="text-body-1">
                {{ images[currentSlide].description || 'No description available.' }}
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
        <VBtn
          color="secondary"
          variant="outlined"
          @click="$emit('close')"
        >
          Close
        </VBtn>
      </VCardActions>
    </VCard>
  </VDialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Image {
  id: string
  url: string
  title?: string
  description?: string
  tags?: string[]
}

interface Props {
  isVisible: boolean
  categoryName: string
  images: Image[]
}

const props = defineProps<Props>()
const emit = defineEmits(['close'])

const currentSlide = ref(0)

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