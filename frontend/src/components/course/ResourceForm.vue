<template>
  <el-form 
    ref="formRef"
    :model="form"
    :rules="rules"
    label-position="top"
    class="resource-form"
  >
    <el-form-item label="资源标题" prop="title">
      <el-input v-model="form.title" placeholder="请输入资源标题"></el-input>
    </el-form-item>
    
    <el-form-item label="资源描述" prop="description">
      <el-input
        v-model="form.description"
        type="textarea"
        :rows="3"
        placeholder="请输入资源描述"
      ></el-input>
    </el-form-item>
    
    <el-form-item label="资源类型" prop="resource_type">
      <el-select v-model="form.resource_type" placeholder="请选择资源类型" style="width: 100%">
        <el-option label="文档" value="document"></el-option>
        <el-option label="视频" value="video"></el-option>
        <el-option label="文件" value="file"></el-option>
      </el-select>
    </el-form-item>
    
    <!-- 表单内容区域 -->
    <div class="form-content-area">
      <!-- 添加加载状态指示 -->
      <div v-if="form.isTypeChanging" class="loading-overlay">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      
      <!-- 根据资源类型显示不同的内容输入 -->
      <template v-if="form.resource_type === 'document'">
        <el-form-item label="文档内容 (Markdown格式)" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="10"
            placeholder="请输入文档内容，支持Markdown格式"
          ></el-input>
        </el-form-item>
      </template>
      
      <template v-else-if="form.resource_type === 'video' && !form.isTypeChanging">
        <el-form-item label="视频URL" prop="content">
          <el-input 
            v-model="form.content" 
            placeholder="请输入视频URL或嵌入代码"
          ></el-input>
        </el-form-item>
      </template>
      
      <template v-else-if="form.resource_type === 'file' && !form.isTypeChanging">
        <el-form-item label="上传文件" prop="file">
          <el-upload
            class="resource-file-upload"
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :file-list="fileList"
            :limit="1"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持PDF、Word、PPT、Excel、图片等格式，文件大小不超过50MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </template>
    </div>
    
    <el-form-item label="显示顺序" prop="order">
      <el-input-number v-model="form.order" :min="1" :max="100"></el-input-number>
    </el-form-item>
    
    <el-form-item>
      <el-button type="primary" @click="submitForm" :loading="submitting">保存</el-button>
      <el-button @click="resetForm">重置</el-button>
    </el-form-item>
  </el-form>
</template>

<script>
import { ref, reactive, computed, watch, onMounted, nextTick, onBeforeUnmount } from 'vue'
import { ElMessage, ElIcon } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { createSafeResizeObserver } from '../../utils/resizeUtil'
import { fileAPI } from '@/services/api'

export default {
  name: 'ResourceForm',
  components: {
    ElIcon,
    Loading
  },
  props: {
    sectionId: {
      type: [Number, String],
      required: true
    },
    resource: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['submit', 'cancel'],
  setup(props, { emit }) {
    const formRef = ref(null)
    const submitting = ref(false)
    
    // 用于防止ResizeObserver循环错误
    const resizeObserver = ref(null)
    
    // 文件上传相关
    const fileList = ref([])
    const selectedFile = ref(null)
    const uploadProgress = ref(0)
    const isUploading = ref(false)
    
    // 表单数据
    const form = reactive({
      title: props.resource.title || '',
      description: props.resource.description || '',
      resource_type: props.resource.resource_type || 'document',
      content: props.resource.content || '',
      file_path: props.resource.file_path || '',
      order: props.resource.order || 1,
      isTypeChanging: false
    })
    
    // 初始化文件列表
    if (props.resource.file_path && props.resource.resource_type === 'file') {
      const filename = props.resource.file_path.split('_').slice(1).join('_');
      fileList.value = [
        { 
          name: filename || '已上传文件',
          url: props.resource.content || ''
        }
      ];
    }
    
    // 表单验证规则
    const rules = {
      title: [
        { required: true, message: '请输入资源标题', trigger: 'blur' },
        { min: 2, max: 100, message: '长度在2到100个字符之间', trigger: 'blur' }
      ],
      description: [
        { required: true, message: '请输入资源描述', trigger: 'blur' }
      ],
      resource_type: [
        { required: true, message: '请选择资源类型', trigger: 'change' }
      ],
      content: [
        { 
          required: true, 
          message: '请输入资源内容', 
          trigger: 'blur',
          validator: (rule, value, callback) => {
            if (form.resource_type === 'file' && !form.file_path && !selectedFile.value) {
              callback(new Error('请上传文件'));
            } else if ((form.resource_type === 'document' || form.resource_type === 'video') && !value) {
              callback(new Error('请输入资源内容'));
            } else {
              callback();
            }
          }
        }
      ]
    }
    
    // 优化资源类型切换处理，防止ResizeObserver错误
    const handleResourceTypeChange = async (newType, oldType) => {
      try {
        // 先断开之前的ResizeObserver连接
        if (resizeObserver.value) {
          resizeObserver.value.disconnect();
          resizeObserver.value = null;
        }
        
        // 标记正在切换状态
        form.isTypeChanging = true;
        
        // 等待DOM更新
        await nextTick();
        
        // 如果类型不同且不是切换到文件类型，重置内容字段
        if (oldType !== newType && newType !== 'file') {
          form.content = '';
        }
        
        // 如果切换到文件类型，但没有选择过文件，清空文件列表
        if (newType === 'file' && !form.file_path) {
          fileList.value = [];
          selectedFile.value = null;
        }
        
        // 延迟结束加载状态
        setTimeout(() => {
          form.isTypeChanging = false;
          
          // 再次等待DOM更新完成
          nextTick().then(() => {
            // 重新设置ResizeObserver
            setupResizeObserver();
          });
        }, 200);
      } catch (error) {
        console.error('资源类型切换处理错误:', error);
        form.isTypeChanging = false;
        
        // 安全恢复
        setTimeout(() => {
          setupResizeObserver();
        }, 500);
      }
    };
    
    // 监听资源类型变化
    watch(() => form.resource_type, (newType, oldType) => {
      handleResourceTypeChange(newType, oldType);
    });
    
    // 处理文件选择变化
    const handleFileChange = (file, fileList) => {
      selectedFile.value = file.raw;
      // 选择新文件时重置进度
      uploadProgress.value = 0;
    };
    
    // 处理文件移除
    const handleFileRemove = () => {
      selectedFile.value = null;
      form.file_path = '';
      form.content = '';
    };
    
    // 上传文件
    const uploadFile = async () => {
      if (!selectedFile.value) return null;
      
      isUploading.value = true;
      
      try {
        const response = await fileAPI.uploadFile(selectedFile.value, (progress) => {
          uploadProgress.value = progress;
        });
        
        isUploading.value = false;
        
        if (response.data.status === 'success') {
          form.file_path = response.data.file_path;
          form.content = response.data.file_url; // 存储文件URL作为内容
          return response.data;
        } else {
          ElMessage.error('文件上传失败');
          return null;
        }
      } catch (error) {
        console.error('文件上传错误:', error);
        isUploading.value = false;
        ElMessage.error('文件上传失败: ' + (error.message || '未知错误'));
        return null;
      }
    };
    
    // 设置安全的ResizeObserver
    const setupResizeObserver = () => {
      // 断开之前的连接
      if (resizeObserver.value) {
        resizeObserver.value.disconnect();
      }
      
      // 使用工具创建安全的ResizeObserver
      resizeObserver.value = createSafeResizeObserver(() => {
        // 最小化回调处理，避免不必要的工作
      }, { delay: 200 });
      
      // 如果表单已挂载，观察表单元素
      if (formRef.value?.$el) {
        resizeObserver.value.observe(formRef.value.$el);
      }
    };
    
    // 清理ResizeObserver的函数
    const cleanupResizeObserver = () => {
      if (resizeObserver.value) {
        resizeObserver.value.disconnect();
        resizeObserver.value = null;
      }
    };
    
    // 提交表单
    const submitForm = async () => {
      if (!formRef.value) return;
      
      try {
        await formRef.value.validate();
        
        submitting.value = true;
        
        // 如果是文件类型且有新文件选择，先上传文件
        let uploadResult = null;
        if (form.resource_type === 'file' && selectedFile.value) {
          uploadResult = await uploadFile();
          if (!uploadResult) {
            submitting.value = false;
            return;
          }
        }
        
        // 发送表单数据到父组件
        emit('submit', {
          id: props.resource.id,
          section_id: props.sectionId,
          title: form.title,
          description: form.description,
          resource_type: form.resource_type,
          content: form.content,
          file_path: form.file_path,
          order: form.order
        });
        
        submitting.value = false;
      } catch (error) {
        submitting.value = false;
        ElMessage.error('表单验证失败，请检查输入');
      }
    };
    
    // 重置表单
    const resetForm = () => {
      if (formRef.value) {
        formRef.value.resetFields();
      }
      
      if (form.resource_type === 'file') {
        fileList.value = [];
        selectedFile.value = null;
        form.file_path = '';
      }
    };
    
    // 组件挂载时设置ResizeObserver
    onMounted(() => {
      setupResizeObserver();
    });
    
    // 组件卸载前清理ResizeObserver
    onBeforeUnmount(() => {
      cleanupResizeObserver();
    });
    
    return {
      formRef,
      form,
      rules,
      fileList,
      submitting,
      uploadProgress,
      handleFileChange,
      handleFileRemove,
      submitForm,
      resetForm,
      cleanupResizeObserver // 导出清理函数以便在父组件使用
    }
  }
}
</script>

<style scoped>
.resource-form {
  /* 添加固定高度，减少动态高度变化导致的ResizeObserver错误 */
  min-height: 500px;
  position: relative;
}

.resource-file-upload {
  width: 100%;
  margin-bottom: 20px;
}

.el-upload__tip {
  color: #909399;
  margin-top: 5px;
}

.form-content-area {
  position: relative;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
}
</style> 