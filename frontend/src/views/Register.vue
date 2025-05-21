<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="register-header">
          <h2>学习分析平台</h2>
          <p>创建一个新账户</p>
        </div>
      </template>
      
      <el-form :model="registerForm" ref="registerFormRef" :rules="rules" label-position="top">
        <el-form-item label="账号" prop="account">
          <el-input v-model="registerForm.account" placeholder="请输入账号（用于登录）"></el-input>
        </el-form-item>
        
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名（用于显示）"></el-input>
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
          <el-radio-group v-model="registerForm.role">
            <el-radio label="student">学生</el-radio>
            <el-radio label="teacher">教师</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submitForm" style="width: 100%">注册</el-button>
        </el-form-item>
      </el-form>
      
      <div class="register-actions">
        <p>已有账户？<router-link to="/login">返回登录</router-link></p>
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
      account: '',
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      role: 'student'
    })
    
    const rules = {
      account: [
        { required: true, message: '请输入账号', trigger: 'blur' },
        { min: 3, max: 20, message: '账号长度在3到20个字符之间', trigger: 'blur' }
      ],
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 2, max: 20, message: '用户名长度在2到20个字符之间', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不少于6个字符', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请再次输入密码', trigger: 'blur' },
        { 
          validator: (rule, value, callback) => {
            if (value !== registerForm.password) {
              callback(new Error('两次输入的密码不一致'))
            } else {
              callback()
            }
          }, 
          trigger: 'blur' 
        }
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
            
            // 准备注册数据，不包含确认密码字段
            const userData = {
              account: registerForm.account,
              username: registerForm.username,
              email: registerForm.email,
              password: registerForm.password,
              role: registerForm.role
            }
            
            await store.dispatch('auth/register', userData)
            ElMessage.success('注册成功，请登录')
            router.push('/login')
          } catch (error) {
            ElMessage.error(error.message || '注册失败，请稍后再试')
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