<template>
  <div class="resource-viewer">
    <div class="resource-header">
      <h3>{{ resource.title }}</h3>
      <el-tag :type="getResourceTypeTag(resource.resource_type)">
        {{ getResourceTypeText(resource.resource_type) }}
      </el-tag>
    </div>
    
    <div class="resource-description">
      {{ resource.description }}
    </div>
    
    <div class="resource-content">
      <!-- 文档类型资源 -->
      <div v-if="resource.resource_type === 'document'" class="document-viewer">
        <el-card class="markdown-content">
          <!-- 使用markdown渲染 -->
          <div v-html="renderedContent"></div>
        </el-card>
      </div>
      
      <!-- 视频类型资源 -->
      <div v-else-if="resource.resource_type === 'video'" class="video-viewer">
        <SafeVideoPlayer 
          :src="resource.content" 
          @timeupdate="handleTimeUpdate"
        />
      </div>
      
      <!-- 测验类型资源 -->
      <div v-else-if="resource.resource_type === 'quiz'" class="quiz-viewer">
        <div v-if="quiz" class="quiz-container">
          <el-card v-for="(question, index) in quiz.questions" :key="index" class="quiz-question">
            <h4>问题 {{ index + 1 }}: {{ question.question }}</h4>
            <el-radio-group v-model="answers[index]">
              <div v-for="(option, optIndex) in question.options" :key="optIndex" class="quiz-option">
                <el-radio :label="optIndex">{{ option }}</el-radio>
              </div>
            </el-radio-group>
          </el-card>
          
          <div class="quiz-actions">
            <el-button type="primary" @click="submitQuiz">提交</el-button>
          </div>
        </div>
        <div v-else class="quiz-error">
          测验数据加载失败
        </div>
      </div>
      
      <!-- 作业类型资源 -->
      <div v-else-if="resource.resource_type === 'assignment'" class="assignment-viewer">
        <div v-if="assignment" class="assignment-container">
          <el-card class="assignment-details">
            <h4>{{ assignment.title }}</h4>
            <p>{{ assignment.description }}</p>
            <div class="assignment-meta">
              <span>截止日期: {{ assignment.due_date }}</span>
            </div>
          </el-card>
          
          <div class="assignment-submission">
            <h4>提交作业</h4>
            <el-input
              v-model="submission.content"
              type="textarea"
              :rows="6"
              placeholder="输入作业内容..."
            ></el-input>
            <div class="submission-actions">
              <el-upload
                class="upload-area"
                action=""
                :auto-upload="false"
                :on-change="handleFileChange"
                :file-list="fileList"
              >
                <el-button type="primary">上传附件</el-button>
              </el-upload>
              <el-button type="success" @click="submitAssignment">提交作业</el-button>
            </div>
          </div>
        </div>
        <div v-else class="assignment-error">
          作业数据加载失败
        </div>
      </div>
      
      <!-- 文件类型资源 -->
      <div v-else-if="resource.resource_type === 'file'" class="file-resource">
        <h3>文件资源</h3>
        <div class="file-info">
          <el-icon><Document /></el-icon>
          <div class="file-name">
            {{ getFileName(resource.file_path) }}
          </div>
          <el-button type="primary" @click="downloadFile" size="small">
            <el-icon><Download /></el-icon> 下载文件
          </el-button>
        </div>
        <div class="file-description">
          {{ resource.description }}
        </div>
      </div>
      
      <!-- 其他类型资源 -->
      <div v-else class="unknown-resource-type">
        未知资源类型
      </div>
    </div>
    
    <!-- 进度标记按钮 -->
    <div class="resource-actions">
      <el-button 
        :type="resource.completed ? 'success' : 'primary'" 
        @click="toggleCompleted"
      >
        {{ resource.completed ? '标记为未完成' : '标记为已完成' }}
      </el-button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElIcon } from 'element-plus'
import { Document, Download } from '@element-plus/icons-vue'
import { marked } from 'marked'
import { useStore } from 'vuex'
import SafeVideoPlayer from '../common/SafeVideoPlayer.vue'
import { courseAPI } from '@/services/api'

export default {
  name: 'ResourceViewer',
  components: {
    SafeVideoPlayer,
    ElIcon,
    Document,
    Download
  },
  props: {
    resource: {
      type: Object,
      required: true
    }
  },
  emits: ['updated'],
  setup(props, { emit }) {
    const store = useStore()
    const currentUser = computed(() => store.state.auth.user || {})
    
    const renderedContent = computed(() => {
      if (props.resource.resource_type === 'document') {
        return marked(props.resource.content || '')
      }
      return ''
    })
    
    const isVideoUrl = computed(() => {
      const content = props.resource.content || ''
      return content.match(/\.(mp4|webm|ogg)$/) || content.startsWith('http')
    })
    
    const quiz = ref(null)
    const answers = ref([])
    
    const assignment = ref(null)
    const submission = ref({
      content: '',
      files: []
    })
    const fileList = ref([])
    
    // 解析资源内容
    const parseResourceContent = () => {
      if (props.resource.resource_type === 'quiz') {
        try {
          quiz.value = JSON.parse(props.resource.content || '{}')
          answers.value = new Array(quiz.value.questions.length).fill(null)
        } catch (e) {
          console.error('解析测验数据失败', e)
          quiz.value = null
        }
      } else if (props.resource.resource_type === 'assignment') {
        try {
          assignment.value = JSON.parse(props.resource.content || '{}')
        } catch (e) {
          console.error('解析作业数据失败', e)
          assignment.value = null
        }
      }
    }
    
    // 获取资源类型标签
    const getResourceTypeTag = (type) => {
      switch (type) {
        case 'document': return 'info'
        case 'video': return 'success'
        case 'quiz': return 'warning'
        case 'assignment': return 'danger'
        case 'file': return 'info'
        default: return 'info'
      }
    }
    
    // 获取资源类型文本
    const getResourceTypeText = (type) => {
      switch (type) {
        case 'document': return '文档'
        case 'video': return '视频'
        case 'quiz': return '测验'
        case 'assignment': return '作业'
        case 'file': return '文件'
        default: return '其他'
      }
    }
    
    // 处理视频进度更新
    const handleTimeUpdate = (currentTime) => {
      // TODO: 保存视频播放进度
      console.log('视频时间更新:', currentTime)
    }
    
    // 提交测验
    const submitQuiz = () => {
      if (answers.value.includes(null)) {
        ElMessage.warning('请回答所有问题')
        return
      }
      
      // TODO: 提交测验答案到后端
      ElMessage.success('测验提交成功')
    }
    
    // 处理文件上传变化
    const handleFileChange = (file) => {
      submission.value.files.push(file.raw)
    }
    
    // 提交作业
    const submitAssignment = () => {
      if (!submission.value.content && submission.value.files.length === 0) {
        ElMessage.warning('请输入作业内容或上传附件')
        return
      }
      
      // TODO: 提交作业到后端
      ElMessage.success('作业提交成功')
    }
    
    // 标记资源为已完成/未完成
    const toggleCompleted = async () => {
      try {
        if (!currentUser.value || !currentUser.value.id) {
          ElMessage.warning('请先登录')
          return
        }
        
        // 切换完成状态
        const updatedResource = {
          ...props.resource,
          completed: !props.resource.completed
        }
        
        // 调用API更新资源完成状态
        const progressData = {
          completed: updatedResource.completed,
          progress_percent: updatedResource.completed ? 100 : 0
        }
        
        await courseAPI.updateResourceProgress(
          currentUser.value.id, 
          updatedResource.id, 
          progressData
        )
        
        ElMessage.success(`标记资源为${updatedResource.completed ? '已完成' : '未完成'}`)
        
        // 通知父组件状态已更新
        emit('updated', updatedResource)
      } catch (error) {
        console.error('更新资源状态失败:', error)
        ElMessage.error('更新状态失败: ' + (error.response?.data?.message || error.message || '未知错误'))
      }
    }
    
    // 获取文件名
    const getFileName = (filePath) => {
      if (!filePath) return '未知文件';
      // 解析文件名，格式是 uuid_filename
      const parts = filePath.split('/');
      const filename = parts[parts.length - 1];
      const nameParts = filename.split('_');
      // 如果有UUID前缀，去掉它
      if (nameParts.length > 1) {
        return nameParts.slice(1).join('_');
      }
      return filename;
    };

    // 处理文件下载
    const downloadFile = () => {
      if (!props.resource.content) {
        ElMessage.error('文件链接不可用');
        return;
      }
      
      // 创建一个临时链接并点击它来下载
      const link = document.createElement('a');
      link.href = props.resource.content;
      link.target = '_blank';
      link.download = getFileName(props.resource.file_path);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    };
    
    onMounted(() => {
      parseResourceContent()
    })
    
    return {
      currentUser,
      renderedContent,
      isVideoUrl,
      quiz,
      answers,
      assignment,
      submission,
      fileList,
      getResourceTypeTag,
      getResourceTypeText,
      handleTimeUpdate,
      submitQuiz,
      handleFileChange,
      submitAssignment,
      toggleCompleted,
      getFileName,
      downloadFile
    }
  }
}
</script>

<style scoped>
.resource-viewer {
  padding: 20px;
}

.resource-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.resource-description {
  margin-bottom: 20px;
  color: #606266;
}

.resource-content {
  margin-bottom: 20px;
  /* 为内容区域设置最小高度，减少动态高度变化 */
  min-height: 300px;
}

.video-viewer {
  max-width: 800px;
  margin: 0 auto;
}

.markdown-content {
  padding: 20px;
}

.question-list {
  margin-top: 20px;
}

.question-item {
  margin-bottom: 25px;
}

.question-title {
  font-weight: 500;
  margin-bottom: 15px;
}

.option-list {
  margin-left: 20px;
}

.options-item {
  margin-bottom: 10px;
}

.quiz-question {
  margin-bottom: 20px;
}

.quiz-option {
  margin: 10px 0;
}

.quiz-actions, .submission-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.assignment-meta {
  margin-top: 10px;
  color: #909399;
}

.assignment-submission {
  margin-top: 20px;
}

.upload-area {
  margin-right: 20px;
}

.resource-actions {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

.file-resource {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 20px;
}

.file-info {
  display: flex;
  align-items: center;
  margin: 15px 0;
  padding: 10px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.file-info .el-icon {
  font-size: 24px;
  color: #409EFF;
  margin-right: 10px;
}

.file-name {
  flex: 1;
  font-weight: 500;
  margin-right: 15px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-description {
  margin-top: 15px;
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
}
</style> 