<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <h1 class="error-code">404</h1>
      <div class="error-icon">
        <el-icon size="64px"><WarningFilled /></el-icon>
      </div>
      <h2 class="error-title">页面找不到了</h2>
      <p class="error-message">很抱歉，您访问的页面不存在或已被移除。</p>
      <div class="actions">
        <el-button type="primary" @click="goHome">返回首页</el-button>
        <el-button @click="goBack">返回上一页</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'NotFound',
  setup() {
    const router = useRouter()
    
    const goHome = () => {
      router.push('/')
    }
    
    const goBack = () => {
      router.go(-1)
    }
    
    return {
      goHome,
      goBack
    }
  }
}
</script>

<style scoped>
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: calc(100vh - 120px);
  text-align: center;
}

.not-found-content {
  max-width: 500px;
  padding: 40px;
}

.error-code {
  font-size: 120px;
  margin: 0;
  color: #409EFF;
  line-height: 1;
}

.error-icon {
  margin: 20px 0;
  color: #E6A23C;
}

.error-title {
  font-size: 28px;
  margin: 0 0 20px 0;
  color: #303133;
}

.error-message {
  font-size: 16px;
  color: #606266;
  margin-bottom: 30px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 10px;
}
</style> 