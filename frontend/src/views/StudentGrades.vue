<template>
  <div class="grades-container">
    <h1>我的成绩</h1>
    
    <div v-loading="loading" class="grades-content">
      <el-empty v-if="!userGrades.length" description="暂无课程成绩记录" />
      
      <div v-else class="grades-list">
        <el-card v-for="grade in userGrades" :key="grade.course_id" class="grade-card">
          <template #header>
            <div class="card-header">
              <span class="course-title">{{ grade.course.title }}</span>
              <el-tag 
                :type="getGradeTagType(grade.total_score)" 
                effect="plain"
              >
                {{ formatTotalScore(grade.total_score) }}
              </el-tag>
            </div>
          </template>
          
          <div class="grade-details">
            <div class="grade-item">
              <span class="label">平时成绩 ({{ grade.settings.regular_grade_weight }}%)</span>
              <span class="value">{{ formatScore(grade.regular_grade) }}</span>
            </div>
            
            <div class="grade-item">
              <span class="label">期末成绩 ({{ grade.settings.final_exam_weight }}%)</span>
              <span class="value">{{ formatScore(grade.final_exam_score) }}</span>
            </div>
            
            <div class="grade-item total">
              <span class="label">总评成绩</span>
              <span class="value">{{ formatScore(grade.total_score) }}</span>
            </div>
            
            <div v-if="grade.comment" class="comment">
              <div class="comment-title">教师评语:</div>
              <div class="comment-content">{{ grade.comment }}</div>
            </div>
          </div>
          
          <div class="grade-footer">
            <span class="instructor">授课教师: {{ grade.course.instructor_name || '未知' }}</span>
            <router-link :to="`/courses/${grade.course_id}`">
              <el-button size="small" type="primary">查看课程</el-button>
            </router-link>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'

export default {
  name: 'StudentGrades',
  setup() {
    const store = useStore()
    
    // 从store获取数据
    const loading = computed(() => store.state.grades.loading)
    const userGrades = computed(() => store.state.grades.userGrades)
    const userId = computed(() => store.state.auth.user?.id)
    
    // 格式化成绩
    const formatScore = (score) => {
      if (score === null || score === undefined) return '未评分'
      return parseFloat(score).toFixed(1)
    }
    
    // 格式化总成绩，添加等级
    const formatTotalScore = (score) => {
      if (score === null || score === undefined) return '未评分'
      const numScore = parseFloat(score).toFixed(1)
      let grade = ''
      
      if (score >= 90) grade = 'A'
      else if (score >= 80) grade = 'B'
      else if (score >= 70) grade = 'C'
      else if (score >= 60) grade = 'D'
      else grade = 'F'
      
      return `${numScore} (${grade})`
    }
    
    // 获取成绩标签类型
    const getGradeTagType = (score) => {
      if (score === null || score === undefined) return 'info'
      if (score >= 90) return 'success'
      if (score >= 80) return 'primary'
      if (score >= 70) return 'warning'
      if (score >= 60) return ''
      return 'danger'
    }
    
    // 获取成绩数据
    const fetchGrades = async () => {
      if (!userId.value) return
      
      try {
        await store.dispatch('grades/fetchUserGrades', userId.value)
      } catch (error) {
        ElMessage.error('获取成绩数据失败: ' + error.message)
      }
    }
    
    // 生命周期钩子
    onMounted(() => {
      fetchGrades()
    })
    
    return {
      loading,
      userGrades,
      formatScore,
      formatTotalScore,
      getGradeTagType
    }
  }
}
</script>

<style scoped>
.grades-container {
  padding: 20px;
}

.grades-content {
  margin-top: 20px;
}

.grades-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.grade-card {
  height: 100%;
  transition: all 0.3s;
}

.grade-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.course-title {
  font-size: 16px;
  font-weight: bold;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 220px;
}

.grade-details {
  margin-bottom: 20px;
}

.grade-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  padding: 8px 0;
  border-bottom: 1px dashed #eee;
}

.grade-item.total {
  font-weight: bold;
  color: #409EFF;
  border-bottom: none;
  margin-top: 10px;
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
}

.label {
  color: #606266;
}

.value {
  font-weight: 500;
}

.comment {
  margin-top: 15px;
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
}

.comment-title {
  font-weight: bold;
  margin-bottom: 5px;
  color: #606266;
}

.comment-content {
  color: #333;
  white-space: pre-line;
}

.grade-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.instructor {
  color: #909399;
  font-size: 13px;
}
</style> 