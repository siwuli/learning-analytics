<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <h1>欢迎使用学习分析平台</h1>
        <p>您可以在这里查看您的学习进度和分析数据</p>
      </el-col>
    </el-row>

    <!-- 学生和教师的统计卡片 -->
    <el-row v-if="currentUser.role !== 'admin'" :gutter="20" class="dashboard-stats">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ enrolledCourses.length }}</div>
          <div class="stat-label">已加入课程</div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ userData.total_activities || 0 }}</div>
          <div class="stat-label">学习活动</div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ userData.completed_activities_percent || 0 }}%</div>
          <div class="stat-label">完成率</div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ formatTime(userData.total_duration || 0) }}</div>
          <div class="stat-label">学习时间</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 管理员的统计卡片 -->
    <el-row v-if="currentUser.role === 'admin'" :gutter="20" class="dashboard-stats">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ systemData.user_counts?.total || 0 }}</div>
          <div class="stat-label">用户总数</div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ systemData.course_counts?.total || 0 }}</div>
          <div class="stat-label">课程总数</div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ systemData.activity_counts?.total || 0 }}</div>
          <div class="stat-label">活动总数</div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ systemData.activity_counts?.completed || 0 }}</div>
          <div class="stat-label">已完成活动</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="dashboard-content">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>最近学习时间趋势</span>
            </div>
          </template>
          <div class="chart-container">
            <div v-if="loading" class="loading-container">
              <el-skeleton :rows="7" animated />
            </div>
            <div v-else-if="!timeChartData || timeChartData.length === 0" class="placeholder-chart">
              暂无学习时间数据
            </div>
            <div v-else class="chart-inner">
              <canvas ref="timeChartCanvas"></canvas>
            </div>
          </div>
        </el-card>
        
        <el-card class="activity-card">
          <template #header>
            <div class="card-header">
              <span>最近活动</span>
            </div>
          </template>
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>
          <div v-else-if="userData.recent_activities && userData.recent_activities.length === 0" class="empty-activities">
            暂无近期学习活动
          </div>
          <el-timeline v-else>
            <el-timeline-item
              v-for="activity in userData.recent_activities"
              :key="activity.id"
              :timestamp="formatDate(activity.created_at)"
              :type="getActivityType(activity.activity_type)"
            >
              {{ getActivityContent(activity) }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <!-- 管理员的附加统计卡片 -->
        <el-card v-if="currentUser.role === 'admin'" class="admin-stats-card">
          <template #header>
            <div class="card-header">
              <span>用户统计</span>
            </div>
          </template>
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="4" animated />
          </div>
          <div v-else class="admin-stats">
            <div class="admin-stat-item">
              <span class="stat-label">学生数:</span>
              <span class="stat-value">{{ systemData.user_counts?.students || 0 }}</span>
            </div>
            <div class="admin-stat-item">
              <span class="stat-label">教师数:</span>
              <span class="stat-value">{{ systemData.user_counts?.teachers || 0 }}</span>
            </div>
            <div class="admin-stat-item">
              <span class="stat-label">管理员数:</span>
              <span class="stat-value">{{ systemData.user_counts?.admins || 0 }}</span>
            </div>
            <div class="admin-stat-item">
              <span class="stat-label">活跃课程:</span>
              <span class="stat-value">{{ systemData.course_counts?.active || 0 }}</span>
            </div>
            <div class="admin-stat-item">
              <span class="stat-label">存档课程:</span>
              <span class="stat-value">{{ systemData.course_counts?.archived || 0 }}</span>
            </div>
          </div>
        </el-card>
        
        <el-card class="course-card">
          <template #header>
            <div class="card-header">
              <span>{{ currentUser.role === 'admin' ? '最活跃课程' : '我的课程' }}</span>
              <el-button class="button" text @click="goToCourses">查看全部</el-button>
            </div>
          </template>
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else-if="currentUser.role === 'admin' && (!systemData.active_courses || systemData.active_courses.length === 0)" class="empty-courses">
            暂无活跃课程数据
          </div>
          <div v-else-if="currentUser.role !== 'admin' && enrolledCourses.length === 0" class="empty-courses">
            您还没有加入任何课程
          </div>
          <div v-else-if="currentUser.role === 'admin'">
            <div v-for="course in systemData.active_courses" :key="course.course_id" class="course-item">
              <div class="course-title">{{ course.course_title }}</div>
              <div class="activity-count">
                <span>活动数: {{ course.activity_count }}</span>
              </div>
              <el-button size="small" type="primary" @click="goToCourseDetail(course.course_id)">
                查看
              </el-button>
            </div>
          </div>
          <div v-else>
            <div v-for="course in enrolledCourses" :key="course.id" class="course-item">
              <div class="course-title">{{ course.title }}</div>
              <div class="course-progress">
                <span>进度: {{ getCourseProgress(course.id) }}%</span>
                <el-progress :percentage="getCourseProgress(course.id)"></el-progress>
              </div>
            </div>
          </div>
        </el-card>
        
        <el-card class="activity-chart-card">
          <template #header>
            <div class="card-header">
              <span>学习活动类型分布</span>
            </div>
          </template>
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="4" animated />
          </div>
          <div v-else-if="!activityTypeData || Object.keys(activityTypeData).length === 0" class="placeholder-chart">
            暂无活动类型数据
          </div>
          <div v-else class="chart-container">
            <canvas ref="activityTypeCanvas"></canvas>
          </div>
        </el-card>
        
        <el-card class="reminder-card">
          <template #header>
            <div class="card-header">
              <span>待办事项</span>
            </div>
          </template>
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else-if="pendingAssignments.length === 0" class="empty-todos">
            暂无待办事项
          </div>
          <div v-else class="todo-list">
            <div v-for="assignment in pendingAssignments" :key="assignment.id" class="todo-item">
              <div class="todo-content">
                <i class="el-icon-document"></i>
                {{ assignment.title }}
              </div>
              <div v-if="currentUser.role === 'teacher' && assignment.ungraded_count" class="todo-count">
                {{ assignment.ungraded_count }}个待批改
              </div>
              <div class="todo-due">{{ formatDeadline(assignment.deadline) }}</div>
              <el-button size="small" type="primary" @click="goToAssignment(assignment.course_id, assignment.id)">
                查看
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { analyticsAPI, courseAPI, activityAPI } from '@/services/api'
import Chart from 'chart.js/auto'

export default {
  name: 'Dashboard',
  setup() {
    const store = useStore()
    const router = useRouter()
    const timeChartCanvas = ref(null)
    const activityTypeCanvas = ref(null)
    const timeChart = ref(null)
    const activityTypeChart = ref(null)
    
    const loading = ref(true)
    const userData = ref({})
    const enrolledCourses = ref([])
    const timeChartData = ref([])
    const activityTypeData = ref({})
    const pendingAssignments = ref([])
    const studentLearningData = ref({})
    const systemData = ref({})
    
    // 计算用户ID
    const currentUser = computed(() => store.state.auth.user)
    
    // 获取课程进度
    const getCourseProgress = (courseId) => {
      if (!userData.value.course_progress) return 0
      
      const courseProgress = userData.value.course_progress.find(cp => cp.course_id === courseId)
      return courseProgress ? Math.round(courseProgress.progress_percent) : 0
    }
    
    // 格式化时间
    const formatTime = (seconds) => {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      
      if (hours > 0) {
        return `${hours}小时${minutes > 0 ? minutes + '分钟' : ''}`
      } else {
        return `${minutes}分钟`
      }
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
    }
    
    // 格式化截止日期
    const formatDeadline = (dateString) => {
      const now = new Date()
      const deadline = new Date(dateString)
      const diffTime = deadline - now
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays < 0) {
        return '已逾期'
      } else if (diffDays === 0) {
        return '今天截止'
      } else if (diffDays === 1) {
        return '明天截止'
      } else if (diffDays < 7) {
        return `${diffDays}天后截止`
      } else {
        return formatDate(dateString) + ' 截止'
      }
    }
    
    // 获取活动类型对应的图标类型
    const getActivityType = (activityType) => {
      const typeMap = {
        'view': 'primary',
        'video': 'success',
        'download': 'info',
        'quiz': 'warning',
        'assignment': 'danger',
        'discussion': 'primary'
      }
      return typeMap[activityType] || 'info'
    }
    
    // 获取活动内容描述
    const getActivityContent = (activity) => {
      const typeTextMap = {
        'view': '查看了',
        'video': '观看了视频',
        'download': '下载了资料',
        'quiz': '完成了测验',
        'assignment': '提交了作业',
        'discussion': '参与了讨论'
      }
      
      let content = typeTextMap[activity.activity_type] || '参与了'
      
      if (activity.course && activity.course.title) {
        content += `《${activity.course.title}》`
      }
      
      if (activity.resource && activity.resource.title) {
        content += `的 ${activity.resource.title}`
      }
      
      return content
    }
    
    // 导航到课程列表
    const goToCourses = () => {
      router.push('/courses')
    }
    
    // 导航到课程详情
    const goToCourseDetail = (courseId) => {
      router.push(`/courses/${courseId}`)
    }
    
    // 导航到作业详情
    const goToAssignment = (courseId, assignmentId) => {
      router.push(`/courses/${courseId}/assignments/${assignmentId}`)
    }
    
    // 创建学习时间趋势图表
    const createTimeChart = () => {
      if (!timeChartCanvas.value || !timeChartData.value || timeChartData.value.length === 0) return
      
      const ctx = timeChartCanvas.value.getContext('2d')
      
      if (timeChart.value) {
        timeChart.value.destroy()
      }
      
      // 根据角色显示不同的标签和数据
      let labels, data, chartTitle
      
      if (currentUser.value.role === 'admin' || currentUser.value.role === 'teacher') {
        // 管理员和教师显示活动趋势
        labels = timeChartData.value.map(item => item.date)
        data = timeChartData.value.map(item => item.count)
        chartTitle = '活动数量'
      } else {
        // 学生显示学习时间趋势
        labels = timeChartData.value.map(item => item.date)
        data = timeChartData.value.map(item => Math.round(item.duration / 60)) // 转换为分钟
        chartTitle = '学习时长(分钟)'
      }
      
      timeChart.value = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: chartTitle,
            data: data,
            backgroundColor: 'rgba(64, 158, 255, 0.2)',
            borderColor: 'rgba(64, 158, 255, 1)',
            borderWidth: 2,
            pointBackgroundColor: 'rgba(64, 158, 255, 1)',
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: currentUser.value.role === 'student' ? '时长(分钟)' : '活动数量'
              }
            },
            x: {
              title: {
                display: true,
                text: '日期'
              }
            }
          }
        }
      })
    }
    
    // 创建活动类型分布图表
    const createActivityTypeChart = () => {
      if (!activityTypeCanvas.value || !activityTypeData.value || Object.keys(activityTypeData.value).length === 0) return
      
      const ctx = activityTypeCanvas.value.getContext('2d')
      
      if (activityTypeChart.value) {
        activityTypeChart.value.destroy()
      }
      
      const typeNames = {
        'view': '浏览资料',
        'video': '观看视频',
        'download': '下载资料',
        'quiz': '完成测验',
        'assignment': '提交作业',
        'discussion': '参与讨论'
      }
      
      const labels = Object.keys(activityTypeData.value).map(key => typeNames[key] || key)
      const data = Object.values(activityTypeData.value)
      
      const backgroundColors = [
        'rgba(64, 158, 255, 0.7)',
        'rgba(103, 194, 58, 0.7)',
        'rgba(245, 108, 108, 0.7)',
        'rgba(230, 162, 60, 0.7)',
        'rgba(144, 147, 153, 0.7)',
        'rgba(78, 110, 242, 0.7)'
      ]
      
      activityTypeChart.value = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
            data: data,
            backgroundColor: backgroundColors,
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      })
    }
    
    // 获取用户分析数据
    const fetchUserData = async () => {
      if (!currentUser.value || !currentUser.value.id) return
      
      try {
        const response = await analyticsAPI.getUserAnalytics(currentUser.value.id)
        userData.value = response.data
        
        // 计算完成率百分比
        if (userData.value.total_activities > 0) {
          userData.value.completed_activities_percent = Math.round(
            (userData.value.completed_activities / userData.value.total_activities) * 100
          )
        } else {
          userData.value.completed_activities_percent = 0
        }
      } catch (error) {
        console.error('获取用户分析数据失败', error)
      }
    }
    
    // 获取用户已加入的课程
    const fetchUserCourses = async () => {
      if (!currentUser.value || !currentUser.value.id) return
      
      try {
        const response = await courseAPI.getEnrolledCourses(currentUser.value.id)
        enrolledCourses.value = response.data.courses || []
      } catch (error) {
        console.error('获取用户课程失败', error)
      }
    }
    
    // 获取学生学习分析数据
    const fetchStudentLearningData = async () => {
      if (!currentUser.value || !currentUser.value.id) return
      
      try {
        // 只有学生角色才获取详细学习分析
        if (currentUser.value.role === 'student') {
          const response = await analyticsAPI.getStudentLearningAnalytics(currentUser.value.id)
          studentLearningData.value = response.data
          
          // 设置学习时间趋势数据
          timeChartData.value = studentLearningData.value.learning_time_trend || []
          
          // 设置活动类型分布数据
          activityTypeData.value = studentLearningData.value.activity_type_distribution || {}
          
          // 设置未完成作业
          pendingAssignments.value = studentLearningData.value.pending_assignments || []
        }
      } catch (error) {
        console.error('获取学生学习分析数据失败', error)
      }
    }
    
    // 获取系统概览数据（针对管理员和教师）
    const fetchSystemOverview = async () => {
      if (!currentUser.value) return
      
      // 只有管理员和教师才获取系统概览
      if (currentUser.value.role === 'admin' || currentUser.value.role === 'teacher') {
        try {
          const response = await analyticsAPI.getSystemOverview()
          systemData.value = response.data
          
          // 对于教师和管理员，显示不同的活动类型分布
          activityTypeData.value = systemData.value.activity_type_distribution || {}
          
          // 对于教师和管理员，使用活动趋势作为时间图表数据
          timeChartData.value = systemData.value.activity_trend || []
          
          // 获取教师负责的课程的待批改作业作为待办事项
          if (currentUser.value.role === 'teacher') {
            // 获取教师的课程
            const coursesResponse = await courseAPI.getCourses()
            const teacherCourses = coursesResponse.data.courses.filter(
              course => course.instructor_id === currentUser.value.id
            )
            
            // 获取每个课程的待批改作业
            const pendingAssignmentsList = []
            for (const course of teacherCourses) {
              try {
                const assignmentsResponse = await courseAPI.getCourseAssignments(course.id)
                const assignments = assignmentsResponse.data.assignments || []
                
                // 对每个作业，检查是否有未批改的提交
                for (const assignment of assignments) {
                  try {
                    const submissionsResponse = await courseAPI.getAssignmentSubmissions(course.id, assignment.id)
                    const submissions = submissionsResponse.data.submissions || []
                    
                    // 过滤出未批改的提交
                    const ungradedSubmissions = submissions.filter(sub => !sub.is_graded)
                    
                    if (ungradedSubmissions.length > 0) {
                      pendingAssignmentsList.push({
                        id: assignment.id,
                        title: `批改《${course.title}》的作业：${assignment.title}`,
                        course_id: course.id,
                        ungraded_count: ungradedSubmissions.length,
                        deadline: assignment.deadline
                      })
                    }
                  } catch (error) {
                    console.error(`获取课程 ${course.id} 作业 ${assignment.id} 的提交失败`, error)
                  }
                }
              } catch (error) {
                console.error(`获取课程 ${course.id} 的作业失败`, error)
              }
            }
            
            // 按未批改数量降序排序
            pendingAssignmentsList.sort((a, b) => b.ungraded_count - a.ungraded_count)
            pendingAssignments.value = pendingAssignmentsList
          }
        } catch (error) {
          console.error('获取系统概览数据失败', error)
        }
      }
    }
    
    // 加载所有数据
    const loadAllData = async () => {
      loading.value = true
      
      try {
        if (currentUser.value.role === 'admin') {
          // 管理员只需要获取系统概览数据
          await fetchSystemOverview()
        } else {
          // 其他角色获取用户数据和课程
          await fetchUserData()
          await fetchUserCourses()
          
          if (currentUser.value.role === 'student') {
            await fetchStudentLearningData()
          } else if (currentUser.value.role === 'teacher') {
            await fetchSystemOverview()
          }
        }
        
        // 创建图表
        setTimeout(() => {
          createTimeChart()
          createActivityTypeChart()
        }, 100)
      } catch (error) {
        console.error('加载仪表盘数据失败', error)
      } finally {
        loading.value = false
      }
    }
    
    onMounted(() => {
      if (currentUser.value && currentUser.value.id) {
        loadAllData()
      }
    })
    
    return {
      enrolledCourses,
      userData,
      systemData,
      loading,
      timeChartCanvas,
      activityTypeCanvas,
      timeChartData,
      activityTypeData,
      pendingAssignments,
      currentUser,
      formatTime,
      formatDate,
      formatDeadline,
      getActivityType,
      getActivityContent,
      getCourseProgress,
      goToCourses,
      goToCourseDetail,
      goToAssignment
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.dashboard-stats {
  margin-top: 20px;
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  border-radius: 8px;
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.dashboard-content {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
  position: relative;
}

.chart-inner {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.placeholder-chart {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #909399;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.activity-card, .activity-chart-card {
  margin-top: 20px;
}

.course-item, .todo-item {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.course-item:last-child, .todo-item:last-child {
  border-bottom: none;
}

.course-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.todo-content {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.todo-content i {
  margin-right: 8px;
}

.todo-due {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.todo-count {
  font-size: 12px;
  color: #F56C6C;
  margin-bottom: 5px;
}

.activity-count {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.reminder-card {
  margin-top: 20px;
}

.admin-stats-card {
  margin-bottom: 20px;
}

.admin-stats {
  padding: 5px 0;
}

.admin-stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #ebeef5;
}

.admin-stat-item:last-child {
  border-bottom: none;
}

.empty-courses, .empty-todos, .empty-activities {
  color: #909399;
  text-align: center;
  padding: 20px 0;
}

.loading-container {
  padding: 10px;
}

.todo-list {
  max-height: 250px;
  overflow-y: auto;
}
</style> 