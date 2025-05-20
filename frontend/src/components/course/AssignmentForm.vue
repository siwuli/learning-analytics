<template>
  <el-form 
    ref="formRef"
    :model="form"
    :rules="rules"
    label-position="top"
  >
    <el-form-item label="作业标题" prop="title">
      <el-input v-model="form.title" placeholder="请输入作业标题"></el-input>
    </el-form-item>
    
    <el-form-item label="作业描述" prop="description">
      <el-input
        v-model="form.description"
        type="textarea"
        :rows="5"
        placeholder="请输入作业描述和要求"
      ></el-input>
    </el-form-item>
    
    <el-form-item label="截止日期" prop="deadline">
      <el-date-picker 
        v-model="form.deadline" 
        type="datetime" 
        placeholder="选择截止日期时间"
        format="YYYY-MM-DD HH:mm"
        value-format="YYYY-MM-DD HH:mm:ss"
        style="width: 100%"
      ></el-date-picker>
    </el-form-item>
    
    <el-form-item label="分数" prop="points">
      <el-input-number v-model="form.points" :min="0" :max="100"></el-input-number>
    </el-form-item>
    
    <el-form-item label="附件">
      <el-upload
        class="assignment-upload"
        action=""
        :auto-upload="false"
        :on-change="handleFileChange"
        :file-list="fileList"
      >
        <el-button type="primary">选择附件</el-button>
        <template #tip>
          <div class="el-upload__tip">可以上传附件提供给学生参考</div>
        </template>
      </el-upload>
    </el-form-item>
    
    <el-form-item>
      <el-button type="primary" @click="submitForm">保存</el-button>
      <el-button @click="resetForm">重置</el-button>
    </el-form-item>
  </el-form>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'AssignmentForm',
  props: {
    courseId: {
      type: [Number, String],
      required: true
    },
    assignment: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['submit', 'cancel'],
  setup(props, { emit }) {
    const formRef = ref(null)
    const fileList = ref([])
    
    // 表单数据
    const form = reactive({
      id: props.assignment.id || '',
      title: props.assignment.title || '',
      description: props.assignment.description || '',
      deadline: props.assignment.deadline || '',
      points: props.assignment.points || 10,
      attachments: props.assignment.attachments || []
    })
    
    // 表单验证规则
    const rules = {
      title: [
        { required: true, message: '请输入作业标题', trigger: 'blur' },
        { min: 2, max: 100, message: '长度在2到100个字符之间', trigger: 'blur' }
      ],
      description: [
        { required: true, message: '请输入作业描述', trigger: 'blur' }
      ],
      deadline: [
        { required: true, message: '请选择截止日期', trigger: 'change' }
      ],
      points: [
        { required: true, message: '请输入分数', trigger: 'blur' }
      ]
    }
    
    // 处理文件变化
    const handleFileChange = (file) => {
      // 实际情况中，应该处理文件上传逻辑
      console.log('已选择文件:', file)
    }
    
    // 提交表单
    const submitForm = async () => {
      if (!formRef.value) return
      
      try {
        await formRef.value.validate()
        
        // 构造提交的数据
        const assignmentData = {
          id: form.id,
          course_id: props.courseId,
          title: form.title,
          description: form.description,
          deadline: form.deadline,
          points: form.points,
          attachments: form.attachments
        }
        
        // 发送表单数据到父组件
        emit('submit', assignmentData)
      } catch (error) {
        ElMessage.error('表单验证失败，请检查输入')
      }
    }
    
    // 重置表单
    const resetForm = () => {
      if (formRef.value) {
        formRef.value.resetFields()
      }
      
      fileList.value = []
    }
    
    return {
      formRef,
      form,
      rules,
      fileList,
      handleFileChange,
      submitForm,
      resetForm
    }
  }
}
</script>

<style scoped>
.assignment-upload {
  width: 100%;
  margin-bottom: 20px;
}

.el-upload__tip {
  color: #909399;
  margin-top: 5px;
}
</style> 