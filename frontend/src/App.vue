<template>
  <div id="app">
    <el-container v-if="isLoggedIn">
      <el-aside width="200px">
        <el-menu
          :router="true"
          class="sidebar-menu"
          :default-active="$route.path"
        >
          <el-menu-item index="/dashboard">
            <i class="el-icon-menu"></i>
            <span>仪表板</span>
          </el-menu-item>
          <el-menu-item index="/courses">
            <i class="el-icon-document"></i>
            <span>课程</span>
          </el-menu-item>
          <el-menu-item index="/analytics">
            <i class="el-icon-s-data"></i>
            <span>数据分析</span>
          </el-menu-item>
          <el-menu-item index="/profile">
            <i class="el-icon-user"></i>
            <span>个人资料</span>
          </el-menu-item>
          <el-menu-item @click="handleLogout">
            <i class="el-icon-switch-button"></i>
            <span>退出登录</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header>
          <div class="header-container">
            <h2>学习分析平台</h2>
            <div class="user-info">
              <span>{{ currentUser.username }}</span>
              <el-avatar :size="32" :src="avatarUrl"></el-avatar>
            </div>
          </div>
        </el-header>
        <el-main>
          <router-view />
        </el-main>
        <el-footer>
          <p>&copy; 2023 学习分析平台</p>
        </el-footer>
      </el-container>
    </el-container>
    
    <div v-else>
      <router-view />
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'App',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const isLoggedIn = computed(() => store.getters['auth/isLoggedIn'])
    const currentUser = computed(() => store.state.auth.user || {})
    const avatarUrl = computed(() => {
      // 如果有用户头像，使用用户头像；否则使用默认头像
      return currentUser.value.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
    })
    
    const handleLogout = async () => {
      try {
        await store.dispatch('auth/logout')
        ElMessage.success('已成功退出登录')
        // 强制导航到登录页面
        router.push('/login')
      } catch (error) {
        console.error('退出登录失败', error)
        ElMessage.error('退出登录失败')
      }
    }
    
    return {
      isLoggedIn,
      currentUser,
      avatarUrl,
      handleLogout
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100vh;
}

.el-header {
  background-color: #fff;
  color: #333;
  border-bottom: 1px solid #eee;
  padding: 0 20px;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.el-aside {
  background-color: #304156;
  color: #fff;
}

.sidebar-menu {
  height: 100%;
  border-right: none;
}

.el-footer {
  text-align: center;
  color: #999;
  padding: 20px;
}
</style> 