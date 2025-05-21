import { adminAPI } from '../../services/api'

// 初始状态
const state = {
  systemOverview: null,
  users: [],
  usersPagination: {
    total: 0,
    pages: 0,
    currentPage: 1
  },
  currentUser: null,
  courses: [],
  coursesPagination: {
    total: 0,
    pages: 0,
    currentPage: 1
  },
  currentCourse: null,
  courseStudents: [],
  loading: false,
  error: null
}

// getters
const getters = {
  systemOverview: state => state.systemOverview,
  users: state => state.users,
  usersPagination: state => state.usersPagination,
  currentUser: state => state.currentUser,
  courses: state => state.courses,
  coursesPagination: state => state.coursesPagination,
  currentCourse: state => state.currentCourse,
  courseStudents: state => state.courseStudents,
  isLoading: state => state.loading,
  error: state => state.error
}

// mutations
const mutations = {
  SET_SYSTEM_OVERVIEW(state, data) {
    state.systemOverview = data
  },
  SET_USERS(state, { users, pagination }) {
    state.users = users
    state.usersPagination = pagination
  },
  SET_CURRENT_USER(state, user) {
    state.currentUser = user
  },
  SET_COURSES(state, { courses, pagination }) {
    state.courses = courses
    state.coursesPagination = pagination
  },
  SET_CURRENT_COURSE(state, course) {
    state.currentCourse = course
  },
  SET_COURSE_STUDENTS(state, students) {
    state.courseStudents = students
  },
  SET_LOADING(state, status) {
    state.loading = status
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  CLEAR_ERROR(state) {
    state.error = null
  }
}

// actions
const actions = {
  // 系统概览
  async fetchSystemOverview({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      console.log('发送获取系统概览请求: /admin/overview')
      const response = await adminAPI.getSystemOverview()
      console.log('获取系统概览API响应:', response.data)
      commit('SET_SYSTEM_OVERVIEW', response.data.data)
      return response
    } catch (error) {
      console.error('获取系统概览失败:', error)
      commit('SET_ERROR', error.response?.data?.message || '获取系统概览失败')
      commit('SET_SYSTEM_OVERVIEW', {
        user_counts: { total: 0, students: 0, teachers: 0, admins: 0 },
        course_counts: { total: 0, active: 0, archived: 0 },
        activity_counts: { total: 0, completed: 0 },
        activity_type_distribution: {}
      })
      return null
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // 用户管理
  async fetchUsers({ commit }, { page = 1, perPage = 10, role = null } = {}) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      console.log('发送获取用户请求:', `/admin/users?page=${page}&per_page=${perPage}${role ? `&role=${role}` : ''}`)
      const response = await adminAPI.getUsers(page, perPage, role)
      console.log('获取用户API响应:', response.data)
      
      const pagination = {
        total: response.data.total,
        pages: response.data.pages,
        currentPage: response.data.current_page
      }
      commit('SET_USERS', { users: response.data.users, pagination })
      return response
    } catch (error) {
      console.error('获取用户列表失败:', error)
      commit('SET_ERROR', error.response?.data?.message || '获取用户列表失败')
      commit('SET_USERS', { 
        users: [], 
        pagination: { total: 0, pages: 0, currentPage: page } 
      })
      return null
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async fetchUserDetail({ commit }, userId) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await adminAPI.getUserDetail(userId)
      commit('SET_CURRENT_USER', response.data.user)
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取用户详情失败')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async createUser({ commit, dispatch }, userData) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await adminAPI.createUser(userData)
      dispatch('fetchUsers') // 刷新用户列表
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '创建用户失败')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async updateUser({ commit, dispatch }, { userId, userData }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await adminAPI.updateUser(userId, userData)
      dispatch('fetchUserDetail', userId) // 刷新用户详情
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '更新用户失败')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async deleteUser({ commit, dispatch }, userId) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await adminAPI.deleteUser(userId)
      dispatch('fetchUsers') // 刷新用户列表
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '删除用户失败')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // 课程管理
  async fetchCourses({ commit }, { page = 1, perPage = 10, status = null } = {}) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      console.log('发送获取课程请求:', `/admin/courses?page=${page}&per_page=${perPage}${status ? `&status=${status}` : ''}`)
      const response = await adminAPI.getCourses(page, perPage, status)
      console.log('获取课程API响应:', response.data)
      
      const pagination = {
        total: response.data.total,
        pages: response.data.pages,
        currentPage: response.data.current_page
      }
      commit('SET_COURSES', { courses: response.data.courses, pagination })
      return response
    } catch (error) {
      console.error('获取课程列表失败:', error)
      commit('SET_ERROR', error.response?.data?.message || '获取课程列表失败')
      commit('SET_COURSES', { 
        courses: [], 
        pagination: { total: 0, pages: 0, currentPage: page } 
      })
      return null
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async fetchCourseDetail({ commit }, courseId) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await adminAPI.getCourseDetail(courseId)
      commit('SET_CURRENT_COURSE', response.data.course)
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取课程详情失败')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async createCourse({ commit, dispatch }, courseData) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await adminAPI.createCourse(courseData)
      dispatch('fetchCourses') // 刷新课程列表
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '创建课程失败')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async updateCourse({ commit, dispatch }, { courseId, courseData }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await adminAPI.updateCourse(courseId, courseData)
      dispatch('fetchCourseDetail', courseId) // 刷新课程详情
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '更新课程失败')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async deleteCourse({ commit, dispatch }, courseId) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await adminAPI.deleteCourse(courseId)
      dispatch('fetchCourses') // 刷新课程列表
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '删除课程失败')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async fetchCourseStudents({ commit }, courseId) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await adminAPI.getCourseStudents(courseId)
      commit('SET_COURSE_STUDENTS', response.data.students)
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取课程学生列表失败')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async addStudentToCourse({ commit, dispatch }, { courseId, studentId }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await adminAPI.addStudentToCourse(courseId, studentId)
      dispatch('fetchCourseStudents', courseId) // 刷新学生列表
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '添加学生到课程失败')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async removeStudentFromCourse({ commit, dispatch }, { courseId, studentId }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await adminAPI.removeStudentFromCourse(courseId, studentId)
      dispatch('fetchCourseStudents', courseId) // 刷新学生列表
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '从课程移除学生失败')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
} 