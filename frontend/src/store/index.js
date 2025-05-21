import { createStore } from 'vuex'
import auth from './modules/auth'
import courses from './modules/courses'
import activities from './modules/activities'
import analytics from './modules/analytics'
import grades from './modules/grades'
import admin from './modules/admin'

export default createStore({
  state: {
    // 全局状态
    loading: false,
    error: null
  },
  getters: {
    // 全局getter
    isLoading: state => state.loading,
    hasError: state => !!state.error,
    getError: state => state.error
  },
  mutations: {
    // 全局mutations
    SET_LOADING(state, isLoading) {
      state.loading = isLoading
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    CLEAR_ERROR(state) {
      state.error = null
    }
  },
  actions: {
    // 全局actions
    setLoading({ commit }, isLoading) {
      commit('SET_LOADING', isLoading)
    },
    setError({ commit }, error) {
      commit('SET_ERROR', error)
    },
    clearError({ commit }) {
      commit('CLEAR_ERROR')
    }
  },
  modules: {
    auth,
    courses,
    activities,
    analytics,
    grades,
    admin
  }
}) 