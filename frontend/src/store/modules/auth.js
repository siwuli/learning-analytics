import axios from 'axios'
import { authAPI, userAPI } from '../../services/api'

// 初始状态
const state = {
  token: localStorage.getItem('token') || null,
  user: JSON.parse(localStorage.getItem('user')) || null
}

// getters
const getters = {
  isLoggedIn: state => !!state.token,
  currentUser: state => state.user
}

// mutations
const mutations = {
  SET_TOKEN(state, token) {
    state.token = token
  },
  SET_USER(state, user) {
    state.user = user
  },
  LOGOUT(state) {
    state.token = null
    state.user = null
  }
}

// actions
const actions = {
  // 登录
  async login({ commit, dispatch }, credentials) {
    try {
      // 使用真实API
      const response = await authAPI.login(credentials)
      
      // 保存令牌和用户信息
      const token = response.data.token
      const user = response.data.user
      
      console.log('登录成功，用户信息:', user)
      console.log('用户角色:', user.role)
      console.log('设置token:', token ? (token.substring(0, 10) + '...') : 'null')
      
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
      
      commit('SET_TOKEN', token)
      commit('SET_USER', user)
      
      return response
    } catch (error) {
      console.error('登录失败:', error)
      dispatch('setError', error.response?.data?.message || '登录失败', { root: true })
      throw error
    }
  },
  
  // 注册
  async register({ commit, dispatch }, userData) {
    try {
      // 使用真实API
      const response = await authAPI.register(userData)
      return response
    } catch (error) {
      dispatch('setError', error.response?.data?.message || '注册失败', { root: true })
      throw error
    }
  },
  
  // 获取当前用户信息
  async fetchCurrentUser({ commit, dispatch }) {
    try {
      // 使用真实API
      const response = await authAPI.getCurrentUser()
      commit('SET_USER', response.data.user)
      return response
    } catch (error) {
      // 如果获取用户信息失败，可能是令牌过期，尝试使用本地存储
      const user = JSON.parse(localStorage.getItem('user'))
      if (user) {
        commit('SET_USER', user)
      } else {
        dispatch('setError', error.response?.data?.message || '获取用户信息失败', { root: true })
        throw error
      }
    }
  },
  
  // 退出登录
  async logout({ commit }) {
    let success = true;
    
    try {
      // 尝试调用登出API
      await authAPI.logout().catch(err => console.warn('登出API调用失败:', err))
    } catch (error) {
      success = false;
    } finally {
      // 无论登出API是否成功，都清除本地存储
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // 更新状态
      commit('LOGOUT')
    }
    
    // 将返回语句移到finally块外部
    return success ? Promise.resolve() : Promise.reject(new Error('退出登录失败'));
  },
  
  // 更新用户资料
  async updateUserProfile({ commit, dispatch }, { userId, userData }) {
    try {
      const response = await userAPI.updateUser(userId, userData)
      
      // 更新本地存储的用户信息
      const updatedUser = response.data.user
      localStorage.setItem('user', JSON.stringify(updatedUser))
      commit('SET_USER', updatedUser)
      
      return response
    } catch (error) {
      dispatch('setError', error.response?.data?.message || '更新用户资料失败', { root: true })
      throw error
    }
  },
  
  // 上传用户头像
  async uploadUserAvatar({ commit, dispatch }, { userId, avatarFile, onProgress }) {
    try {
      const response = await userAPI.uploadAvatar(userId, avatarFile, onProgress)
      
      // 更新本地存储的用户信息
      const updatedUser = response.data.user
      localStorage.setItem('user', JSON.stringify(updatedUser))
      commit('SET_USER', updatedUser)
      
      return response
    } catch (error) {
      dispatch('setError', error.response?.data?.message || '上传头像失败', { root: true })
      throw error
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