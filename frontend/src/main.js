import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'
import { setupErrorHandler } from './utils/errorHandler'
import VueAxios from 'vue-axios'
import * as echarts from 'echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, TitleComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'

// 设置错误处理器
setupErrorHandler();

// 设置默认axios基础URL
axios.defaults.baseURL = 'http://localhost:5000/api'
axios.defaults.withCredentials = true

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
      store.dispatch('auth/logout').then(() => {
        router.push('/login')
      })
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

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue错误:', err)
  console.error('错误组件:', vm)
  console.error('错误信息:', info)
}

// 捕获未处理的Promise错误
window.addEventListener('unhandledrejection', event => {
  console.error('未处理的Promise错误:', event.reason)
})

app.config.globalProperties.$http = axios
app.use(store)
app.use(router)
app.use(VueAxios, axios)
app.use(ElementPlus, {
  locale: zhCn
})

// 手动注册echarts需要的组件
use([
  CanvasRenderer,
  PieChart,
  BarChart,
  LineChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent
])

// 全局注册ECharts组件
app.component('v-chart', VChart)
// 将ECharts添加到全局属性中
app.config.globalProperties.$echarts = echarts

app.mount('#app') 