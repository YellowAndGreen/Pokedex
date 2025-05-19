import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import CategoryListView from '../views/CategoryListView.vue';
import CategoryDetailView from '../views/CategoryDetailView.vue';
import NotFoundView from '../views/NotFoundView.vue';

const routes: Array<RouteRecordRaw> = [
  { 
    path: '/',
    name: 'Home',
    component: CategoryListView,
    meta: { title: '首页 - 类别列表' }
  },
  {
    path: '/categories',
    name: 'CategoryList',
    component: CategoryListView,
    meta: { title: '类别列表' }
  },
  {
    path: '/category/:id',
    name: 'CategoryDetail',
    component: CategoryDetailView,
    props: true,
    meta: { title: '类别详情' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundView,
    meta: { title: '页面未找到' }
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

router.beforeEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} - Pokedex` : 'Pokedex';
});

export default router;
