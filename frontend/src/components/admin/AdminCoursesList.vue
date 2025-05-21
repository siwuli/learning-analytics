<template>
  <div class="admin-courses">
    <!-- 添加课程按钮 -->
    <div class="action-bar">
      <el-button type="primary" @click="showAddCourseDialog">
        <i class="el-icon-plus"></i> 添加课程
      </el-button>
      
      <!-- 状态筛选 -->
      <el-radio-group v-model="statusFilter" @change="handleStatusFilterChange" class="status-filter">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button label="active">活跃</el-radio-button>
        <el-radio-button label="archived">存档</el-radio-button>
      </el-radio-group>
    </div>
    
    <!-- 课程表格 -->
    <el-table
      v-loading="loading"
      :data="courses"
      border
      style="width: 100%"
    >
      <el-table-column label="ID" prop="id" width="80" />
      <el-table-column label="课程名称" prop="title" min-width="200" />
      <el-table-column label="教师" width="120">
        <template #default="scope">
          <span>{{ scope.row.instructor?.username || '未分配' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="开始日期" width="120">
        <template #default="scope">
          {{ formatDate(scope.row.start_date, true) }}
        </template>
      </el-table-column>
      <el-table-column label="结束日期" width="120">
        <template #default="scope">
          {{ formatDate(scope.row.end_date, true) }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="scope">
          <el-tag
            :type="scope.row.status === 'active' ? 'success' : 'info'"
          >
            {{ scope.row.status === 'active' ? '活跃' : '存档' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="120">
        <template #default="scope">
          {{ formatDate(scope.row.created_at, true) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250">
        <template #default="scope">
          <el-button 
            size="mini" 
            @click="handleViewDetails(scope.row)"
          >
            详情
          </el-button>
          <el-button 
            size="mini" 
            type="primary" 
            @click="handleEdit(scope.row)"
          >
            编辑
          </el-button>
          <el-button 
            size="mini" 
            type="danger" 
            @click="handleDelete(scope.row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="pagination.currentPage"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="pagination.total"
      >
      </el-pagination>
    </div>
    
    <!-- 课程表单对话框 -->
    <el-dialog
      :title="dialogMode === 'add' ? '添加课程' : '编辑课程'"
      v-model="dialogVisible"
      width="600px"
    >
      <el-form
        ref="courseFormRef"
        :model="courseForm"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="课程名称" prop="title">
          <el-input v-model="courseForm.title" />
        </el-form-item>
        <el-form-item label="课程描述" prop="description">
          <el-input v-model="courseForm.description" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="负责教师" prop="instructor_id">
          <el-select 
            v-model="courseForm.instructor_id" 
            placeholder="请选择教师"
            filterable
            clearable
          >
            <el-option 
              v-for="teacher in teachers" 
              :key="teacher.id" 
              :label="teacher.username" 
              :value="teacher.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker 
            v-model="courseForm.start_date" 
            type="date" 
            placeholder="选择开始日期"
            value-format="yyyy-MM-dd"
          />
        </el-form-item>
        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker 
            v-model="courseForm.end_date" 
            type="date" 
            placeholder="选择结束日期"
            value-format="yyyy-MM-dd"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="courseForm.status">
            <el-radio label="active">活跃</el-radio>
            <el-radio label="archived">存档</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitCourseForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 课程详情对话框 -->
    <el-dialog
      title="课程详情"
      v-model="detailsVisible"
      width="800px"
    >
      <div v-if="currentCourse" class="course-details">
        <el-descriptions title="基本信息" :column="2" border>
          <el-descriptions-item label="课程ID">{{ currentCourse.id }}</el-descriptions-item>
          <el-descriptions-item label="课程名称">{{ currentCourse.title }}</el-descriptions-item>
          <el-descriptions-item label="负责教师">{{ currentCourse.instructor?.username || '未分配' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentCourse.status === 'active' ? 'success' : 'info'">
              {{ currentCourse.status === 'active' ? '活跃' : '存档' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始日期">{{ formatDate(currentCourse.start_date) }}</el-descriptions-item>
          <el-descriptions-item label="结束日期">{{ formatDate(currentCourse.end_date) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentCourse.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(currentCourse.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="学生人数">{{ currentCourse.students_count || 0 }}</el-descriptions-item>
          <el-descriptions-item label="活动数量">{{ currentCourse.activities_count || 0 }}</el-descriptions-item>
          <el-descriptions-item label="平均完成率" :span="2">
            <el-progress :percentage="currentCourse.average_progress || 0" />
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="description-section">
          <h3>课程描述</h3>
          <p>{{ currentCourse.description || '无课程描述' }}</p>
        </div>
        
        <!-- 学生列表和管理 -->
        <div class="students-section">
          <div class="section-header">
            <h3>学生管理</h3>
            <el-button type="primary" size="small" @click="showAddStudentDialog">
              添加学生
            </el-button>
          </div>
          
          <el-table
            v-loading="studentsLoading"
            :data="courseStudents"
            border
            style="width: 100%"
          >
            <el-table-column label="ID" prop="id" width="80" />
            <el-table-column label="用户名" prop="username" />
            <el-table-column label="账号" prop="account" />
            <el-table-column label="邮箱" prop="email" />
            <el-table-column label="完成进度" width="200">
              <template #default="scope">
                <el-progress :percentage="scope.row.progress || 0" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button 
                  size="mini" 
                  type="danger" 
                  @click="handleRemoveStudent(scope.row)"
                >
                  移除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
    
    <!-- 添加学生对话框 -->
    <el-dialog
      title="添加学生到课程"
      v-model="addStudentVisible"
      width="500px"
    >
      <div class="student-select-container">
        <el-form :model="studentForm" label-width="80px">
          <el-form-item label="选择学生">
            <el-select
              v-model="studentForm.student_id"
              placeholder="请选择学生"
              filterable
              style="width: 100%"
            >
              <el-option
                v-for="student in availableStudents"
                :key="student.id"
                :label="`${student.username} (${student.account})`"
                :value="student.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addStudentVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="handleAddStudentToCourse" 
            :disabled="!studentForm.student_id"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, reactive } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'AdminCoursesList',
  setup() {
    const store = useStore()
    const courseFormRef = ref(null)
    const dialogVisible = ref(false)
    const detailsVisible = ref(false)
    const addStudentVisible = ref(false)
    const dialogMode = ref('add') // 'add' 或 'edit'
    const statusFilter = ref('') // 状态筛选
    const pageSize = ref(10)
    const currentPage = ref(1)
    const studentsLoading = ref(false)
    const availableStudents = ref([])
    
    // 课程表单数据
    const courseForm = reactive({
      id: null,
      title: '',
      description: '',
      instructor_id: null,
      start_date: '',
      end_date: '',
      status: 'active'
    })
    
    // 学生表单数据
    const studentForm = reactive({
      student_id: null
    })
    
    // 表单验证规则
    const rules = reactive({
      title: [
        { required: true, message: '请输入课程名称', trigger: 'blur' },
        { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
      ],
      description: [
        { required: true, message: '请输入课程描述', trigger: 'blur' }
      ],
      status: [
        { required: true, message: '请选择课程状态', trigger: 'change' }
      ]
    })
    
    // 从store获取数据
    const courses = computed(() => store.state.admin.courses)
    const pagination = computed(() => store.state.admin.coursesPagination)
    const loading = computed(() => store.state.admin.loading)
    const currentCourse = computed(() => store.state.admin.currentCourse)
    const courseStudents = computed(() => store.state.admin.courseStudents)
    
    // 获取教师列表（用于选择教师）
    const teachers = ref([])
    
    // 获取教师列表
    const fetchTeachers = async () => {
      try {
        const response = await store.dispatch('admin/fetchUsers', {
          page: 1,
          perPage: 100,
          role: 'teacher'
        })
        teachers.value = response.data.users
      } catch (error) {
        console.error('获取教师列表失败:', error)
      }
    }
    
    // 获取可以添加到课程的学生
    const fetchAvailableStudents = async (courseId) => {
      try {
        // 获取所有学生
        const response = await store.dispatch('admin/fetchUsers', {
          page: 1,
          perPage: 1000,
          role: 'student'
        })
        
        const allStudents = response.data.users || []
        
        // 获取当前课程的学生
        await store.dispatch('admin/fetchCourseStudents', courseId)
        
        // 过滤掉已经在课程中的学生
        const enrolledStudentIds = courseStudents.value.map(student => student.id)
        availableStudents.value = allStudents.filter(
          student => !enrolledStudentIds.includes(student.id)
        )
      } catch (error) {
        console.error('获取可用学生失败:', error)
      }
    }
    
    // 获取课程列表
    const fetchCourses = async () => {
      try {
        console.log('正在获取课程列表...')
        await store.dispatch('admin/fetchCourses', {
          page: currentPage.value,
          perPage: pageSize.value,
          status: statusFilter.value
        })
        console.log('课程列表获取成功:', courses.value)
      } catch (error) {
        console.error('获取课程列表失败:', error)
      }
    }
    
    // 显示添加课程对话框
    const showAddCourseDialog = () => {
      dialogMode.value = 'add'
      // 重置表单
      Object.assign(courseForm, {
        id: null,
        title: '',
        description: '',
        instructor_id: null,
        start_date: '',
        end_date: '',
        status: 'active'
      })
      fetchTeachers()
      dialogVisible.value = true
    }
    
    // 显示编辑课程对话框
    const handleEdit = (course) => {
      dialogMode.value = 'edit'
      // 填充表单数据
      Object.assign(courseForm, {
        id: course.id,
        title: course.title,
        description: course.description || '',
        instructor_id: course.instructor_id,
        start_date: course.start_date ? course.start_date.split('T')[0] : '',
        end_date: course.end_date ? course.end_date.split('T')[0] : '',
        status: course.status || 'active'
      })
      fetchTeachers()
      dialogVisible.value = true
    }
    
    // 处理删除课程
    const handleDelete = (course) => {
      ElMessageBox.confirm(
        `确定要删除课程 "${course.title}" 吗？此操作不可恢复！`,
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
        .then(async () => {
          try {
            await store.dispatch('admin/deleteCourse', course.id)
            ElMessage.success('课程删除成功')
          } catch (error) {
            ElMessage.error('删除课程失败：' + (error.message || '未知错误'))
          }
        })
        .catch(() => {
          // 用户取消
        })
    }
    
    // 提交课程表单
    const submitCourseForm = () => {
      courseFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            if (dialogMode.value === 'add') {
              // 创建新课程
              await store.dispatch('admin/createCourse', courseForm)
              ElMessage.success('课程创建成功')
            } else {
              // 编辑课程
              await store.dispatch('admin/updateCourse', {
                courseId: courseForm.id,
                courseData: courseForm
              })
              ElMessage.success('课程更新成功')
            }
            dialogVisible.value = false
          } catch (error) {
            ElMessage.error((error.response?.data?.message) || '操作失败')
          }
        } else {
          return false
        }
      })
    }
    
    // 状态筛选变化
    const handleStatusFilterChange = () => {
      currentPage.value = 1
      fetchCourses()
    }
    
    // 分页大小变化
    const handleSizeChange = (size) => {
      pageSize.value = size
      fetchCourses()
    }
    
    // 当前页变化
    const handleCurrentChange = (page) => {
      currentPage.value = page
      fetchCourses()
    }
    
    // 格式化日期
    const formatDate = (dateString, shortFormat = false) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      if (shortFormat) {
        return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
      }
      return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
    }
    
    // 查看课程详情
    const handleViewDetails = async (course) => {
      try {
        studentsLoading.value = true
        // 获取课程详情
        await store.dispatch('admin/fetchCourseDetail', course.id)
        // 获取课程学生
        await store.dispatch('admin/fetchCourseStudents', course.id)
        detailsVisible.value = true
      } catch (error) {
        ElMessage.error('获取课程详情失败：' + (error.message || '未知错误'))
      } finally {
        studentsLoading.value = false
      }
    }
    
    // 显示添加学生对话框
    const showAddStudentDialog = async () => {
      if (!currentCourse.value) return
      
      try {
        await fetchAvailableStudents(currentCourse.value.id)
        studentForm.student_id = null
        addStudentVisible.value = true
      } catch (error) {
        ElMessage.error('获取可用学生失败')
      }
    }
    
    // 添加学生到课程
    const handleAddStudentToCourse = async () => {
      if (!studentForm.student_id || !currentCourse.value) {
        return
      }
      
      try {
        await store.dispatch('admin/addStudentToCourse', {
          courseId: currentCourse.value.id,
          studentId: studentForm.student_id
        })
        
        ElMessage.success('学生添加成功')
        addStudentVisible.value = false
        
        // 刷新学生列表
        await store.dispatch('admin/fetchCourseStudents', currentCourse.value.id)
        // 刷新课程详情
        await store.dispatch('admin/fetchCourseDetail', currentCourse.value.id)
      } catch (error) {
        ElMessage.error('添加学生失败：' + (error.response?.data?.message || '未知错误'))
      }
    }
    
    // 从课程中移除学生
    const handleRemoveStudent = (student) => {
      if (!currentCourse.value) return
      
      ElMessageBox.confirm(
        `确定要将学生 "${student.username}" 从课程中移除吗？`,
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
        .then(async () => {
          try {
            await store.dispatch('admin/removeStudentFromCourse', {
              courseId: currentCourse.value.id,
              studentId: student.id
            })
            
            ElMessage.success('学生已从课程中移除')
            
            // 刷新学生列表和课程详情
            await store.dispatch('admin/fetchCourseStudents', currentCourse.value.id)
            await store.dispatch('admin/fetchCourseDetail', currentCourse.value.id)
          } catch (error) {
            ElMessage.error('移除学生失败：' + (error.response?.data?.message || '未知错误'))
          }
        })
        .catch(() => {
          // 用户取消
        })
    }
    
    onMounted(() => {
      fetchCourses()
    })
    
    return {
      courses,
      pagination,
      loading,
      currentCourse,
      courseStudents,
      studentsLoading,
      availableStudents,
      teachers,
      dialogVisible,
      detailsVisible,
      addStudentVisible,
      dialogMode,
      courseForm,
      studentForm,
      courseFormRef,
      rules,
      statusFilter,
      pageSize,
      currentPage,
      showAddCourseDialog,
      handleEdit,
      handleDelete,
      submitCourseForm,
      handleStatusFilterChange,
      handleSizeChange,
      handleCurrentChange,
      formatDate,
      handleViewDetails,
      showAddStudentDialog,
      handleAddStudentToCourse,
      handleRemoveStudent
    }
  }
}
</script>

<style scoped>
.admin-courses {
  margin-top: 20px;
}

.action-bar {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
}

.status-filter {
  margin-left: auto;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.course-details {
  margin-top: 20px;
}

.description-section {
  margin-top: 20px;
  margin-bottom: 20px;
}

.students-section {
  margin-top: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
</style> 