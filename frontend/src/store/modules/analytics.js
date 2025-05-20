import { analyticsAPI } from '../../services/api';

// 初始状态
const state = {
  userAnalytics: null,
  courseAnalytics: null,
  systemOverview: null,
  studentLearningAnalytics: null,
  classPerformanceAnalytics: null,
  loading: false,
  error: null
};

// getters
const getters = {
  getUserAnalytics: state => state.userAnalytics,
  getCourseAnalytics: state => state.courseAnalytics,
  getSystemOverview: state => state.systemOverview,
  getStudentLearningAnalytics: state => state.studentLearningAnalytics,
  getClassPerformanceAnalytics: state => state.classPerformanceAnalytics,
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
  SET_STUDENT_LEARNING_ANALYTICS(state, data) {
    state.studentLearningAnalytics = data;
  },
  SET_CLASS_PERFORMANCE_ANALYTICS(state, data) {
    state.classPerformanceAnalytics = data;
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
      
      // 处理数据
      const analyticsData = {
        userId: userId,
        totalDuration: response.data.total_duration || 0,
        totalActivities: response.data.total_activities || 0,
        completedActivities: response.data.completed_activities || 0,
        avgScore: response.data.avg_score || 0,
        courseProgress: response.data.course_progress || [],
        recentActivities: response.data.recent_activities || []
      };
      
      commit('SET_USER_ANALYTICS', analyticsData);
      commit('SET_LOADING', false);
      return analyticsData;
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
      
      // 处理数据
      const analyticsData = {
        courseId: courseId,
        studentCount: response.data.student_count || 0,
        activityCount: response.data.activity_count || 0,
        completionRate: response.data.completion_rate || 0,
        avgScore: response.data.avg_score || 0,
        activeStudents: response.data.active_students || [],
        activityTypes: response.data.activity_types || {},
        progressDistribution: response.data.progress_distribution || {},
        assignmentStats: response.data.assignment_stats || []
      };
      
      commit('SET_COURSE_ANALYTICS', analyticsData);
      commit('SET_LOADING', false);
      return analyticsData;
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
      
      // 处理数据
      const overviewData = {
        userCounts: response.data.user_counts || {},
        courseCounts: response.data.course_counts || {},
        activityCounts: response.data.activity_counts || {},
        activityTrend: response.data.activity_trend || [],
        activityTypeDistribution: response.data.activity_type_distribution || {},
        activeCourses: response.data.active_courses || []
      };
      
      // 添加前端需要的额外数据
      overviewData.totalUsers = overviewData.userCounts.total || 0;
      overviewData.totalCourses = overviewData.courseCounts.total || 0;
      overviewData.totalActivities = overviewData.activityCounts.total || 0;
      
      // 计算平均完成率
      if (overviewData.activityCounts.total > 0) {
        overviewData.avgCompletionRate = Math.round(
          (overviewData.activityCounts.completed / overviewData.activityCounts.total) * 100
        );
      } else {
        overviewData.avgCompletionRate = 0;
      }
      
      // 计算用户增长率 (暂时模拟)
      overviewData.userGrowthRate = 8;
      
      commit('SET_SYSTEM_OVERVIEW', overviewData);
      commit('SET_LOADING', false);
      return overviewData;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取系统概览数据失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 获取学生学习分析数据
  async fetchStudentLearningAnalytics({ commit }, userId) {
    try {
      commit('SET_LOADING', true);
      const response = await analyticsAPI.getStudentLearningAnalytics(userId);
      
      // 处理数据
      const analyticsData = {
        userId: userId,
        learningTimeTrend: response.data.learning_time_trend || [],
        activityTypeDistribution: response.data.activity_type_distribution || {},
        scoreComparisons: response.data.score_comparisons || [],
        hourlyDistribution: response.data.hourly_distribution || {},
        durationDistribution: response.data.duration_distribution || {},
        pendingAssignments: response.data.pending_assignments || []
      };
      
      commit('SET_STUDENT_LEARNING_ANALYTICS', analyticsData);
      commit('SET_LOADING', false);
      return analyticsData;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取学生学习分析数据失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 获取班级表现分析数据
  async fetchClassPerformanceAnalytics({ commit }, courseId) {
    try {
      commit('SET_LOADING', true);
      const response = await analyticsAPI.getClassPerformanceAnalytics(courseId);
      
      // 处理数据
      const analyticsData = {
        courseId: courseId,
        studentCount: response.data.student_count || 0,
        progressData: response.data.progress_data || [],
        completionStats: response.data.completion_stats || {},
        completionDistribution: response.data.completion_distribution || {},
        scoreStats: response.data.score_stats || {},
        scoreDistribution: response.data.score_distribution || {},
        engagementRanking: response.data.engagement_ranking || [],
        performanceRanking: response.data.performance_ranking || []
      };
      
      commit('SET_CLASS_PERFORMANCE_ANALYTICS', analyticsData);
      commit('SET_LOADING', false);
      return analyticsData;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取班级表现分析数据失败');
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