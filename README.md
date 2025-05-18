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
flask db init
flask db migrate
flask db upgrade
```

4. 运行开发服务器
```
python run.py
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

## 技术栈

### 后端
- Python 3.8+
- Flask - Web框架
- SQLAlchemy - ORM
- Flask-RESTful - RESTful API开发
- Flask-Migrate - 数据库迁移

### 前端
- Vue.js 3 - 前端框架
- Vuex - 状态管理
- Vue Router - 路由管理
- Element Plus - UI组件库
- Chart.js - 数据可视化

## 贡献

欢迎提交问题和改进建议。请先fork本仓库，创建分支，提交代码后发起pull request。

## 许可证

[MIT](LICENSE) 