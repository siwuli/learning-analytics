<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="register-header">
          <h2>学习分析平台</h2>
          <p>创建您的账户</p>
        </div>
      </template>
      
      <el-form :model="registerForm" ref="registerFormRef" :rules="rules" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱"></el-input>
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入密码"></el-input>
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="registerForm.role" placeholder="请选择角色">
            <el-option label="学生" value="student"></el-option>
            <el-option label="教师" value="teacher"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submitForm" style="width: 100%">注册</el-button>
        </el-form-item>
      </el-form>
      
      <div class="register-actions">
        <p>已有账户？<router-link to="/login">立即登录</router-link></p>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'Register',
  setup() {
    const store = useStore()
    const router = useRouter()
    const registerFormRef = ref(null)
    
    const registerForm = reactive({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      role: 'student'
    })
    
    const validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入密码'))
      } else {
        if (registerForm.confirmPassword !== '') {
          registerFormRef.value.validateField('confirmPassword')
        }
        callback()
      }
    }
    
    const validatePass2 = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== registerForm.password) {
        callback(new Error('两次输入密码不一致'))
      } else {
        callback()
      }
    }
    
    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度在3到20个字符之间', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      password: [
        { required: true, validator: validatePass, trigger: 'blur' },
        { min: 6, message: '密码长度不少于6个字符', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, validator: validatePass2, trigger: 'blur' }
      ],
      role: [
        { required: true, message: '请选择角色', trigger: 'change' }
      ]
    }
    
    const loading = computed(() => store.state.loading)
    
    const submitForm = () => {
      registerFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            store.dispatch('setLoading', true)
            
            // 提取注册信息，去除确认密码字段
            const userData = {
              username: registerForm.username,
              email: registerForm.email,
              password: registerForm.password,
              role: registerForm.role
            }
            
            await store.dispatch('auth/register', userData)
            ElMessage.success('注册成功，请登录')
            router.push('/login')
          } catch (error) {
            ElMessage.error(error.message || '注册失败，请稍后重试')
          } finally {
            store.dispatch('setLoading', false)
          }
        }
      })
    }
    
    return {
      registerFormRef,
      registerForm,
      rules,
      loading,
      submitForm
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.register-card {
  width: 400px;
}

.register-header {
  text-align: center;
}

.register-header h2 {
  margin-bottom: 5px;
  color: #303133;
}

.register-header p {
  color: #606266;
  margin-top: 0;
}

.register-actions {
  text-align: center;
  margin-top: 20px;
  color: #606266;
}

.register-actions a {
  color: #409eff;
  text-decoration: none;
}
</style> 