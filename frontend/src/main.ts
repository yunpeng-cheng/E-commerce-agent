import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 全局样式
import './assets/css/index.css'

const app = createApp(App)
app.use(ElementPlus)
app.mount('#app')
