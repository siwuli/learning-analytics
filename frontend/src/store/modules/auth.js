import axios from 'axios'

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
      // 注意：这里应该调用真实的API，下面是模拟
      // const response = await axios.post('/auth/login', credentials)
      const response = { data: { token: 'fake-token', user: { id: 1, username: credentials.username, role: 'student' } } }
      
      // 保存令牌和用户信息
      const token = response.data.token
      const user = response.data.user
      
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
      
      commit('SET_TOKEN', token)
      commit('SET_USER', user)
      
      return response
    } catch (error) {
      dispatch('setError', error.response?.data?.message || '登录失败', { root: true })
      throw error
    }
  },
  
  // 注册
  async register({ commit, dispatch }, userData) {
    try {
      // 注意：这里应该调用真实的API，下面是模拟
      // const response = await axios.post('/auth/register', userData)
      const response = { data: { message: '注册成功' } }
      
      return response
    } catch (error) {
      dispatch('setError', error.response?.data?.message || '注册失败', { root: true })
      throw error
    }
  },
  
  // 获取当前用户信息
  async fetchCurrentUser({ commit, dispatch }) {
    try {
      // 注意：这里应该调用真实的API，下面是模拟
      // const response = await axios.get('/auth/me')
      const user = JSON.parse(localStorage.getItem('user'))
      if (user) {
        commit('SET_USER', user)
      }
    } catch (error) {
      dispatch('setError', error.response?.data?.message || '获取用户信息失败', { root: true })
      throw error
    }
  },
  
  // 退出登录
  logout({ commit }) {
    // 清除本地存储
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    
    // 更新状态
    commit('LOGOUT')
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
} 