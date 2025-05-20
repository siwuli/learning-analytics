import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'

// 配置axios默认值
axios.defaults.baseURL = 'http://127.0.0.1:5000/api'
axios.defaults.headers.common['Content-Type'] = 'application/json'

// 添加请求拦截器
axios.interceptors.request.use(config => {
  const token = store.state.auth.token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 添加响应拦截器
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // 未授权，可能需要重新登录
      store.dispatch('auth/logout')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

const app = createApp(App)

app.config.globalProperties.$http = axios

app.use(store)
   .use(router)
   .use(ElementPlus)
   .mount('#app') 