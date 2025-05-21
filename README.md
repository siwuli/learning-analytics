# 学习分析系统

这是一个基于Python Flask + Vue.js的学习分析系统，用于追踪和分析学生的学习行为和进度。

## 项目界面与功能

系统分为教师端、学生端和管理员端三大界面：

### 教师端功能

教师端类似后台管理界面，提供以下功能：

- **数据仪表盘**：直观展示课程整体进度、学生参与度和活动分布
- **数据管理**：对系统数据进行增删查改操作
- **课程管理**：创建、修改、删除课程，管理课程内容
- **任务发布**：为课程创建和发布学习任务
- **学生管理**：查看和管理学生账户信息
- **成绩统计**：统计和分析学生成绩数据
- **课程统计**：查看各课程学生名单和学习情况
- **数据分析**：通过图表直观展示学习数据和趋势

### 学生端功能

学生端为学习者提供友好的界面，包含以下功能：

- **个人仪表盘**：展示学习概览、进度统计和最近活动
- **课程查看**：浏览和查看已选课程
- **任务管理**：查看和完成课程分配的任务
- **成绩查询**：查询个人各课程成绩和评价
- **学习记录**：跟踪个人学习活动和进度
- **个人资料**：管理个人账户信息

### 管理员端功能

管理员拥有系统最高权限，可以：

- **系统仪表盘**：查看全系统用户、课程和活动统计
- **用户管理**：创建和管理所有用户账户
- **系统监控**：监控整个平台的运行状态
- **全局数据统计**：查看全平台的学习数据统计

## 项目结构

```
learning-analytics/
├── backend/                  # Flask后端
│   ├── app/                  # 应用代码
│   │   ├── api/              # API端点
│   │   ├── models/           # 数据模型
│   │   ├── services/         # 业务逻辑
│   │   └── utils/            # 工具函数
│   ├── config.py             # 配置文件
│   ├── migrations/           # 数据库迁移文件
│   ├── requirements.txt      # Python依赖
│   └── run.py                # 启动脚本
└── frontend/                 # Vue.js前端
    ├── public/               # 静态资源
    └── src/                  # 源代码
        ├── assets/           # 前端资源
        ├── components/       # Vue组件
        ├── store/            # Vuex状态管理
        ├── views/            # 页面视图
        └── router/           # 路由配置
```

## 核心功能特性

- **用户角色管理**：支持学生、教师和管理员角色，不同角色拥有不同权限和视图
- **数据驱动仪表盘**：
  - 集成实时API数据的响应式仪表盘
  - 学习活动类型分布图表（饼图）
  - 学习时间/活动趋势图表（折线图）
  - 角色特定内容展示（学生、教师、管理员）
- **课程管理**：创建、编辑和管理课程，跟踪课程进度
- **学习活动追踪**：记录视频观看、文档阅读、测验和作业等学习活动
- **数据分析**：学生进度分析、课程参与度分析
- **可视化展示**：直观展示学习数据和指标
- **多维度分析**：基于学习行为的多维度分析

## 系统角色与权限

### 教师角色
- 创建和管理课程
- 发布学习任务和材料
- 查看学生的学习数据和成绩
- 分析课程整体学习情况
- 管理课程学生名单

### 学生角色
- 查看和选择课程
- 完成学习任务
- 查看个人学习进度
- 查询个人成绩
- 管理个人资料

### 管理员角色
- 管理所有用户和课程
- 查看全系统数据统计
- 监控系统运行状态
- 管理系统配置

## 安装与运行

### 环境要求
- Python 3.8+
- Node.js 14+
- MySQL 5.7+

### 后端

1. 克隆项目到本地
```
git clone https://github.com/your-username/learning-analytics.git
cd learning-analytics
```

2. 进入后端目录
```
cd backend
```

3. 安装依赖
```
pip install -r requirements.txt
```

4. 配置环境变量
创建`.flaskenv`文件并配置:
```
FLASK_APP=run.py
FLASK_ENV=development
```

5. 初始化数据库
```
flask --app run db init
flask --app run db migrate -m "初始化数据库"
flask --app run db upgrade
```

6. 创建测试数据（可选）
```
python create_test_data.py
```

7. 运行开发服务器
```
flask --app run run --debug
```

### 前端

1. 进入前端目录
```
cd frontend
```

2. 安装依赖
```
npm install
```

3. 配置API地址
在`src/services/api.js`文件中检查和修改API基础URL，确保与后端服务地址一致。

4. 运行开发服务器
```
npm run serve
```

5. 构建生产版本
```
npm run build
```

## API端点

后端提供了以下主要API端点：

### 用户API
- GET /api/users - 获取所有用户
- GET /api/users/{id} - 获取单个用户
- POST /api/users - 创建用户
- PUT /api/users/{id} - 更新用户
- DELETE /api/users/{id} - 删除用户

### 课程API
- GET /api/courses - 获取所有课程
- GET /api/courses/{id} - 获取单个课程
- POST /api/courses - 创建课程
- PUT /api/courses/{id} - 更新课程
- DELETE /api/courses/{id} - 删除课程
- POST /api/courses/{id}/enroll/{user_id} - 将学生加入课程
- GET /api/courses/{id}/students - 获取课程的所有学生

### 活动API
- GET /api/activities - 获取活动记录
- GET /api/activities/{id} - 获取单个活动记录
- POST /api/activities - 创建活动记录
- PUT /api/activities/{id} - 更新活动记录
- DELETE /api/activities/{id} - 删除活动记录
- GET /api/users/{id}/activities - 获取用户的所有活动记录
- GET /api/courses/{id}/activities - 获取课程的所有活动记录

### 分析API
- GET /api/analytics/user/{id} - 获取用户的学习分析数据
- GET /api/analytics/course/{id} - 获取课程的分析数据
- GET /api/analytics/overview - 获取系统整体分析概览
- GET /api/analytics/student-learning/{id} - 获取学生的详细学习分析
- GET /api/analytics/class-performance/{id} - 获取班级整体表现分析

## 技术栈

### 后端
- Python 3.8+
- Flask - Web框架
- SQLAlchemy - ORM
- Flask-Migrate - 数据库迁移
- Flask-CORS - 跨域资源共享

### 前端
- Vue.js 3 - 前端框架
- Vuex - 状态管理
- Vue Router - 路由管理
- Element Plus - UI组件库
- Chart.js - 数据可视化
- Axios - HTTP客户端

## 最近改进记录

### 仪表盘功能完善
- 集成实时API数据，替代了先前的模拟数据
- 添加学习活动类型分布图表，支持中文显示不同活动类型
- 添加学习时间/活动趋势图表，展示用户参与度
- 针对学生、教师和管理员实现不同的仪表盘内容

### 教师课程进度显示优化
- 修复教师端课程进度获取和显示问题
- 解决数据加载完成后界面消失的问题
- 设置默认进度值，确保进度条正常显示

### 活动类型显示优化
- 为英文活动类型添加中文翻译，提升用户体验
- 特别优化'document_read'和'video_watch'等活动类型的显示

### 用户界面优化
- 移除导致404错误的待办事项组件
- 清理相关UI组件、数据获取逻辑、样式和函数