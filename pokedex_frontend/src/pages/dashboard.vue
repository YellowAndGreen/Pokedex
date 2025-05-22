<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getCategories, API_BASE_URL } from '@/services/apiService' // getImages is no longer needed here
import type { CategoryRead } from '@/types' // ImageRead is no longer needed here

// CategoryWithDisplayInfo is no longer needed, CategoryRead now has all required fields.

// Define an interface for the category with its expansion state and random border color
interface ExtendedCategory extends CategoryRead {
  isExpanded: boolean;
  randomBorderColorHex: string;
  randomBorderColorRGB: string;
}

const categories = ref<ExtendedCategory[]>([]) // Use ExtendedCategory
const isLoading = ref(true)
const error = ref<string | null>(null)

// Placeholder image if no thumbnail is available
const placeholderImage = '/placeholder-image.png' // Make sure you have this image in your public folder or update the path

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

onMounted(async () => {
  try {
    isLoading.value = true
    const fetchedCategories = await getCategories(0, 50) // Fetch categories

    categories.value = fetchedCategories.map(category => {
      let displayImageUrl: string | null = null
      if (category.thumbnail_url) {
        displayImageUrl = category.thumbnail_url.startsWith('http') || category.thumbnail_url.startsWith('/')
          ? category.thumbnail_url
          : `${API_BASE_URL}${category.thumbnail_url}`
      }

      const hexColor = colorPalette[Math.floor(Math.random() * colorPalette.length)];
      const rgbColorString = hexToRgbString(hexColor);

      return {
        ...category,
        // Ensure all CategoryRead fields are present, and add processed ones if any
        // In this case, we format the date directly in the template or use a computed prop if more complex
        // and derive displayImageUrl directly.
        // The main change is that `updated_at` and `thumbnail_url` come directly from `category`.
        // We are essentially just ensuring `displayImageUrl` has a fallback and is correctly prefixed.
        thumbnail_url: displayImageUrl || placeholderImage, // Override thumbnail_url with processed one for template
        isExpanded: false, // Initialize expansion state
        randomBorderColorHex: hexColor,
        randomBorderColorRGB: rgbColorString,
      }
    })

    error.value = null
  }
  catch (e: any) {
    console.error('Failed to fetch categories:', e)
    error.value = e.message || 'An unknown error occurred while fetching categories.'
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
const handleViewMoreImages = (category: ExtendedCategory) => {
  // 这里暂时为空函数，将来可以添加查看图片的逻辑
  console.log('View more images for category:', category.name);
  // 未来可以添加打开模态框、导航到详情页等操作
};
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
              class="d-flex justify-center align-start pa-3 mb-2 rounded overflow-hidden" 
              :style="{ backgroundColor: `rgba(var(--card-border-color-rgb), 0.15)` }"
            >
              <VImg
                :src="category.thumbnail_url || placeholderImage"
                height="140px"
                width="145px"
                aspect-ratio="1"
                cover
                class="rounded-lg image-fade-in"
                transition="fade-transition"
              >
                <template #placeholder>
                  <div class="d-flex align-center justify-center" style="height: 140px; width: 145px;">
                    <VSkeletonLoader
                      type="image"
                      height="140"
                      width="145"
                      class="rounded-lg"
                      :style="{ backgroundColor: `rgba(var(--card-border-color-rgb), 0.05)` }"
                    />
                  </div>
                </template>
                <template #error>
                  <VImg :src="placeholderImage" height="140px" width="145px" cover class="rounded-lg" transition="fade-transition" />
                </template>
              </VImg>
            </div>

            <div class="px-4 pb-4">
              <h5 class="text-h5 mb-1 text-left">{{ category.name }}</h5>
              <p class="text-body-2 text-medium-emphasis mb-2 text-left">
                {{ category.description || 'No description available.' }}
              </p>

              <VExpandTransition>
                <div v-show="category.isExpanded" class="expanded-content-area">
                  <div class="d-flex justify-space-between my-4 gap-4 flex-wrap">
                    <div v-if="category.updated_at" class="d-flex align-center gap-x-2 mx-auto">
                      <VAvatar 
                        variant="tonal" 
                        rounded 
                        :style="{ color: category.randomBorderColorHex }"
                      >
                        <VIcon icon="ri-calendar-line" />
                      </VAvatar>
                      <div>
                        <div class="text-body-1 text-high-emphasis">{{ formatDateManually(category.updated_at) }}</div>
                        <div class="text-caption text-medium-emphasis">更新</div>
                      </div>
                    </div>

                    <div v-if="category.created_at" class="d-flex align-center gap-x-2 mx-auto">
                      <VAvatar 
                        variant="tonal" 
                        rounded 
                        :style="{ color: category.randomBorderColorHex }"
                      >
                        <VIcon icon="ri-time-line" />
                      </VAvatar>
                      <div>
                        <div class="text-body-1 text-high-emphasis">{{ formatDateManually(category.created_at) }}</div>
                        <div class="text-caption text-medium-emphasis">创建</div>
                      </div>
                    </div>
                  </div>
                  
                  <VBtn 
                    block 
                    class="mt-4"
                    variant="flat"
                    :color="false"
                    :style="{ 
                      backgroundColor: category.randomBorderColorHex,
                      color: 'white'
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
  </VContainer>
</template>

<style scoped>
.bg-light-primary {
  background-color: rgba(var(--v-theme-primary), 0.1) !important;
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
