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
  
  getCourseStudents(courseId) {
    return axios.get(`/courses/${courseId}/students`);
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