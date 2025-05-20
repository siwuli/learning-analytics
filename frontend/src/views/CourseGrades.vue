<template>
  <div class="grades-container">
    <h1>课程成绩管理</h1>
    
    <div v-if="currentCourse" class="course-info">
      <h2>{{ currentCourse.title }}</h2>
      <p>{{ currentCourse.description }}</p>
    </div>
    
    <div class="settings-card">
      <h3>成绩设置</h3>
      <el-form :model="gradeSettings" label-width="120px">
        <el-form-item label="期末成绩比重">
          <el-input-number 
            v-model="gradeSettings.final_exam_weight" 
            :min="0" 
            :max="100" 
            :step="5"
            @change="updateRegularWeight"
          />
          <span class="weight-label">{{ gradeSettings.final_exam_weight }}%</span>
        </el-form-item>
        
        <el-form-item label="平时成绩比重">
          <el-input-number 
            v-model="gradeSettings.regular_grade_weight" 
            :min="0" 
            :max="100" 
            :step="5"
            @change="updateFinalWeight"
          />
          <span class="weight-label">{{ gradeSettings.regular_grade_weight }}%</span>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="saveGradeSettings" :loading="saving">保存设置</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <div class="students-grades">
      <h3>学生成绩列表</h3>
      
      <div class="table-actions">
        <el-button type="primary" @click="saveAllGrades" :loading="savingGrades">保存所有更改</el-button>
        <el-button @click="downloadGrades">导出成绩表</el-button>
      </div>
      
      <el-table 
        v-loading="loading" 
        :data="courseGrades"
        style="width: 100%"
        border
      >
        <el-table-column prop="student.username" label="学生姓名" width="150"></el-table-column>
        <el-table-column prop="student.email" label="邮箱" width="220"></el-table-column>
        <el-table-column label="平时成绩" width="150">
          <template #default="scope">
            <el-input-number 
              v-model="scope.row.regular_grade" 
              :min="0" 
              :max="100" 
              :precision="1"
              :step="5"
              controls-position="right"
              size="small"
              @change="calcTotalScore(scope.row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="期末成绩" width="150">
          <template #default="scope">
            <el-input-number 
              v-model="scope.row.final_exam_score" 
              :min="0" 
              :max="100" 
              :precision="1"
              :step="5"
              controls-position="right"
              size="small"
              @change="calcTotalScore(scope.row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="总评成绩" width="120">
          <template #default="scope">
            <span>{{ formatScore(scope.row.total_score) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="评语">
          <template #default="scope">
            <el-input 
              v-model="scope.row.comment" 
              type="textarea" 
              :rows="1"
              placeholder="教师评语"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="saveStudentGrade(scope.row)"
              :loading="savingStudentId === scope.row.user_id"
            >保存</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'CourseGrades',
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    
    // 状态
    const loading = computed(() => store.state.grades.loading)
    const courseId = computed(() => parseInt(route.params.id))
    const currentCourse = ref(null)
    const saving = ref(false)
    const savingGrades = ref(false)
    const savingStudentId = ref(null)
    
    // 成绩设置
    const gradeSettings = reactive({
      final_exam_weight: 60,
      regular_grade_weight: 40
    })
    
    // 成绩列表
    const courseGrades = computed(() => {
      return store.state.grades.courseGrades.map(grade => ({
        ...grade,
        regular_grade: grade.regular_grade || 0,
        final_exam_score: grade.final_exam_score || 0
      }))
    })
    
    // 方法
    const fetchData = async () => {
      try {
        // 获取课程信息
        const course = await store.dispatch('courses/fetchCourse', courseId.value)
        currentCourse.value = course
        
        // 获取课程成绩信息
        const gradeData = await store.dispatch('grades/fetchCourseGrades', courseId.value)
        
        // 更新成绩设置表单
        Object.assign(gradeSettings, gradeData.settings)
      } catch (error) {
        ElMessage.error('获取课程成绩数据失败: ' + error.message)
      }
    }
    
    const updateRegularWeight = (val) => {
      gradeSettings.regular_grade_weight = 100 - val
    }
    
    const updateFinalWeight = (val) => {
      gradeSettings.final_exam_weight = 100 - val
    }
    
    const saveGradeSettings = async () => {
      try {
        saving.value = true
        
        // 验证权重总和
        const totalWeight = gradeSettings.final_exam_weight + gradeSettings.regular_grade_weight
        if (Math.abs(totalWeight - 100) > 0.01) {
          ElMessage.warning('成绩权重总和必须为100%')
          return
        }
        
        // 保存成绩设置
        await store.dispatch('grades/updateGradeSettings', {
          courseId: courseId.value,
          settingsData: {
            final_exam_weight: gradeSettings.final_exam_weight,
            regular_grade_weight: gradeSettings.regular_grade_weight
          }
        })
        
        ElMessage.success('成绩设置已保存')
        
        // 更新所有学生的总评成绩
        courseGrades.value.forEach(grade => {
          calcTotalScore(grade)
        })
      } catch (error) {
        ElMessage.error('保存成绩设置失败: ' + error.message)
      } finally {
        saving.value = false
      }
    }
    
    const calcTotalScore = (grade) => {
      if (grade.final_exam_score != null && grade.regular_grade != null) {
        const finalWeight = gradeSettings.final_exam_weight / 100
        const regularWeight = gradeSettings.regular_grade_weight / 100
        
        grade.total_score = (grade.final_exam_score * finalWeight) + (grade.regular_grade * regularWeight)
      }
      return grade
    }
    
    const saveStudentGrade = async (grade) => {
      try {
        savingStudentId.value = grade.user_id
        
        await store.dispatch('grades/updateStudentGrade', {
          courseId: courseId.value,
          studentId: grade.user_id,
          gradeData: {
            final_exam_score: grade.final_exam_score,
            regular_grade: grade.regular_grade,
            comment: grade.comment
          }
        })
        
        ElMessage.success('学生成绩已保存')
      } catch (error) {
        ElMessage.error('保存学生成绩失败: ' + error.message)
      } finally {
        savingStudentId.value = null
      }
    }
    
    const saveAllGrades = async () => {
      try {
        savingGrades.value = true
        
        const gradesData = {
          grades: courseGrades.value.map(grade => ({
            user_id: grade.user_id,
            final_exam_score: grade.final_exam_score,
            regular_grade: grade.regular_grade,
            comment: grade.comment
          }))
        }
        
        await store.dispatch('grades/batchUpdateGrades', {
          courseId: courseId.value,
          gradesData
        })
        
        ElMessage.success('所有学生成绩已保存')
      } catch (error) {
        ElMessage.error('批量保存成绩失败: ' + error.message)
      } finally {
        savingGrades.value = false
      }
    }
    
    const downloadGrades = () => {
      // 准备导出数据
      const csvContent = generateCsvContent()
      
      // 创建下载链接
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.setAttribute('href', url)
      link.setAttribute('download', `${currentCourse.value.title}_成绩表.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
    
    const generateCsvContent = () => {
      // CSV表头
      let csvContent = '\uFEFF' // UTF-8 BOM，解决中文乱码
      csvContent += '学生姓名,邮箱,平时成绩,期末成绩,总评成绩,评语\n'
      
      // 添加数据行
      courseGrades.value.forEach(grade => {
        const row = [
          grade.student.username,
          grade.student.email,
          grade.regular_grade || '',
          grade.final_exam_score || '',
          formatScore(grade.total_score),
          grade.comment || ''
        ].map(cell => `"${cell}"`).join(',')
        
        csvContent += row + '\n'
      })
      
      return csvContent
    }
    
    const formatScore = (score) => {
      if (score === null || score === undefined) return '-'
      return parseFloat(score).toFixed(1)
    }
    
    // 生命周期钩子
    onMounted(() => {
      fetchData()
    })
    
    return {
      loading,
      currentCourse,
      courseGrades,
      gradeSettings,
      saving,
      savingGrades,
      savingStudentId,
      updateRegularWeight,
      updateFinalWeight,
      saveGradeSettings,
      calcTotalScore,
      saveStudentGrade,
      saveAllGrades,
      downloadGrades,
      formatScore
    }
  }
}
</script>

<style scoped>
.grades-container {
  padding: 20px;
}

.course-info {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.settings-card {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.weight-label {
  margin-left: 10px;
  color: #606266;
}

.students-grades {
  background-color: #fff;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.table-actions {
  margin-bottom: 15px;
  display: flex;
  justify-content: flex-end;
}

.table-actions .el-button {
  margin-left: 10px;
}
</style> 