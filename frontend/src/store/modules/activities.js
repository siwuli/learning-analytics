import { activityAPI } from '../../services/api';

// 初始状态
const state = {
  activities: [],
  userActivities: [],
  courseActivities: [],
  currentActivity: null,
  loading: false,
  error: null
};

// getters
const getters = {
  getAllActivities: state => state.activities,
  getUserActivities: state => state.userActivities,
  getCourseActivities: state => state.courseActivities,
  getCurrentActivity: state => state.currentActivity,
  isLoading: state => state.loading
};

// mutations
const mutations = {
  SET_ACTIVITIES(state, activities) {
    state.activities = activities;
  },
  SET_USER_ACTIVITIES(state, activities) {
    state.userActivities = activities;
  },
  SET_COURSE_ACTIVITIES(state, activities) {
    state.courseActivities = activities;
  },
  SET_CURRENT_ACTIVITY(state, activity) {
    state.currentActivity = activity;
  },
  ADD_ACTIVITY(state, activity) {
    state.activities.push(activity);
    
    // 如果是当前用户的活动，也添加到用户活动列表
    if (activity.user_id === state.userActivities.userId) {
      state.userActivities.push(activity);
    }
    
    // 如果是当前课程的活动，也添加到课程活动列表
    if (activity.course_id === state.courseActivities.courseId) {
      state.courseActivities.push(activity);
    }
  },
  UPDATE_ACTIVITY(state, updatedActivity) {
    // 更新所有活动列表
    const activityIndex = state.activities.findIndex(a => a.id === updatedActivity.id);
    if (activityIndex !== -1) {
      state.activities.splice(activityIndex, 1, updatedActivity);
    }
    
    // 更新用户活动列表
    const userActivityIndex = state.userActivities.findIndex(a => a.id === updatedActivity.id);
    if (userActivityIndex !== -1) {
      state.userActivities.splice(userActivityIndex, 1, updatedActivity);
    }
    
    // 更新课程活动列表
    const courseActivityIndex = state.courseActivities.findIndex(a => a.id === updatedActivity.id);
    if (courseActivityIndex !== -1) {
      state.courseActivities.splice(courseActivityIndex, 1, updatedActivity);
    }
    
    // 如果是当前活动，也更新
    if (state.currentActivity && state.currentActivity.id === updatedActivity.id) {
      state.currentActivity = updatedActivity;
    }
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
  // 获取所有活动
  async fetchActivities({ commit }) {
    try {
      commit('SET_LOADING', true);
      const response = await activityAPI.getActivities();
      commit('SET_ACTIVITIES', response.data.activities);
      commit('SET_LOADING', false);
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取活动失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 获取用户活动
  async fetchUserActivities({ commit }, userId) {
    try {
      commit('SET_LOADING', true);
      const response = await activityAPI.getUserActivities(userId);
      // 存储用于识别这些活动属于哪个用户
      response.data.activities.userId = userId;
      commit('SET_USER_ACTIVITIES', response.data.activities);
      commit('SET_LOADING', false);
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取用户活动失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 获取课程活动
  async fetchCourseActivities({ commit }, courseId) {
    try {
      commit('SET_LOADING', true);
      const response = await activityAPI.getCourseActivities(courseId);
      // 存储用于识别这些活动属于哪个课程
      response.data.activities.courseId = courseId;
      commit('SET_COURSE_ACTIVITIES', response.data.activities);
      commit('SET_LOADING', false);
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取课程活动失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 创建新活动
  async createActivity({ commit }, activityData) {
    try {
      commit('SET_LOADING', true);
      const response = await activityAPI.createActivity(activityData);
      commit('ADD_ACTIVITY', response.data.activity);
      commit('SET_LOADING', false);
      return response.data.activity;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '创建活动失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 更新活动
  async updateActivity({ commit }, { activityId, activityData }) {
    try {
      commit('SET_LOADING', true);
      const response = await activityAPI.updateActivity(activityId, activityData);
      commit('UPDATE_ACTIVITY', response.data.activity);
      commit('SET_LOADING', false);
      return response.data.activity;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '更新活动失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 标记活动为已完成
  async completeActivity({ commit }, { activityId, completionData }) {
    try {
      commit('SET_LOADING', true);
      const activityData = {
        completed: true,
        ...completionData
      };
      const response = await activityAPI.updateActivity(activityId, activityData);
      commit('UPDATE_ACTIVITY', response.data.activity);
      commit('SET_LOADING', false);
      return response.data.activity;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '完成活动失败');
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