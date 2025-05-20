import { gradeAPI } from '../../services/api';

// 初始状态
const state = {
  courseGrades: [],
  userGrades: [],
  gradeSettings: null,
  loading: false,
  error: null
};

// getters
const getters = {
  getCourseGrades: state => state.courseGrades,
  getUserGrades: state => state.userGrades,
  getGradeSettings: state => state.gradeSettings,
  isLoading: state => state.loading
};

// mutations
const mutations = {
  SET_COURSE_GRADES(state, grades) {
    state.courseGrades = grades;
  },
  SET_USER_GRADES(state, grades) {
    state.userGrades = grades;
  },
  SET_GRADE_SETTINGS(state, settings) {
    state.gradeSettings = settings;
  },
  UPDATE_STUDENT_GRADE(state, updatedGrade) {
    const index = state.courseGrades.findIndex(g => g.user_id === updatedGrade.user_id);
    if (index !== -1) {
      state.courseGrades.splice(index, 1, updatedGrade);
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
  // 获取课程成绩设置
  async fetchGradeSettings({ commit }, courseId) {
    try {
      commit('SET_LOADING', true);
      const response = await gradeAPI.getGradeSettings(courseId);
      commit('SET_GRADE_SETTINGS', response.data.settings);
      commit('SET_LOADING', false);
      return response.data.settings;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取成绩设置失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 更新课程成绩设置
  async updateGradeSettings({ commit }, { courseId, settingsData }) {
    try {
      commit('SET_LOADING', true);
      const response = await gradeAPI.updateGradeSettings(courseId, settingsData);
      commit('SET_GRADE_SETTINGS', response.data.settings);
      commit('SET_LOADING', false);
      return response.data.settings;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '更新成绩设置失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 获取课程所有学生的成绩
  async fetchCourseGrades({ commit }, courseId) {
    try {
      commit('SET_LOADING', true);
      const response = await gradeAPI.getCourseGrades(courseId);
      commit('SET_COURSE_GRADES', response.data.grades);
      commit('SET_GRADE_SETTINGS', response.data.settings);
      commit('SET_LOADING', false);
      return {
        grades: response.data.grades,
        settings: response.data.settings
      };
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取课程成绩失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 更新学生成绩
  async updateStudentGrade({ commit }, { courseId, studentId, gradeData }) {
    try {
      commit('SET_LOADING', true);
      const response = await gradeAPI.updateStudentGrade(courseId, studentId, gradeData);
      commit('UPDATE_STUDENT_GRADE', response.data.grade);
      commit('SET_LOADING', false);
      return response.data.grade;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '更新学生成绩失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 批量更新学生成绩
  async batchUpdateGrades({ commit, dispatch }, { courseId, gradesData }) {
    try {
      commit('SET_LOADING', true);
      const response = await gradeAPI.batchUpdateGrades(courseId, gradesData);
      // 重新获取课程成绩
      await dispatch('fetchCourseGrades', courseId);
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '批量更新成绩失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 获取用户在所有课程中的成绩
  async fetchUserGrades({ commit }, userId) {
    try {
      commit('SET_LOADING', true);
      const response = await gradeAPI.getUserGrades(userId);
      commit('SET_USER_GRADES', response.data.grades);
      commit('SET_LOADING', false);
      return response.data.grades;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取用户成绩失败');
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