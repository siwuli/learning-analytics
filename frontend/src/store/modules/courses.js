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
  },
  updateCourseProgress(state, { courseId, progress }) {
    console.log(`开始更新课程${courseId}的进度为${progress}`);
    
    if (state.currentCourse && state.currentCourse.id === parseInt(courseId)) {
      console.log('找到当前课程，更新进度');
      state.currentCourse = {
        ...state.currentCourse,
        progress: progress
      };
      console.log('更新后的当前课程:', state.currentCourse);
    }
    
    // 同时更新课程列表中的课程进度
    const courseIndex = state.allCourses.findIndex(c => c.id === parseInt(courseId));
    if (courseIndex !== -1) {
      console.log(`找到课程列表中的课程，索引:${courseIndex}，更新进度`);
      state.allCourses[courseIndex] = {
        ...state.allCourses[courseIndex],
        progress: progress
      };
      console.log('更新后的课程列表项:', state.allCourses[courseIndex]);
    } else {
      console.warn(`在课程列表中未找到ID为${courseId}的课程`);
    }
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
      return response.data.courses;
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
      const response = await courseAPI.getCourses();
      const user = rootState.auth.user;
      // 筛选当前用户作为教师的课程
      const teachingCourses = response.data.courses.filter(course => 
        course.instructor_id === user.id
      );
      commit('SET_TEACHING_COURSES', teachingCourses);
      commit('SET_LOADING', false);
      return teachingCourses;
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
      
      const userId = rootState.auth.user.id;
      // 调用专门的API获取学生已选课程
      const response = await courseAPI.getEnrolledCourses(userId);
      
      commit('SET_ENROLLED_COURSES', response.data.courses);
      commit('SET_LOADING', false);
      return response.data.courses;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取已选课程失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 获取可选课程
  async fetchAvailableCourses({ commit, state, rootState, dispatch }) {
    try {
      commit('SET_LOADING', true);
      
      // 获取所有课程
      const allCourses = await dispatch('fetchAllCourses');
      const user = rootState.auth.user;
      
      // 获取已选课程ID列表
      const enrolledCourseIds = state.enrolledCourses.map(course => course.id);
      
      // 筛选出未选的活跃课程
      const availableCourses = allCourses.filter(course => 
        !enrolledCourseIds.includes(course.id) && 
        course.status === 'active' && 
        course.instructor_id !== user.id // 排除自己教授的课程
      );
      
      commit('SET_AVAILABLE_COURSES', availableCourses);
      commit('SET_LOADING', false);
      return availableCourses;
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
      return response.data.course;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取课程详情失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 创建新课程
  async createCourse({ commit, rootState }, courseData) {
    try {
      commit('SET_LOADING', true);
      
      // 确保设置教师ID为当前用户
      const user = rootState.auth.user;
      const newCourseData = {
        ...courseData,
        instructor_id: user.id
      };
      
      const response = await courseAPI.createCourse(newCourseData);
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
      return response.data.students;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '获取课程学生失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 学生选课
  async enrollCourse({ commit, dispatch }, { courseId, userId }) {
    try {
      commit('SET_LOADING', true);
      const response = await courseAPI.enrollStudent(courseId, userId);
      
      // 选课成功后更新已选课程和可选课程列表
      await dispatch('fetchEnrolledCourses');
      await dispatch('fetchAvailableCourses');
      
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '选课失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 学生退选课程
  async dropCourse({ commit, dispatch }, { courseId, userId }) {
    try {
      commit('SET_LOADING', true);
      await courseAPI.dropStudent(courseId, userId);
      
      // 退选成功后更新已选课程和可选课程列表
      await dispatch('fetchEnrolledCourses');
      await dispatch('fetchAvailableCourses');
      
      commit('SET_LOADING', false);
      return { success: true };
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '退选课程失败');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // 添加学生到课程
  async enrollStudent({ commit, dispatch }, { courseId, userId }) {
    try {
      commit('SET_LOADING', true);
      const response = await courseAPI.enrollStudent(courseId, userId);
      
      // 选课成功后更新已选课程和可选课程列表
      await dispatch('fetchEnrolledCourses');
      await dispatch('fetchAvailableCourses');
      
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || '选课失败');
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