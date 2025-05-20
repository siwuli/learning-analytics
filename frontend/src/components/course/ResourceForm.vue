<template>
  <el-form 
    ref="formRef"
    :model="form"
    :rules="rules"
    label-position="top"
    class="resource-form"
  >
    <el-form-item label="资源标题" prop="title">
      <el-input v-model="form.title" placeholder="请输入资源标题"></el-input>
    </el-form-item>
    
    <el-form-item label="资源描述" prop="description">
      <el-input
        v-model="form.description"
        type="textarea"
        :rows="3"
        placeholder="请输入资源描述"
      ></el-input>
    </el-form-item>
    
    <el-form-item label="资源类型" prop="resource_type">
      <el-select v-model="form.resource_type" placeholder="请选择资源类型" style="width: 100%">
        <el-option label="文档" value="document"></el-option>
        <el-option label="视频" value="video"></el-option>
        <el-option label="测验" value="quiz"></el-option>
        <el-option label="作业" value="assignment"></el-option>
      </el-select>
    </el-form-item>
    
    <!-- 表单内容区域 -->
    <div class="form-content-area">
      <!-- 添加加载状态指示 -->
      <div v-if="form.isTypeChanging" class="loading-overlay">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      
      <!-- 根据资源类型显示不同的内容输入 -->
      <template v-if="form.resource_type === 'document'">
        <el-form-item label="文档内容 (Markdown格式)" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="10"
            placeholder="请输入文档内容，支持Markdown格式"
          ></el-input>
        </el-form-item>
      </template>
      
      <template v-else-if="form.resource_type === 'video' && !form.isTypeChanging">
        <el-form-item label="视频URL" prop="content">
          <el-input 
            v-model="form.content" 
            placeholder="请输入视频URL或嵌入代码"
          ></el-input>
        </el-form-item>
      </template>
      
      <template v-else-if="form.resource_type === 'quiz' && !form.isTypeChanging">
        <el-divider content-position="left">测验题目</el-divider>
        
        <div v-for="(question, index) in quizQuestions" :key="index" class="quiz-question">
          <el-card>
            <div class="question-header">
              <h4>问题 {{ index + 1 }}</h4>
              <el-button 
                type="danger" 
                size="small" 
                icon="Delete"
                circle
                @click="removeQuestion(index)"
              ></el-button>
            </div>
            
            <el-form-item :label="`问题${index + 1}标题`" :prop="`quizQuestions.${index}.question`">
              <el-input 
                v-model="question.question" 
                placeholder="请输入问题"
              ></el-input>
            </el-form-item>
            
            <div class="question-options">
              <div v-for="(option, optIndex) in question.options" :key="optIndex" class="option-item">
                <el-input 
                  v-model="question.options[optIndex]" 
                  placeholder="选项内容"
                >
                  <template #prepend>
                    <el-radio 
                      v-model="question.answer" 
                      :label="optIndex"
                      @change="() => {}"
                    ></el-radio>
                  </template>
                  <template #append>
                    <el-button 
                      type="danger" 
                      icon="Delete"
                      @click="removeOption(index, optIndex)"
                    ></el-button>
                  </template>
                </el-input>
              </div>
            </div>
            
            <el-button 
              type="success" 
              size="small" 
              @click="addOption(index)"
            >
              添加选项
            </el-button>
          </el-card>
        </div>
        
        <div class="add-question">
          <el-button 
            type="primary" 
            @click="addQuestion"
          >
            添加问题
          </el-button>
        </div>
      </template>
      
      <template v-else-if="form.resource_type === 'assignment' && !form.isTypeChanging">
        <el-form-item label="作业标题" prop="assignmentTitle">
          <el-input 
            v-model="assignmentData.title" 
            placeholder="请输入作业标题"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="作业描述" prop="assignmentDescription">
          <el-input
            v-model="assignmentData.description"
            type="textarea"
            :rows="5"
            placeholder="请输入作业描述和要求"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="截止日期" prop="assignmentDueDate">
          <el-date-picker 
            v-model="assignmentData.due_date" 
            type="date" 
            placeholder="选择截止日期"
            style="width: 100%"
          ></el-date-picker>
        </el-form-item>
      </template>
    </div>
    
    <el-form-item label="显示顺序" prop="order">
      <el-input-number v-model="form.order" :min="1" :max="100"></el-input-number>
    </el-form-item>
    
    <el-form-item>
      <el-button type="primary" @click="submitForm">保存</el-button>
      <el-button @click="resetForm">重置</el-button>
    </el-form-item>
  </el-form>
</template>

<script>
import { ref, reactive, computed, watch, onMounted, nextTick, onBeforeUnmount } from 'vue'
import { ElMessage, ElIcon } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { createSafeResizeObserver } from '../../utils/resizeUtil'

export default {
  name: 'ResourceForm',
  components: {
    ElIcon,
    Loading
  },
  props: {
    sectionId: {
      type: [Number, String],
      required: true
    },
    resource: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['submit', 'cancel'],
  setup(props, { emit }) {
    const formRef = ref(null)
    
    // 用于防止ResizeObserver循环错误
    const resizeObserver = ref(null)
    
    // 测验问题
    const quizQuestions = ref([])
    
    // 作业数据
    const assignmentData = reactive({
      title: '',
      description: '',
      due_date: ''
    })
    
    // 表单数据
    const form = reactive({
      title: props.resource.title || '',
      description: props.resource.description || '',
      resource_type: props.resource.resource_type || 'document',
      content: props.resource.content || '',
      order: props.resource.order || 1,
      isTypeChanging: false
    })
    
    // 初始化测验数据
    const initQuizData = () => {
      if (form.resource_type === 'quiz' && form.content) {
        try {
          const quizData = JSON.parse(form.content)
          quizQuestions.value = quizData.questions || []
        } catch (e) {
          console.error('解析测验数据失败', e)
          quizQuestions.value = [{
            question: '',
            options: ['', ''],
            answer: 0
          }]
        }
      } else {
        quizQuestions.value = [{
          question: '',
          options: ['', ''],
          answer: 0
        }]
      }
    }
    
    // 初始化作业数据
    const initAssignmentData = () => {
      if (form.resource_type === 'assignment' && form.content) {
        try {
          const data = JSON.parse(form.content)
          assignmentData.title = data.title || ''
          assignmentData.description = data.description || ''
          assignmentData.due_date = data.due_date || ''
        } catch (e) {
          console.error('解析作业数据失败', e)
        }
      }
    }
    
    // 优化资源类型切换处理，防止ResizeObserver错误
    const handleResourceTypeChange = async (newType, oldType) => {
      try {
        // 先断开之前的ResizeObserver连接
        if (resizeObserver.value) {
          resizeObserver.value.disconnect();
          resizeObserver.value = null;
        }
        
        // 标记正在切换状态，以减少不必要的重渲染
        form.isTypeChanging = true;
        
        // 使用nextTick等待DOM更新
        await nextTick();
        
        // 视频类型切换需要特殊处理
        if (oldType === 'video' || newType === 'video') {
          // 延迟初始化以避免ResizeObserver错误
          setTimeout(() => {
            // 重置内容字段，避免不同类型间的内容混淆
            if (oldType !== newType) {
              form.content = '';
            }
            
            // 根据新类型初始化相应数据
            if (newType === 'quiz') {
              initQuizData();
            } else if (newType === 'assignment') {
              initAssignmentData();
            }
            
            // 延迟结束加载状态，确保DOM完全更新
            setTimeout(() => {
              form.isTypeChanging = false;
              
              // 安全地设置新的ResizeObserver
              nextTick().then(() => {
                setTimeout(setupResizeObserver, 300);
              });
            }, 200);
          }, 300);
        } else {
          // 非视频类型的切换处理
          // 重置内容字段，避免不同类型间的内容混淆
          if (oldType !== newType) {
            form.content = '';
          }
          
          if (newType === 'quiz') {
            initQuizData();
          } else if (newType === 'assignment') {
            initAssignmentData();
          }
          
          // 延迟结束加载状态
          setTimeout(() => {
            form.isTypeChanging = false;
            
            // 再次等待DOM更新完成
            nextTick().then(() => {
              // 重新设置ResizeObserver
              setupResizeObserver();
            });
          }, 200);
        }
      } catch (error) {
        console.error('资源类型切换处理错误:', error);
        // 确保错误情况下也会重置加载状态
        form.isTypeChanging = false;
        
        // 尝试安全地恢复
        setTimeout(() => {
          setupResizeObserver();
        }, 500);
      }
    };
    
    // 监听资源类型变化
    watch(() => form.resource_type, (newType, oldType) => {
      handleResourceTypeChange(newType, oldType);
    });
    
    // 设置安全的ResizeObserver
    const setupResizeObserver = () => {
      // 断开之前的连接
      if (resizeObserver.value) {
        resizeObserver.value.disconnect();
      }
      
      // 使用工具创建安全的ResizeObserver
      resizeObserver.value = createSafeResizeObserver(() => {
        // 最小化回调处理，避免不必要的工作
      }, { delay: 200 });
      
      // 如果表单已挂载，观察表单元素
      if (formRef.value?.$el) {
        resizeObserver.value.observe(formRef.value.$el);
      }
    };
    
    // 清理ResizeObserver的函数
    const cleanupResizeObserver = () => {
      if (resizeObserver.value) {
        resizeObserver.value.disconnect();
        resizeObserver.value = null;
      }
    };
    
    // 表单验证规则
    const rules = {
      title: [
        { required: true, message: '请输入资源标题', trigger: 'blur' },
        { min: 2, max: 100, message: '长度在2到100个字符之间', trigger: 'blur' }
      ],
      description: [
        { required: true, message: '请输入资源描述', trigger: 'blur' }
      ],
      resource_type: [
        { required: true, message: '请选择资源类型', trigger: 'change' }
      ],
      content: [
        { required: true, message: '请输入资源内容', trigger: 'blur' }
      ]
    }
    
    // 添加问题
    const addQuestion = () => {
      quizQuestions.value.push({
        question: '',
        options: ['', ''],
        answer: 0
      })
    }
    
    // 移除问题
    const removeQuestion = (index) => {
      if (quizQuestions.value.length > 1) {
        quizQuestions.value.splice(index, 1)
      } else {
        ElMessage.warning('至少保留一个问题')
      }
    }
    
    // 添加选项
    const addOption = (questionIndex) => {
      quizQuestions.value[questionIndex].options.push('')
    }
    
    // 移除选项
    const removeOption = (questionIndex, optionIndex) => {
      const options = quizQuestions.value[questionIndex].options
      const answer = quizQuestions.value[questionIndex].answer
      
      if (options.length > 2) {
        options.splice(optionIndex, 1)
        
        // 如果删除的是当前答案，重置答案
        if (optionIndex === answer) {
          quizQuestions.value[questionIndex].answer = 0
        } else if (optionIndex < answer) {
          quizQuestions.value[questionIndex].answer--
        }
      } else {
        ElMessage.warning('至少保留两个选项')
      }
    }
    
    // 提交表单前的数据处理
    const prepareFormData = () => {
      if (form.resource_type === 'quiz') {
        form.content = JSON.stringify({
          questions: quizQuestions.value
        })
      } else if (form.resource_type === 'assignment') {
        form.content = JSON.stringify(assignmentData)
      }
    }
    
    // 提交表单
    const submitForm = async () => {
      if (!formRef.value) return
      
      try {
        await formRef.value.validate()
        
        // 准备表单数据
        prepareFormData()
        
        // 发送表单数据到父组件
        emit('submit', {
          id: props.resource.id,
          section_id: props.sectionId,
          title: form.title,
          description: form.description,
          resource_type: form.resource_type,
          content: form.content,
          order: form.order
        })
      } catch (error) {
        ElMessage.error('表单验证失败，请检查输入')
      }
    }
    
    // 重置表单
    const resetForm = () => {
      if (formRef.value) {
        formRef.value.resetFields()
      }
      
      if (form.resource_type === 'quiz') {
        initQuizData()
      } else if (form.resource_type === 'assignment') {
        initAssignmentData()
      }
    }
    
    // 组件挂载时设置ResizeObserver
    onMounted(() => {
      // 初始化资源类型数据
      if (props.resource.resource_type === 'quiz') {
        initQuizData()
      } else if (props.resource.resource_type === 'assignment') {
        initAssignmentData()
      }
      
      setupResizeObserver();
    });
    
    // 组件卸载前清理ResizeObserver
    onBeforeUnmount(() => {
      cleanupResizeObserver();
    });
    
    return {
      formRef,
      form,
      rules,
      quizQuestions,
      assignmentData,
      submitForm,
      resetForm,
      addQuestion,
      removeQuestion,
      addOption,
      removeOption,
      cleanupResizeObserver // 导出清理函数以便在父组件使用
    }
  }
}
</script>

<style scoped>
.resource-form {
  /* 添加固定高度，减少动态高度变化导致的ResizeObserver错误 */
  min-height: 500px;
  position: relative;
}

.quiz-question {
  margin-bottom: 20px;
  /* 添加稳定的布局属性 */
  position: relative;
  width: 100%;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.question-options {
  margin-bottom: 15px;
}

.option-item {
  margin-bottom: 10px;
}

.add-question {
  margin: 20px 0;
  display: flex;
  justify-content: center;
}

.form-content-area {
  position: relative;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
}
</style> 