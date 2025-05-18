<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="login-header">
          <h2>学习分析平台</h2>
          <p>登录您的账户</p>
        </div>
      </template>
      
      <el-form :model="loginForm" ref="loginFormRef" :rules="rules" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submitForm" style="width: 100%">登录</el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-actions">
        <p>还没有账户？<router-link to="/register">立即注册</router-link></p>
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
  name: 'Login',
  setup() {
    const store = useStore()
    const router = useRouter()
    const loginFormRef = ref(null)
    
    const loginForm = reactive({
      username: '',
      password: ''
    })
    
    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度在3到20个字符之间', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不少于6个字符', trigger: 'blur' }
      ]
    }
    
    const loading = computed(() => store.state.loading)
    
    const submitForm = () => {
      loginFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            store.dispatch('setLoading', true)
            await store.dispatch('auth/login', loginForm)
            ElMessage.success('登录成功')
            router.push('/dashboard')
          } catch (error) {
            ElMessage.error(error.message || '登录失败，请检查您的用户名和密码')
          } finally {
            store.dispatch('setLoading', false)
          }
        }
      })
    }
    
    return {
      loginFormRef,
      loginForm,
      rules,
      loading,
      submitForm
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.login-card {
  width: 400px;
}

.login-header {
  text-align: center;
}

.login-header h2 {
  margin-bottom: 5px;
  color: #303133;
}

.login-header p {
  color: #606266;
  margin-top: 0;
}

.login-actions {
  text-align: center;
  margin-top: 20px;
  color: #606266;
}

.login-actions a {
  color: #409eff;
  text-decoration: none;
}
</style> 