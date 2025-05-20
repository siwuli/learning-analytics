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
      
      <el-card v-if="!loading">
        <el-tabs 
          v-model="activeTab" 
          type="border-card"
          @tab-click="handleTabClick"
        >
          <el-tab-pane label="课程内容" name="content">
            <el-collapse v-if="courseSections.length > 0">
              <el-collapse-item 
                v-for="section in courseSections" 
                :key="section.id"
                :name="section.id"
              >
                <template #title>
                  <div class="section-title-wrapper">
                    <span>{{ section.title }}</span>
                    <el-button 
                      v-if="isTeacher"
                      type="danger" 
                      size="small"
                      @click.stop="confirmDeleteSection(section)"
                    >
                      删除章节
                    </el-button>
                  </div>
                </template>
                <div class="section-header">
                  <p class="section-description">{{ section.description }}</p>
                  <div class="progress-info">
                    <el-progress 
                      :percentage="section.progress" 
                      :format="format => `${format}%`"
                      :stroke-width="10"
                      :status="section.progress === 100 ? 'success' : ''"
                    ></el-progress>
                    <div class="progress-text" v-if="section.totalResources > 0">
                      {{ section.completedResources }}/{{ section.totalResources }} 个资源已完成
                    </div>
                  </div>
                </div>
                
                <el-timeline>
                  <el-timeline-item
                    v-for="item in section.items"
                    :key="item.id"
                    :type="getItemType(item.type)"
                    :color="item.completed ? '#67C23A' : '#409EFF'"
                  >
                    <div class="timeline-item-content">
                      <div class="item-title">{{ item.title }}</div>
                      <div class="item-description">{{ item.description }}</div>
                      <div class="item-actions">
                        <el-button 
                          type="primary" 
                          size="small" 
                          @click="viewResource(item)"
                        >
                          查看
                        </el-button>
                        <el-tag 
                          :type="item.completed ? 'success' : 'info'"
                          size="small"
                        >
                          {{ item.completed ? '已完成' : '未完成' }}
                        </el-tag>
                        <el-button 
                          v-if="isTeacher" 
                          type="danger" 
                          size="small" 
                          @click="confirmDeleteResource(section.id, item)"
                        >
                          删除
                        </el-button>
                      </div>
                    </div>
                  </el-timeline-item>
                </el-timeline>
                
                <div v-if="isTeacher" class="add-resource-button">
                  <el-button 
                    type="primary" 
                    plain 
                    size="small" 
                    @click="showAddResourceDialog(section.id)"
                  >
                    添加资源
                  </el-button>
                </div>
              </el-collapse-item>
            </el-collapse>
            
            <el-empty v-else description="暂无课程内容"></el-empty>
            
            <div v-if="isTeacher" class="add-section-button">
              <el-button 
                type="primary" 
                @click="showAddSectionDialog"
              >
                添加章节
              </el-button>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="作业" name="assignments">
            <div class="assignment-list static-content-container">
              <el-table 
                :data="assignments" 
                style="width: 100%"
                v-loading="loadingAssignments"
                :height="isFixedHeight ? 400 : null"
              >
                <el-table-column prop="title" label="名称"></el-table-column>
                <el-table-column prop="deadline" label="截止日期"></el-table-column>
                <el-table-column prop="points" label="分数"></el-table-column>
                <el-table-column label="状态">
                  <template #default="scope">
                    <el-tag :type="getStatusType(scope.row.status)">
                      {{ getStatusText(scope.row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作">
                  <template #default="scope">
                    <el-button 
                      type="primary" 
                      size="small" 
                      @click="viewAssignment(scope.row)"
                    >
                      查看
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              
              <div v-if="isTeacher" class="add-assignment-button">
                <el-button 
                  type="primary" 
                  @click="showAddAssignmentDialog"
                >
                  添加作业
                </el-button>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="讨论" name="discussions">
            <div class="discussion-list static-content-container">
              <el-table 
                :data="discussions" 
                style="width: 100%"
                v-loading="loadingDiscussions"
                :height="isFixedHeight ? 400 : null"
              >
                <el-table-column prop="title" label="标题"></el-table-column>
                <el-table-column prop="author" label="发起人"></el-table-column>
                <el-table-column prop="replies" label="回复数"></el-table-column>
                <el-table-column prop="created_at" label="发布时间"></el-table-column>
                <el-table-column label="操作">
                  <template #default="scope">
                    <el-button 
                      type="primary" 
                      size="small" 
                      @click="viewDiscussion(scope.row)"
                    >
                      查看
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              
              <div class="add-discussion-button">
                <el-button 
                  type="primary" 
                  @click="showAddDiscussionDialog"
                >
                  发起讨论
                </el-button>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane v-if="isTeacher" label="学生" name="students">
            <el-table 
              :data="courseStudents" 
              style="width: 100%"
              v-loading="loadingStudents"
            >
              <el-table-column prop="username" label="用户名"></el-table-column>
              <el-table-column prop="email" label="邮箱"></el-table-column>
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="viewStudentProgress(scope.row)"
                  >
                    查看进度
                  </el-button>
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click="removeStudent(scope.row)"
                  >
                    移除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </el-card>
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
    
    <!-- 查看资源对话框 -->
    <el-dialog
      v-model="resourceDialogVisible"
      :title="currentResource.title || '查看资源'"
      width="70%"
      destroy-on-close
    >
      <resource-viewer 
        v-if="currentResource.id" 
        :resource="currentResource"
        @updated="handleResourceUpdated"
      />
    </el-dialog>
    
    <!-- 添加章节对话框 -->
    <el-dialog
      v-model="sectionDialogVisible"
      :title="currentSection.id ? '编辑章节' : '添加章节'"
      width="50%"
      destroy-on-close
    >
      <section-form
        :course-id="courseId"
        :section="currentSection"
        @submit="handleSectionSubmit"
        @cancel="sectionDialogVisible = false"
      />
    </el-dialog>
    
    <!-- 添加资源对话框 -->
    <el-dialog
      v-model="resourceFormDialogVisible"
      :title="currentResource.id ? '编辑资源' : '添加资源'"
      width="70%"
      destroy-on-close
      :before-close="handleResourceDialogClose"
    >
      <resource-form 
        ref="resourceFormRef"
        :section-id="currentSectionId"
        :resource="currentResource"
        @submit="handleResourceSubmit"
        @cancel="closeResourceFormDialog"
      />
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, reactive } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElDialog } from 'element-plus'
import { courseAPI } from '../services/api'
import ResourceViewer from '../components/course/ResourceViewer.vue'
import SectionForm from '../components/course/SectionForm.vue'
import ResourceForm from '../components/course/ResourceForm.vue'
import { setupScrollContainer } from '../utils/resizeUtil'

export default {
  name: 'CourseDetail',
  components: {
    ResourceViewer,
    SectionForm,
    ResourceForm
  },
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    
    const loading = ref(true)
    const loadingStudents = ref(false)
    const loadingAssignments = ref(false)
    const loadingDiscussions = ref(false)
    const activeTab = ref('content')
    const activeSection = ref([])
    const addStudentsDialogVisible = ref(false)
    const studentSearchQuery = ref('')
    const selectedStudents = ref([])
    
    // 使用固定高度减少ResizeObserver错误
    const isFixedHeight = ref(true)
    
    // 资源查看对话框
    const resourceDialogVisible = ref(false)
    const currentResource = ref({})
    
    // 章节管理对话框
    const sectionDialogVisible = ref(false)
    const currentSection = ref({})
    
    // 资源管理对话框
    const resourceFormDialogVisible = ref(false)
    const currentSectionId = ref(null)
    
    // 资源表单引用
    const resourceFormRef = ref(null)
    
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
        loading.value = true;
        
        // 加载课程详情
        await store.dispatch('courses/fetchCourse', courseId.value);
        
        // 加载课程章节
        const sectionsResponse = await courseAPI.getCourseSections(courseId.value);
        courseSections.value = [];
        
        // 如果有章节数据，加载每个章节的资源
        if (sectionsResponse.data.sections && sectionsResponse.data.sections.length > 0) {
          // 为每个章节加载资源
          for (const section of sectionsResponse.data.sections) {
            const sectionDetail = await courseAPI.getCourseSection(courseId.value, section.id);
            const enrichedSection = {
              ...sectionDetail.data.section,
              progress: 0, // 默认进度为0
              completedResources: 0, // 计数完成的资源
              totalResources: 0 // 总资源数
            };
            
            // 将资源转换为前端需要的格式
            if (enrichedSection.resources) {
              enrichedSection.totalResources = enrichedSection.resources.length;
              
              enrichedSection.items = await Promise.all(enrichedSection.resources.map(async resource => {
                const resourceItem = {
                  id: resource.id,
                  section_id: section.id,
                  type: resource.resource_type,
                  title: resource.title,
                  description: resource.description,
                  completed: false // 默认未完成
                };
                
                // 如果用户已登录，尝试获取资源进度
                if (store.state.auth.user?.id) {
                  try {
                    const progressResponse = await courseAPI.getResourceProgress(
                      store.state.auth.user.id, 
                      resource.id
                    );
                    if (progressResponse.data.status === 'success') {
                      resourceItem.completed = progressResponse.data.progress.completed;
                      
                      // 如果资源已完成，增加章节完成资源计数
                      if (resourceItem.completed) {
                        enrichedSection.completedResources++;
                      }
                    }
                  } catch (error) {
                    // 如果获取失败，使用默认值
                    console.warn(`无法获取资源 ${resource.id} 的进度:`, error);
                  }
                }
                
                return resourceItem;
              }));
              
              // 计算章节完成度百分比
              if (enrichedSection.totalResources > 0) {
                enrichedSection.progress = Math.round(
                  (enrichedSection.completedResources / enrichedSection.totalResources) * 100
                );
              }
              
              delete enrichedSection.resources;
            } else {
              enrichedSection.items = [];
            }
            
            courseSections.value.push(enrichedSection);
          }
        }
        
        // 如果是教师，加载课程学生
        if (isTeacher.value) {
          loadingStudents.value = true;
          await store.dispatch('courses/fetchCourseStudents', courseId.value);
          loadingStudents.value = false;
        }
        
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
        ];
        
        // 模拟讨论数据
        discussions.value = [];
        
      } catch (error) {
        ElMessage.error('加载课程数据失败: ' + error.message);
      } finally {
        loading.value = false;
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
    
    // 移除学生
    const removeStudent = async (student) => {
      try {
        await ElMessageBox.confirm(
          `确定要将学生 "${student.username}" 从课程中移除吗？`,
          '警告',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        await store.dispatch('courses/dropCourse', {
          courseId: courseId.value,
          userId: student.id
        })
        
        // 重新加载课程学生
        await store.dispatch('courses/fetchCourseStudents', courseId.value)
        ElMessage.success('学生已从课程中移除')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('移除学生失败: ' + (error.message || '未知错误'))
        }
      }
    }
    
    // 返回上一页
    const goBack = () => {
      router.back()
    }
    
    // 获取资源类型图标
    const getItemType = (type) => {
      switch (type) {
        case 'document':
          return 'primary'
        case 'video':
          return 'success'
        case 'quiz':
          return 'warning'
        case 'assignment':
          return 'danger'
        default:
          return 'info'
      }
    }
    
    // 获取状态类型
    const getStatusType = (status) => {
      switch (status) {
        case 'completed':
          return 'success'
        case 'pending':
          return 'warning'
        case 'not_started':
          return 'info'
        case 'overdue':
          return 'danger'
        default:
          return 'info'
      }
    }
    
    // 获取状态文本
    const getStatusText = (status) => {
      switch (status) {
        case 'completed':
          return '已完成'
        case 'pending':
          return '进行中'
        case 'not_started':
          return '未开始'
        case 'overdue':
          return '已逾期'
        default:
          return '未知状态'
      }
    }
    
    // 查看资源
    const viewResource = (resource) => {
      currentResource.value = {
        id: resource.id,
        title: resource.title,
        description: resource.description,
        resource_type: resource.type,
        content: '',
        completed: resource.completed
      }
      
      // 加载资源详细内容
      courseAPI.getSectionResource(resource.section_id, resource.id)
        .then(response => {
          currentResource.value = response.data.resource
          resourceDialogVisible.value = true
        })
        .catch(error => {
          ElMessage.error('加载资源失败: ' + error.message)
        })
    }
    
    // 资源更新后的处理
    const handleResourceUpdated = async (updatedResource) => {
      ElMessage.success('资源状态已更新')
      
      // 更新本地资源列表中的状态
      courseSections.value.forEach(section => {
        const resourceItem = section.items.find(item => item.id === updatedResource.id)
        if (resourceItem) {
          resourceItem.completed = updatedResource.completed
        }
      })
      
      // 关闭对话框
      resourceDialogVisible.value = false
      
      // 重新加载课程数据以获取最新的进度信息
      // 延迟执行，确保后端数据已经更新
      setTimeout(async () => {
        await loadCourseData()
      }, 500)
    }
    
    // 查看作业
    const viewAssignment = (assignment) => {
      ElMessage.info(`查看作业: ${assignment.title}`)
      // TODO: 实现一个完整的作业查看/提交组件
    }
    
    // 查看讨论
    const viewDiscussion = (discussion) => {
      ElMessage.info(`查看讨论: ${discussion.title}`)
      // TODO: 实现一个完整的讨论组件
    }
    
    // 查看学生进度
    const viewStudentProgress = (student) => {
      ElMessage.info(`查看学生${student.username}的进度`)
      // TODO: 实现学生进度查看功能
    }
    
    // 显示添加章节对话框
    const showAddSectionDialog = () => {
      currentSection.value = {
        title: '',
        description: '',
        order: courseSections.value.length + 1
      }
      sectionDialogVisible.value = true
    }
    
    // 处理章节表单提交
    const handleSectionSubmit = async (sectionData) => {
      try {
        if (sectionData.id) {
          // 更新现有章节
          await courseAPI.updateCourseSection(courseId.value, sectionData.id, sectionData)
          ElMessage.success('章节已更新')
        } else {
          // 创建新章节
          await courseAPI.createCourseSection(courseId.value, sectionData)
          ElMessage.success('章节已添加')
        }
        
        // 重新加载课程章节
        await loadCourseData()
        sectionDialogVisible.value = false
      } catch (error) {
        ElMessage.error('保存章节失败: ' + error.message)
      }
    }
    
    // 显示添加资源对话框
    const showAddResourceDialog = (sectionId) => {
      currentSectionId.value = sectionId
      currentResource.value = {
        title: '',
        description: '',
        resource_type: 'document',
        content: '',
        order: 1
      }
      resourceFormDialogVisible.value = true
    }
    
    // 处理资源表单提交
    const handleResourceSubmit = async (resourceData) => {
      try {
        if (resourceData.id) {
          // 更新现有资源
          await courseAPI.updateSectionResource(
            resourceData.section_id, 
            resourceData.id, 
            resourceData
          )
          ElMessage.success('资源已更新')
        } else {
          // 创建新资源
          await courseAPI.createSectionResource(resourceData.section_id, resourceData)
          ElMessage.success('资源已添加')
        }
        
        // 重新加载课程章节
        await loadCourseData()
        resourceFormDialogVisible.value = false
      } catch (error) {
        ElMessage.error('保存资源失败: ' + error.message)
      }
    }
    
    // 显示添加作业对话框
    const showAddAssignmentDialog = () => {
      ElMessage.info('添加作业')
      // TODO: 实现添加作业功能
    }
    
    // 显示添加讨论对话框
    const showAddDiscussionDialog = () => {
      ElMessage.info('发起讨论')
      // TODO: 实现添加讨论功能
    }
    
    // 处理标签页切换
    const handleTabClick = () => {
      // 延迟处理，确保DOM已更新
      setTimeout(() => {
        try {
          // 设置固定高度状态
          isFixedHeight.value = true
          
          // 根据当前选中的标签页设置相应容器
          if (activeTab.value === 'assignments') {
            setupScrollContainer('.assignment-list')
          } else if (activeTab.value === 'discussions') {
            setupScrollContainer('.discussion-list')
          } else if (activeTab.value === 'students') {
            setupScrollContainer('.el-table')
          }
        } catch (e) {
          console.log('处理标签页错误', e)
        }
      }, 50)
    }
    
    // 关闭资源表单对话框
    const closeResourceFormDialog = () => {
      resourceFormDialogVisible.value = false
    }
    
    // 资源对话框关闭前处理
    const handleResourceDialogClose = (done) => {
      // 清理ResizeObserver以防止错误
      if (resourceFormRef.value?.cleanupResizeObserver) {
        resourceFormRef.value.cleanupResizeObserver()
      }
      done()
    }
    
    // 删除资源
    const confirmDeleteResource = async (sectionId, resource) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除资源 "${resource.title}" 吗？`,
          '警告',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        await courseAPI.deleteSectionResource(sectionId, resource.id)
        
        // 重新加载课程章节
        await loadCourseData()
        ElMessage.success('资源已删除')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除资源失败: ' + (error.message || '未知错误'))
        }
      }
    }
    
    // 删除章节
    const confirmDeleteSection = async (section) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除章节 "${section.title}" 吗？`,
          '警告',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        await courseAPI.deleteCourseSection(courseId.value, section.id)
        
        // 重新加载课程章节
        await loadCourseData()
        ElMessage.success('章节已删除')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除章节失败: ' + (error.message || '未知错误'))
        }
      }
    }
    
    onMounted(() => {
      loadCourseData()
      
      // 初始化时也设置容器，减少ResizeObserver错误
      setTimeout(() => {
        setupScrollContainer('.el-tabs__content')
      }, 500)
    })
    
    return {
      loading,
      loadingStudents,
      loadingAssignments,
      loadingDiscussions,
      activeTab,
      activeSection,
      addStudentsDialogVisible,
      studentSearchQuery,
      selectedStudents,
      resourceDialogVisible,
      currentResource,
      sectionDialogVisible,
      currentSection,
      resourceFormDialogVisible,
      currentSectionId,
      isFixedHeight,
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
      removeStudent,
      goBack,
      getItemType,
      getStatusType,
      getStatusText,
      viewResource,
      viewAssignment,
      viewDiscussion,
      viewStudentProgress,
      showAddSectionDialog,
      showAddResourceDialog,
      showAddAssignmentDialog,
      showAddDiscussionDialog,
      handleResourceUpdated,
      handleSectionSubmit,
      handleResourceSubmit,
      handleTabClick,
      resourceFormRef,
      closeResourceFormDialog,
      handleResourceDialogClose,
      confirmDeleteResource,
      confirmDeleteSection
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

.section-title-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex: 1;
}

.section-title-wrapper button {
  margin-left: 20px;
}

.timeline-item-content {
  width: 100%;
}

.item-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-top: 10px;
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

.progress-info {
  margin-bottom: 20px;
}

.progress-text {
  margin-top: 5px;
  font-size: 13px;
  color: #909399;
  text-align: right;
}

.section-items {
  margin-top: 15px;
  min-height: 200px;
}

.item-card {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  transition: all 0.3s;
  min-height: 80px;
  height: auto;
  overflow: hidden;
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

/* 新增CSS样式，优化布局减少ResizeObserver错误 */
.static-content-container {
  position: relative;
  min-height: 400px;
  overflow: auto;
  margin-bottom: 20px;
}

/* 为el-tabs组件添加固定高度 */
.el-tabs__content {
  min-height: 500px;
  position: relative;
}

/* 防止元素在标签页切换时的闪烁 */
.el-tabs__item {
  transition: color 0.15s !important;
}

/* 优化表格布局 */
.el-table {
  width: 100% !important;
}
</style> 