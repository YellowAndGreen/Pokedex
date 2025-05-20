# Vite 项目代码规范

## 1. 引言

本规范旨在为 Vite 项目提供一套统一的编码标准与最佳实践，以提升代码质量、可读性、可维护性，并促进团队高效协作。

## 2. 通用原则

* **一致性**: 项目全局遵循统一的编码风格。
* **可读性**: 代码力求清晰易懂，通过合理的命名、注释和组织实现。
* **简洁性**: 避免不必要的复杂化，追求代码的简单直接。
* **可维护性**: 代码应易于修改与扩展，重视模块化与关注点分离。
* **工具驱动**: 积极运用 ESLint, Prettier, Stylelint 等工具保障代码规范的自动化执行。

## 3. 目录结构 (推荐)

清晰的目录结构是高效协作的基础。推荐结构如下，可根据项目需求调整：

project-root/├── public/                  # 静态资源 (Vite 不处理)│   └── favicon.ico├── src/│   ├── assets/              # 项目资源 (Vite 处理，如图片、字体)│   │   ├── fonts/│   │   └── images/│   ├── components/          # 可复用 UI 组件│   │   ├── common/          # 通用基础组件 (Button, Input, Modal 等)│   │   └── layout/          # 布局组件 (Header, Footer, Sidebar 等)│   │   └── MyComponent/│   │       ├── index.ts     # 组件导出 (可选)│   │       ├── MyComponent.vue│   │       └── MyComponent.spec.ts # 单元测试│   ├── views/               # 页面级组件 (路由视图)│   │   ├── HomeView.vue│   │   └── AboutView.vue│   ├── router/              # 路由配置│   │   └── index.ts│   ├── store/               # 状态管理 (Pinia / Vuex)│   │   ├── index.ts│   │   └── modules/│   │       └── user.ts│   ├── services/            # API 服务封装│   │   ├── index.ts│   │   └── userService.ts│   ├── utils/               # 工具函数模块│   │   ├── request.ts       # 封装的请求函数│   │   └── validators.ts│   ├── styles/              # 全局样式与变量│   │   ├── main.scss        # 全局主样式│   │   ├── _variables.scss  # SCSS 变量 (通常作为 partial 导入)│   │   └── _mixins.scss     # SCSS Mixins (通常作为 partial 导入)│   ├── App.vue              # 应用根组件│   ├── main.ts              # 应用入口│   └── env.d.ts             # TypeScript 环境变量声明├── .editorconfig            # 编辑器配置├── .eslintrc.cjs            # ESLint 配置├── .eslintignore            # ESLint 忽略规则├── .prettierrc.json         # Prettier 配置├── .prettierignore          # Prettier 忽略规则├── index.html               # HTML 入口文件├── package.json├── tsconfig.json            # TypeScript 项目配置├── tsconfig.node.json       # TypeScript Node 环境配置└── vite.config.ts           # Vite 配置文件
## 4. 命名规范

统一的命名规范是代码可读性的基石。

### 4.1. 文件与目录

* **目录名**: 小写字母，单词间以短横线 `-` 连接 (kebab-case)。例: `user-profile`, `api-services`。
* **组件文件名 (.vue)**: 大驼峰命名法 (PascalCase)。例: `UserProfile.vue`, `BaseButton.vue`。
* **JS/TS 文件名 (.js, .ts)**:
    * 通用模块/工具: 小驼峰命名法 (camelCase)。例: `utils.ts`, `apiClient.js`。
    * 类/构造函数: 大驼峰命名法 (PascalCase)。例: `UserService.ts`。
* **样式文件名 (.css, .scss, .less)**: 小写字母，单词间以短横线 `-` 连接 (kebab-case)。例: `variables.scss`, `main-layout.css`。

### 4.2. 变量

* **常量**: 全大写，单词间下划线 `_` 分隔 (SNAKE_CASE)。例: `const MAX_USERS = 100;`。
* **普通变量/函数参数**: 小驼峰命名法 (camelCase)。例: `let userName = 'Alice';`。
* **布尔类型**: 通常以 `is`, `has`, `should`, `can` 开头。例: `const isActive = true;`。

### 4.3. 函数

* 采用小驼峰命名法 (camelCase)，名称应为动词或动词短语，清晰表达其作用。例: `getUserData()`, `calculateTotalPrice()`。

### 4.4. CSS 类名

* 推荐 BEM 规范 (`.block__element--modifier`) 或纯小写加短横线 (kebab-case) 以提升可维护性与避免冲突。例: `.card__title--highlighted`, `.user-profile-avatar`。
* 优先使用类选择器，避免使用 ID 选择器定义样式。

### 4.5. Vue 组件

* **组件名 (模板中使用)**: 推荐 kebab-case (`<my-component>`)，亦可 PascalCase (`<MyComponent>`)。
* **Props 定义**: camelCase。例: `props: { userId: String }`。
* **Props 使用 (模板中)**: kebab-case。例: `<user-profile user-id="123"></user-profile>`。
* **Events 触发与监听**: kebab-case。触发: `this.$emit('update-value', newValue);` 监听: `<my-input @update-value="handleUpdate"></my-input>`。

## 5. 代码风格与格式化

借助工具自动化保障代码风格一致性。

* **Prettier (强制)**: 统一代码格式。配置 `.prettierrc.json`，示例：
    ```json
    {
      "semi": true,
      "singleQuote": true,
      "trailingComma": "es5",
      "printWidth": 100,
      "tabWidth": 2,
      "arrowParens": "always"
    }
    ```
* **ESLint (强制)**: 代码质量检查与风格约束。推荐基于 `@vitejs/plugin-vue` 的配置，并按需扩展。配置 `.eslintrc.cjs`。
* **EditorConfig**: 跨编辑器/IDE 维护基础编码风格。配置 `.editorconfig`，示例：
    ```ini
    root = true

    [*]
    indent_style = space
    indent_size = 2
    end_of_line = lf
    charset = utf-8
    trim_trailing_whitespace = true
    insert_final_newline = true

    [*.md]
    trim_trailing_whitespace = false
    ```

## 6. Vue 组件最佳实践

### 6.1. 组件结构顺序

`<script setup>` 内部推荐顺序：

1.  `import` 语句
2.  `defineProps`, `defineEmits`, `defineExpose`
3.  响应式状态 (`ref`, `reactive`, `computed`)
4.  生命周期钩子 (按执行顺序排列)
5.  `watch`, `watchEffect`
6.  方法 (事件处理器、业务逻辑函数等)

Options API 组件内部推荐顺序：

1.  `name`, `components`, `directives`, `filters`
2.  `extends`, `mixins`
3.  `props`, `emits`
4.  `data`, `computed`
5.  `watch`
6.  生命周期钩子 (按执行顺序排列)
7.  `methods`

### 6.2. Props

* **类型明确**: 始终为 Props 定义类型，并尽可能详细 (如 `String`, `Number`, `Object`, `Array`, `Boolean`, `Function`, `Symbol` 或自定义构造函数)。
* **必需性**: 对必需 Props 设置 `required: true`。
* **默认值**: 为可选 Props 提供合理的 `default` 值，对象或数组的默认值应通过工厂函数返回。
* **校验器**: 对复杂 Props 使用 `validator` 函数进行校验。

### 6.3. Events

* 显式声明：使用 `defineEmits` (Composition API) 或 `emits` 选项 (Options API) 清晰声明组件所触发的事件。
* 命名：事件名统一使用 kebab-case。

### 6.4. `v-for` 指令

* **必须提供 `key`**: `key` 值需唯一且稳定，以优化渲染性能。
* 避免与 `v-if` 同用：不在同一元素上同时使用 `v-if` 和 `v-for`。若需条件渲染列表，可将 `v-if` 置于外层容器，或通过计算属性预先过滤数据源。

### 6.5. 单文件组件 (SFC)

* **保持简洁**: 过长的 `<script>` 或 `<style>` 部分考虑拆分为独立文件导入。
* **样式作用域**: 默认使用 `<style scoped>` 防止样式污染。全局样式统一在 `src/styles` 目录管理。

## 7. TypeScript 高效实践 (若使用)

* **类型优先**: 积极利用 TypeScript 类型系统，为变量、函数参数及返回值添加明确类型。
* **接口 (Interface) 与类型别名 (Type Alias)**: 使用接口定义对象/类的结构，类型别名用于组合类型、联合类型或工具类型。
* **避免 `any`**: `any` 会削弱类型检查优势。优先使用 `unknown` 并配合类型守卫，或定义更具体的类型。
* **善用泛型**: 提升代码复用性与类型安全性。
* **路径别名**: 在 `tsconfig.json` 和 `vite.config.ts` 中配置路径别名 (如 `@/*` 指向 `src/*`)，简化模块导入。

## 8. API 请求管理

* **服务层封装**: 将 API 请求逻辑集中于 `src/services` (或 `src/api`) 目录，按业务模块组织。例: `userService.ts`。
* **统一请求处理**: 创建统一的请求实例 (如 `axios` 实例)，集中处理基础 URL、请求头、拦截器 (请求/响应)、错误上报、Loading 状态等。
* **环境变量**: API 端点、密钥等敏感或环境相关配置通过 `.env` 文件管理 (Vite 中以 `VITE_` 为前缀)。

## 9. 状态管理 (Pinia / Vuex)

* **模块化设计**: 按功能领域划分状态模块，保持各模块职责单一。
* **职责分离**: Actions 处理异步操作与复杂业务逻辑；Mutations (Vuex) 或直接修改 State (Pinia) 应为纯粹的同步状态变更。
* **Getters/Computed 派生状态**: 封装可复用的派生状态逻辑，避免在组件中进行过多计算。
* **命名一致**: State, Getters, Actions/Mutations 命名需清晰、表意且遵循统一模式。

## 10. 注释规范

* **必要性注释**: 为复杂算法、业务逻辑、重要决策、潜在风险或临时方案编写清晰注释。
* **JSDoc 标准**: 对公共函数、模块、组件 Props 等使用 JSDoc 风格注释，便于生成文档和增强 IDE 提示。
    ```typescript
    /**
     * Retrieves user profile information.
     * @param userId - The unique identifier of the user.
     * @returns A promise resolving to the user profile object, or null if not found.
     */
    async function fetchUserProfile(userId: string): Promise<UserProfile | null> {
      // Implementation details...
    }
    ```
* **避免冗余**: 不为显而易见的代码添加注释。
* **及时更新**: 代码变更时，务必同步更新相关注释。
* **标记注释**: 使用 `// TODO:` 标记待办事项，`// FIXME:` 标记待修复问题，并附简要说明。

## 11. Git 版本控制规范

### 11.1. 分支策略 (推荐 Gitflow 或简化版)

* `main` (或 `master`): 稳定的生产分支，代码随时可发布。
* `develop`: 主要开发分支，集成各功能。
* `feature/<feature-name>`: 新功能开发分支，从 `develop` 切出，完成后合并回 `develop`。
* `fix/<issue-id>` 或 `hotfix/<version>`: Bug 修复分支。常规 Bug 从 `develop` 切出；紧急线上 Bug (hotfix) 从 `main` 切出，修复后同时合并到 `main` 和 `develop`。
* `release/<version>`: 发布准备分支，从 `develop` 切出，用于版本发布前的最后测试和调整。

### 11.2. 提交信息 (Commit Message)

* **遵循 Conventional Commits 规范**: (参考 <https://www.conventionalcommits.org/>) 格式为 `<type>(<scope>): <subject>`。
    * `type`: 如 `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore` 等。
    * `scope` (可选): 影响范围 (如组件名、模块名)。
    * `subject`: 简洁描述，动词开头，首字母小写。
    * 示例: `feat(auth): implement user login via email`
* **工具辅助**: 可选用 `commitizen` 等工具规范提交信息。

### 11.3. 代码审查 (Code Review)

* **强制执行**: 所有向 `develop` 或 `main` 分支的合并请求 (Merge/Pull Request) 必须经过至少一名团队成员审查。
* **审查重点**: 功能实现、代码风格、可读性、性能、安全性、测试覆盖、潜在缺陷等。

## 12. 测试策略

* **单元测试**: 针对组件、工具函数、状态管理模块等独立单元编写测试。
    * 工具: Vitest, Jest。
    * 目标: 覆盖核心逻辑、边界条件和异常处理。
* **端到端测试 (E2E)**: 模拟用户真实操作场景，验证完整业务流程。
    * 工具: Cypress, Playwright。
* **测试覆盖率**: 设定合理的覆盖率目标，并持续追踪和提升。

## 13. 构建与部署

* **环境区分**: 使用 `.env.[mode]` (如 `.env.development`, `.env.production`) 管理不同环境的配置。
* **构建优化**: 利用 Vite 内置的生产构建优化 (代码压缩、Tree Shaking 等)。按需审查和调整 `vite.config.ts` 中的 `build` 配置。
* **代码分割 (Chunk Splitting)**: 理解并按需优化 Vite 的代码分割策略，以提升应用加载性能。

## 14. 持续集成/持续部署 (CI/CD)

* **自动化流程**: 推荐采用 GitHub Actions, GitLab CI/CD, Jenkins 等工具，建立自动化测试、构建和部署流水线。

## 15. 规范的持续演进

本规范是一个起点。团队应结合项目实践和技术发展，定期回顾、讨论并迭代本规范，确保其持续适用与有效。通过代码审查和技术分享促进规范的理解与执行。
