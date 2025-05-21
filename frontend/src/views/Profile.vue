<template>
  <div class="profile-container">
    <h1>个人资料</h1>
    
    <div v-if="loading" class="loading-container">
      <el-skeleton style="width: 100%" animated>
        <template #template>
          <el-skeleton-item variant="text" style="width: 50%" />
          <el-skeleton-item variant="text" style="margin-top: 16px; width: 80%" />
          <el-skeleton-item variant="text" style="margin-top: 16px; width: 30%" />
        </template>
      </el-skeleton>
    </div>
    
    <div v-else class="profile-content">
      <el-card class="profile-card">
        <div class="profile-header">
          <div class="profile-avatar">
            <el-avatar :size="100" :src="userAvatar"></el-avatar>
            <div class="profile-upload">
              <el-upload
                class="avatar-uploader"
                action="#"
                :auto-upload="false"
                :show-file-list="false"
                :on-change="handleAvatarChange"
              >
                <el-button size="small">更换头像</el-button>
              </el-upload>
              <el-progress 
                v-if="uploadProgress > 0 && uploadProgress < 100" 
                :percentage="uploadProgress" 
                :format="percentFormat"
                style="margin-top: 10px;"
              ></el-progress>
            </div>
          </div>
          <div class="profile-info">
            <h2>{{ user.username }}</h2>
            <p>账号: {{ user.account }}</p>
            <p>{{ roleText }}</p>
            <p>邮箱: {{ user.email }}</p>
            <p>注册时间: {{ formatDate(user.created_at) }}</p>
          </div>
        </div>
        
        <el-divider />
        
        <div class="profile-edit">
          <h3>编辑个人资料</h3>
          <el-form 
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-width="100px"
          >
            <el-form-item label="账号">
              <el-input v-model="user.account" disabled></el-input>
              <div class="form-tip">账号不可修改</div>
            </el-form-item>
            
            <el-form-item label="用户名" prop="username">
              <el-input v-model="profileForm.username" placeholder="请输入用户名"></el-input>
            </el-form-item>
            
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" placeholder="请输入邮箱"></el-input>
            </el-form-item>
            
            <el-form-item label="个人简介" prop="bio">
              <el-input 
                v-model="profileForm.bio" 
                type="textarea" 
                rows="4"
                placeholder="请输入个人简介"
              ></el-input>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveProfile" :loading="saving">保存更改</el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <el-divider />
        
        <div class="password-change">
          <h3>修改密码</h3>
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="100px"
          >
            <el-form-item label="当前密码" prop="currentPassword">
              <el-input 
                v-model="passwordForm.currentPassword" 
                type="password"
                placeholder="请输入当前密码"
                show-password
              ></el-input>
            </el-form-item>
            
            <el-form-item label="新密码" prop="newPassword">
              <el-input 
                v-model="passwordForm.newPassword" 
                type="password"
                placeholder="请输入新密码"
                show-password
              ></el-input>
            </el-form-item>
            
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input 
                v-model="passwordForm.confirmPassword" 
                type="password"
                placeholder="请再次输入新密码"
                show-password
              ></el-input>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="changePassword" :loading="changingPassword">修改密码</el-button>
              <el-button @click="resetPasswordForm">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'

export default {
  name: 'Profile',
  setup() {
    const store = useStore()
    const loading = ref(true)
    const saving = ref(false)
    const changingPassword = ref(false)
    const profileFormRef = ref(null)
    const passwordFormRef = ref(null)
    const uploadProgress = ref(0)
    
    // 获取用户信息
    const user = computed(() => store.state.auth.user || {})
    
    // 用户角色文本
    const roleText = computed(() => {
      return user.value.role === 'teacher' ? '教师' : '学生'
    })
    
    // 用户头像
    const userAvatar = computed(() => {
      // 检查是否有有效的头像URL
      if (user.value && user.value.avatar) {
        // 如果是以http开头的完整URL，直接使用
        if (user.value.avatar.startsWith('http')) {
          return user.value.avatar;
        }
        
        // 处理相对路径
        if (user.value.avatar.startsWith('/')) {
          // 从环境变量获取API基础URL，如果没有则使用默认
          const baseUrl = import.meta.env?.VITE_APP_API_URL || 
                         process.env.VUE_APP_API_URL || 
                         'http://localhost:5000';
          return baseUrl + user.value.avatar;
        }
        
        // 如果只是文件名，添加完整路径
        return `http://localhost:5000/api/static/uploads/avatars/${user.value.avatar}`;
      }
      
      // 无头像时使用默认头像
      return 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png';
    })
    
    // 个人资料表单
    const profileForm = reactive({
      username: '',
      email: '',
      bio: ''
    })
    
    // 密码表单
    const passwordForm = reactive({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    // 表单验证规则
    const profileRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 2, max: 20, message: '长度在2到20个字符之间', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱地址', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
      ]
    }
    
    const passwordRules = {
      currentPassword: [
        { required: true, message: '请输入当前密码', trigger: 'blur' }
      ],
      newPassword: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请再次输入新密码', trigger: 'blur' },
        { 
          validator: (rule, value, callback) => {
            if (value !== passwordForm.newPassword) {
              callback(new Error('两次输入的密码不一致'))
            } else {
              callback()
            }
          }, 
          trigger: 'blur' 
        }
      ]
    }
    
    // 百分比格式化
    const percentFormat = (percentage) => {
      return `${percentage}%`
    }
    
    // 初始化表单数据
    const initFormData = () => {
      profileForm.username = user.value.username || ''
      profileForm.email = user.value.email || ''
      profileForm.bio = user.value.bio || ''
    }
    
    // 保存个人资料
    const saveProfile = () => {
      profileFormRef.value.validate(async (valid) => {
        if (valid) {
          saving.value = true
          try {
            // 调用更新用户API
            await store.dispatch('auth/updateUserProfile', {
              userId: user.value.id,
              userData: {
                username: profileForm.username,
                email: profileForm.email,
                bio: profileForm.bio
              }
            })
            
            ElMessage.success('个人资料更新成功')
          } catch (error) {
            ElMessage.error('更新失败: ' + (error.message || '未知错误'))
          } finally {
            saving.value = false
          }
        }
      })
    }
    
    // 修改密码
    const changePassword = () => {
      passwordFormRef.value.validate(async (valid) => {
        if (valid) {
          changingPassword.value = true
          try {
            // 这里应该调用修改密码API
            // 模拟API调用
            await new Promise(resolve => setTimeout(resolve, 1000))
            
            // 重置密码表单
            resetPasswordForm()
            
            ElMessage.success('密码修改成功')
          } catch (error) {
            ElMessage.error('修改失败: ' + (error.message || '未知错误'))
          } finally {
            changingPassword.value = false
          }
        }
      })
    }
    
    // 重置个人资料表单
    const resetForm = () => {
      profileFormRef.value.resetFields()
      initFormData()
    }
    
    // 重置密码表单
    const resetPasswordForm = () => {
      passwordFormRef.value.resetFields()
    }
    
    // 处理头像变更
    const handleAvatarChange = (file) => {
      if (!file) return
      
      // 图片类型验证
      const isImage = file.raw.type.startsWith('image/')
      if (!isImage) {
        ElMessage.error('只能上传图片文件!')
        return
      }
      
      // 图片大小验证 (限制为5MB)
      const isLt5M = file.size / 1024 / 1024 < 5
      if (!isLt5M) {
        ElMessage.error('图片大小不能超过5MB!')
        return
      }
      
      // 上传头像
      uploadProgress.value = 0
      
      store.dispatch('auth/uploadUserAvatar', {
        userId: user.value.id,
        avatarFile: file.raw,
        onProgress: (percent) => {
          uploadProgress.value = percent
        }
      }).then(() => {
        ElMessage.success('头像上传成功')
        // 重置进度条
        setTimeout(() => {
          uploadProgress.value = 0
        }, 1000)
      }).catch(error => {
        ElMessage.error('头像上传失败: ' + (error.message || '未知错误'))
        uploadProgress.value = 0
      })
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    }
    
    onMounted(() => {
      // 模拟加载数据
      setTimeout(() => {
        initFormData()
        loading.value = false
      }, 500)
    })
    
    return {
      loading,
      saving,
      changingPassword,
      user,
      roleText,
      userAvatar,
      profileForm,
      passwordForm,
      profileRules,
      passwordRules,
      profileFormRef,
      passwordFormRef,
      uploadProgress,
      percentFormat,
      saveProfile,
      changePassword,
      resetForm,
      resetPasswordForm,
      handleAvatarChange,
      formatDate
    }
  }
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.loading-container {
  margin-top: 20px;
}

.profile-content {
  margin-top: 20px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.profile-card {
  padding: 20px;
}

.profile-header {
  display: flex;
  align-items: flex-start;
  margin-bottom: 30px;
}

.profile-avatar {
  margin-right: 30px;
  text-align: center;
}

.profile-upload {
  margin-top: 10px;
}

.profile-info h2 {
  margin-top: 0;
  margin-bottom: 10px;
}

.profile-info p {
  margin: 5px 0;
  color: #606266;
}

.profile-edit,
.password-change {
  margin-top: 20px;
  margin-bottom: 20px;
}

.profile-edit h3,
.password-change h3 {
  margin-bottom: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style> 