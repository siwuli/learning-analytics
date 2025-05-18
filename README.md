# 学习分析系统

这是一个基于Python Flask + Vue.js的学习分析系统，用于追踪和分析学生的学习行为和进度。

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

## 功能特性

- 用户管理：支持学生、教师和管理员角色
- 课程管理：创建、编辑和管理课程
- 学习活动追踪：记录视频观看、测验和作业等学习活动
- 数据分析：学生进度分析、课程参与度分析
- 可视化仪表板：直观展示学习数据和指标
- 多维度分析：基于学习行为的多维度分析

## 安装与运行

### 后端

1. 进入后端目录
```
cd backend
```

2. 安装依赖
```
pip install -r requirements.txt
```

3. 初始化数据库
```
flask --app run db init
flask --app run db migrate -m "初始化数据库"
flask --app run db upgrade
```

4. 运行开发服务器
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

3. 运行开发服务器
```
npm run serve
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

## 开发指南

### 添加新模型
1. 在 `backend/app/models/` 目录下创建新的模型文件
2. 在 `backend/app/models/__init__.py` 中导入新模型
3. 运行 `flask --app run db migrate -m "添加新模型"` 创建迁移
4. 运行 `flask --app run db upgrade` 应用迁移

### 添加新API
1. 在 `backend/app/api/` 目录下创建新的API文件或在现有文件中添加路由
2. 在 `backend/app/api/__init__.py` 中导入新API模块

## 贡献

欢迎提交问题和改进建议。请先fork本仓库，创建分支，提交代码后发起pull request。

## 许可证

[MIT](LICENSE) 