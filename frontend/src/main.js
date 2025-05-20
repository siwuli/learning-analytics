import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'
import { setupErrorHandler } from './utils/errorHandler'

// 设置错误处理器
setupErrorHandler();

// 设置默认axios基础URL
axios.defaults.baseURL = 'http://127.0.0.1:5000/api'

// 添加请求拦截器，为每个请求添加token
axios.interceptors.request.use(
  config => {
    const token = store.state.auth.token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 添加响应拦截器
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // 如果接收到401响应，则用户未授权
      store.dispatch('auth/logout')
      router.push('/login')
    } else if (error.response && error.response.status === 404) {
      // 对于404错误，记录在控制台但不显示错误通知
      console.warn('API不存在:', error.config.url)
      return Promise.reject({
        ...error,
        isApiNotFound: true,
        message: 'API不存在'
      })
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