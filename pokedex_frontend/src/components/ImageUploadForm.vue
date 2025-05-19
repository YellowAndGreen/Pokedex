<template>
      <el-dialog :model-value="visible" title="上传新图片" width="500px" @close="handleClose" :close-on-click-modal="false">
        <el-form ref="uploadFormRef" :model="formState" :rules="rules" label-width="100px">
          <el-form-item label="目标类别"><el-input :model-value="targetCategoryName" disabled /></el-form-item>
          <el-form-item label="选择图片" prop="fileList">
            <el-upload ref="uploadRef" v-model:file-list="formState.fileList" action="#" list-type="picture-card" :limit="1" :auto-upload="false" :on-exceed="handleExceed" :on-change="handleFileChange" :on-remove="handleFileRemove">
              <el-icon><Plus /></el-icon>
              <template #tip><div class="el-upload__tip">只能上传一张图片，格式为 jpg/png/gif/webp，大小不超过 5MB。</div></template>
            </el-upload>
          </el-form-item>
          <el-form-item label="图片描述" prop="description"><el-input v-model="formState.description" type="textarea" placeholder="请输入图片描述（可选）" /></el-form-item>
        </el-form>
        <template #footer><span class="dialog-footer"><el-button @click="handleClose">取消</el-button><el-button type="primary" @click="handleSubmit" :loading="isSubmitting">{{ isSubmitting ? '上传中...' : '确认上传' }}</el-button></span></template>
      </el-dialog>
    </template>
    <script setup lang="ts">
    import { ref, reactive, watch, computed } from 'vue';
    import type { UploadInstance, UploadProps, UploadUserFile, FormInstance, FormRules } from 'element-plus';
    import { ElMessage } from 'element-plus'; import { Plus } from '@element-plus/icons-vue';
    import apiService from '../services/apiService'; import type { ImageRead } from '../types';
    interface Props { visible: boolean; categoryId: number | string; categoryName: string; }
    const props = defineProps<Props>(); const emit = defineEmits(['update:visible', 'upload-success']);
    const uploadFormRef = ref<FormInstance>(); const uploadRef = ref<UploadInstance>(); const isSubmitting = ref(false);
    interface FormState { fileList: UploadUserFile[]; description: string; }
    const formState = reactive<FormState>({ fileList: [], description: '', });
    const rules = reactive<FormRules<FormState>>({ fileList: [{ required: true, message: '请选择要上传的图片文件', trigger: 'change', validator: (rule, value) => value.length > 0 }]});
    const handleClose = () => { if (isSubmitting.value) return; uploadFormRef.value?.resetFields(); formState.fileList = []; uploadRef.value?.clearFiles(); emit('update:visible', false); };
    const handleExceed: UploadProps['onExceed'] = (files) => { 
      uploadRef.value!.clearFiles(); 
      const file = files[0] as UploadUserFile; 
      // @ts-ignore Linter complains about type mismatch, but this is how Element Plus internally handles it and it works.
      // We need to pass the raw file to handleStart.
      if (file.raw) uploadRef.value!.handleStart(file.raw); 
    };
    const handleFileChange: UploadProps['onChange'] = (uploadFile, uploadFiles) => {
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']; const maxSize = 5 * 1024 * 1024;
      if (uploadFile.raw) {
        if (!allowedTypes.includes(uploadFile.raw.type)) { ElMessage.error('图片格式不支持！'); formState.fileList = uploadFiles.filter(f => f.uid !== uploadFile.uid); return false; }
        if (uploadFile.raw.size > maxSize) { ElMessage.error('图片大小不能超过 5MB！'); formState.fileList = uploadFiles.filter(f => f.uid !== uploadFile.uid); return false; }
      }
      formState.fileList = uploadFiles.length > 1 ? [uploadFiles[uploadFiles.length - 1]] : [...uploadFiles];
    };
    const handleFileRemove: UploadProps['onRemove'] = () => { formState.fileList = []; };
    const handleSubmit = async () => {
      if (!uploadFormRef.value) return;
      await uploadFormRef.value.validate(async (valid) => {
        if (valid) {
          if (formState.fileList.length === 0 || !formState.fileList[0].raw) { ElMessage.error('请选择图片文件！'); return; }
          isSubmitting.value = true; const formData = new FormData(); formData.append('file', formState.fileList[0].raw); formData.append('category_id', String(props.categoryId));
          if (formState.description) formData.append('description', formState.description);
          try {
            const newImage: ImageRead = await apiService.uploadImageFile(formData); ElMessage.success('图片上传成功！'); emit('upload-success', newImage); handleClose();
          } catch (error: any) { console.error('图片上传失败:', error); ElMessage.error(`图片上传失败: ${error.response?.data?.detail || error.message || '未知错误'}`);
          } finally { isSubmitting.value = false; }
        } else { 
          ElMessage.error('请检查表单填写是否正确！'); 
          // The validate method itself will reject the promise on validation failure.
          // So, we don't need to explicitly return false here.
        }
      });
    };
    watch(() => props.visible, (newVal) => { if (!newVal) { uploadFormRef.value?.resetFields(); formState.fileList = []; uploadRef.value?.clearFiles(); }});
    const targetCategoryName = computed(() => props.categoryName);
    </script>
    <style scoped>
    /* 样式应与原有UI风格一致或基于Element Plus统一设计 */
    .el-upload__tip { font-size: 12px; color: #909399; margin-top: 5px; }
    :deep(.el-upload--picture-card) { display: inline-flex; } /* 修正el-upload在picture-card模式下的布局问题 */
    :deep(.el-upload-list--picture-card .el-upload-list__item) { margin: 0 8px 8px 0; }
    </style> 