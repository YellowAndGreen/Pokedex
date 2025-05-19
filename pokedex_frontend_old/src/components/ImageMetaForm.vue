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
  (e: 'submit', data: ImageUpdate, imageId: string): void;
  (e: 'cancel'): void;
}>();

const categoryStore = useCategoryStore();
const formRef = ref<FormInstance>();

const form = reactive<ImageUpdate & { id: string }>({
  id: props.initialData.id,
  title: props.initialData.title,
  description: props.initialData.description,
  categoryId: props.initialData.categoryId
});

const rules = {
  description: [
    { max: 500, message: 'Description cannot exceed 500 characters', trigger: 'blur' }
  ],
  title: [
    { max: 100, message: 'Title cannot exceed 100 characters', trigger: 'blur' }
  ]
};

onMounted(async () => {
  if (!categoryStore.categories.length) {
    await categoryStore.fetchCategories();
  }
});

const submitForm = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      const updateData: ImageUpdate = {
        title: form.title,
        description: form.description,
        categoryId: form.categoryId
      };
      emit('submit', updateData, form.id);
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
    <ElFormItem label="Title" prop="title">
      <ElInput v-model="form.title" placeholder="Enter image title" />
    </ElFormItem>

    <ElFormItem label="Category" prop="categoryId">
      <ElSelect 
        v-model="form.categoryId" 
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