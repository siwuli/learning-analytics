<template>
  <el-form 
    ref="formRef"
    :model="form"
    :rules="rules"
    label-position="top"
  >
    <el-form-item label="章节标题" prop="title">
      <el-input v-model="form.title" placeholder="请输入章节标题"></el-input>
    </el-form-item>
    
    <el-form-item label="章节描述" prop="description">
      <el-input
        v-model="form.description"
        type="textarea"
        :rows="4"
        placeholder="请输入章节描述"
      ></el-input>
    </el-form-item>
    
    <el-form-item label="章节顺序" prop="order">
      <el-input-number v-model="form.order" :min="1" :max="100"></el-input-number>
    </el-form-item>
    
    <el-form-item>
      <el-button type="primary" @click="submitForm">保存</el-button>
      <el-button @click="resetForm">重置</el-button>
    </el-form-item>
  </el-form>
</template>

<script>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'SectionForm',
  props: {
    courseId: {
      type: [Number, String],
      required: true
    },
    section: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['submit', 'cancel'],
  setup(props, { emit }) {
    const formRef = ref(null)
    
    // 表单数据
    const form = reactive({
      title: props.section.title || '',
      description: props.section.description || '',
      order: props.section.order || 1
    })
    
    // 表单验证规则
    const rules = {
      title: [
        { required: true, message: '请输入章节标题', trigger: 'blur' },
        { min: 2, max: 100, message: '长度在2到100个字符之间', trigger: 'blur' }
      ],
      description: [
        { required: true, message: '请输入章节描述', trigger: 'blur' }
      ]
    }
    
    // 提交表单
    const submitForm = async () => {
      if (!formRef.value) return
      
      try {
        await formRef.value.validate()
        
        // 发送表单数据到父组件
        emit('submit', {
          id: props.section.id,
          title: form.title,
          description: form.description,
          order: form.order,
          course_id: props.courseId
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
    }
    
    return {
      formRef,
      form,
      rules,
      submitForm,
      resetForm
    }
  }
}
</script>

<style scoped>
/* 样式 */
</style> 