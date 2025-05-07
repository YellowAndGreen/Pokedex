import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import './style.css'

// Create and mount the app
const app = createApp(App)

// Use plugins
app.use(createPinia())
app.use(router)
app.use(ElementPlus)

// Mock data for development (remove in production)
if (import.meta.env.DEV) {
  // Import mock data service
  import('./services/mockData').then(({ setupMocks }) => {
    setupMocks();
    // Mount the app after mocks are set up
    app.mount('#app')
  });
} else {
  // In production, mount directly
  app.mount('#app')
}