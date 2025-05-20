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
              <v-chart :option="activityTrendOptions" autoresize />
            </div>
          </div>

          <el-row :gutter="20" class="mt-20">
            <el-col :span="12">
              <div class="chart-section">
                <h3>活动类型分布</h3>
                <div class="chart-container">
                  <v-chart :option="activityTypeOptions" autoresize />
                </div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="chart-section">
                <h3>最活跃课程</h3>
                <div class="chart-container">
                  <v-chart :option="activeCoursesOptions" autoresize />
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
        <div v-else-if="loading" class="loading-section">
          <el-skeleton :rows="10" animated />
        </div>
        <div v-else class="error-section">
          <el-empty description="暂无数据" />
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="学生分析" name="students" v-if="isTeacher">
        <div class="student-filter">
          <el-select v-model="selectedCourseId" placeholder="选择课程" @change="handleCourseChange">
            <el-option v-for="course in courses" :key="course.id" :label="course.title" :value="course.id"></el-option>
          </el-select>
        </div>

        <div v-if="classPerformanceAnalytics && selectedCourseId" class="class-performance">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-title">学生数量</div>
                <div class="stat-value">{{ classPerformanceAnalytics.studentCount }}</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-title">平均完成率</div>
                <div class="stat-value">{{ Math.round(classPerformanceAnalytics.completionStats.avg) }}%</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-title">平均得分</div>
                <div class="stat-value">{{ Math.round(classPerformanceAnalytics.scoreStats.avg) }}</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-title">最高得分</div>
                <div class="stat-value">{{ Math.round(classPerformanceAnalytics.scoreStats.max) }}</div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="20" class="mt-20">
            <el-col :span="12">
              <div class="chart-section">
                <h3>完成率分布</h3>
                <div class="chart-container">
                  <v-chart :option="completionDistributionOptions" autoresize />
                </div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="chart-section">
                <h3>成绩分布</h3>
                <div class="chart-container">
                  <v-chart :option="scoreDistributionOptions" autoresize />
                </div>
              </div>
            </el-col>
          </el-row>

          <div class="chart-section mt-20">
            <h3>学生参与度排名</h3>
            <el-table :data="classPerformanceAnalytics.engagementRanking" border style="width: 100%">
              <el-table-column prop="username" label="学生" width="180"></el-table-column>
              <el-table-column prop="activity_count" label="活动数量" width="180"></el-table-column>
              <el-table-column prop="completion_rate" label="完成率">
                <template #default="scope">
                  {{ Math.round(scope.row.completion_rate) }}%
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div class="chart-section mt-20">
            <h3>学生成绩排名</h3>
            <el-table :data="classPerformanceAnalytics.performanceRanking" border style="width: 100%">
              <el-table-column prop="username" label="学生" width="180"></el-table-column>
              <el-table-column prop="avg_score" label="平均得分" width="180">
                <template #default="scope">
                  {{ Math.round(scope.row.avg_score) }}
                </template>
              </el-table-column>
              <el-table-column prop="progress_percent" label="进度">
                <template #default="scope">
                  {{ Math.round(scope.row.progress_percent) }}%
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
        <div v-else-if="loading" class="loading-section">
          <el-skeleton :rows="10" animated />
        </div>
        <div v-else class="select-course-prompt">
          <el-empty description="请选择一个课程查看学生分析数据" />
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="课程分析" name="courses" v-if="isTeacher">
        <div class="course-filter">
          <el-select v-model="selectedAnalyticsCourseId" placeholder="选择课程" @change="handleAnalyticsCourseChange">
            <el-option v-for="course in courses" :key="course.id" :label="course.title" :value="course.id"></el-option>
          </el-select>
        </div>

        <div v-if="courseAnalytics && selectedAnalyticsCourseId" class="course-analytics">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-title">学生数量</div>
                <div class="stat-value">{{ courseAnalytics.studentCount }}</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-title">活动数量</div>
                <div class="stat-value">{{ courseAnalytics.activityCount }}</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-title">完成率</div>
                <div class="stat-value">{{ Math.round(courseAnalytics.completionRate) }}%</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-title">平均得分</div>
                <div class="stat-value">{{ Math.round(courseAnalytics.avgScore) }}</div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="20" class="mt-20">
            <el-col :span="12">
              <div class="chart-section">
                <h3>活动类型分布</h3>
                <div class="chart-container">
                  <v-chart :option="courseActivityTypeOptions" autoresize />
                </div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="chart-section">
                <h3>进度分布</h3>
                <div class="chart-container">
                  <v-chart :option="courseProgressOptions" autoresize />
                </div>
              </div>
            </el-col>
          </el-row>

          <div class="chart-section mt-20">
            <h3>作业完成情况</h3>
            <el-table :data="courseAnalytics.assignmentStats" border style="width: 100%">
              <el-table-column prop="title" label="作业名称" width="300"></el-table-column>
              <el-table-column prop="completion_rate" label="完成率" width="180">
                <template #default="scope">
                  {{ Math.round(scope.row.completion_rate) }}%
                </template>
              </el-table-column>
              <el-table-column prop="avg_score" label="平均得分">
                <template #default="scope">
                  {{ Math.round(scope.row.avg_score) }}
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div class="chart-section mt-20">
            <h3>最活跃的学生</h3>
            <el-table :data="courseAnalytics.activeStudents" border style="width: 100%">
              <el-table-column prop="username" label="学生" width="250"></el-table-column>
              <el-table-column prop="activity_count" label="活动数量"></el-table-column>
            </el-table>
          </div>
        </div>
        <div v-else-if="loading" class="loading-section">
          <el-skeleton :rows="10" animated />
        </div>
        <div v-else class="select-course-prompt">
          <el-empty description="请选择一个课程查看课程分析数据" />
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="个人学习分析" name="personal" v-if="!isTeacher">
        <div v-if="studentLearningAnalytics" class="personal-analytics">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card class="stat-card">
                <div class="stat-title">待完成作业</div>
                <div class="stat-value">{{ studentLearningAnalytics.pendingAssignments.length }}</div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="stat-card">
                <div class="stat-title">活动类型</div>
                <div class="stat-value">{{ Object.keys(studentLearningAnalytics.activityTypeDistribution).length }}</div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="stat-card">
                <div class="stat-title">总学习课程</div>
                <div class="stat-value">{{ studentLearningAnalytics.scoreComparisons.length }}</div>
              </el-card>
            </el-col>
          </el-row>

          <div class="chart-section mt-20">
            <h3>学习时间趋势（近30天）</h3>
            <div class="chart-container">
              <v-chart :option="learningTimeTrendOptions" autoresize />
            </div>
          </div>

          <el-row :gutter="20" class="mt-20">
            <el-col :span="12">
              <div class="chart-section">
                <h3>学习活动类型分布</h3>
                <div class="chart-container">
                  <v-chart :option="learningActivityTypeOptions" autoresize />
                </div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="chart-section">
                <h3>学习时长分布</h3>
                <div class="chart-container">
                  <v-chart :option="learningDurationOptions" autoresize />
                </div>
              </div>
            </el-col>
          </el-row>

          <div class="chart-section mt-20">
            <h3>每日学习时段分布</h3>
            <div class="chart-container">
              <v-chart :option="hourlyDistributionOptions" autoresize />
            </div>
          </div>

          <div class="chart-section mt-20">
            <h3>课程得分对比</h3>
            <el-table :data="studentLearningAnalytics.scoreComparisons" border style="width: 100%">
              <el-table-column prop="course_title" label="课程" width="250"></el-table-column>
              <el-table-column prop="student_avg_score" label="我的平均分" width="150">
                <template #default="scope">
                  {{ Math.round(scope.row.student_avg_score) }}
                </template>
              </el-table-column>
              <el-table-column prop="course_avg_score" label="课程平均分" width="150">
                <template #default="scope">
                  {{ Math.round(scope.row.course_avg_score) }}
                </template>
              </el-table-column>
              <el-table-column label="对比">
                <template #default="scope">
                  <span :style="{color: scope.row.student_avg_score >= scope.row.course_avg_score ? '#67c23a' : '#f56c6c'}">
                    {{ scope.row.student_avg_score >= scope.row.course_avg_score ? '高于平均' : '低于平均' }}
                    {{ Math.abs(Math.round(scope.row.student_avg_score - scope.row.course_avg_score)) }} 分
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div class="chart-section mt-20">
            <h3>待完成作业</h3>
            <el-table :data="studentLearningAnalytics.pendingAssignments" border style="width: 100%">
              <el-table-column prop="title" label="作业名称" width="250"></el-table-column>
              <el-table-column prop="course_title" label="所属课程" width="250"></el-table-column>
              <el-table-column prop="due_date" label="截止日期">
                <template #default="scope">
                  {{ formatDate(scope.row.due_date) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
        <div v-else-if="loading" class="loading-section">
          <el-skeleton :rows="10" animated />
        </div>
        <div v-else class="error-section">
          <el-empty description="暂无个人学习数据" />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'

export default {
  name: 'Analytics',
  setup() {
    const store = useStore()
    const activeTab = ref('system')
    const loading = ref(true)
    const selectedCourseId = ref(null)
    const selectedAnalyticsCourseId = ref(null)
    const courses = ref([])
    
    // 从store获取数据
    const systemOverview = computed(() => store.getters['analytics/getSystemOverview'])
    const userAnalytics = computed(() => store.getters['analytics/getUserAnalytics'])
    const courseAnalytics = computed(() => store.getters['analytics/getCourseAnalytics'])
    const studentLearningAnalytics = computed(() => store.getters['analytics/getStudentLearningAnalytics'])
    const classPerformanceAnalytics = computed(() => store.getters['analytics/getClassPerformanceAnalytics'])
    
    // 是否为教师
    const isTeacher = computed(() => {
      const user = store.state.auth.user
      return user && user.role === 'teacher'
    })

    const currentUserId = computed(() => {
      return store.state.auth.user?.id
    })
    
    // 加载数据
    const loadSystemOverview = async () => {
      try {
        loading.value = true
        await store.dispatch('analytics/fetchSystemOverview')
      } catch (error) {
        ElMessage.error('获取系统概览数据失败')
        console.error(error)
      } finally {
        loading.value = false
      }
    }

    const loadCourses = async () => {
      try {
        const response = await store.dispatch('courses/fetchCourses')
        courses.value = response
      } catch (error) {
        ElMessage.error('获取课程列表失败')
        console.error(error)
      }
    }

    const loadStudentLearningAnalytics = async () => {
      if (!currentUserId.value) return
      
      try {
        loading.value = true
        await store.dispatch('analytics/fetchStudentLearningAnalytics', currentUserId.value)
      } catch (error) {
        ElMessage.error('获取个人学习数据失败')
        console.error(error)
      } finally {
        loading.value = false
      }
    }

    const handleCourseChange = async () => {
      if (!selectedCourseId.value) return
      
      try {
        loading.value = true
        await store.dispatch('analytics/fetchClassPerformanceAnalytics', selectedCourseId.value)
      } catch (error) {
        ElMessage.error('获取班级表现数据失败')
        console.error(error)
      } finally {
        loading.value = false
      }
    }

    const handleAnalyticsCourseChange = async () => {
      if (!selectedAnalyticsCourseId.value) return
      
      try {
        loading.value = true
        await store.dispatch('analytics/fetchCourseAnalytics', selectedAnalyticsCourseId.value)
      } catch (error) {
        ElMessage.error('获取课程分析数据失败')
        console.error(error)
      } finally {
        loading.value = false
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return '无日期'
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', { 
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    // 图表配置
    const activityTrendOptions = computed(() => {
      if (!systemOverview.value?.activityTrend) return {}
      
      const data = systemOverview.value.activityTrend
      const xData = data.map(item => item.date)
      const yData = data.map(item => item.count)
      
      return {
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: xData
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '活动数量',
            type: 'line',
            smooth: true,
            data: yData,
            areaStyle: {}
          }
        ]
      }
    })

    const activityTypeOptions = computed(() => {
      if (!systemOverview.value?.activityTypeDistribution) return {}
      
      const data = []
      Object.entries(systemOverview.value.activityTypeDistribution).forEach(([key, value]) => {
        data.push({ name: key, value: value })
      })
      
      return {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'center'
        },
        series: [
          {
            name: '活动类型',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: data
          }
        ]
      }
    })

    const activeCoursesOptions = computed(() => {
      if (!systemOverview.value?.activeCourses) return {}
      
      const data = systemOverview.value.activeCourses
      const courseNames = data.map(item => item.course_title)
      const activityCounts = data.map(item => item.activity_count)
      
      return {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        xAxis: {
          type: 'value'
        },
        yAxis: {
          type: 'category',
          data: courseNames,
          axisLabel: {
            width: 100,
            overflow: 'truncate'
          }
        },
        series: [
          {
            name: '活动数量',
            type: 'bar',
            data: activityCounts
          }
        ]
      }
    })

    // 班级表现分析图表
    const completionDistributionOptions = computed(() => {
      if (!classPerformanceAnalytics.value?.completionDistribution) return {}
      
      const data = []
      Object.entries(classPerformanceAnalytics.value.completionDistribution).forEach(([key, value]) => {
        data.push({ name: key, value: value })
      })
      
      return {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'center'
        },
        series: [
          {
            name: '完成率分布',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: data
          }
        ]
      }
    })

    const scoreDistributionOptions = computed(() => {
      if (!classPerformanceAnalytics.value?.scoreDistribution) return {}
      
      const data = []
      Object.entries(classPerformanceAnalytics.value.scoreDistribution).forEach(([key, value]) => {
        data.push({ name: key, value: value })
      })
      
      return {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'center'
        },
        series: [
          {
            name: '成绩分布',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: data
          }
        ]
      }
    })

    // 课程分析图表
    const courseActivityTypeOptions = computed(() => {
      if (!courseAnalytics.value?.activityTypes) return {}
      
      const data = []
      Object.entries(courseAnalytics.value.activityTypes).forEach(([key, value]) => {
        data.push({ name: key, value: value })
      })
      
      return {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'center'
        },
        series: [
          {
            name: '活动类型',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: data
          }
        ]
      }
    })

    const courseProgressOptions = computed(() => {
      if (!courseAnalytics.value?.progressDistribution) return {}
      
      const data = []
      Object.entries(courseAnalytics.value.progressDistribution).forEach(([key, value]) => {
        data.push({ name: key, value: value })
      })
      
      return {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'center'
        },
        series: [
          {
            name: '进度分布',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: data
          }
        ]
      }
    })

    // 个人学习分析图表
    const learningTimeTrendOptions = computed(() => {
      if (!studentLearningAnalytics.value?.learningTimeTrend) return {}
      
      const data = studentLearningAnalytics.value.learningTimeTrend
      const xData = data.map(item => item.date)
      const yData = data.map(item => Math.round(item.duration / 60)) // 转为分钟
      
      return {
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: xData
        },
        yAxis: {
          type: 'value',
          name: '分钟'
        },
        series: [
          {
            name: '学习时长',
            type: 'line',
            smooth: true,
            data: yData,
            areaStyle: {}
          }
        ]
      }
    })

    const learningActivityTypeOptions = computed(() => {
      if (!studentLearningAnalytics.value?.activityTypeDistribution) return {}
      
      const data = []
      Object.entries(studentLearningAnalytics.value.activityTypeDistribution).forEach(([key, value]) => {
        data.push({ name: key, value: value })
      })
      
      return {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'center'
        },
        series: [
          {
            name: '活动类型',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: data
          }
        ]
      }
    })

    const learningDurationOptions = computed(() => {
      if (!studentLearningAnalytics.value?.durationDistribution) return {}
      
      const data = []
      Object.entries(studentLearningAnalytics.value.durationDistribution).forEach(([key, value]) => {
        data.push({ name: key, value: value })
      })
      
      return {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'center'
        },
        series: [
          {
            name: '学习时长分布',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: data
          }
        ]
      }
    })

    const hourlyDistributionOptions = computed(() => {
      if (!studentLearningAnalytics.value?.hourlyDistribution) return {}
      
      const hours = []
      const counts = []
      
      for (let i = 0; i < 24; i++) {
        hours.push(`${i}点`)
        counts.push(studentLearningAnalytics.value.hourlyDistribution[i] || 0)
      }
      
      return {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        xAxis: {
          type: 'category',
          data: hours
        },
        yAxis: {
          type: 'value',
          name: '活动数'
        },
        series: [
          {
            name: '活动数量',
            type: 'bar',
            data: counts
          }
        ]
      }
    })

    // 根据激活的标签页加载相应数据
    watch(activeTab, (newTab) => {
      if (newTab === 'system') {
        loadSystemOverview()
      } else if (newTab === 'personal' && !isTeacher.value) {
        loadStudentLearningAnalytics()
      } else if (newTab === 'students' || newTab === 'courses') {
        loadCourses()
      }
    })
    
    onMounted(() => {
      loadSystemOverview()
      if (!isTeacher.value) {
        loadStudentLearningAnalytics()
      }
      loadCourses()
    })
    
    return {
      activeTab,
      loading,
      systemOverview,
      userAnalytics,
      courseAnalytics,
      studentLearningAnalytics,
      classPerformanceAnalytics,
      isTeacher,
      courses,
      selectedCourseId,
      selectedAnalyticsCourseId,
      handleCourseChange,
      handleAnalyticsCourseChange,
      formatDate,
      // 图表选项
      activityTrendOptions,
      activityTypeOptions,
      activeCoursesOptions,
      completionDistributionOptions,
      scoreDistributionOptions,
      courseActivityTypeOptions,
      courseProgressOptions,
      learningTimeTrendOptions,
      learningActivityTypeOptions,
      learningDurationOptions,
      hourlyDistributionOptions
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
  background-color: #ffffff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
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

.course-filter,
.student-filter {
  margin-bottom: 20px;
}

.mt-20 {
  margin-top: 20px;
}

.select-course-prompt {
  margin-top: 100px;
  text-align: center;
}

.el-table {
  margin-top: 15px;
}
</style> 