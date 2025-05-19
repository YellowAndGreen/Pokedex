import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';

const routes: Array<RouteRecordRaw> = [
  { path: '/', name: 'Home', component: () => import('../views/CategoryListView.vue'), meta: { title: '首页 - 类别列表' } },
  { path: '/categories', name: 'CategoryList', component: () => import('../views/CategoryListView.vue'), meta: { title: '类别列表' } },
  { path: '/category/:id', name: 'CategoryDetail', component: () => import('../views/CategoryDetailView.vue'), props: true, meta: { title: '类别详情' } },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('../views/NotFoundView.vue'), meta: { title: '页面未找到' } }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - Pokedex` : 'Pokedex';
  next();
});

export default router;
