<template>
  <div class="admin-users">
    <!-- 添加用户按钮 -->
    <div class="action-bar">
      <el-button type="primary" @click="showAddUserDialog">
        <i class="el-icon-plus"></i> 添加用户
      </el-button>
      
      <!-- 角色筛选 -->
      <el-radio-group v-model="roleFilter" @change="handleRoleFilterChange" class="role-filter">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button label="student">学生</el-radio-button>
        <el-radio-button label="teacher">教师</el-radio-button>
        <el-radio-button label="admin">管理员</el-radio-button>
      </el-radio-group>
    </div>
    
    <!-- 用户表格 -->
    <el-table
      v-loading="loading"
      :data="users"
      border
      style="width: 100%"
    >
      <el-table-column label="ID" prop="id" width="80" />
      <el-table-column label="头像" width="80">
        <template #default="scope">
          <el-avatar :src="scope.row.avatar" :size="40"></el-avatar>
        </template>
      </el-table-column>
      <el-table-column label="用户名" prop="username" />
      <el-table-column label="账号" prop="account" />
      <el-table-column label="邮箱" prop="email" />
      <el-table-column label="角色" width="100">
        <template #default="scope">
          <el-tag
            :type="getRoleTagType(scope.row.role)"
          >
            {{ getRoleText(scope.row.role) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button 
            size="mini" 
            type="primary" 
            @click="handleEdit(scope.row)"
            :disabled="scope.row.id === currentUser.id"
          >
            编辑
          </el-button>
          <el-button 
            size="mini" 
            type="danger" 
            @click="handleDelete(scope.row)"
            :disabled="scope.row.id === currentUser.id"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="pagination.currentPage"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="pagination.total"
      >
      </el-pagination>
    </div>
    
    <!-- 用户表单对话框 -->
    <el-dialog
      :title="dialogMode === 'add' ? '添加用户' : '编辑用户'"
      v-model="dialogVisible"
      width="500px"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="账号" prop="account">
          <el-input v-model="userForm.account" :disabled="dialogMode === 'edit'" />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" />
          <div v-if="dialogMode === 'edit'" class="password-hint">
            <small>* 留空表示不修改密码</small>
          </div>
        </el-form-item>
        <el-form-item label="个人简介" prop="bio">
          <el-input v-model="userForm.bio" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitUserForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, reactive } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'AdminUsersList',
  setup() {
    const store = useStore()
    const userFormRef = ref(null)
    const dialogVisible = ref(false)
    const dialogMode = ref('add') // 'add' 或 'edit'
    const roleFilter = ref('') // 角色筛选
    const pageSize = ref(10)
    const currentPage = ref(1)
    
    // 用户表单数据
    const userForm = reactive({
      id: null,
      account: '',
      username: '',
      email: '',
      password: '',
      role: 'student',
      bio: ''
    })
    
    // 表单验证规则
    const rules = reactive({
      account: [
        { required: true, message: '请输入账号', trigger: 'blur' },
        { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
      ],
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
      ],
      password: [
        { required: dialogMode.value === 'add', message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
      ],
      role: [
        { required: true, message: '请选择角色', trigger: 'change' }
      ]
    })
    
    // 从store获取数据
    const users = computed(() => store.state.admin.users)
    const pagination = computed(() => store.state.admin.usersPagination)
    const loading = computed(() => store.state.admin.loading)
    const currentUser = computed(() => store.state.auth.user)
    
    // 获取用户列表
    const fetchUsers = async () => {
      try {
        console.log('正在获取用户列表...')
        await store.dispatch('admin/fetchUsers', {
          page: currentPage.value,
          perPage: pageSize.value,
          role: roleFilter.value
        })
        console.log('用户列表获取成功:', users.value)
      } catch (error) {
        console.error('获取用户列表失败:', error)
      }
    }
    
    // 显示添加用户对话框
    const showAddUserDialog = () => {
      dialogMode.value = 'add'
      // 重置表单
      Object.assign(userForm, {
        id: null,
        account: '',
        username: '',
        email: '',
        password: '',
        role: 'student',
        bio: ''
      })
      dialogVisible.value = true
    }
    
    // 显示编辑用户对话框
    const handleEdit = (user) => {
      dialogMode.value = 'edit'
      // 填充表单数据
      Object.assign(userForm, {
        id: user.id,
        account: user.account,
        username: user.username,
        email: user.email,
        password: '', // 编辑时不填充密码
        role: user.role,
        bio: user.bio || ''
      })
      dialogVisible.value = true
    }
    
    // 处理删除用户
    const handleDelete = (user) => {
      ElMessageBox.confirm(
        `确定要删除用户 "${user.username}" 吗？此操作不可恢复！`,
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
        .then(async () => {
          try {
            await store.dispatch('admin/deleteUser', user.id)
            ElMessage.success('用户删除成功')
          } catch (error) {
            ElMessage.error('删除用户失败：' + (error.message || '未知错误'))
          }
        })
        .catch(() => {
          // 用户取消
        })
    }
    
    // 提交用户表单
    const submitUserForm = () => {
      userFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            if (dialogMode.value === 'add') {
              // 创建新用户
              await store.dispatch('admin/createUser', userForm)
              ElMessage.success('用户创建成功')
            } else {
              // 编辑用户
              const userData = { ...userForm }
              // 如果密码为空，不更新密码
              if (!userData.password) {
                delete userData.password
              }
              await store.dispatch('admin/updateUser', {
                userId: userForm.id,
                userData
              })
              ElMessage.success('用户更新成功')
            }
            dialogVisible.value = false
          } catch (error) {
            ElMessage.error((error.response?.data?.message) || '操作失败')
          }
        } else {
          return false
        }
      })
    }
    
    // 角色筛选变化
    const handleRoleFilterChange = () => {
      currentPage.value = 1
      fetchUsers()
    }
    
    // 分页大小变化
    const handleSizeChange = (size) => {
      pageSize.value = size
      fetchUsers()
    }
    
    // 当前页变化
    const handleCurrentChange = (page) => {
      currentPage.value = page
      fetchUsers()
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
    }
    
    // 获取角色显示文本
    const getRoleText = (role) => {
      const roleMap = {
        'student': '学生',
        'teacher': '教师',
        'admin': '管理员'
      }
      return roleMap[role] || role
    }
    
    // 获取角色标签类型
    const getRoleTagType = (role) => {
      const typeMap = {
        'student': 'info',
        'teacher': 'success',
        'admin': 'danger'
      }
      return typeMap[role] || ''
    }
    
    onMounted(() => {
      fetchUsers()
    })
    
    return {
      users,
      pagination,
      loading,
      currentUser,
      dialogVisible,
      dialogMode,
      userForm,
      userFormRef,
      rules,
      roleFilter,
      pageSize,
      currentPage,
      showAddUserDialog,
      handleEdit,
      handleDelete,
      submitUserForm,
      handleRoleFilterChange,
      handleSizeChange,
      handleCurrentChange,
      formatDate,
      getRoleText,
      getRoleTagType
    }
  }
}
</script>

<style scoped>
.admin-users {
  margin-top: 20px;
}

.action-bar {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
}

.role-filter {
  margin-left: auto;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.password-hint {
  color: #909399;
  margin-top: 5px;
}
</style> 