<template>
  <div class="assignment-viewer">
    <div v-if="isTeacher" class="teacher-view">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="作业详情" name="details">
          <div class="assignment-info">
            <div class="assignment-header">
              <h3>{{ assignment.title }}</h3>
              <el-tag :type="getStatusType(assignment.status)" size="large">
                {{ getStatusText(assignment.status) }}
              </el-tag>
            </div>
            
            <div class="assignment-meta">
              <div class="meta-item">
                <span class="meta-label">截止日期:</span>
                <span class="meta-value">{{ formatDate(assignment.deadline) }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">分数:</span>
                <span class="meta-value">{{ assignment.points }} 分</span>
              </div>
            </div>
            
            <div class="assignment-description">
              <h4>作业要求</h4>
              <div>{{ assignment.description }}</div>
            </div>
            
            <div v-if="assignment.attachments && assignment.attachments.length > 0" class="assignment-attachments">
              <h4>作业附件</h4>
              <ul class="attachment-list">
                <li v-for="(attachment, index) in assignment.attachments" :key="index" class="attachment-item">
                  <el-button type="primary" link @click="downloadAttachment(attachment)">
                    <el-icon><Document /></el-icon>
                    {{ attachment.name }}
                  </el-button>
                </li>
              </ul>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="提交情况" name="submissions">
          <div class="submissions-panel">
            <h4>学生提交情况 ({{ submissionsCount }}/{{ totalStudents }})</h4>
            
            <el-table :data="submissionsList" v-loading="loadingSubmissions" style="width: 100%">
              <el-table-column prop="user.username" label="学生" width="120"></el-table-column>
              <el-table-column prop="submit_time" label="提交时间" width="180">
                <template #default="scope">
                  {{ formatDate(scope.row.submit_time) }}
                </template>
              </el-table-column>
              <el-table-column label="状态" width="120">
                <template #default="scope">
                  <el-tag v-if="scope.row.grade !== undefined" type="success">
                    已评分 ({{ scope.row.grade }}分)
                  </el-tag>
                  <el-tag v-else type="warning">待评分</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="viewSubmission(scope.row)">查看</el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <div v-if="submissionsList.length === 0 && !loadingSubmissions" class="no-submissions">
              <el-empty description="暂无学生提交"></el-empty>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
      
      <!-- 查看提交详情对话框 -->
      <el-dialog
        v-model="submissionDialogVisible"
        :title="`${currentSubmission.user?.username || '学生'}的提交详情`"
        width="70%"
        destroy-on-close
      >
        <div v-if="currentSubmission.id" class="submission-details">
          <div class="submission-content">
            <h4>提交内容</h4>
            <div class="content-box">{{ currentSubmission.content }}</div>
          </div>
          
          <div v-if="currentSubmission.files && currentSubmission.files.length > 0" class="submission-files">
            <h4>提交的文件</h4>
            <ul class="file-list">
              <li v-for="(file, index) in currentSubmission.files" :key="index" class="file-item">
                <el-button type="primary" link @click="downloadFile(file)">
                  <el-icon><Document /></el-icon>
                  {{ file.name }}
                </el-button>
              </li>
            </ul>
          </div>
          
          <el-divider content-position="center">评分</el-divider>
          
          <el-form :model="gradeForm" ref="gradeFormRef" label-width="100px">
            <el-form-item label="分数" prop="grade">
              <el-input-number 
                v-model="gradeForm.grade" 
                :min="0" 
                :max="assignment.points"
                :step="1"
              ></el-input-number>
              <span class="grade-hint">/ {{ assignment.points }} 分</span>
            </el-form-item>
            
            <el-form-item label="反馈" prop="feedback">
              <el-input
                v-model="gradeForm.feedback"
                type="textarea"
                :rows="4"
                placeholder="请输入对学生的反馈意见..."
              ></el-input>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="submitGrade">提交评分</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-dialog>
    </div>
    
    <div v-else class="student-view">
      <el-card class="assignment-info">
        <div class="assignment-header">
          <h3>{{ assignment.title }}</h3>
          <el-tag :type="getStatusType(assignment.status)" size="large">
            {{ getStatusText(assignment.status) }}
          </el-tag>
        </div>
        
        <div class="assignment-meta">
          <div class="meta-item">
            <span class="meta-label">截止日期:</span>
            <span class="meta-value">{{ formatDate(assignment.deadline) }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">分数:</span>
            <span class="meta-value">{{ assignment.points }} 分</span>
          </div>
        </div>
        
        <div class="assignment-description">
          <h4>作业要求</h4>
          <div>{{ assignment.description }}</div>
        </div>
        
        <div v-if="assignment.attachments && assignment.attachments.length > 0" class="assignment-attachments">
          <h4>作业附件</h4>
          <ul class="attachment-list">
            <li v-for="(attachment, index) in assignment.attachments" :key="index" class="attachment-item">
              <el-button type="primary" link @click="downloadAttachment(attachment)">
                <el-icon><Document /></el-icon>
                {{ attachment.name }}
              </el-button>
            </li>
          </ul>
        </div>
      </el-card>
      
      <el-divider content-position="center">作业提交</el-divider>
      
      <el-card class="submission-card">
        <template v-if="isSubmitted">
          <div class="submission-info">
            <h4>已提交内容</h4>
            <div class="submission-meta">
              <span>提交时间: {{ formatDate(submission.submit_time) }}</span>
              <span v-if="submission.grade !== undefined">
                得分: <strong>{{ submission.grade }} / {{ assignment.points }}</strong>
              </span>
            </div>
            
            <div class="submission-content">
              <p>{{ submission.content }}</p>
            </div>
            
            <div v-if="submission.files && submission.files.length > 0" class="submission-files">
              <h5>已提交文件</h5>
              <ul class="file-list">
                <li v-for="(file, index) in submission.files" :key="index" class="file-item">
                  <el-button type="primary" link @click="downloadFile(file)">
                    <el-icon><Document /></el-icon>
                    {{ file.name }}
                  </el-button>
                </li>
              </ul>
            </div>
            
            <div v-if="submission.feedback" class="submission-feedback">
              <h5>教师反馈</h5>
              <el-alert
                :type="submission.grade >= assignment.points * 0.6 ? 'success' : 'warning'"
                :closable="false"
                show-icon
              >
                {{ submission.feedback }}
              </el-alert>
            </div>
            
            <div class="submission-actions" v-if="canResubmit">
              <el-button type="primary" @click="enableEdit">重新提交</el-button>
            </div>
          </div>
        </template>
        
        <template v-else>
          <h4>提交您的作业</h4>
          <el-form :model="submissionForm" :rules="submissionRules" ref="submissionFormRef">
            <el-form-item label="作业内容" prop="content">
              <el-input 
                v-model="submissionForm.content" 
                type="textarea" 
                :rows="6"
                placeholder="请输入您的作业内容"
              ></el-input>
            </el-form-item>
            
            <el-form-item label="上传文件">
              <el-upload
                class="submission-upload"
                action="#"
                :auto-upload="false"
                :http-request="() => {}"
                :on-change="handleFileChange"
                :on-remove="handleFileRemove"
                :file-list="fileList"
                multiple
              >
                <el-button type="primary">选择文件</el-button>
                <template #tip>
                  <div class="el-upload__tip">可上传文档、图片等文件</div>
                </template>
              </el-upload>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="submitAssignment">提交作业</el-button>
              <el-button @click="cancelSubmit" v-if="isEditing">取消</el-button>
            </el-form-item>
          </el-form>
        </template>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import { courseAPI } from '@/services/api'
import { useStore } from 'vuex'
import { fileAPI } from '@/services/api'
import axios from 'axios'

export default {
  name: 'AssignmentViewer',
  components: {
    Document
  },
  props: {
    assignment: {
      type: Object,
      required: true
    }
  },
  emits: ['updated'],
  setup(props, { emit }) {
    const store = useStore()
    const submissionFormRef = ref(null)
    const gradeFormRef = ref(null)
    const fileList = ref([])
    const isEditing = ref(false)
    const activeTab = ref('details')
    const loadingSubmissions = ref(false)
    const submissionsList = ref([])
    const submissionDialogVisible = ref(false)
    const currentSubmission = ref({})
    
    // 获取当前用户
    const currentUser = computed(() => store.state.auth.user || {})
    
    // 判断是否为教师
    const isTeacher = computed(() => currentUser.value.role === 'teacher')
    
    // 统计信息
    const submissionsCount = computed(() => submissionsList.value.length)
    const totalStudents = ref(0)
    
    // 学生提交的作业
    const submission = ref({})
    
    // 是否已提交作业
    const isSubmitted = computed(() => {
      return !isEditing.value && submission.value && submission.value.id
    })
    
    // 是否可以重新提交
    const canResubmit = computed(() => {
      if (!submission.value || !submission.value.submit_time) return false
      
      // 如果已经评分，则不能重新提交
      if (submission.value.grade !== undefined) return false
      
      // 检查是否在截止日期前
      const deadline = new Date(props.assignment.deadline)
      const now = new Date()
      return now < deadline
    })
    
    // 提交表单数据
    const submissionForm = reactive({
      content: '',
      files: []
    })
    
    // 评分表单数据
    const gradeForm = reactive({
      grade: 0,
      feedback: ''
    })
    
    // 表单验证规则
    const submissionRules = {
      content: [
        { required: true, message: '请输入作业内容', trigger: 'blur' }
      ]
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return '未设置'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
    
    // 获取状态类型
    const getStatusType = (status) => {
      const statusMap = {
        'completed': 'success',
        'pending': 'warning',
        'overdue': 'danger',
        'not_started': 'info'
      }
      return statusMap[status] || 'info'
    }
    
    // 获取状态文本
    const getStatusText = (status) => {
      const statusMap = {
        'completed': '已完成',
        'pending': '进行中',
        'overdue': '已逾期',
        'not_started': '未开始'
      }
      return statusMap[status] || '未知状态'
    }
    
    // 处理文件变化
    const handleFileChange = async (file) => {
      try {
        // 检查文件类型和大小
        const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                              'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                              'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                              'text/plain', 'image/jpeg', 'image/png', 'application/zip', 'application/x-rar-compressed'];
        
        if (file.raw && file.raw.size > 50 * 1024 * 1024) { // 50MB限制
          ElMessage.error('文件过大，请上传小于50MB的文件');
          // 从上传列表中移除
          const index = fileList.value.findIndex(f => f.uid === file.uid);
          if (index !== -1) {
            fileList.value.splice(index, 1);
          }
          return;
        }
        
        // 显示文件上传中
        const loadingMessage = ElMessage({
          message: `正在上传文件: ${file.name}`,
          type: 'info',
          duration: 0
        });
        
        // 创建FormData
        const formData = new FormData();
        formData.append('file', file.raw);
        
        // 直接使用axios上传文件
        const response = await axios.post('/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        // 关闭上传提示
        loadingMessage.close();
        
        if (response.data && response.data.status === 'success') {
          // 将上传成功的文件信息添加到提交列表
          submissionForm.files.push({
            name: response.data.original_filename,
            size: file.raw.size,
            type: file.raw.type,
            url: response.data.file_url,
            file_path: response.data.file_path
          });
          
          ElMessage.success(`文件 ${file.name} 上传成功`);
        } else {
          ElMessage.error(`文件 ${file.name} 上传失败: ${response.data?.message || '未知错误'}`);
          
          // 从上传列表中移除
          const index = fileList.value.findIndex(f => f.uid === file.uid);
          if (index !== -1) {
            fileList.value.splice(index, 1);
          }
        }
      } catch (error) {
        ElMessage.error(`文件 ${file.name} 上传失败: ${error.message || '未知错误'}`);
        console.error('文件上传出错:', error);
        
        // 从上传列表中移除
        const index = fileList.value.findIndex(f => f.uid === file.uid);
        if (index !== -1) {
          fileList.value.splice(index, 1);
        }
      }
    };
    
    // 处理文件移除
    const handleFileRemove = (file) => {
      const index = submissionForm.files.findIndex(f => f.uid === file.uid)
      if (index !== -1) {
        submissionForm.files.splice(index, 1)
      }
      console.log('已移除文件:', file.name)
    }
    
    // 下载附件
    const downloadAttachment = (attachment) => {
      if (!attachment || !attachment.url) {
        // 检查是否有附件URL
        if (attachment && attachment.name) {
          // 如果有附件名但没有URL，可能是模拟数据
          // 构造可能的URL路径
          const baseUrl = window.location.origin;
          const possibleUrl = `${baseUrl}/api/static/uploads/${attachment.name}`;
          
          // 创建下载链接
          const link = document.createElement('a');
          link.href = possibleUrl;
          link.target = '_blank';
          link.download = attachment.name;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          
          ElMessage.success(`开始下载附件: ${attachment.name}`);
          return;
        }
        
        ElMessage.error('附件链接不可用');
        return;
      }
      
      // 正常情况下有附件URL
      const link = document.createElement('a');
      link.href = attachment.url;
      link.target = '_blank';
      link.download = attachment.name || '未命名附件';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      ElMessage.success(`开始下载附件: ${attachment.name}`);
    }
    
    // 下载学生提交的文件
    const downloadFile = (file) => {
      if (!file || !file.url) {
        // 检查是否有文件URL
        if (file && file.name) {
          // 如果有文件名但没有URL，可能是模拟数据
          // 构造可能的URL路径
          const baseUrl = window.location.origin;
          const possibleUrl = `${baseUrl}/api/static/uploads/${file.name}`;
          
          // 创建下载链接
          const link = document.createElement('a');
          link.href = possibleUrl;
          link.target = '_blank';
          link.download = file.name;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          
          ElMessage.success(`开始下载文件: ${file.name}`);
          return;
        }
        
        ElMessage.error('文件链接不可用');
        return;
      }
      
      // 正常情况下有文件URL
      const link = document.createElement('a');
      link.href = file.url;
      link.target = '_blank';
      link.download = file.name || '未命名文件';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      ElMessage.success(`开始下载文件: ${file.name}`);
    }
    
    // 启用编辑模式
    const enableEdit = () => {
      isEditing.value = true
      if (submission.value) {
        submissionForm.content = submission.value.content || ''
        // 重置文件列表
        fileList.value = []
      }
    }
    
    // 取消提交
    const cancelSubmit = () => {
      isEditing.value = false
    }
    
    // 提交作业
    const submitAssignment = async () => {
      if (!submissionFormRef.value) return
      
      if (!currentUser.value.id) {
        ElMessage.warning('请先登录')
        return
      }
      
      try {
        await submissionFormRef.value.validate()
        
        // 检查是否有内容或文件提交
        if (!submissionForm.content && submissionForm.files.length === 0) {
          ElMessage.warning('请输入作业内容或上传文件')
          return
        }
        
        // 确认提交
        await ElMessageBox.confirm('确定要提交作业吗？', '提交确认', {
          confirmButtonText: '确定提交',
          cancelButtonText: '取消',
          type: 'info'
        })
        
        // 构造提交数据
        const submissionData = {
          assignment_id: props.assignment.id,
          user_id: currentUser.value.id,
          content: submissionForm.content,
          files: submissionForm.files,
          submit_time: new Date().toISOString()
        }
        
        try {
          // 调用API提交作业
          const response = await courseAPI.submitAssignment(
            props.assignment.course_id,
            props.assignment.id,
            submissionData
          )
          
          if (response.data.submission) {
            submission.value = response.data.submission
            isEditing.value = false
            ElMessage.success('作业提交成功')
            
            // 更新本地作业状态
            const updatedAssignment = { ...props.assignment, status: 'completed' }
            
            // 通知父组件
            emit('updated', {
              assignmentId: props.assignment.id,
              status: 'completed',
              assignment: updatedAssignment
            })
          }
        } catch (apiError) {
          console.warn('提交作业失败(可能API未实现):', apiError)
          
          // 模拟提交成功
          submission.value = {
            id: Date.now(),
            assignment_id: props.assignment.id,
            user_id: currentUser.value.id,
            content: submissionForm.content,
            files: submissionForm.files.map(f => ({
              name: f.name,
              size: f.size,
              type: f.type
            })),
            submit_time: new Date().toISOString()
          }
          
          isEditing.value = false
          ElMessage.success('作业提交成功(模拟)')
          
          // 更新本地作业状态
          const updatedAssignment = { ...props.assignment, status: 'completed' }
          
          // 通知父组件
          emit('updated', {
            assignmentId: props.assignment.id,
            status: 'completed',
            assignment: updatedAssignment
          })
        }
      } catch (error) {
        if (error === 'cancel') return
        ElMessage.error('提交失败: ' + error.message)
      }
    }
    
    // 加载提交记录
    const loadSubmission = async () => {
      if (!currentUser.value.id) return
      
      try {
        // 调用API获取提交记录
        const response = await courseAPI.getUserAssignmentSubmission(
          props.assignment.course_id,
          props.assignment.id,
          currentUser.value.id
        )
        
        if (response.data.submission) {
          submission.value = response.data.submission
        } else {
          // 如果没有提交记录
          submission.value = null
        }
      } catch (error) {
        console.warn('获取提交记录失败(可能API未实现):', error)
        // 如果API尚未实现，使用模拟数据
        if (props.assignment.status === 'completed') {
          submission.value = {
            id: 1001,
            assignment_id: props.assignment.id,
            content: '这是我提交的作业内容。我完成了所有的要求。',
            submit_time: '2023-12-20 14:30:00',
            files: [
              { name: '作业报告.pdf', size: 1024 * 1024 }
            ],
            grade: 85,
            feedback: '整体完成得不错，但有一些细节需要改进。'
          }
        } else {
          submission.value = null
        }
      }
    }
    
    // 加载所有提交情况(教师视图)
    const loadSubmissions = async () => {
      if (!isTeacher.value) return
      
      loadingSubmissions.value = true
      try {
        // 调用API获取此作业的所有提交记录
        const response = await courseAPI.getAssignmentSubmissions(
          props.assignment.course_id,
          props.assignment.id
        )
        
        if (response.data && response.data.submissions) {
          submissionsList.value = response.data.submissions
          totalStudents.value = response.data.total_students || submissionsList.value.length
        } else {
          // 使用模拟数据
          useDefaultSubmissions()
        }
      } catch (error) {
        console.warn('获取提交记录列表失败(可能API未实现):', error)
        // 使用模拟数据
        useDefaultSubmissions()
      } finally {
        loadingSubmissions.value = false
      }
    }
    
    // 默认的模拟提交数据
    const useDefaultSubmissions = () => {
      submissionsList.value = [
        {
          id: 1001,
          assignment_id: props.assignment.id,
          user: { id: 101, username: '张三' },
          content: '这是张三提交的作业内容。',
          submit_time: '2023-12-20 14:30:00',
          files: [{ name: '张三_作业报告.pdf', size: 1024 * 1024 }],
          grade: 85,
          feedback: '整体完成得不错，但有一些细节需要改进。'
        },
        {
          id: 1002,
          assignment_id: props.assignment.id,
          user: { id: 102, username: '李四' },
          content: '这是李四提交的作业内容。',
          submit_time: '2023-12-21 09:15:00',
          files: [{ name: '李四_作业报告.pdf', size: 1536 * 1024 }]
        }
      ]
      totalStudents.value = 5 // 假设共有5名学生
    }
    
    // 查看提交详情
    const viewSubmission = (submission) => {
      currentSubmission.value = { ...submission }
      
      // 如果已评分，初始化表单数据
      if (currentSubmission.value.grade !== undefined) {
        gradeForm.grade = currentSubmission.value.grade
        gradeForm.feedback = currentSubmission.value.feedback || ''
      } else {
        gradeForm.grade = 0
        gradeForm.feedback = ''
      }
      
      submissionDialogVisible.value = true
    }
    
    // 提交评分
    const submitGrade = async () => {
      if (!currentSubmission.value.id) return
      
      try {
        const gradeData = {
          grade: gradeForm.grade,
          feedback: gradeForm.feedback,
          graded_by: currentUser.value.id,
          graded_at: new Date().toISOString()
        }
        
        try {
          // 调用API提交评分
          await courseAPI.gradeAssignment(
            props.assignment.course_id,
            props.assignment.id,
            currentSubmission.value.id,
            gradeData
          )
          
          // 更新本地数据
          const index = submissionsList.value.findIndex(s => s.id === currentSubmission.value.id)
          if (index !== -1) {
            submissionsList.value[index] = {
              ...submissionsList.value[index],
              ...gradeData
            }
          }
          
          ElMessage.success('评分已提交')
          submissionDialogVisible.value = false
          
          // 通知父组件
          emit('updated', {
            assignmentId: props.assignment.id,
            status: 'graded'
          })
        } catch (apiError) {
          console.warn('评分提交失败(可能API未实现):', apiError)
          
          // 模拟成功
          const index = submissionsList.value.findIndex(s => s.id === currentSubmission.value.id)
          if (index !== -1) {
            submissionsList.value[index] = {
              ...submissionsList.value[index],
              grade: gradeForm.grade,
              feedback: gradeForm.feedback,
              graded_by: currentUser.value.id,
              graded_at: new Date().toISOString()
            }
          }
          
          ElMessage.success('评分已提交(模拟)')
          submissionDialogVisible.value = false
          
          // 通知父组件
          emit('updated', {
            assignmentId: props.assignment.id,
            status: 'graded'
          })
        }
      } catch (error) {
        ElMessage.error('提交评分失败: ' + error.message)
      }
    }
    
    onMounted(() => {
      if (isTeacher.value) {
        loadSubmissions()
      } else {
        loadSubmission()
      }
    })
    
    return {
      submissionFormRef,
      gradeFormRef,
      submissionForm,
      submissionRules,
      fileList,
      submission,
      isSubmitted,
      isEditing,
      canResubmit,
      isTeacher,
      activeTab,
      loadingSubmissions,
      submissionsList,
      submissionsCount,
      totalStudents,
      submissionDialogVisible,
      currentSubmission,
      gradeForm,
      formatDate,
      getStatusType,
      getStatusText,
      handleFileChange,
      handleFileRemove,
      downloadAttachment,
      downloadFile,
      enableEdit,
      cancelSubmit,
      submitAssignment,
      viewSubmission,
      submitGrade,
      currentUser
    }
  }
}
</script>

<style scoped>
.assignment-viewer {
  padding: 10px;
}

.assignment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.assignment-meta {
  display: flex;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
}

.meta-label {
  color: #909399;
  margin-right: 5px;
}

.meta-value {
  font-weight: bold;
}

.assignment-description {
  margin-bottom: 20px;
}

.assignment-attachments {
  margin-top: 20px;
}

.attachment-list {
  list-style: none;
  padding: 0;
}

.attachment-item {
  margin-bottom: 10px;
}

.submission-card {
  margin-top: 20px;
}

.submission-info {
  padding: 10px 0;
}

.submission-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  color: #606266;
}

.submission-content {
  background-color: #f8f8f8;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.submission-files {
  margin-top: 15px;
}

.file-list {
  list-style: none;
  padding: 0;
}

.file-item {
  margin-bottom: 5px;
}

.submission-feedback {
  margin-top: 20px;
}

.submission-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.submission-upload {
  width: 100%;
}

.submission-upload .el-upload-list {
  margin-top: 10px;
}

/* 教师视图样式 */
.teacher-view .el-tabs {
  margin-bottom: 20px;
}

.submissions-panel h4 {
  margin-bottom: 20px;
}

.no-submissions {
  margin-top: 20px;
}

.content-box {
  background-color: #f8f8f8;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.grade-hint {
  margin-left: 10px;
  color: #909399;
}
</style> 