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
  
  uploadAvatar(userId, file, onProgress) {
    const formData = new FormData();
    formData.append('avatar', file);
    
    return axios.post(`/users/${userId}/avatar`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: progressEvent => {
        if (onProgress) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      }
    });
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
  
  batchEnrollStudents(courseId, data) {
    return axios.post(`/courses/${courseId}/batch-enroll`, data);
  },
  
  searchNotEnrolledStudents(courseId, query = '') {
    return axios.get(`/courses/${courseId}/students/search?q=${query}`);
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
  },
  
  // 作业相关方法
  getCourseAssignments(courseId, userId = null) {
    let url = `/courses/${courseId}/assignments`;
    if (userId) {
      url += `?user_id=${userId}`;
    }
    return axios.get(url);
  },
  
  getCourseAssignment(courseId, assignmentId, userId = null) {
    let url = `/courses/${courseId}/assignments/${assignmentId}`;
    if (userId) {
      url += `?user_id=${userId}`;
    }
    return axios.get(url);
  },
  
  createCourseAssignment(courseId, assignmentData) {
    return axios.post(`/courses/${courseId}/assignments`, assignmentData);
  },
  
  updateCourseAssignment(courseId, assignmentId, assignmentData) {
    return axios.put(`/courses/${courseId}/assignments/${assignmentId}`, assignmentData);
  },
  
  deleteCourseAssignment(courseId, assignmentId) {
    return axios.delete(`/courses/${courseId}/assignments/${assignmentId}`);
  },
  
  // 作业提交相关方法
  getAssignmentSubmissions(courseId, assignmentId) {
    return axios.get(`/courses/${courseId}/assignments/${assignmentId}/submissions`);
  },
  
  getUserAssignmentSubmission(courseId, assignmentId, userId) {
    return axios.get(`/courses/${courseId}/assignments/${assignmentId}/submissions/${userId}`);
  },
  
  submitAssignment(courseId, assignmentId, submissionData) {
    return axios.post(`/courses/${courseId}/assignments/${assignmentId}/submissions`, submissionData);
  },
  
  updateSubmission(courseId, assignmentId, submissionId, submissionData) {
    return axios.put(`/courses/${courseId}/assignments/${assignmentId}/submissions/${submissionId}`, submissionData);
  },
  
  // 教师评分相关方法
  gradeAssignment(courseId, assignmentId, submissionId, gradeData) {
    return axios.post(`/courses/${courseId}/assignments/${assignmentId}/submissions/${submissionId}/grade`, gradeData);
  },
  
  // 课程讨论相关方法
  getCourseDiscussions(courseId) {
    return axios.get(`/courses/${courseId}/discussions`);
  },
  
  getCourseDiscussion(courseId, discussionId) {
    return axios.get(`/courses/${courseId}/discussions/${discussionId}`);
  },
  
  createCourseDiscussion(courseId, discussionData) {
    return axios.post(`/courses/${courseId}/discussions`, discussionData);
  },
  
  updateCourseDiscussion(courseId, discussionId, discussionData) {
    return axios.put(`/courses/${courseId}/discussions/${discussionId}`, discussionData);
  },
  
  deleteCourseDiscussion(courseId, discussionId) {
    return axios.delete(`/courses/${courseId}/discussions/${discussionId}`);
  },
  
  // 讨论回复相关方法
  createDiscussionReply(courseId, discussionId, replyData) {
    return axios.post(`/courses/${courseId}/discussions/${discussionId}/replies`, replyData);
  },
  
  updateDiscussionReply(replyId, replyData) {
    return axios.put(`/discussions/replies/${replyId}`, replyData);
  },
  
  deleteDiscussionReply(replyId) {
    return axios.delete(`/discussions/replies/${replyId}`);
  },
  
  // 讨论置顶
  toggleDiscussionPinned(courseId, discussionId) {
    return axios.post(`/courses/${courseId}/discussions/${discussionId}/toggle-pin`);
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
  },
  
  getStudentLearningAnalytics(userId) {
    return axios.get(`/analytics/student-learning/${userId}`);
  },
  
  getClassPerformanceAnalytics(courseId) {
    return axios.get(`/analytics/class-performance/${courseId}`);
  }
};

// 文件上传API
export const fileAPI = {
  uploadFile(file, onProgress) {
    const formData = new FormData();
    formData.append('file', file);
    
    return axios.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: progressEvent => {
        if (onProgress) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      }
    });
  }
};

// 成绩相关API
export const gradeAPI = {
  // 获取课程成绩设置
  getGradeSettings(courseId) {
    return axios.get(`/courses/${courseId}/grade-settings`);
  },
  
  // 更新课程成绩设置
  updateGradeSettings(courseId, settingsData) {
    return axios.put(`/courses/${courseId}/grade-settings`, settingsData);
  },
  
  // 获取学生在指定课程中的成绩
  getStudentGrade(courseId, studentId) {
    return axios.get(`/courses/${courseId}/students/${studentId}/grades`);
  },
  
  // 更新学生成绩
  updateStudentGrade(courseId, studentId, gradeData) {
    return axios.put(`/courses/${courseId}/students/${studentId}/grades`, gradeData);
  },
  
  // 获取课程所有学生的成绩
  getCourseGrades(courseId) {
    return axios.get(`/courses/${courseId}/grades`);
  },
  
  // 批量更新学生成绩
  batchUpdateGrades(courseId, gradesData) {
    return axios.post(`/courses/${courseId}/grades/batch`, gradesData);
  },
  
  // 获取用户在所有课程中的成绩
  getUserGrades(userId) {
    return axios.get(`/users/${userId}/grades`);
  }
}; 