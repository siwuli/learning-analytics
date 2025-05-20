import { analyticsAPI } from '../../services/api';

// 初始状态
const state = {
  userAnalytics: null,
  courseAnalytics: null,
  systemOverview: null,
  loading: false,
  error: null
};

// getters
const getters = {
  getUserAnalytics: state => state.userAnalytics,
  getCourseAnalytics: state => state.courseAnalytics,
  getSystemOverview: state => state.systemOverview,
  isLoading: state => state.loading
};

// mutations
const mutations = {
  SET_USER_ANALYTICS(state, data) {
    state.userAnalytics = data;
  },
  SET_COURSE_ANALYTICS(state, data) {
    state.courseAnalytics = data;
  },
  SET_SYSTEM_OVERVIEW(state, data) {
    state.systemOverview = data;
  },
  SET_LOADING(state, status) {
    state.loading = status;
  },
  SET_ERROR(state, error) {
    state.error = error;
  }
};

// actions
const actions = {
  // 获取用户分析数据
  async fetchUserAnalytics({ commit }, userId) {
    try {
      commit('SET_LOADING', true);
      const response = await analyticsAPI.getUserAnalytics(userId);
      commit('SET_USER_ANALYTICS', response.data.analytics);
      commit('SET_LOADING', false);
      return response.data.analytics;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取用户分析数据失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 获取课程分析数据
  async fetchCourseAnalytics({ commit }, courseId) {
    try {
      commit('SET_LOADING', true);
      const response = await analyticsAPI.getCourseAnalytics(courseId);
      commit('SET_COURSE_ANALYTICS', response.data.analytics);
      commit('SET_LOADING', false);
      return response.data.analytics;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取课程分析数据失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 获取系统概览数据
  async fetchSystemOverview({ commit }) {
    try {
      commit('SET_LOADING', true);
      const response = await analyticsAPI.getSystemOverview();
      commit('SET_SYSTEM_OVERVIEW', response.data.overview);
      commit('SET_LOADING', false);
      return response.data.overview;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取系统概览数据失败');
      commit('SET_LOADING', false);
      throw error;
    }
  }
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}; 