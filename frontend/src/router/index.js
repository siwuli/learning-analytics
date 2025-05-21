import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

// 懒加载视图组件
const Dashboard = () => import('../views/Dashboard.vue')
const Login = () => import('../views/Login.vue')
const Register = () => import('../views/Register.vue')
const Courses = () => import('../views/Courses.vue')
const CourseDetail = () => import('../views/CourseDetail.vue')
const CourseGrades = () => import('../views/CourseGrades.vue')
const StudentGrades = () => import('../views/StudentGrades.vue')
const Analytics = () => import('../views/Analytics.vue')
const Profile = () => import('../views/Profile.vue')
const NotFound = () => import('../views/NotFound.vue')
const AdminDashboard = () => import('../views/AdminDashboard.vue')

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/courses',
    name: 'Courses',
    component: Courses,
    meta: { requiresAuth: true }
  },
  {
    path: '/courses/:id',
    name: 'CourseDetail',
    component: CourseDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/courses/:id/grades',
    name: 'CourseGrades',
    component: CourseGrades,
    meta: { requiresAuth: true, teacherOnly: true }
  },
  {
    path: '/grades',
    name: 'StudentGrades',
    component: StudentGrades,
    meta: { requiresAuth: true, studentOnly: true }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: Analytics,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: {
      requiresAuth: true,
      adminOnly: true,
      title: '管理员控制台'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 导航守卫
router.beforeEach((to, from, next) => {
  console.log('路由变化:', from.path, '->', to.path)
  console.log('当前用户状态:', store.getters['auth/isLoggedIn'], store.state.auth.user)
  
  const isLoggedIn = store.getters['auth/isLoggedIn']
  const userRole = store.state.auth.user?.role

  // 如果路由需要认证但用户未登录，重定向到登录页面
  if (to.matched.some(record => record.meta.requiresAuth) && !isLoggedIn) {
    console.log('需要认证但未登录，重定向到登录页面')
    next({ name: 'Login' })
  } 
  // 如果用户已登录且尝试访问登录/注册页面，重定向到仪表板
  else if (isLoggedIn && (to.name === 'Login' || to.name === 'Register')) {
    console.log('已登录用户尝试访问登录/注册页面，重定向到仪表板')
    next({ name: 'Dashboard' })
  }
  // 如果路由仅限管理员但用户不是管理员，重定向到仪表板
  else if (to.matched.some(record => record.meta.adminOnly) && userRole !== 'admin') {
    console.log('路由仅限管理员但用户不是管理员，重定向到仪表板')
    next({ name: 'Dashboard' })
  }
  // 如果路由仅限教师但用户不是教师，重定向到仪表板
  else if (to.matched.some(record => record.meta.teacherOnly) && userRole !== 'teacher') {
    console.log('路由仅限教师但用户不是教师，重定向到仪表板')
    next({ name: 'Dashboard' })
  }
  // 如果路由仅限学生但用户不是学生，重定向到仪表板
  else if (to.matched.some(record => record.meta.studentOnly) && userRole !== 'student') {
    console.log('路由仅限学生但用户不是学生，重定向到仪表板')
    next({ name: 'Dashboard' })
  }
  else {
    console.log('允许访问路由:', to.path)
    next()
  }
})

export default router