<template>
  <div class="discussion-list">
    <div class="discussion-header">
      <h3>课程讨论区</h3>
      <el-button 
        type="primary" 
        @click="showCreateDiscussionDialog"
      >
        发起讨论
      </el-button>
    </div>
    
    <div v-loading="loading">
      <div v-if="pinnedDiscussions.length > 0" class="pinned-discussions">
        <div class="section-title">
          <el-tag type="warning" effect="dark">置顶</el-tag>
        </div>
        
        <div class="discussion-items">
          <div 
            v-for="discussion in pinnedDiscussions" 
            :key="discussion.id"
            class="discussion-item"
            @click="viewDiscussion(discussion)"
          >
            <div class="discussion-main">
              <div class="discussion-title">
                <span class="pinned-icon">📌</span>
                {{ discussion.title }}
              </div>
              <div class="discussion-meta">
                <span class="user-info">
                  {{ discussion.user.username }}
                  <el-tag v-if="discussion.user.role === 'teacher'" size="small" type="success">教师</el-tag>
                </span>
                <span class="post-time">{{ formatDate(discussion.created_at) }}</span>
                <span class="replies-count">{{ discussion.replies_count }} 回复</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="regular-discussions">
        <div v-if="pinnedDiscussions.length > 0" class="section-title">
          <span>全部话题</span>
        </div>
        
        <div class="discussion-items">
          <div 
            v-for="discussion in regularDiscussions" 
            :key="discussion.id"
            class="discussion-item"
            @click="viewDiscussion(discussion)"
          >
            <div class="discussion-main">
              <div class="discussion-title">
                {{ discussion.title }}
              </div>
              <div class="discussion-meta">
                <span class="user-info">
                  {{ discussion.user.username }}
                  <el-tag v-if="discussion.user.role === 'teacher'" size="small" type="success">教师</el-tag>
                </span>
                <span class="post-time">{{ formatDate(discussion.created_at) }}</span>
                <span class="replies-count">{{ discussion.replies_count }} 回复</span>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="discussions.length === 0 && !loading" class="no-discussions">
          <el-empty description="暂无讨论话题"></el-empty>
        </div>
      </div>
    </div>
    
    <!-- 创建讨论对话框 -->
    <el-dialog 
      v-model="createDialogVisible" 
      title="发起讨论" 
      width="600px"
      destroy-on-close
    >
      <el-form 
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入讨论标题"></el-input>
        </el-form-item>
        
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="5"
            placeholder="请输入讨论内容"
          ></el-input>
        </el-form-item>
        
        <el-form-item v-if="isTeacher">
          <el-checkbox v-model="form.is_pinned">置顶此讨论</el-checkbox>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="createDiscussion"
          :loading="submitting"
        >
          发布讨论
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 查看讨论详情对话框 -->
    <el-dialog 
      v-model="detailDialogVisible" 
      :title="currentDiscussion.title" 
      width="800px"
      destroy-on-close
    >
      <div v-loading="loadingDetail" class="discussion-detail">
        <div v-if="currentDiscussion.id" class="discussion-content">
          <div class="author-info">
            <span class="author-name">
              {{ currentDiscussion.user?.username }}
              <el-tag v-if="currentDiscussion.user?.role === 'teacher'" size="small" type="success">教师</el-tag>
            </span>
            <span class="post-time">{{ formatDate(currentDiscussion.created_at) }}</span>
          </div>
          
          <div class="content-text">
            {{ currentDiscussion.content }}
          </div>
          
          <el-divider>回复 ({{ currentDiscussion.replies?.length || 0 }})</el-divider>
          
          <div v-if="currentDiscussion.replies && currentDiscussion.replies.length > 0" class="replies-list">
            <div 
              v-for="reply in currentDiscussion.replies" 
              :key="reply.id"
              class="reply-item"
            >
              <div class="reply-author">
                <span class="author-name">
                  {{ reply.user?.username }}
                  <el-tag v-if="reply.user?.role === 'teacher'" size="small" type="success">教师</el-tag>
                </span>
                <span class="reply-time">{{ formatDate(reply.created_at) }}</span>
              </div>
              <div class="reply-content">
                {{ reply.content }}
              </div>
            </div>
          </div>
          
          <div v-else class="no-replies">
            <p>暂无回复</p>
          </div>
          
          <el-divider>发表回复</el-divider>
          
          <div class="reply-form">
            <el-input
              v-model="replyContent"
              type="textarea"
              :rows="3"
              placeholder="请输入回复内容"
            ></el-input>
            
            <div class="reply-actions">
              <el-button 
                type="primary" 
                @click="submitReply"
                :loading="submittingReply"
                :disabled="!replyContent.trim()"
              >
                提交回复
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { courseAPI } from '@/services/api'
import { useStore } from 'vuex'

export default {
  name: 'DiscussionList',
  props: {
    courseId: {
      type: [Number, String],
      required: true
    }
  },
  setup(props) {
    const store = useStore()
    const loading = ref(false)
    const loadingDetail = ref(false)
    const submitting = ref(false)
    const submittingReply = ref(false)
    const discussions = ref([])
    const currentDiscussion = ref({})
    const createDialogVisible = ref(false)
    const detailDialogVisible = ref(false)
    const formRef = ref(null)
    const replyContent = ref('')
    
    // 获取当前用户
    const currentUser = computed(() => store.state.auth.user || {})
    
    // 判断是否为教师
    const isTeacher = computed(() => currentUser.value.role === 'teacher')
    
    // 置顶讨论
    const pinnedDiscussions = computed(() => 
      discussions.value.filter(discussion => discussion.is_pinned)
    )
    
    // 普通讨论
    const regularDiscussions = computed(() => 
      discussions.value.filter(discussion => !discussion.is_pinned)
    )
    
    // 表单数据
    const form = ref({
      title: '',
      content: '',
      is_pinned: false
    })
    
    // 表单验证规则
    const rules = {
      title: [
        { required: true, message: '请输入讨论标题', trigger: 'blur' },
        { min: 2, max: 100, message: '长度在2到100个字符之间', trigger: 'blur' }
      ],
      content: [
        { required: true, message: '请输入讨论内容', trigger: 'blur' }
      ]
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
    
    // 加载讨论列表
    const loadDiscussions = async () => {
      loading.value = true
      try {
        const response = await courseAPI.getCourseDiscussions(props.courseId)
        discussions.value = response.data.discussions || []
      } catch (error) {
        console.error('获取讨论失败:', error)
        ElMessage.error('获取讨论列表失败')
        discussions.value = []
      } finally {
        loading.value = false
      }
    }
    
    // 显示创建讨论对话框
    const showCreateDiscussionDialog = () => {
      createDialogVisible.value = true
      form.value = {
        title: '',
        content: '',
        is_pinned: false
      }
    }
    
    // 创建讨论
    const createDiscussion = async () => {
      if (!formRef.value) return
      
      try {
        await formRef.value.validate()
        
        submitting.value = true
        const discussionData = {
          ...form.value,
          course_id: props.courseId,
          user_id: currentUser.value.id
        }
        
        try {
          await courseAPI.createCourseDiscussion(props.courseId, discussionData)
          
          ElMessage.success('讨论创建成功')
          createDialogVisible.value = false
          await loadDiscussions()
        } catch (apiError) {
          console.error('创建讨论失败:', apiError)
          // 使用模拟数据（如果API未实现）
          const mockedDiscussion = {
            id: Date.now(),
            course_id: props.courseId,
            user_id: currentUser.value.id,
            user: {
              id: currentUser.value.id,
              username: currentUser.value.username,
              role: currentUser.value.role
            },
            title: form.value.title,
            content: form.value.content,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            is_pinned: form.value.is_pinned,
            replies_count: 0
          }
          
          discussions.value.unshift(mockedDiscussion)
          ElMessage.success('讨论创建成功(模拟)')
          createDialogVisible.value = false
        }
      } catch (error) {
        console.error('表单验证失败:', error)
      } finally {
        submitting.value = false
      }
    }
    
    // 查看讨论详情
    const viewDiscussion = async (discussion) => {
      currentDiscussion.value = { ...discussion }
      detailDialogVisible.value = true
      loadingDetail.value = true
      
      try {
        const response = await courseAPI.getCourseDiscussion(props.courseId, discussion.id)
        currentDiscussion.value = response.data.discussion || discussion
      } catch (error) {
        console.error('获取讨论详情失败:', error)
        
        // 使用模拟数据（如果API未实现）
        currentDiscussion.value = {
          ...discussion,
          replies: []
        }
        
        ElMessage.warning('使用模拟数据显示讨论详情')
      } finally {
        loadingDetail.value = false
      }
    }
    
    // 提交回复
    const submitReply = async () => {
      if (!replyContent.value.trim() || !currentDiscussion.value.id) return
      
      submittingReply.value = true
      try {
        const replyData = {
          discussion_id: currentDiscussion.value.id,
          user_id: currentUser.value.id,
          content: replyContent.value.trim()
        }
        
        try {
          await courseAPI.createDiscussionReply(props.courseId, currentDiscussion.value.id, replyData)
          
          // 重新加载讨论详情
          await viewDiscussion(currentDiscussion.value)
          ElMessage.success('回复已提交')
          replyContent.value = ''
        } catch (apiError) {
          console.error('提交回复失败:', apiError)
          
          // 使用模拟数据（如果API未实现）
          const mockedReply = {
            id: Date.now(),
            discussion_id: currentDiscussion.value.id,
            user_id: currentUser.value.id,
            user: {
              id: currentUser.value.id,
              username: currentUser.value.username,
              role: currentUser.value.role
            },
            content: replyContent.value.trim(),
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          }
          
          if (!currentDiscussion.value.replies) {
            currentDiscussion.value.replies = []
          }
          
          currentDiscussion.value.replies.push(mockedReply)
          currentDiscussion.value.replies_count = (currentDiscussion.value.replies_count || 0) + 1
          
          // 更新列表中的回复计数
          const listIndex = discussions.value.findIndex(d => d.id === currentDiscussion.value.id)
          if (listIndex !== -1) {
            discussions.value[listIndex].replies_count = currentDiscussion.value.replies_count
          }
          
          ElMessage.success('回复已提交(模拟)')
          replyContent.value = ''
        }
      } finally {
        submittingReply.value = false
      }
    }
    
    onMounted(() => {
      loadDiscussions()
    })
    
    return {
      loading,
      loadingDetail,
      discussions,
      pinnedDiscussions,
      regularDiscussions,
      currentDiscussion,
      submitting,
      submittingReply,
      createDialogVisible,
      detailDialogVisible,
      formRef,
      form,
      rules,
      replyContent,
      currentUser,
      isTeacher,
      formatDate,
      showCreateDiscussionDialog,
      createDiscussion,
      viewDiscussion,
      submitReply
    }
  }
}
</script>

<style scoped>
.discussion-list {
  margin-bottom: 20px;
}

.discussion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  margin: 15px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.discussion-items {
  margin-bottom: 20px;
}

.discussion-item {
  padding: 15px;
  margin-bottom: 10px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
}

.discussion-item:hover {
  background-color: #f5f7fa;
}

.discussion-main {
  flex: 1;
}

.discussion-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 8px;
}

.pinned-icon {
  margin-right: 5px;
}

.discussion-meta {
  font-size: 13px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 5px;
}

.post-time, .replies-count {
  white-space: nowrap;
}

.no-discussions {
  margin-top: 40px;
}

/* 详情样式 */
.discussion-detail {
  min-height: 200px;
}

.discussion-content {
  margin-bottom: 20px;
}

.author-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.author-name {
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 5px;
}

.content-text {
  line-height: 1.6;
  margin-bottom: 20px;
  white-space: pre-wrap;
}

.replies-list {
  margin: 20px 0;
}

.reply-item {
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}

.reply-item:last-child {
  border-bottom: none;
}

.reply-author {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.reply-time {
  font-size: 13px;
  color: #909399;
}

.reply-content {
  white-space: pre-wrap;
  line-height: 1.5;
}

.reply-form {
  margin-top: 20px;
}

.reply-actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.no-replies {
  text-align: center;
  color: #909399;
  padding: 20px 0;
}
</style> 