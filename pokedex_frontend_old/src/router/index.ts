import { createRouter, createWebHistory } from 'vue-router';
import CategoryListView from '../views/CategoryListView.vue';
import CategoryImagesView from '../views/CategoryImagesView.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: CategoryListView
    },
    {
      path: '/categories',
      name: 'categories',
      component: CategoryListView
    },
    {
      path: '/categories/:id',
      name: 'category-detail',
      component: CategoryImagesView,
      props: true
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      redirect: '/'
    }
  ]
});

export default router;