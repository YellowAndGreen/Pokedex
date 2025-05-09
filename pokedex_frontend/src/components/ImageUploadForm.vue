<script setup lang="ts">
import { ref, reactive } from 'vue';
import { 
  ElUpload,
  ElButton,
  ElInput,
  ElForm,
  ElFormItem,
  ElMessage,
  ElCheckbox,
  ElIcon
} from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import type { UploadProps, UploadUserFile, UploadFile } from 'element-plus';
import type { FormInstance } from 'element-plus';
import { useCategoryStore } from '../store/categoryStore';

const props = defineProps<{
  categoryId: string;
}>();

const emit = defineEmits<{
  (e: 'upload-success'): void;
  (e: 'upload-error', error: Error): void;
  (e: 'cancel'): void;
}>();

const categoryStore = useCategoryStore();
const formRef = ref<FormInstance>();
const fileList = ref<UploadUserFile[]>([]);
const form = reactive({
  description: ''
});
const setAsThumbnail = ref(false);
const isUploading = ref(false);

const rules = {
  description: [
    { max: 500, message: 'Description cannot exceed 500 characters', trigger: 'blur' }
  ]
};

const handleExceed: UploadProps['onExceed'] = (_files) => {
  ElMessage.warning(
    'Only one image can be uploaded at a time. Please remove the existing image first if you want to change it.'
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
  
  if (isImage && isLt5M) {
    fileList.value = [file as UploadUserFile];
    return false;
  }
  return false;
};

const submitForm = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      if (fileList.value.length === 0 || !fileList.value[0].raw) {
        ElMessage.error('Please select an image to upload');
        return;
      }
      
      isUploading.value = true;
      const formData = new FormData();
      formData.append('file', fileList.value[0].raw);
      formData.append('description', form.description);
      formData.append('category_id', props.categoryId);

      try {
        await categoryStore.uploadImageAndUpdateCategoryThumbnailIfNeeded(
          formData, 
          props.categoryId, 
          setAsThumbnail.value
        );
        ElMessage.success('Image uploaded successfully!');
        emit('upload-success');
        fileList.value = [];
        form.description = '';
        setAsThumbnail.value = false;
        formRef.value?.resetFields();
      } catch (error: any) {
        console.error("Upload error in form:", error);
        ElMessage.error(error.message || 'Image upload failed.');
        emit('upload-error', error);
      } finally {
        isUploading.value = false;
      }
    }
  });
};

const cancel = () => {
  fileList.value = [];
  form.description = '';
  setAsThumbnail.value = false;
  if (formRef.value) {
    formRef.value.resetFields();
  }
  emit('cancel');
};

const handleFileChange: UploadProps['onChange'] = (uploadFile, uploadFiles) => {
  if (uploadFiles.length > 0) {
    fileList.value = [uploadFiles[uploadFiles.length - 1]];
  }
};

const handleRemove = () => {
  fileList.value = [];
};
</script>

<template>
  <ElForm
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="120px"
    class="upload-form"
    @submit.prevent="submitForm"
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
        :on-change="handleFileChange"
        :on-remove="handleRemove"
        list-type="picture-card"
      >
        <template #default>
          <el-icon><Plus /></el-icon>
        </template>
        <template #trigger>
          <ElButton type="primary">Select Image</ElButton>
        </template>
        <template #tip>
          <div class="el-upload__tip">
            JPG/PNG/GIF files with a size less than 5MB. Only 1 image at a time.
          </div>
        </template>
      </ElUpload>
    </ElFormItem>
    
    <ElFormItem label="Description" prop="description">
      <ElInput
        v-model="form.description"
        type="textarea"
        :rows="4"
        placeholder="Enter image description (optional)"
      />
    </ElFormItem>

    <ElFormItem label="Set as Thumbnail">
      <ElCheckbox v-model="setAsThumbnail" label="Set this image as category thumbnail" />
    </ElFormItem>
    
    <ElFormItem>
      <ElButton type="primary" @click="submitForm" :loading="isUploading">Upload</ElButton>
      <ElButton @click="cancel" :disabled="isUploading">Cancel</ElButton>
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

:deep(.el-upload--picture-card) {
  width: 100px;
  height: 100px;
  line-height: 110px;
}
:deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 100px;
  height: 100px;
}
</style>