<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElForm, ElFormItem, ElInput, ElButton } from 'element-plus';
import type { CategoryCreate, CategoryRead } from '../types';

const props = defineProps<{
  initialData?: CategoryRead;
  isEditMode?: boolean;
}>();

const emit = defineEmits<{
  (e: 'submit', data: CategoryCreate): void;
  (e: 'cancel'): void;
}>();

const form = ref<CategoryCreate>({
  name: '',
  description: ''
});

const formRef = ref();
const rules = {
  name: [
    { required: true, message: 'Category name is required', trigger: 'blur' },
    { min: 2, max: 50, message: 'Length should be 2 to 50 characters', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: 'Description cannot exceed 500 characters', trigger: 'blur' }
  ]
};

onMounted(() => {
  if (props.initialData) {
    form.value.name = props.initialData.name;
    form.value.description = props.initialData.description;
  }
});

const submitForm = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      emit('submit', form.value);
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
    class="category-form"
  >
    <ElFormItem label="Name" prop="name">
      <ElInput v-model="form.name" placeholder="Enter bird species name" />
    </ElFormItem>
    
    <ElFormItem label="Description" prop="description">
      <ElInput
        v-model="form.description"
        type="textarea"
        :rows="4"
        placeholder="Enter description for this bird species"
      />
    </ElFormItem>
    
    <ElFormItem>
      <ElButton type="primary" @click="submitForm">
        {{ isEditMode ? 'Update' : 'Create' }}
      </ElButton>
      <ElButton @click="cancel">Cancel</ElButton>
    </ElFormItem>
  </ElForm>
</template>

<style scoped>
.category-form {
  max-width: 600px;
  margin: 0 auto;
}
</style>