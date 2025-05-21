<template>
  <div class="admin-dashboard">
    <h1>管理员控制台</h1>
    
    <!-- 系统概览统计卡片 -->
    <el-row :gutter="20" class="dashboard-stats">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ systemData?.user_counts?.total || 0 }}</div>
          <div class="stat-label">用户总数</div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ systemData?.course_counts?.total || 0 }}</div>
          <div class="stat-label">课程总数</div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ systemData?.activity_counts?.total || 0 }}</div>
          <div class="stat-label">活动总数</div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ systemData?.activity_counts?.completed || 0 }}</div>
          <div class="stat-label">已完成活动</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 管理选项卡 -->
    <el-tabs v-model="activeTab" type="border-card" class="admin-tabs">
      <el-tab-pane label="用户管理" name="users">
        <template #label>
          <span><i class="el-icon-user"></i> 用户管理</span>
        </template>
        <admin-users-list />
      </el-tab-pane>
      
      <el-tab-pane label="课程管理" name="courses">
        <template #label>
          <span><i class="el-icon-document"></i> 课程管理</span>
        </template>
        <admin-courses-list />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import AdminUsersList from '../components/admin/AdminUsersList.vue'
import AdminCoursesList from '../components/admin/AdminCoursesList.vue'

export default {
  name: 'AdminDashboard',
  components: {
    AdminUsersList,
    AdminCoursesList
  },
  setup() {
    const store = useStore()
    const activeTab = ref('users')
    
    // 获取系统概览数据
    const systemData = computed(() => store.state.admin.systemOverview)
    const loading = computed(() => store.state.admin.loading)
    
    // 逐步加载管理员数据
    const loadAdminData = async () => {
      console.log('开始加载管理员数据')
      
      try {
        // 先加载用户列表
        console.log('加载用户列表...')
        await store.dispatch('admin/fetchUsers')
        console.log('用户列表加载成功')
        
        // 再加载课程列表
        console.log('加载课程列表...')
        try {
          await store.dispatch('admin/fetchCourses')
          console.log('课程列表加载成功')
        } catch (error) {
          console.error('加载课程列表失败:', error)
        }
        
        // 最后再尝试加载系统概览
        console.log('加载系统概览...')
        try {
          await store.dispatch('admin/fetchSystemOverview')
          console.log('系统概览加载成功')
        } catch (error) {
          console.error('加载系统概览失败:', error)
        }
      } catch (error) {
        console.error('管理员数据加载失败:', error)
      }
    }
    
    onMounted(() => {
      loadAdminData()
    })
    
    return {
      activeTab,
      systemData,
      loading
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  padding: 20px;
}

.dashboard-stats {
  margin-top: 20px;
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  border-radius: 8px;
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.admin-tabs {
  margin-top: 20px;
}
</style> 