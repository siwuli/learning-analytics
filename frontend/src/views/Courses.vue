<template>
  <div class="courses-container">
    <h1>课程管理</h1>
    
    <!-- 教师视图 -->
    <div v-if="isTeacher">
      <div class="page-header">
        <h2>我的教学课程</h2>
        <el-button type="primary" @click="showCreateCourseDialog">创建新课程</el-button>
      </div>
      
      <el-table 
        v-loading="loading" 
        :data="teachingCourses"
        style="width: 100%"
        class="course-table"
      >
        <el-table-column prop="title" label="课程名称" width="220">
          <template #default="scope">
            <router-link :to="`/courses/${scope.row.id}`">{{ scope.row.title }}</router-link>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="课程描述" show-overflow-tooltip></el-table-column>
        <el-table-column prop="studentCount" label="学生数量" width="120" align="center"></el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
              {{ scope.row.status === 'active' ? '进行中' : '已归档' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template #default="scope">
            <el-button size="small" @click="editCourse(scope.row)">编辑</el-button>
            <el-button size="small" type="success" @click="manageCourseStudents(scope.row)">管理学生</el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="deleteCourse(scope.row)"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 学生视图 -->
    <div v-else>
      <h2>我的课程</h2>
      
      <el-row :gutter="20" class="course-list">
        <el-col 
          v-for="course in enrolledCourses" 
          :key="course.id" 
          :xs="24" 
          :sm="12" 
          :md="8" 
          :lg="6"
        >
          <el-card class="course-card">
            <div class="course-info">
              <div class="course-title">{{ course.title }}</div>
              <div class="course-description">{{ course.description }}</div>
              <div class="course-progress">
                <span>完成进度: {{ course.progress }}%</span>
                <el-progress :percentage="course.progress" :stroke-width="5"></el-progress>
              </div>
              <div class="course-actions">
                <router-link :to="`/courses/${course.id}`">
                  <el-button type="primary" size="small">进入学习</el-button>
                </router-link>
                <el-button type="danger" size="small" @click="dropCourse(course)">退选</el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 可选课程列表 -->
      <div class="available-courses">
        <h2>可选课程</h2>
        <el-table 
          v-loading="loadingAvailableCourses" 
          :data="availableCourses"
          style="width: 100%"
        >
          <el-table-column prop="title" label="课程名称" width="220"></el-table-column>
          <el-table-column prop="description" label="课程描述" show-overflow-tooltip></el-table-column>
          <el-table-column prop="instructorName" label="教师" width="150"></el-table-column>
          <el-table-column label="操作" width="100" align="center">
            <template #default="scope">
              <el-button type="primary" size="small" @click="enrollCourse(scope.row)">选课</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
    
    <!-- 创建/编辑课程对话框 -->
    <el-dialog
      v-model="courseDialogVisible"
      :title="isEditMode ? '编辑课程' : '创建新课程'"
      width="50%"
    >
      <el-form :model="courseForm" :rules="courseRules" ref="courseFormRef" label-width="100px">
        <el-form-item label="课程名称" prop="title">
          <el-input v-model="courseForm.title" placeholder="请输入课程名称"></el-input>
        </el-form-item>
        
        <el-form-item label="课程描述" prop="description">
          <el-input v-model="courseForm.description" type="textarea" rows="4" placeholder="请输入课程描述"></el-input>
        </el-form-item>
        
        <el-form-item label="开始日期" prop="startDate">
          <el-date-picker v-model="courseForm.startDate" type="date" placeholder="选择开始日期"></el-date-picker>
        </el-form-item>
        
        <el-form-item label="结束日期" prop="endDate">
          <el-date-picker v-model="courseForm.endDate" type="date" placeholder="选择结束日期"></el-date-picker>
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-select v-model="courseForm.status" placeholder="请选择课程状态">
            <el-option label="进行中" value="active"></el-option>
            <el-option label="已归档" value="archived"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="courseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCourse" :loading="savingCourse">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 管理学生对话框 -->
    <el-dialog
      v-model="studentsDialogVisible"
      title="课程学生管理"
      width="60%"
    >
      <div v-if="currentCourse">
        <h3>{{ currentCourse.title }} - 学生列表</h3>
        
        <el-input
          v-model="studentSearchQuery"
          placeholder="搜索学生..."
          style="width: 300px; margin-bottom: 20px;"
          clearable
        >
          <template #append>
            <el-button @click="searchStudents">搜索</el-button>
          </template>
        </el-input>
        
        <el-table
          v-loading="loadingStudents"
          :data="courseStudents"
          style="width: 100%"
        >
          <el-table-column prop="username" label="用户名"></el-table-column>
          <el-table-column prop="email" label="邮箱"></el-table-column>
          <el-table-column prop="enrolledAt" label="加入时间">
            <template #default="scope">
              {{ formatDate(scope.row.enrolledAt) }}
            </template>
          </el-table-column>
          <el-table-column prop="progress" label="完成进度" width="200">
            <template #default="scope">
              <el-progress :percentage="scope.row.progress || 0"></el-progress>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button type="danger" size="small" @click="removeStudent(scope.row)">
                移除学生
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="add-student-section">
          <h4>添加学生</h4>
          
          <el-select
            v-model="selectedStudentId"
            filterable
            remote
            reserve-keyword
            placeholder="搜索学生..."
            :remote-method="searchAvailableStudents"
            :loading="loadingAvailableStudents"
            style="width: 300px;"
          >
            <el-option
              v-for="item in availableStudents"
              :key="item.id"
              :label="`${item.username} (${item.email})`"
              :value="item.id"
            >
            </el-option>
          </el-select>
          
          <el-button type="primary" @click="addStudentToCourse" :disabled="!selectedStudentId">
            添加到课程
          </el-button>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="studentsDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'Courses',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    // 状态
    const loading = computed(() => store.state.courses.loading)
    const loadingAvailableCourses = ref(false)
    const loadingStudents = ref(false)
    const loadingAvailableStudents = ref(false)
    const savingCourse = ref(false)
    const courseDialogVisible = ref(false)
    const studentsDialogVisible = ref(false)
    const isEditMode = ref(false)
    const currentCourse = ref(null)
    const studentSearchQuery = ref('')
    const selectedStudentId = ref('')
    
    // 表单
    const courseFormRef = ref(null)
    const courseForm = reactive({
      id: null,
      title: '',
      description: '',
      startDate: '',
      endDate: '',
      status: 'active'
    })
    
    // 数据从Vuex获取
    const teachingCourses = computed(() => store.state.courses.teachingCourses)
    const enrolledCourses = computed(() => store.state.courses.enrolledCourses)
    const availableCourses = computed(() => store.state.courses.availableCourses)
    const courseStudents = computed(() => store.state.courses.courseStudents)
    
    // 计算属性
    const isTeacher = computed(() => {
      const user = store.state.auth.user
      return user && user.role === 'teacher'
    })
    
    // 方法
    const showCreateCourseDialog = () => {
      isEditMode.value = false
      resetCourseForm()
      courseDialogVisible.value = true
    }
    
    const editCourse = (course) => {
      isEditMode.value = true
      Object.assign(courseForm, {
        id: course.id,
        title: course.title,
        description: course.description,
        startDate: course.start_date ? new Date(course.start_date) : '',
        endDate: course.end_date ? new Date(course.end_date) : '',
        status: course.status
      })
      courseDialogVisible.value = true
    }
    
    const resetCourseForm = () => {
      courseForm.id = null
      courseForm.title = ''
      courseForm.description = ''
      courseForm.startDate = ''
      courseForm.endDate = ''
      courseForm.status = 'active'
    }
    
    const saveCourse = () => {
      courseFormRef.value.validate(async (valid) => {
        if (valid) {
          savingCourse.value = true
          
          try {
            const courseData = {
              title: courseForm.title,
              description: courseForm.description,
              start_date: courseForm.startDate ? courseForm.startDate.toISOString().split('T')[0] : null,
              end_date: courseForm.endDate ? courseForm.endDate.toISOString().split('T')[0] : null,
              status: courseForm.status,
              instructor_id: store.state.auth.user.id
            }
            
            if (isEditMode.value) {
              await store.dispatch('courses/updateCourse', { 
                courseId: courseForm.id, 
                courseData 
              })
              ElMessage.success('课程更新成功')
            } else {
              await store.dispatch('courses/createCourse', courseData)
              ElMessage.success('课程创建成功')
            }
            
            courseDialogVisible.value = false
          } catch (error) {
            ElMessage.error('操作失败: ' + error.message)
          } finally {
            savingCourse.value = false
          }
        }
      })
    }
    
    const deleteCourse = (course) => {
      ElMessageBox.confirm(
        `确定要删除课程 "${course.title}" 吗？`,
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          await store.dispatch('courses/deleteCourse', course.id)
          ElMessage.success('课程删除成功')
        } catch (error) {
          ElMessage.error('删除失败: ' + error.message)
        }
      }).catch(() => {
        // 取消删除
      })
    }
    
    const manageCourseStudents = (course) => {
      currentCourse.value = course
      loadingStudents.value = true
      
      store.dispatch('courses/fetchCourseStudents', course.id)
        .then(() => {
          loadingStudents.value = false
          studentsDialogVisible.value = true
        })
        .catch(error => {
          loadingStudents.value = false
          ElMessage.error('获取学生列表失败: ' + error.message)
        })
    }
    
    const searchStudents = () => {
      if (!currentCourse.value) return
      
      loadingStudents.value = true
      
      // 实际应用中应该调用API进行搜索
      // 这里简化处理，在前端过滤
      setTimeout(() => {
        loadingStudents.value = false
      }, 300)
    }
    
    const searchAvailableStudents = (query) => {
      if (query) {
        loadingAvailableStudents.value = true
        
        // 应该调用API搜索可用学生
        // 这里模拟
        setTimeout(() => {
          loadingAvailableStudents.value = false
        }, 300)
      }
    }
    
    const addStudentToCourse = () => {
      if (!selectedStudentId.value || !currentCourse.value) return
      
      store.dispatch('courses/enrollStudent', {
        courseId: currentCourse.value.id,
        userId: selectedStudentId.value
      })
      .then(() => {
        ElMessage.success('学生已添加到课程')
        selectedStudentId.value = ''
      })
      .catch(error => {
        ElMessage.error('添加学生失败: ' + error.message)
      })
    }
    
    const removeStudent = (student) => {
      if (!currentCourse.value) return
      
      ElMessageBox.confirm(
        `确定要将学生 "${student.username}" 从课程中移除吗？`,
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          await store.dispatch('courses/dropCourse', {
            courseId: currentCourse.value.id,
            userId: student.id
          })
          
          // 刷新课程学生列表
          await store.dispatch('courses/fetchCourseStudents', currentCourse.value.id)
          
          ElMessage.success('学生已从课程中移除')
        } catch (error) {
          ElMessage.error('移除学生失败: ' + error.message)
        }
      }).catch(() => {
        // 取消操作
      })
    }
    
    const enrollCourse = (course) => {
      ElMessageBox.confirm(
        `确定要选修课程 "${course.title}" 吗？`,
        '确认选课',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        }
      ).then(async () => {
        try {
          await store.dispatch('courses/enrollCourse', {
            courseId: course.id,
            userId: store.state.auth.user.id
          })
          
          ElMessage.success('选课成功')
        } catch (error) {
          ElMessage.error('选课失败: ' + error.message)
        }
      }).catch(() => {
        // 取消选课
      })
    }
    
    const dropCourse = (course) => {
      ElMessageBox.confirm(
        `确定要退选课程 "${course.title}" 吗？`,
        '确认退选',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          await store.dispatch('courses/dropCourse', {
            courseId: course.id,
            userId: store.state.auth.user.id
          })
          
          ElMessage.success('退选成功')
        } catch (error) {
          ElMessage.error('退选失败: ' + error.message)
        }
      }).catch(() => {
        // 取消退选
      })
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('zh-CN');
    }
    
    // 生命周期钩子
    onMounted(async () => {
      try {
        if (isTeacher.value) {
          // 如果是教师，获取教学课程
          await store.dispatch('courses/fetchTeachingCourses')
        } else {
          // 如果是学生，获取已选课程和可选课程
          await Promise.all([
            store.dispatch('courses/fetchEnrolledCourses'),
            store.dispatch('courses/fetchAvailableCourses')
          ])
        }
      } catch (error) {
        ElMessage.error('获取课程数据失败: ' + error.message)
      }
    })
    
    // 监视用户角色变化，重新加载数据
    watch(() => store.state.auth.user, async (newUser) => {
      if (newUser) {
        try {
          if (newUser.role === 'teacher') {
            await store.dispatch('courses/fetchTeachingCourses')
          } else {
            await Promise.all([
              store.dispatch('courses/fetchEnrolledCourses'),
              store.dispatch('courses/fetchAvailableCourses')
            ])
          }
        } catch (error) {
          ElMessage.error('获取课程数据失败: ' + error.message)
        }
      }
    })
    
    return {
      loading,
      loadingAvailableCourses,
      loadingStudents,
      loadingAvailableStudents,
      savingCourse,
      courseDialogVisible,
      studentsDialogVisible,
      isEditMode,
      currentCourse,
      studentSearchQuery,
      selectedStudentId,
      courseFormRef,
      courseForm,
      courseRules: {
        title: [
          { required: true, message: '请输入课程名称', trigger: 'blur' },
          { min: 2, max: 100, message: '长度在2到100个字符之间', trigger: 'blur' }
        ],
        description: [
          { required: true, message: '请输入课程描述', trigger: 'blur' }
        ],
        status: [
          { required: true, message: '请选择课程状态', trigger: 'change' }
        ]
      },
      teachingCourses,
      enrolledCourses,
      availableCourses,
      courseStudents,
      availableStudents: ref([]),
      isTeacher,
      showCreateCourseDialog,
      editCourse,
      saveCourse,
      deleteCourse,
      manageCourseStudents,
      searchStudents,
      searchAvailableStudents,
      addStudentToCourse,
      removeStudent,
      enrollCourse,
      dropCourse,
      formatDate
    }
  }
}
</script>

<style scoped>
.courses-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.course-table {
  margin-bottom: 30px;
}

.course-list {
  margin-top: 20px;
  margin-bottom: 40px;
}

.course-card {
  margin-bottom: 20px;
  transition: transform 0.3s;
  height: 100%;
}

.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.course-image {
  display: none;
}

.course-info {
  padding: 15px;
}

.course-title {
  font-weight: bold;
  font-size: 18px;
  margin-bottom: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.course-description {
  color: #666;
  margin-bottom: 15px;
  min-height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.course-progress {
  margin-bottom: 15px;
}

.course-actions {
  display: flex;
  justify-content: flex-end;
}

.available-courses {
  margin-top: 40px;
}

.add-student-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
</style> 