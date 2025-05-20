<template>
  <div class="safe-video-container">
    <div class="video-wrapper" ref="videoWrapper">
      <video
        v-if="videoUrl"
        ref="videoPlayer"
        class="video-element"
        controls
        :src="videoUrl"
        @loadedmetadata="handleVideoLoaded"
        @timeupdate="handleTimeUpdate"
        @error="handleVideoError"
      ></video>
      <div v-else-if="!videoUrl && !error" class="video-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>视频加载中...</span>
      </div>
      <div v-else-if="error" class="video-error">
        <el-icon><Warning /></el-icon>
        <span>{{ error }}</span>
        <div class="error-url">
          <el-link :href="src" target="_blank" type="primary">
            打开视频链接
          </el-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ElIcon } from 'element-plus'
import { Loading, Warning } from '@element-plus/icons-vue'

export default {
  name: 'SafeVideoPlayer',
  components: {
    ElIcon,
    Loading,
    Warning
  },
  props: {
    src: {
      type: String,
      required: true
    }
  },
  emits: ['timeupdate'],
  setup(props, { emit }) {
    const videoWrapper = ref(null)
    const videoPlayer = ref(null)
    const videoUrl = ref('')
    const error = ref('')
    const isLoaded = ref(false)
    
    // 处理视频加载
    const loadVideo = () => {
      error.value = ''
      
      // 检查URL格式
      if (!props.src) {
        error.value = '无效的视频链接'
        return
      }
      
      // 检查是否为有效的视频URL
      if (isValidVideoUrl(props.src)) {
        videoUrl.value = props.src
      } else {
        error.value = '不支持的视频格式'
      }
    }
    
    // 验证视频URL
    const isValidVideoUrl = (url) => {
      // 简单检查是否为常见视频格式或URL
      const videoExtensions = /\.(mp4|webm|ogg|mov)$/i
      return url.match(videoExtensions) || url.startsWith('http')
    }
    
    // 视频元数据加载完成
    const handleVideoLoaded = () => {
      if (videoPlayer.value) {
        // 使视频元素可见
        videoPlayer.value.style.visibility = 'visible'
        videoPlayer.value.style.opacity = '1'
        isLoaded.value = true
      }
    }
    
    // 视频播放进度更新
    const handleTimeUpdate = (event) => {
      // 降低更新频率，减少不必要的事件
      const now = Date.now()
      if (!handleTimeUpdate.lastUpdate || now - handleTimeUpdate.lastUpdate > 1000) {
        handleTimeUpdate.lastUpdate = now
        emit('timeupdate', event.target.currentTime)
      }
    }
    
    // 视频加载错误
    const handleVideoError = () => {
      error.value = '视频加载失败'
    }
    
    // 组件挂载时加载视频
    onMounted(() => {
      loadVideo()
      
      // 延迟加载，避免立即触发ResizeObserver
      setTimeout(() => {
        // 如果视频未成功加载，尝试刷新
        if (videoPlayer.value && !isLoaded.value) {
          videoPlayer.value.load()
        }
      }, 500)
    })
    
    return {
      videoWrapper,
      videoPlayer,
      videoUrl,
      error,
      handleVideoLoaded,
      handleTimeUpdate,
      handleVideoError
    }
  }
}
</script>

<style scoped>
.safe-video-container {
  width: 100%;
  margin: 0 auto;
}

.video-wrapper {
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 56.25%; /* 16:9宽高比 */
  overflow: hidden;
  background-color: #f0f0f0;
  border-radius: 4px;
}

.video-element {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  visibility: hidden;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.video-loading,
.video-error {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #909399;
}

.video-loading .el-icon,
.video-error .el-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.error-url {
  margin-top: 12px;
}
</style> 