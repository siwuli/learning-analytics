<template>
  <div class="student-manager">
    <h3 class="student-manager-title">
      学生管理
      <el-button 
        type="primary" 
        size="small" 
        @click="showAddStudentDialog"
      >
        添加学生
      </el-button>
    </h3>
    
    <el-table 
      :data="students" 
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column prop="id" label="学号" width="80"></el-table-column>
      <el-table-column prop="username" label="姓名" width="120"></el-table-column>
      <el-table-column prop="email" label="邮箱"></el-table-column>
      <el-table-column label="操作" width="100" align="center">
        <template #default="scope">
          <el-button 
            type="danger" 
            size="small" 
            @click="confirmRemoveStudent(scope.row)"
          >
            移除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 空状态 -->
    <div v-if="students.length === 0 && !loading" class="no-students">
      <el-empty description="暂无学生"></el-empty>
    </div>
    
    <!-- 添加学生对话框 -->
    <el-dialog 
      v-model="addStudentDialogVisible" 
      title="添加学生" 
      width="600px"
      destroy-on-close
    >
      <div class="search-box">
        <el-input 
          v-model="searchQuery" 
          placeholder="搜索学生姓名或邮箱" 
          prefix-icon="el-icon-search"
          clearable
          @input="handleSearch"
        ></el-input>
      </div>
      
      <div class="selection-area">
        <div class="selection-list">
          <h4>可选学生列表</h4>
          <div v-loading="searchLoading">
            <el-checkbox-group v-model="selectedStudents">
              <div v-for="student in availableStudents" :key="student.id" class="student-item">
                <el-checkbox :label="student.id">
                  {{ student.username }} ({{ student.email }})
                </el-checkbox>
              </div>
            </el-checkbox-group>
            
            <div v-if="availableStudents.length === 0 && !searchLoading" class="no-results">
              <el-empty description="没有找到匹配的学生" :image-size="100"></el-empty>
            </div>
          </div>
        </div>
        
        <div class="selection-preview">
          <h4>已选 ({{ selectedStudents.length }})</h4>
          <el-tag 
            v-for="id in selectedStudents" 
            :key="id"
            closable
            @close="removeSelectedStudent(id)"
            class="selected-tag"
          >
            {{ getStudentName(id) }}
          </el-tag>
          
          <div v-if="selectedStudents.length === 0" class="no-selection">
            <span class="hint-text">请从左侧列表选择学生</span>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="addStudentDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="addStudents"
          :disabled="selectedStudents.length === 0"
          :loading="addingStudents"
        >
          添加 {{ selectedStudents.length }} 个学生
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { courseAPI } from '@/services/api'
import { debounce } from 'lodash'

export default {
  name: 'StudentManager',
  props: {
    courseId: {
      type: [Number, String],
      required: true
    }
  },
  emits: ['updated'],
  setup(props, { emit }) {
    const loading = ref(false)
    const students = ref([])
    const addStudentDialogVisible = ref(false)
    const searchQuery = ref('')
    const searchLoading = ref(false)
    const availableStudents = ref([])
    const selectedStudents = ref([])
    const addingStudents = ref(false)
    
    // 获取学生列表
    const loadStudents = async () => {
      loading.value = true
      try {
        const response = await courseAPI.getCourseStudents(props.courseId)
        students.value = response.data.students || []
      } catch (error) {
        console.error('获取学生列表失败:', error)
        ElMessage.error('获取学生列表失败')
      } finally {
        loading.value = false
      }
    }
    
    // 搜索未选课学生
    const searchStudents = async (query) => {
      searchLoading.value = true
      try {
        const response = await courseAPI.searchNotEnrolledStudents(props.courseId, query)
        availableStudents.value = response.data.students || []
      } catch (error) {
        console.error('搜索学生失败:', error)
        ElMessage.error('搜索学生失败')
        availableStudents.value = []
      } finally {
        searchLoading.value = false
      }
    }
    
    // 使用防抖函数处理搜索输入
    const handleSearch = debounce((val) => {
      searchStudents(searchQuery.value)
    }, 500)
    
    // 显示添加学生对话框
    const showAddStudentDialog = () => {
      addStudentDialogVisible.value = true
      selectedStudents.value = []
      searchQuery.value = ''
      searchStudents('')
    }
    
    // 从选定列表中移除学生
    const removeSelectedStudent = (id) => {
      const index = selectedStudents.value.indexOf(id)
      if (index !== -1) {
        selectedStudents.value.splice(index, 1)
      }
    }
    
    // 批量添加学生
    const addStudents = async () => {
      if (selectedStudents.value.length === 0) return
      
      addingStudents.value = true
      try {
        const response = await courseAPI.batchEnrollStudents(
          props.courseId, 
          { student_ids: selectedStudents.value }
        )
        
        ElMessage.success(response.data.message || '学生添加成功')
        addStudentDialogVisible.value = false
        await loadStudents()  // 重新加载学生列表
        emit('updated')
      } catch (error) {
        console.error('添加学生失败:', error)
        ElMessage.error('添加学生失败: ' + (error.response?.data?.message || error.message))
      } finally {
        addingStudents.value = false
      }
    }
    
    // 确认移除学生
    const confirmRemoveStudent = (student) => {
      ElMessageBox.confirm(
        `确定要将学生 ${student.username} 从课程中移除吗？`,
        '确认移除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
        .then(() => removeStudent(student.id))
        .catch(() => {})
    }
    
    // 移除学生
    const removeStudent = async (studentId) => {
      loading.value = true
      try {
        await courseAPI.dropStudent(props.courseId, studentId)
        ElMessage.success('学生已成功移除')
        await loadStudents()  // 重新加载学生列表
        emit('updated')
      } catch (error) {
        console.error('移除学生失败:', error)
        ElMessage.error('移除学生失败: ' + (error.response?.data?.message || error.message))
      } finally {
        loading.value = false
      }
    }
    
    // 获取学生名称
    const getStudentName = (id) => {
      const student = availableStudents.value.find(s => s.id === id)
      return student ? student.username : id
    }
    
    onMounted(() => {
      loadStudents()
    })
    
    return {
      loading,
      students,
      addStudentDialogVisible,
      searchQuery,
      searchLoading,
      availableStudents,
      selectedStudents,
      addingStudents,
      showAddStudentDialog,
      handleSearch,
      removeSelectedStudent,
      addStudents,
      confirmRemoveStudent,
      getStudentName
    }
  }
}
</script>

<style scoped>
.student-manager {
  margin-bottom: 20px;
}

.student-manager-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.search-box {
  margin-bottom: 20px;
}

.selection-area {
  display: flex;
  gap: 20px;
  min-height: 300px;
}

.selection-list {
  flex: 1;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 10px;
  overflow-y: auto;
  max-height: 300px;
}

.selection-preview {
  flex: 1;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 10px;
  overflow-y: auto;
  max-height: 300px;
}

.student-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.student-item:last-child {
  border-bottom: none;
}

.selected-tag {
  margin: 5px;
}

.no-selection, .no-results {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
  color: #909399;
}

.hint-text {
  color: #909399;
  font-size: 14px;
}

.no-students {
  margin-top: 20px;
}
</style> 