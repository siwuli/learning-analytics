import { courseAPI } from '../../services/api';

// 初始状态
const state = {
  allCourses: [],
  teachingCourses: [],
  enrolledCourses: [],
  availableCourses: [],
  currentCourse: null,
  courseStudents: [],
  loading: false,
  error: null
};

// getters
const getters = {
  getTeachingCourses: state => state.teachingCourses,
  getEnrolledCourses: state => state.enrolledCourses,
  getAvailableCourses: state => state.availableCourses,
  getCurrentCourse: state => state.currentCourse,
  getCourseStudents: state => state.courseStudents,
  isLoading: state => state.loading
};

// mutations
const mutations = {
  SET_ALL_COURSES(state, courses) {
    state.allCourses = courses;
  },
  SET_TEACHING_COURSES(state, courses) {
    state.teachingCourses = courses;
  },
  SET_ENROLLED_COURSES(state, courses) {
    state.enrolledCourses = courses;
  },
  SET_AVAILABLE_COURSES(state, courses) {
    state.availableCourses = courses;
  },
  SET_CURRENT_COURSE(state, course) {
    state.currentCourse = course;
  },
  SET_COURSE_STUDENTS(state, students) {
    state.courseStudents = students;
  },
  ADD_COURSE(state, course) {
    state.allCourses.push(course);
    state.teachingCourses.push(course);
  },
  UPDATE_COURSE(state, updatedCourse) {
    // 更新所有课程列表
    const courseIndex = state.allCourses.findIndex(c => c.id === updatedCourse.id);
    if (courseIndex !== -1) {
      state.allCourses.splice(courseIndex, 1, updatedCourse);
    }
    
    // 更新教学课程列表
    const teachingIndex = state.teachingCourses.findIndex(c => c.id === updatedCourse.id);
    if (teachingIndex !== -1) {
      state.teachingCourses.splice(teachingIndex, 1, updatedCourse);
    }
    
    // 更新已选课程列表
    const enrolledIndex = state.enrolledCourses.findIndex(c => c.id === updatedCourse.id);
    if (enrolledIndex !== -1) {
      state.enrolledCourses.splice(enrolledIndex, 1, updatedCourse);
    }
    
    // 如果是当前课程，也更新
    if (state.currentCourse && state.currentCourse.id === updatedCourse.id) {
      state.currentCourse = updatedCourse;
    }
  },
  REMOVE_COURSE(state, courseId) {
    state.allCourses = state.allCourses.filter(c => c.id !== courseId);
    state.teachingCourses = state.teachingCourses.filter(c => c.id !== courseId);
    state.enrolledCourses = state.enrolledCourses.filter(c => c.id !== courseId);
  },
  ADD_STUDENT_TO_COURSE(state, { courseId, student }) {
    if (state.currentCourse && state.currentCourse.id === courseId) {
      state.courseStudents.push(student);
    }
  },
  REMOVE_STUDENT_FROM_COURSE(state, { courseId, studentId }) {
    if (state.currentCourse && state.currentCourse.id === courseId) {
      state.courseStudents = state.courseStudents.filter(s => s.id !== studentId);
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
  // 获取所有课程
  async fetchAllCourses({ commit }) {
    try {
      commit('SET_LOADING', true);
      const response = await courseAPI.getCourses();
      commit('SET_ALL_COURSES', response.data.courses);
      commit('SET_LOADING', false);
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取课程失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 获取教师的教学课程
  async fetchTeachingCourses({ commit, rootState }) {
    try {
      commit('SET_LOADING', true);
      // 从所有课程中筛选教学课程
      const response = await courseAPI.getCourses();
      const user = rootState.auth.user;
      const teachingCourses = response.data.courses.filter(course => course.instructor_id === user.id);
      commit('SET_TEACHING_COURSES', teachingCourses);
      commit('SET_LOADING', false);
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取教学课程失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 获取学生已选课程
  async fetchEnrolledCourses({ commit, rootState }) {
    try {
      commit('SET_LOADING', true);
      const user = rootState.auth.user;
      // 这里应该有一个API来获取学生的已选课程
      // 暂时模拟
      const response = await courseAPI.getCourses();
      // 在实际API中，这部分筛选应该由后端完成
      const enrolledCourses = response.data.courses.filter(course => {
        // 简单模拟，实际应该检查课程enrollments
        return Math.random() > 0.5;
      });
      commit('SET_ENROLLED_COURSES', enrolledCourses);
      commit('SET_LOADING', false);
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取已选课程失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 获取可选课程
  async fetchAvailableCourses({ commit, rootState, state }) {
    try {
      commit('SET_LOADING', true);
      const user = rootState.auth.user;
      // 获取所有课程
      const response = await courseAPI.getCourses();
      // 筛选出未选的课程
      const enrolledCourseIds = state.enrolledCourses.map(course => course.id);
      const availableCourses = response.data.courses.filter(course => 
        !enrolledCourseIds.includes(course.id) && course.status === 'active'
      );
      commit('SET_AVAILABLE_COURSES', availableCourses);
      commit('SET_LOADING', false);
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取可选课程失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 获取单个课程详情
  async fetchCourse({ commit }, courseId) {
    try {
      commit('SET_LOADING', true);
      const response = await courseAPI.getCourse(courseId);
      commit('SET_CURRENT_COURSE', response.data.course);
      commit('SET_LOADING', false);
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取课程详情失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 创建新课程
  async createCourse({ commit }, courseData) {
    try {
      commit('SET_LOADING', true);
      const response = await courseAPI.createCourse(courseData);
      commit('ADD_COURSE', response.data.course);
      commit('SET_LOADING', false);
      return response.data.course;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '创建课程失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 更新课程
  async updateCourse({ commit }, { courseId, courseData }) {
    try {
      commit('SET_LOADING', true);
      const response = await courseAPI.updateCourse(courseId, courseData);
      commit('UPDATE_COURSE', response.data.course);
      commit('SET_LOADING', false);
      return response.data.course;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '更新课程失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 删除课程
  async deleteCourse({ commit }, courseId) {
    try {
      commit('SET_LOADING', true);
      await courseAPI.deleteCourse(courseId);
      commit('REMOVE_COURSE', courseId);
      commit('SET_LOADING', false);
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '删除课程失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 获取课程学生
  async fetchCourseStudents({ commit }, courseId) {
    try {
      commit('SET_LOADING', true);
      const response = await courseAPI.getCourseStudents(courseId);
      commit('SET_COURSE_STUDENTS', response.data.students);
      commit('SET_LOADING', false);
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取课程学生失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 添加学生到课程
  async enrollStudent({ commit }, { courseId, userId }) {
    try {
      commit('SET_LOADING', true);
      await courseAPI.enrollStudent(courseId, userId);
      // 重新获取课程学生列表
      const response = await courseAPI.getCourseStudents(courseId);
      commit('SET_COURSE_STUDENTS', response.data.students);
      commit('SET_LOADING', false);
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '添加学生失败');
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