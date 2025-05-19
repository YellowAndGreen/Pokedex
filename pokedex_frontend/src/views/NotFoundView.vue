<template>
  <div class="not-found-view">
    <el-result 
      icon="error"
      title="404 - 页面未找到"
      sub-title="抱歉，您访问的页面不存在或已被移除。"
    >
      <template #extra>
        <el-button type="primary" @click="goHome">返回首页</el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
const router = useRouter();
const goHome = () => router.push('/');
</script>

<style scoped>
.not-found-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}
</style>
