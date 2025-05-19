<template>
      <el-dialog :model-value="visible" :title="formMode === 'create' ? '创建新类别' : '编辑类别'" width="500px" @close="handleClose" :close-on-click-modal="false">
        <el-form ref="categoryFormRef" :model="formState" :rules="rules" label-width="80px">
          <el-form-item label="类别名称" prop="name"><el-input v-model="formState.name" placeholder="请输入类别名称" /></el-form-item>
          <el-form-item label="类别描述" prop="description"><el-input v-model="formState.description" type="textarea" placeholder="请输入类别描述（可选）" /></el-form-item>
        </el-form>
        <template #footer><span class="dialog-footer"><el-button @click="handleClose">取消</el-button><el-button type="primary" @click="handleSubmit" :loading="isSubmitting">{{ isSubmitting ? '处理中...' : '确认' }}</el-button></span></template>
      </el-dialog>
    </template>
    <script setup lang="ts">
    import { ref, reactive, watch, toRefs } from 'vue';
    import type { FormInstance, FormRules } from 'element-plus';
    import { ElMessage } from 'element-plus';
    import { useCategoryStore } from '../store/categoryStore'; 
    import type { CategoryCreate, CategoryRead, CategoryUpdate } from '../types';
    interface Props { visible: boolean; mode?: 'create' | 'edit'; initialData?: CategoryRead | null; }
    const props = withDefaults(defineProps<Props>(), { mode: 'create', initialData: null });
    const emit = defineEmits(['update:visible', 'submit-success']);
    const categoryFormRef = ref<FormInstance>(); const isSubmitting = ref(false);
    const categoryStore = useCategoryStore(); 
    interface FormState { name: string; description: string; }
    const formState = reactive<FormState>({ name: '', description: '' });
    const rules = reactive<FormRules<FormState>>({ name: [{ required: true, message: '类别名称不能为空', trigger: 'blur' }, { min: 2, max: 50, message: '名称长度应为 2 到 50 个字符', trigger: 'blur' }], description: [{ max: 200, message: '描述不能超过200个字符', trigger: 'blur' }]});
    const formMode = toRefs(props).mode;
    
    watch(() => props.visible, (newVal) => { 
      if (newVal) { 
        categoryFormRef.value?.resetFields(); 
        if (props.mode === 'edit' && props.initialData) { 
          formState.name = props.initialData.name; 
          formState.description = props.initialData.description || ''; 
        } else { 
          formState.name = ''; 
          formState.description = ''; 
        } 
      } 
    });

    const handleClose = () => { if (isSubmitting.value) return; emit('update:visible', false); };
    const handleSubmit = async () => {
      if (!categoryFormRef.value) return;
      await categoryFormRef.value.validate(async (valid) => {
        if (valid) {
          isSubmitting.value = true;
          try {
            const payload: CategoryCreate = { name: formState.name, description: formState.description || null };
            if (props.mode === 'create') {
              await categoryStore.addCategory(payload); 
              ElMessage.success('新类别创建成功！');
            } else if (props.mode === 'edit' && props.initialData) {
              // 编辑逻辑，调用 categoryStore.updateCategory(props.initialData.id, payload)
              ElMessage.warning('编辑功能暂未实现'); 
            }
            emit('submit-success'); 
            handleClose();
          } catch (error: any) { ElMessage.error(`操作失败: ${error.response?.data?.detail || error.message || '未知错误'}`);
          } finally { isSubmitting.value = false; }
        } else { 
          ElMessage.error('请检查表单填写是否正确！');
        }
      });
    };
    </script> 