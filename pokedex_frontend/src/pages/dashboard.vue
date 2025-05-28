<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getCategories, API_BASE_URL } from '@/services/apiService' // getImages is no longer needed here
import type { CategoryRead, ImageRead, ExifData } from '@/types' // Removed TagRead as it's not defined as a separate type
import { useCategoryStore } from '@/store/categoryStore'
import { useImageStore } from '@/store/imageStore' // 引入 imageStore
import placeholderImage from '@/assets/images/logo.svg'
import ImageGalleryDialog from '@/components/ImageGalleryDialog.vue' // 引入对话框组件

// CategoryWithDisplayInfo is no longer needed, CategoryRead now has all required fields.

// Define an interface for the category with its expansion state and random border color
interface ExtendedCategory extends CategoryRead {
  isExpanded: boolean;
  randomBorderColorHex: string;
  randomBorderColorRGB: string;
  // images?: ImageRead[] //  将不再直接在 category 中存储图片
}

const categoryStore = useCategoryStore()
const imageStore = useImageStore() // 初始化 imageStore

const categories = ref<ExtendedCategory[]>([]) // Use ExtendedCategory
const isLoading = ref(true)
const error = ref<string | null>(null)

// 对话框相关状态
const isGalleryDialogVisible = ref(false)
const selectedCategoryName = ref('')
const selectedCategoryImages = ref<Array<{ id: string, url: string, title?: string, description?: string, tags?: string[], exif_info?: ExifData | null }>>([])

// Color palette for random border colors - changed to deeper pastel colors
const colorPalette = [
  '#B8A2E3', // 更深的紫色 (Deeper Lavender)
  '#E8D0A9', // 更深的米黄色 (Deeper Beige)
  '#7DCE82', // 更深的淡绿色 (Deeper Pale Green)
];

// Helper function to convert hex to RGB string
function hexToRgbString(hex: string): string {
  const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
  hex = hex.replace(shorthandRegex, (m, r, g, b) => r + r + g + g + b + b);
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? `${parseInt(result[1], 16)},${parseInt(result[2], 16)},${parseInt(result[3], 16)}` : '0,0,0';
}

// Replaced formatDate with formatDateManually
const formatDateManually = (dateString?: string | null): string | null => {
  if (!dateString) return null;
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) { // Check if date is valid
      console.error('Invalid date string for formatting:', dateString);
      return dateString; // Return original if date is invalid
    }
    const day = date.getDate();
    // Ensure month is in English for consistency if locale is different, e.g., 'en-US'
    const month = date.toLocaleString('en-US', { month: 'short' }); 
    const year = date.getFullYear().toString().slice(-2);
    return `${day} ${month} ${year}`;
  }
  catch (e) {
    console.error('Error formatting date manually:', e);
    return dateString;
  }
};

const generateRandomColor = () => {
  const r = Math.floor(Math.random() * 200) 
  const g = Math.floor(Math.random() * 200)
  const b = Math.floor(Math.random() * 200)

  return {
    hex: `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`,
    rgb: `${r},${g},${b}`,
  }
}

onMounted(async () => {
  isLoading.value = true
  error.value = null
  try {
    await categoryStore.fetchCategories()
    categories.value = categoryStore.categories.map(cat => {
      const colors = generateRandomColor()

      return {
        ...cat,
        randomBorderColorHex: colors.hex,
        randomBorderColorRGB: colors.rgb,
        isExpanded: false,
      }
    })
  }
  catch (err: any) {
    console.error('Failed to load categories:', err)
    error.value = err.message || 'Failed to load categories. Please try again later.'
    categories.value = []
  }
  finally {
    isLoading.value = false
  }
})

// Function to toggle the expansion state of a category
const toggleExpansion = (category: ExtendedCategory) => {
  category.isExpanded = !category.isExpanded;
};

// 处理查看更多图片的操作
const handleViewMoreImages = async (category: ExtendedCategory) => {
  selectedCategoryName.value = category.name
  try {
    await imageStore.fetchImages(0, 50, category.id) 
    selectedCategoryImages.value = imageStore.images.map(img => {
      let parsedTags: string[] = []
      if (img.tags) {
        try {
          const tagsArray = JSON.parse(img.tags)
          if (Array.isArray(tagsArray)) {
            parsedTags = tagsArray.filter(tag => typeof tag === 'string')
          }
        }
        catch (e) {
          parsedTags = img.tags.split(',').map(tag => tag.trim()).filter(tag => tag !== '')
        }
      }

      return {
        id: img.id,
        url: img.image_url, // Ensure API provides this, removed placeholder fallback
        title: img.title || 'Untitled Image',
        description: img.description || 'No description.',
        tags: parsedTags,
        exif_info: img.exif_info,
      }
    })
    isGalleryDialogVisible.value = true
  }
  catch (err) {
    console.error('Error fetching images for category:', category.name, err)
    error.value = `Failed to load images for ${category.name}.`
    selectedCategoryImages.value = [] 
    isGalleryDialogVisible.value = true 
  }
}
</script>

<template>
  <VContainer fluid>
    <VRow v-if="isLoading">
      <VCol cols="12" class="text-center">
        <VProgressCircular indeterminate color="primary" />
        <p>Loading categories...</p>
      </VCol>
    </VRow>

    <VRow v-else-if="error">
      <VCol cols="12">
        <VAlert type="error" prominent>
          {{ error }}
        </VAlert>
      </VCol>
    </VRow>

    <VRow v-else-if="categories.length === 0">
      <VCol cols="12" class="text-center">
        <p>No categories found.</p>
      </VCol>
    </VRow>

    <VRow v-else>
      <VCol
        v-for="category in categories"
        :key="category.id"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <VCard 
          class="mx-auto category-card-bottom-border" 
          :style="{
            '--card-border-color-hex': category.randomBorderColorHex,
            '--card-border-color-rgb': category.randomBorderColorRGB
          }"
          max-width="400"
          hover
          ripple
          :elevation="2"
          style="cursor: pointer;"
          @click="toggleExpansion(category)"
        >
          <VCardText class="pa-0">
            <div 
              class="d-flex justify-center align-start pa-3 mb-2 rounded overflow-hidden image-container-transition"
              :style="[
                { backgroundColor: `rgba(var(--card-border-color-rgb), 0.15)` },
                category.isExpanded ? { 'max-height': '500px' } : {}
              ]"
            >
              <VImg
                :src="category.thumbnail_url || placeholderImage"
                :height="undefined"
                :width="category.isExpanded ? '145px' : '100%'"
                :aspect-ratio="category.isExpanded ? undefined : 1"
                :cover="!category.isExpanded"
                class="rounded-lg image-fade-in"
                transition="fade-transition"
              >
                <template #placeholder>
                  <div 
                    class="d-flex align-center justify-center"
                    :style="{ 
                      height: category.isExpanded ? '140px' : 'auto', 
                      width: category.isExpanded ? '145px' : '100%' 
                    }"
                  >
                    <VSkeletonLoader
                      type="image"
                      :height="category.isExpanded ? '140' : undefined"
                      :width="category.isExpanded ? '145' : '100%'"
                      :aspect-ratio="category.isExpanded ? undefined : 1"
                      class="rounded-lg"
                      :style="{ backgroundColor: `rgba(var(--card-border-color-rgb), 0.05)` }"
                    />
                  </div>
                </template>
                <template #error>
                  <VImg 
                    :src="placeholderImage" 
                    :height="undefined"
                    :width="category.isExpanded ? '145px' : '100%'"
                    :aspect-ratio="category.isExpanded ? undefined : 1"
                    :cover="!category.isExpanded"
                    class="rounded-lg" 
                    transition="fade-transition" 
                  />
                </template>
              </VImg>
            </div>

            <div class="px-4 pb-4">
              <div class="d-flex justify-space-between align-center mb-2">
                <h6 class="text-h6">
                  {{ category.name }}
                </h6>
                <!-- Temporarily removed image_count as it's not in CategoryRead -->
                <!-- <VChip
                  label
                  size="small"
                  class="text-xs"
                  :color="category.randomBorderColorHex"
                  variant="tonal"
                >
                  {{ category.image_count }} Images
                </VChip> -->
              </div>

              <p
                class="text-body-2 text-medium-emphasis mb-3"
                style="min-height: 40px;"
              >
                {{ category.description ? category.description.substring(0, 60) + (category.description.length > 60 ? '...' : '') : 'No description.' }}
              </p>

              <VExpandTransition>
                <div v-show="category.isExpanded">
                  <VDivider class="my-3" />
                  <p class="text-caption text-disabled">
                    <strong>ID:</strong> {{ category.id }}<br>
                    <strong>Created:</strong> {{ new Date(category.created_at).toLocaleDateString() }}<br>
                    <strong>Updated:</strong> {{ new Date(category.updated_at).toLocaleDateString() }}
                  </p>
                  <VBtn
                    block
                    class="mt-4"
                    variant="flat"
                    :style="{
                      backgroundColor: category.randomBorderColorHex,
                      color: 'white',
                    }"
                    @click.stop="handleViewMoreImages(category)"
                  >
                    More Images
                  </VBtn>
                </div>
              </VExpandTransition>
            </div>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>

    <!-- Image Gallery Dialog -->
    <ImageGalleryDialog
      :is-visible="isGalleryDialogVisible"
      :category-name="selectedCategoryName"
      :images="selectedCategoryImages"
      @close="isGalleryDialogVisible = false"
    />
  </VContainer>
</template>

<style scoped>
.bg-light-primary {
  background-color: rgba(var(--v-theme-primary), 0.1) !important;
}

.image-container-transition {
  transition: max-height 0.5s ease-in-out;
  overflow: hidden; /* 确保在折叠动画过程中内容不会溢出 */
}

@keyframes bottomBorderGlow {
  0% {
    border-bottom-color: rgba(var(--card-border-color-rgb), 0.4);
  }
  50% {
    border-bottom-color: rgba(var(--card-border-color-rgb), 1);
  }
  100% {
    border-bottom-color: rgba(var(--card-border-color-rgb), 0.4);
  }
}

.category-card-bottom-border {
  border-bottom-width: 3px;
  border-bottom-style: solid;
  /* Default border color using the random color with 70% opacity */
  border-bottom-color: rgba(var(--card-border-color-rgb), 0.7);
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.category-card-bottom-border:hover {
  animation: bottomBorderGlow 1.5s infinite;
}

.category-card-bottom-border:active {
  transform: scale(0.98);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
}

.expanded-content-area {
  /* This class is present in the template from previous steps for VExpandTransition */
  /* Adding some basic styling for the expanded area if it's still desired, but not the random background. */
  padding: 12px 0px; /* Adjust padding as needed, removed horizontal padding from here */
  margin-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.12); /* 添加灰色顶部边框 */
  padding-top: 16px; /* 增加顶部内边距，让边框与内容有更好的分隔 */
}

/* 自定义过渡效果 */
.fade-transition-enter-active {
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.fade-transition-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.fade-transition-enter-to {
  opacity: 1;
  transform: scale(1);
}

/* 让骨架屏有一个呼吸闪烁效果 */
@keyframes skeletonPulse {
  0% {
    opacity: 0.5;
  }
  50% {
    opacity: 0.8;
  }
  100% {
    opacity: 0.5;
  }
}

.v-skeleton-loader {
  animation: skeletonPulse 1.5s infinite ease-in-out;
}
</style>
