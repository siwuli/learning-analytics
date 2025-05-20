<template>
  <div class="course-detail">
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
    
    <div v-else-if="currentCourse" class="course-content">
      <div class="course-header">
        <h1>{{ currentCourse.title }}</h1>
        <div class="course-meta">
          <el-tag v-if="currentCourse.status === 'active'" type="success">进行中</el-tag>
          <el-tag v-else type="info">已归档</el-tag>
          <span class="instructor">教师: {{ currentCourse.instructorName }}</span>
          <span class="dates">
            {{ formatDate(currentCourse.start_date) }} - {{ formatDate(currentCourse.end_date) }}
          </span>
        </div>
        <p class="course-description">{{ currentCourse.description }}</p>
      </div>
      
      <el-tabs v-model="activeTab" class="course-tabs">
        <el-tab-pane label="课程内容" name="content">
          <div class="course-sections">
            <div v-if="courseSections.length === 0" class="empty-data">
              <el-empty description="暂无内容" />
            </div>
            
            <el-collapse v-else v-model="activeSection">
              <el-collapse-item 
                v-for="section in courseSections" 
                :key="section.id"
                :name="section.id"
              >
                <template #title>
                  <div class="section-title">
                    <span>{{ section.title }}</span>
                    <el-progress 
                      v-if="!isTeacher" 
                      :percentage="section.progress || 0" 
                      :format="percentFormat"
                      style="width: 120px; margin-left: 20px;"
                    ></el-progress>
                  </div>
                </template>
                
                <div class="section-content">
                  <div class="section-description">{{ section.description }}</div>
                  
                  <div class="section-items">
                    <div 
                      v-for="item in section.items" 
                      :key="item.id"
                      class="item-card"
                    >
                      <div class="item-icon">
                        <el-icon v-if="item.type === 'document'"><Document /></el-icon>
                        <el-icon v-else-if="item.type === 'video'"><VideoCamera /></el-icon>
                        <el-icon v-else-if="item.type === 'quiz'"><QuestionFilled /></el-icon>
                        <el-icon v-else><Notebook /></el-icon>
                      </div>
                      
                      <div class="item-info">
                        <div class="item-title">{{ item.title }}</div>
                        <div class="item-description">{{ item.description }}</div>
                      </div>
                      
                      <div class="item-status">
                        <el-button size="small" type="primary">
                          {{ isTeacher ? '编辑' : '查看' }}
                        </el-button>
                        
                        <el-tag v-if="!isTeacher && item.completed" type="success">已完成</el-tag>
                      </div>
                    </div>
                  </div>
                  
                  <div v-if="isTeacher" class="add-item">
                    <el-button type="success" size="small" plain>添加内容</el-button>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
            
            <div v-if="isTeacher" class="add-section">
              <el-button type="primary" plain>添加章节</el-button>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="学生" name="students" v-if="isTeacher">
          <div class="course-students">
            <div class="students-header">
              <h3>已选课学生</h3>
              <el-button type="primary" size="small" @click="openAddStudentsDialog">添加学生</el-button>
            </div>
            
            <el-table :data="courseStudents" v-loading="loadingStudents" style="width: 100%">
              <el-table-column prop="username" label="姓名"></el-table-column>
              <el-table-column prop="email" label="邮箱"></el-table-column>
              <el-table-column prop="progress" label="完成进度" width="200">
                <template #default="scope">
                  <el-progress :percentage="scope.row.progress || 0"></el-progress>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="viewStudentDetail(scope.row)">
                    查看详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="作业" name="assignments">
          <div class="course-assignments">
            <div class="assignments-header">
              <h3>课程作业</h3>
              <el-button v-if="isTeacher" type="primary" size="small">发布作业</el-button>
            </div>
            
            <div v-if="assignments.length === 0" class="empty-data">
              <el-empty description="暂无作业" />
            </div>
            
            <div v-else class="assignments-list">
              <el-card v-for="assignment in assignments" :key="assignment.id" class="assignment-card">
                <div class="assignment-header">
                  <h4>{{ assignment.title }}</h4>
                  <div class="assignment-status">
                    <el-tag :type="getAssignmentStatusType(assignment)">
                      {{ getAssignmentStatusText(assignment) }}
                    </el-tag>
                  </div>
                </div>
                
                <div class="assignment-info">
                  <p>{{ assignment.description }}</p>
                  <div class="assignment-meta">
                    <span class="deadline">截止日期: {{ formatDate(assignment.deadline) }}</span>
                    <span class="points">分值: {{ assignment.points }} 分</span>
                  </div>
                </div>
                
                <div class="assignment-actions">
                  <el-button type="primary" size="small">
                    {{ isTeacher ? '查看提交' : '提交作业' }}
                  </el-button>
                </div>
              </el-card>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="讨论" name="discussions">
          <div class="course-discussions">
            <div class="discussions-header">
              <h3>课程讨论</h3>
              <el-button type="primary" size="small">发起讨论</el-button>
            </div>
            
            <div v-if="discussions.length === 0" class="empty-data">
              <el-empty description="暂无讨论" />
            </div>
            
            <div v-else class="discussions-list">
              <!-- 讨论列表 -->
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="数据分析" name="analytics" v-if="isTeacher">
          <div class="course-analytics">
            <h3>课程数据分析</h3>
            <!-- 数据分析内容 -->
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <div v-else class="error-container">
      <el-result
        icon="error"
        title="课程不存在"
        sub-title="您访问的课程不存在或已被删除"
      >
        <template #extra>
          <el-button type="primary" @click="goBack">返回</el-button>
        </template>
      </el-result>
    </div>
    
    <!-- 添加学生对话框 -->
    <el-dialog
      v-model="addStudentsDialogVisible"
      title="添加学生到课程"
      width="50%"
    >
      <el-form :inline="true" class="demo-form-inline">
        <el-form-item>
          <el-input
            v-model="studentSearchQuery"
            placeholder="搜索学生..."
            clearable
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchStudents">搜索</el-button>
        </el-form-item>
      </el-form>
      
      <el-table
        :data="availableStudents"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column prop="username" label="姓名"></el-table-column>
        <el-table-column prop="email" label="邮箱"></el-table-column>
      </el-table>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addStudentsDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="addStudentsToCourse" :disabled="selectedStudents.length === 0">
            添加 ({{ selectedStudents.length }} 名学生)
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'CourseDetail',
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    
    const loading = ref(true)
    const loadingStudents = ref(false)
    const activeTab = ref('content')
    const activeSection = ref([])
    const addStudentsDialogVisible = ref(false)
    const studentSearchQuery = ref('')
    const selectedStudents = ref([])
    
    // 获取当前课程ID
    const courseId = computed(() => route.params.id)
    
    // 获取当前课程数据
    const currentCourse = computed(() => store.state.courses.currentCourse)
    
    // 获取课程学生
    const courseStudents = computed(() => store.state.courses.courseStudents)
    
    // 判断当前用户是否为教师
    const isTeacher = computed(() => {
      const user = store.state.auth.user
      return user && user.role === 'teacher'
    })
    
    // 模拟数据 - 实际应从API获取
    const courseSections = ref([])
    const assignments = ref([])
    const discussions = ref([])
    const availableStudents = ref([])
    
    // 初始化加载课程数据
    const loadCourseData = async () => {
      try {
        loading.value = true
        
        // 加载课程详情
        await store.dispatch('courses/fetchCourse', courseId.value)
        
        // 如果是教师，加载课程学生
        if (isTeacher.value) {
          loadingStudents.value = true
          await store.dispatch('courses/fetchCourseStudents', courseId.value)
          loadingStudents.value = false
        }
        
        // 模拟加载课程章节数据
        courseSections.value = [
          {
            id: 1,
            title: '第一章：课程介绍',
            description: '本章介绍课程的基本内容和学习目标',
            progress: 100,
            items: [
              {
                id: 101,
                type: 'document',
                title: '课程大纲',
                description: '详细介绍课程的内容与安排',
                completed: true
              },
              {
                id: 102,
                type: 'video',
                title: '课程导览视频',
                description: '5分钟视频介绍课程内容',
                completed: true
              }
            ]
          },
          {
            id: 2,
            title: '第二章：基础知识',
            description: '学习本课程所需的基础理论',
            progress: 50,
            items: [
              {
                id: 201,
                type: 'document',
                title: '基础理论文档',
                description: '基础理论详解',
                completed: true
              },
              {
                id: 202,
                type: 'quiz',
                title: '基础知识测试',
                description: '检验基础知识掌握情况',
                completed: false
              }
            ]
          }
        ]
        
        // 模拟加载作业数据
        assignments.value = [
          {
            id: 1,
            title: '第一次作业：基础理论练习',
            description: '完成课本第二章课后习题1-10',
            deadline: '2023-12-25',
            points: 10,
            status: 'pending'
          },
          {
            id: 2,
            title: '第二次作业：实践操作',
            description: '按照要求完成实验并提交报告',
            deadline: '2024-01-05',
            points: 15,
            status: 'not_started'
          }
        ]
        
        // 模拟讨论数据
        discussions.value = []
        
      } catch (error) {
        ElMessage.error('加载课程数据失败: ' + error.message)
      } finally {
        loading.value = false
      }
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return '未设置'
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    }
    
    // 格式化进度百分比
    const percentFormat = (percent) => {
      return percent + '%'
    }
    
    // 获取作业状态样式
    const getAssignmentStatusType = (assignment) => {
      const statusMap = {
        'completed': 'success',
        'pending': 'warning',
        'overdue': 'danger',
        'not_started': 'info'
      }
      return statusMap[assignment.status] || 'info'
    }
    
    // 获取作业状态文本
    const getAssignmentStatusText = (assignment) => {
      const statusMap = {
        'completed': '已完成',
        'pending': '进行中',
        'overdue': '已逾期',
        'not_started': '未开始'
      }
      return statusMap[assignment.status] || '未知状态'
    }
    
    // 打开添加学生对话框
    const openAddStudentsDialog = () => {
      addStudentsDialogVisible.value = true
      // 模拟获取可添加的学生
      availableStudents.value = [
        { id: 101, username: '张三', email: 'zhangsan@example.com' },
        { id: 102, username: '李四', email: 'lisi@example.com' },
        { id: 103, username: '王五', email: 'wangwu@example.com' }
      ]
    }
    
    // 搜索学生
    const searchStudents = () => {
      // 实际应调用API搜索学生
      console.log('搜索学生:', studentSearchQuery.value)
    }
    
    // 表格选择变化
    const handleSelectionChange = (selection) => {
      selectedStudents.value = selection
    }
    
    // 添加学生到课程
    const addStudentsToCourse = async () => {
      try {
        // 这里应该调用API添加学生
        const promises = selectedStudents.value.map(student => 
          store.dispatch('courses/enrollStudent', {
            courseId: courseId.value,
            userId: student.id
          })
        )
        
        await Promise.all(promises)
        
        ElMessage.success(`已成功添加 ${selectedStudents.value.length} 名学生到课程`)
        addStudentsDialogVisible.value = false
        
        // 重新加载课程学生
        await store.dispatch('courses/fetchCourseStudents', courseId.value)
      } catch (error) {
        ElMessage.error('添加学生失败: ' + error.message)
      }
    }
    
    // 查看学生详情
    const viewStudentDetail = (student) => {
      ElMessage.info('查看学生详情功能待实现')
    }
    
    // 返回上一页
    const goBack = () => {
      router.back()
    }
    
    onMounted(() => {
      loadCourseData()
    })
    
    return {
      loading,
      loadingStudents,
      activeTab,
      activeSection,
      addStudentsDialogVisible,
      studentSearchQuery,
      selectedStudents,
      courseId,
      currentCourse,
      courseStudents,
      isTeacher,
      courseSections,
      assignments,
      discussions,
      availableStudents,
      formatDate,
      percentFormat,
      getAssignmentStatusType,
      getAssignmentStatusText,
      openAddStudentsDialog,
      searchStudents,
      handleSelectionChange,
      addStudentsToCourse,
      viewStudentDetail,
      goBack
    }
  }
}
</script>

<style scoped>
.course-detail {
  padding: 20px;
}

.loading-container,
.error-container {
  margin-top: 20px;
}

.course-header {
  margin-bottom: 30px;
}

.course-header h1 {
  margin-bottom: 10px;
}

.course-meta {
  margin-bottom: 15px;
  display: flex;
  gap: 20px;
  align-items: center;
}

.course-description {
  color: #606266;
  margin-top: 15px;
  font-size: 16px;
  line-height: 1.6;
}

.course-tabs {
  margin-top: 20px;
}

.empty-data {
  padding: 40px 0;
}

.section-title {
  display: flex;
  align-items: center;
}

.section-content {
  padding: 10px 0;
}

.section-description {
  color: #606266;
  margin-bottom: 20px;
}

.section-items {
  margin-top: 15px;
}

.item-card {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  transition: all 0.3s;
}

.item-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.item-icon {
  font-size: 24px;
  margin-right: 15px;
  color: #409EFF;
}

.item-info {
  flex: 1;
}

.item-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.item-description {
  color: #606266;
  font-size: 14px;
}

.item-status {
  margin-left: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.add-item,
.add-section {
  margin-top: 20px;
  text-align: center;
}

.students-header,
.assignments-header,
.discussions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.assignment-card {
  margin-bottom: 15px;
}

.assignment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.assignment-header h4 {
  margin: 0;
}

.assignment-info {
  margin-bottom: 15px;
}

.assignment-meta {
  display: flex;
  gap: 20px;
  color: #909399;
  font-size: 14px;
  margin-top: 10px;
}

.assignment-actions {
  display: flex;
  justify-content: flex-end;
}
</style> 