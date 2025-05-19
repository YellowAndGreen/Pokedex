import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './style.css'
import { createPinia } from 'pinia'

// Create and mount the app
const app = createApp(App)
const pinia = createPinia()

// Use plugins
app.use(router)
app.use(ElementPlus)
app.use(pinia)

app.mount('#app')