<script setup lang="ts">
import { ref, reactive } from 'vue';
import { 
  ElUpload,
  ElButton,
  ElInput,
  ElForm,
  ElFormItem,
  ElMessage,
} from 'element-plus';
import type { UploadProps, UploadUserFile, UploadFile } from 'element-plus';
import type { FormInstance } from 'element-plus';

const props = defineProps<{
  categoryId: string;
}>();

// Destructure to acknowledge usage, even if only in template
const { categoryId } = props;

const emit = defineEmits<{
  (e: 'upload-success'): void;
  (e: 'upload-error', error: Error): void;
  (e: 'cancel'): void;
}>();

const formRef = ref<FormInstance>();
const fileList = ref<UploadUserFile[]>([]);
const form = reactive({
  description: ''
});

const rules = {
  description: [
    { max: 500, message: 'Description cannot exceed 500 characters', trigger: 'blur' }
  ]
};

const handleExceed: UploadProps['onExceed'] = (_files) => {
  ElMessage.warning(
    'Only one image can be uploaded at a time'
  );
};

const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isImage = file.type.startsWith('image/');
  const isLt5M = file.size / 1024 / 1024 < 5;

  if (!isImage) {
    ElMessage.error('You can only upload image files!');
  }
  
  if (!isLt5M) {
    ElMessage.error('Image size can not exceed 5MB!');
  }
  
  return isImage && isLt5M;
};

const submitForm = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      if (fileList.value.length === 0) {
        ElMessage.error('Please select an image to upload');
        return;
      }
      
      try {
        // Here we're simulating the upload - in a real app we'd call the store or API
        // Actually uploading would be handled by the store/api
        ElMessage.success('Image upload successful!');
        emit('upload-success');
        // Reset form
        fileList.value = [];
        form.description = '';
      } catch (error: any) {
        emit('upload-error', error);
      }
    }
  });
};

const cancel = () => {
  emit('cancel');
};

const handleRemove = (file: UploadFile) => {
  fileList.value = fileList.value.filter(f => f.uid !== file.uid);
};
</script>

<template>
  <ElForm
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="120px"
    class="upload-form"
  >
    <ElFormItem label="Image" required>
      <ElUpload
        class="image-uploader"
        action="#"
        :auto-upload="false"
        :limit="1"
        :file-list="fileList"
        :on-exceed="handleExceed"
        :before-upload="beforeUpload"
        :on-remove="handleRemove"
        list-type="picture-card"
      >
        <ElButton type="primary">Select Image</ElButton>
        <template #tip>
          <div class="el-upload__tip">
            JPG/PNG files with a size less than 5MB
          </div>
        </template>
      </ElUpload>
    </ElFormItem>
    
    <ElFormItem label="Description" prop="description">
      <ElInput
        v-model="form.description"
        type="textarea"
        :rows="4"
        placeholder="Enter image description"
      />
    </ElFormItem>
    
    <input type="hidden" :value="categoryId" name="category_id" />
    
    <ElFormItem>
      <ElButton type="primary" @click="submitForm">Upload</ElButton>
      <ElButton @click="cancel">Cancel</ElButton>
    </ElFormItem>
  </ElForm>
</template>

<style scoped>
.upload-form {
  max-width: 600px;
  margin: 0 auto;
}

.image-uploader {
  width: 100%;
}
</style>