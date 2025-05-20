<template>
  <div class="analytics-container">
    <h1>数据分析</h1>
    
    <el-tabs v-model="activeTab">
      <el-tab-pane label="系统概览" name="system">
        <div v-if="systemOverview" class="overview-section">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-title">总用户数</div>
                <div class="stat-value">{{ systemOverview.totalUsers }}</div>
                <div class="stat-trend">
                  <span>
                    <i class="el-icon-top" style="color: #67c23a"></i>
                    {{ systemOverview.userGrowthRate }}%
                  </span>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-title">总课程数</div>
                <div class="stat-value">{{ systemOverview.totalCourses }}</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-title">总活动数</div>
                <div class="stat-value">{{ systemOverview.totalActivities }}</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-title">平均完成率</div>
                <div class="stat-value">{{ systemOverview.avgCompletionRate }}%</div>
              </el-card>
            </el-col>
          </el-row>
          
          <div class="chart-section">
            <h3>用户活跃度趋势</h3>
            <div class="chart-container">
              <!-- 这里可以插入图表组件 -->
              <div class="placeholder-chart">图表加载中...</div>
            </div>
          </div>
        </div>
        <div v-else-if="loading" class="loading-section">
          <el-skeleton :rows="10" animated />
        </div>
        <div v-else class="error-section">
          <el-empty description="暂无数据" />
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="学生分析" name="students" v-if="isTeacher">
        <div class="student-analytics">
          <h3>学生学习情况分析</h3>
          <div class="placeholder-chart">学生数据分析图表加载中...</div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="课程分析" name="courses" v-if="isTeacher">
        <div class="course-analytics">
          <h3>课程数据分析</h3>
          <div class="placeholder-chart">课程数据分析图表加载中...</div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="个人学习分析" name="personal" v-if="!isTeacher">
        <div class="personal-analytics">
          <h3>我的学习情况</h3>
          <div class="placeholder-chart">个人学习数据分析图表加载中...</div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'

export default {
  name: 'Analytics',
  setup() {
    const store = useStore()
    const activeTab = ref('system')
    const loading = ref(true)
    
    // 从store获取数据
    const systemOverview = computed(() => store.getters['analytics/getSystemOverview'])
    const userAnalytics = computed(() => store.getters['analytics/getUserAnalytics'])
    const courseAnalytics = computed(() => store.getters['analytics/getCourseAnalytics'])
    
    // 是否为教师
    const isTeacher = computed(() => {
      const user = store.state.auth.user
      return user && user.role === 'teacher'
    })
    
    // 加载数据
    const loadSystemOverview = async () => {
      try {
        loading.value = true
        await store.dispatch('analytics/fetchSystemOverview')
      } catch (error) {
        ElMessage.error('获取系统概览数据失败')
      } finally {
        loading.value = false
      }
    }
    
    onMounted(() => {
      loadSystemOverview()
    })
    
    return {
      activeTab,
      loading,
      systemOverview,
      userAnalytics,
      courseAnalytics,
      isTeacher
    }
  }
}
</script>

<style scoped>
.analytics-container {
  padding: 20px;
}

.overview-section {
  margin-top: 20px;
}

.stat-card {
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.stat-title {
  font-size: 16px;
  color: #909399;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-trend {
  margin-top: 10px;
  font-size: 14px;
}

.chart-section {
  margin-top: 30px;
}

.chart-container {
  margin-top: 15px;
  height: 350px;
}

.placeholder-chart {
  width: 100%;
  height: 350px;
  background-color: #f5f7fa;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #909399;
  border-radius: 4px;
}

.loading-section {
  padding: 20px;
}

.error-section {
  margin-top: 40px;
}

.student-analytics,
.course-analytics,
.personal-analytics {
  margin-top: 20px;
}
</style> 