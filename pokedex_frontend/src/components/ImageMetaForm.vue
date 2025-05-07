<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { 
  ElForm, 
  ElFormItem, 
  ElInput, 
  ElButton, 
  ElSelect,
  ElOption 
} from 'element-plus';
import type { FormInstance } from 'element-plus';
import type { ImageRead, ImageUpdate, CategoryRead } from '../types';
import { useCategoryStore } from '../store/categoryStore';

const props = defineProps<{
  initialData: ImageRead;
  categories?: CategoryRead[];
}>();

const emit = defineEmits<{
  (e: 'submit', data: ImageUpdate & { id: number }): void;
  (e: 'cancel'): void;
}>();

const categoryStore = useCategoryStore();
const formRef = ref<FormInstance>();

const form = reactive<ImageUpdate & { id: number }>({
  id: props.initialData.id,
  description: props.initialData.description,
  tags: props.initialData.tags,
  category_id: props.initialData.category_id
});

const tagsString = ref(props.initialData.tags.join(', '));

const rules = {
  description: [
    { max: 500, message: 'Description cannot exceed 500 characters', trigger: 'blur' }
  ]
};

onMounted(async () => {
  if (!categoryStore.categories.length) {
    await categoryStore.fetchCategories();
  }
});

const submitForm = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate((valid) => {
    if (valid) {
      // Convert tags string to array
      form.tags = tagsString.value.split(',').map(tag => tag.trim()).filter(tag => tag);
      emit('submit', { ...form });
    }
  });
};

const cancel = () => {
  emit('cancel');
};
</script>

<template>
  <ElForm
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="120px"
    class="meta-form"
  >
    <ElFormItem label="Category" prop="category_id">
      <ElSelect 
        v-model="form.category_id" 
        placeholder="Select category"
        class="full-width"
      >
        <ElOption
          v-for="category in categoryStore.categories"
          :key="category.id"
          :label="category.name"
          :value="category.id"
        />
      </ElSelect>
    </ElFormItem>
    
    <ElFormItem label="Description" prop="description">
      <ElInput
        v-model="form.description"
        type="textarea"
        :rows="4"
        placeholder="Enter image description"
      />
    </ElFormItem>
    
    <ElFormItem label="Tags">
      <ElInput
        v-model="tagsString"
        placeholder="Enter tags separated by commas"
      />
      <div class="tags-help">Example: nature, wildlife, forest</div>
    </ElFormItem>
    
    <ElFormItem>
      <ElButton type="primary" @click="submitForm">Update</ElButton>
      <ElButton @click="cancel">Cancel</ElButton>
    </ElFormItem>
  </ElForm>
</template>

<style scoped>
.meta-form {
  max-width: 600px;
  margin: 0 auto;
}

.full-width {
  width: 100%;
}

.tags-help {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>