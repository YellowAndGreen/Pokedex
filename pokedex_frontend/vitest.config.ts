/// <reference types="vitest" />
import { defineConfig, mergeConfig } from 'vitest/config';
import viteConfig from './vite.config'; // 导入您的主 Vite 应用程序配置

export default mergeConfig(
  viteConfig, // 首先应用 vite.config.ts 中的配置 (包括 resolve.alias)
  defineConfig({
    test: {
      // 将 Vitest API 设置为全局可用，无需在每个文件中导入
      // (例如 describe, it, expect, vi)
      globals: true,

      // 模拟 DOM 环境。
      // 'happy-dom' 通常比 'jsdom' 更快，但兼容性可能略差。
      // 根据您的需求选择 'jsdom' 或 'happy-dom'。
      environment: 'happy-dom',

      // (可选) 指定一个或多个在所有测试文件运行前执行的设置文件
      // 例如，用于全局 mock、设置 Pinia 实例等。
      // setupFiles: ['./tests/setup/setup.ts'],

      // (可选) 配置测试覆盖率报告
      coverage: {
        // 选择覆盖率提供程序 ('v8' 或 'istanbul')
        // 'v8' 通常更快，但可能不如 'istanbul' 精确。
        provider: 'v8', // 或者 'istanbul'

        // 配置报告输出的格式
        reporter: ['text', 'json', 'html', 'lcov'],

        // 指定覆盖率报告的输出目录
        reportsDirectory: './tests/coverage',

        // (可选) 指定要包含在覆盖率报告中的文件
        // include: ['src/**/*.{ts,vue}'],

        // (可选) 指定要从覆盖率报告中排除的文件
        // exclude: [
        //   'src/main.ts',
        //   'src/router/index.ts',
        //   'src/App.vue',
        //   'src/vite-env.d.ts',
        //   'src/types/index.ts', // 通常类型定义文件不需要覆盖率
        //   'src/**/index.ts',    // 如果有导出模块的 index 文件
        //   'src/**/*.spec.ts',   // 测试文件本身
        //   'src/**/*.test.ts',
        // ],

        // (可选) 设置覆盖率阈值，如果未达到则测试失败
        // thresholds: {
        //   lines: 80,
        //   functions: 80,
        //   branches: 80,
        //   statements: 80,
        // },
      },

      // (可选) 如果您的测试文件不在默认位置 (例如 `*.{test,spec}.{js,ts,jsx,tsx}`)
      // 或者您想更精确地控制包含哪些文件：
      // include: ['tests/unit/**/*.spec.ts'],

      // (可选) 排除某些文件或目录
      // exclude: [
      //   'node_modules/**',
      //   'dist/**',
      //   '.idea/**',
      //   '.git/**',
      //   'tests/e2e/**', // 如果有端到端测试，可能想分开运行
      // ],

      // (可选) 如果您在 Vue 组件测试中遇到序列化问题
      // vueWrapper.html() 可能包含 Vitest 不期望的注释
      // snapshotSerializers: ['jest-serializer-vue'], // 需要安装 jest-serializer-vue
    },
  })
);
