<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <h1>欢迎使用学习分析平台</h1>
        <p>您可以在这里查看您的学习进度和分析数据</p>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="dashboard-stats">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ enrolledCourses.length }}</div>
          <div class="stat-label">已加入课程</div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ totalActivities }}</div>
          <div class="stat-label">学习活动</div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ completedActivitiesPercent }}%</div>
          <div class="stat-label">完成率</div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ formatTime(totalLearningTime) }}</div>
          <div class="stat-label">学习时间</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="dashboard-content">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>最近学习活动</span>
            </div>
          </template>
          <div class="chart-container">
            <!-- 这里可以放置学习活动图表 -->
            <div class="placeholder-chart">学习活动图表将在这里显示</div>
          </div>
        </el-card>
        
        <el-card class="activity-card">
          <template #header>
            <div class="card-header">
              <span>最近活动</span>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in recentActivities"
              :key="index"
              :timestamp="activity.time"
              :type="activity.type"
            >
              {{ activity.content }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="course-card">
          <template #header>
            <div class="card-header">
              <span>我的课程</span>
              <el-button class="button" text>查看全部</el-button>
            </div>
          </template>
          <div v-if="enrolledCourses.length === 0" class="empty-courses">
            您还没有加入任何课程
          </div>
          <div v-else>
            <div v-for="course in enrolledCourses" :key="course.id" class="course-item">
              <div class="course-title">{{ course.title }}</div>
              <div class="course-progress">
                <span>进度: {{ course.progress }}%</span>
                <el-progress :percentage="course.progress"></el-progress>
              </div>
            </div>
          </div>
        </el-card>
        
        <el-card class="reminder-card">
          <template #header>
            <div class="card-header">
              <span>待办事项</span>
            </div>
          </template>
          <div v-if="todos.length === 0" class="empty-todos">
            暂无待办事项
          </div>
          <el-checkbox-group v-model="checkedTodos">
            <div v-for="todo in todos" :key="todo.id" class="todo-item">
              <el-checkbox :label="todo.id">{{ todo.content }}</el-checkbox>
              <div class="todo-due">{{ todo.dueDate }}</div>
            </div>
          </el-checkbox-group>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'Dashboard',
  setup() {
    const store = useStore()
    
    // 模拟数据
    const enrolledCourses = ref([
      { id: 1, title: '数据科学导论', progress: 75 },
      { id: 2, title: '机器学习基础', progress: 30 },
      { id: 3, title: 'Web开发实践', progress: 60 }
    ])
    
    const recentActivities = ref([
      { type: 'primary', content: '完成了《数据科学导论》的第5章测验', time: '2023-05-15 14:30' },
      { type: 'success', content: '开始学习《机器学习基础》课程', time: '2023-05-14 10:15' },
      { type: 'info', content: '提交了《Web开发实践》的项目作业', time: '2023-05-12 16:45' },
      { type: 'warning', content: '参与了《数据科学导论》的讨论', time: '2023-05-10 09:20' }
    ])
    
    const todos = ref([
      { id: 1, content: '完成机器学习基础的第3章测验', dueDate: '明天截止' },
      { id: 2, content: '提交Web开发实践的项目报告', dueDate: '3天后截止' },
      { id: 3, content: '参加数据科学导论的线上讨论', dueDate: '下周一' }
    ])
    
    const checkedTodos = ref([])
    
    // 计算属性
    const totalActivities = computed(() => 45) // 模拟数据
    const completedActivitiesPercent = computed(() => 65) // 模拟数据
    const totalLearningTime = computed(() => 3600 * 25) // 模拟数据：25小时
    
    // 格式化时间
    const formatTime = (seconds) => {
      const hours = Math.floor(seconds / 3600)
      return `${hours}小时`
    }
    
    // 模拟加载数据
    onMounted(() => {
      // 在实际应用中，这里应该调用API获取实际数据
      console.log('Dashboard mounted')
    })
    
    return {
      enrolledCourses,
      recentActivities,
      todos,
      checkedTodos,
      totalActivities,
      completedActivitiesPercent,
      totalLearningTime,
      formatTime
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

.activity-card {
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

.todo-due {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  margin-left: 24px;
}

.reminder-card {
  margin-top: 20px;
}

.empty-courses, .empty-todos {
  color: #909399;
  text-align: center;
  padding: 20px 0;
}
</style> 