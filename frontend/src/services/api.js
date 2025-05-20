import axios from 'axios';

// 认证相关API
export const authAPI = {
  login(credentials) {
    return axios.post('/auth/login', credentials);
  },
  
  register(userData) {
    return axios.post('/auth/register', userData);
  },
  
  logout() {
    return axios.post('/auth/logout');
  },
  
  getCurrentUser() {
    return axios.get('/auth/user');
  }
};

// 用户相关API
export const userAPI = {
  getUsers(query = '') {
    return axios.get(`/users${query}`);
  },
  
  getUser(id) {
    return axios.get(`/users/${id}`);
  },
  
  updateUser(id, userData) {
    return axios.put(`/users/${id}`, userData);
  },
  
  deleteUser(id) {
    return axios.delete(`/users/${id}`);
  }
};

// 课程相关API
export const courseAPI = {
  getCourses() {
    return axios.get('/courses');
  },
  
  getCourse(id) {
    return axios.get(`/courses/${id}`);
  },
  
  createCourse(courseData) {
    return axios.post('/courses', courseData);
  },
  
  updateCourse(id, courseData) {
    return axios.put(`/courses/${id}`, courseData);
  },
  
  deleteCourse(id) {
    return axios.delete(`/courses/${id}`);
  },
  
  enrollStudent(courseId, userId) {
    return axios.post(`/courses/${courseId}/enroll/${userId}`);
  },
  
  dropStudent(courseId, userId) {
    return axios.delete(`/courses/${courseId}/enroll/${userId}`);
  },
  
  getEnrolledCourses(userId) {
    return axios.get(`/users/${userId}/courses`);
  },
  
  getCourseStudents(courseId) {
    return axios.get(`/courses/${courseId}/students`);
  },
  
  // 章节相关方法
  getCourseSections(courseId) {
    return axios.get(`/courses/${courseId}/sections`);
  },
  
  getCourseSection(courseId, sectionId) {
    return axios.get(`/courses/${courseId}/sections/${sectionId}`);
  },
  
  createCourseSection(courseId, sectionData) {
    return axios.post(`/courses/${courseId}/sections`, sectionData);
  },
  
  updateCourseSection(courseId, sectionId, sectionData) {
    return axios.put(`/courses/${courseId}/sections/${sectionId}`, sectionData);
  },
  
  deleteCourseSection(courseId, sectionId) {
    return axios.delete(`/courses/${courseId}/sections/${sectionId}`);
  },
  
  // 资源相关方法
  getSectionResources(sectionId) {
    return axios.get(`/sections/${sectionId}/resources`);
  },
  
  getSectionResource(sectionId, resourceId) {
    return axios.get(`/sections/${sectionId}/resources/${resourceId}`);
  },
  
  createSectionResource(sectionId, resourceData) {
    return axios.post(`/sections/${sectionId}/resources`, resourceData);
  },
  
  updateSectionResource(sectionId, resourceId, resourceData) {
    return axios.put(`/sections/${sectionId}/resources/${resourceId}`, resourceData);
  },
  
  deleteSectionResource(sectionId, resourceId) {
    return axios.delete(`/sections/${sectionId}/resources/${resourceId}`);
  },
  
  // 资源进度相关方法
  getResourceProgress(userId, resourceId) {
    return axios.get(`/users/${userId}/resources/${resourceId}/progress`);
  },
  
  updateResourceProgress(userId, resourceId, progressData) {
    return axios.put(`/users/${userId}/resources/${resourceId}/progress`, progressData);
  },
  
  // 课程进度相关方法
  getCourseProgress(userId, courseId) {
    return axios.get(`/users/${userId}/courses/${courseId}/progress`);
  },
  
  updateCourseProgress(userId, courseId, progressData) {
    return axios.put(`/users/${userId}/courses/${courseId}/progress`, progressData);
  }
};

// 活动相关API
export const activityAPI = {
  getActivities(query = '') {
    return axios.get(`/activities${query}`);
  },
  
  getUserActivities(userId) {
    return axios.get(`/users/${userId}/activities`);
  },
  
  getCourseActivities(courseId) {
    return axios.get(`/courses/${courseId}/activities`);
  },
  
  createActivity(activityData) {
    return axios.post('/activities', activityData);
  },
  
  updateActivity(id, activityData) {
    return axios.put(`/activities/${id}`, activityData);
  }
};

// 分析相关API
export const analyticsAPI = {
  getUserAnalytics(userId) {
    return axios.get(`/analytics/user/${userId}`);
  },
  
  getCourseAnalytics(courseId) {
    return axios.get(`/analytics/course/${courseId}`);
  },
  
  getSystemOverview() {
    return axios.get('/analytics/overview');
  }
}; 