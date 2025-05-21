from flask import jsonify, request
from . import api_bp
from ..models import User, Course, Activity, CourseProgress
from .. import db
from ..utils.auth import authenticate, require_role
from sqlalchemy import func
from werkzeug.security import generate_password_hash
from datetime import datetime

# 管理员路由

@api_bp.route('/admin/overview', methods=['GET'])
@authenticate
@require_role('admin')
def admin_overview():
    """获取系统概览数据"""
    # 用户统计
    user_counts = {
        'total': User.query.count(),
        'students': User.query.filter_by(role='student').count(),
        'teachers': User.query.filter_by(role='teacher').count(),
        'admins': User.query.filter_by(role='admin').count()
    }
    
    # 课程统计
    course_counts = {
        'total': Course.query.count(),
        'active': Course.query.filter_by(status='active').count(),
        'archived': Course.query.filter_by(status='archived').count()
    }
    
    # 活动统计
    activity_counts = {
        'total': Activity.query.count(),
        'completed': Activity.query.filter(Activity.completion_status == 'completed').count()
    }
    
    # 按活动类型分布
    activity_types = db.session.query(
        Activity.activity_type, 
        func.count(Activity.id)
    ).group_by(Activity.activity_type).all()
    
    activity_type_distribution = {type_name: count for type_name, count in activity_types}
    
    data = {
        'user_counts': user_counts,
        'course_counts': course_counts,
        'activity_counts': activity_counts,
        'activity_type_distribution': activity_type_distribution
    }
    
    print("返回系统概览数据:", data)
    
    return jsonify({
        'status': 'success',
        'data': data
    })

# 用户管理API

@api_bp.route('/admin/users', methods=['GET'])
@authenticate
@require_role('admin')
def admin_get_all_users():
    """获取所有用户信息"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    role_filter = request.args.get('role', None)
    
    print(f"获取用户列表: page={page}, per_page={per_page}, role={role_filter}")
    
    query = User.query
    
    # 按角色筛选
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    # 分页查询
    pagination = query.paginate(page=page, per_page=per_page)
    users = pagination.items
    
    result = {
        'status': 'success',
        'users': [user.to_dict() for user in users],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }
    
    print(f"返回用户数据: {len(result['users'])}条记录")
    
    return jsonify(result)

@api_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@authenticate
@require_role('admin')
def admin_get_user_detail(user_id):
    """获取单个用户详细信息"""
    user = User.query.get_or_404(user_id)
    
    # 获取用户的课程信息
    courses_data = []
    if user.role == 'student':
        # 学生的选修课程
        for course in user.enrolled_courses:
            course_dict = course.to_dict()
            # 获取课程进度
            progress = CourseProgress.query.filter_by(
                user_id=user_id, course_id=course.id
            ).first()
            course_dict['progress'] = progress.progress_percent if progress else 0
            courses_data.append(course_dict)
    elif user.role == 'teacher':
        # 教师的教授课程
        courses_data = [course.to_dict() for course in user.teaching_courses]
    
    # 获取用户活动统计
    activities_count = Activity.query.filter_by(user_id=user_id).count()
    
    user_data = user.to_dict()
    user_data['courses'] = courses_data
    user_data['activities_count'] = activities_count
    
    return jsonify({
        'status': 'success',
        'user': user_data
    })

@api_bp.route('/admin/users', methods=['POST'])
@authenticate
@require_role('admin')
def admin_create_user():
    """创建新用户"""
    data = request.json
    
    # 验证必填字段
    if not all(k in data for k in ('account', 'username', 'email', 'password', 'role')):
        return jsonify({
            'status': 'error',
            'message': '缺少必要的用户信息'
        }), 400
    
    # 验证角色
    if data['role'] not in ('student', 'teacher', 'admin'):
        return jsonify({
            'status': 'error',
            'message': '无效的用户角色'
        }), 400
    
    # 检查账号是否已存在
    if User.query.filter_by(account=data['account']).first():
        return jsonify({
            'status': 'error',
            'message': '账号已被占用'
        }), 400
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'status': 'error',
            'message': '邮箱已被注册'
        }), 400
    
    # 创建新用户
    new_user = User(
        account=data['account'],
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        role=data['role'],
        bio=data.get('bio', ''),
        created_at=datetime.utcnow()
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '用户创建成功',
        'user': new_user.to_dict()
    }), 201

@api_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@authenticate
@require_role('admin')
def admin_update_user(user_id):
    """更新用户信息"""
    user = User.query.get_or_404(user_id)
    data = request.json
    
    # 更新字段
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        # 检查邮箱是否已被其他用户使用
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({
                'status': 'error',
                'message': '邮箱已被其他用户注册'
            }), 400
        user.email = data['email']
    if 'role' in data:
        if data['role'] not in ('student', 'teacher', 'admin'):
            return jsonify({
                'status': 'error',
                'message': '无效的用户角色'
            }), 400
        user.role = data['role']
    if 'bio' in data:
        user.bio = data['bio']
    if 'password' in data and data['password']:
        user.password_hash = generate_password_hash(data['password'])
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '用户信息更新成功',
        'user': user.to_dict()
    })

@api_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@authenticate
@require_role('admin')
def admin_delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    
    # 检查是否为删除自己
    current_user = request.current_user
    if current_user.id == user_id:
        return jsonify({
            'status': 'error',
            'message': '不能删除当前登录的管理员用户'
        }), 400
    
    # 删除用户相关数据（可以根据需要处理级联删除）
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '用户删除成功'
    })

# 课程管理API

@api_bp.route('/admin/courses', methods=['GET'])
@authenticate
@require_role('admin')
def admin_get_all_courses():
    """获取所有课程信息"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status_filter = request.args.get('status', None)
    
    query = Course.query
    
    # 按状态筛选
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    # 分页查询
    pagination = query.paginate(page=page, per_page=per_page)
    courses = pagination.items
    
    return jsonify({
        'status': 'success',
        'courses': [course.to_dict() for course in courses],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@api_bp.route('/admin/courses/<int:course_id>', methods=['GET'])
@authenticate
@require_role('admin')
def admin_get_course_detail(course_id):
    """获取课程详细信息"""
    course = Course.query.get_or_404(course_id)
    
    # 获取课程统计信息
    students_count = course.students.count()
    activities_count = Activity.query.filter_by(course_id=course_id).count()
    
    # 获取进度统计
    progress_stats = db.session.query(
        func.avg(CourseProgress.progress_percent)
    ).filter_by(course_id=course_id).first()
    
    avg_progress = progress_stats[0] if progress_stats[0] else 0
    
    course_data = course.to_dict()
    course_data['students_count'] = students_count
    course_data['activities_count'] = activities_count
    course_data['average_progress'] = round(avg_progress, 2)
    
    return jsonify({
        'status': 'success',
        'course': course_data
    })

@api_bp.route('/admin/courses/<int:course_id>/students', methods=['GET'])
@authenticate
@require_role('admin')
def admin_get_course_students(course_id):
    """获取课程学生及进度"""
    course = Course.query.get_or_404(course_id)
    
    # 获取所有学生及其进度
    students_data = []
    for student in course.students:
        student_dict = student.to_dict()
        # 获取进度
        progress = CourseProgress.query.filter_by(
            user_id=student.id, course_id=course_id
        ).first()
        student_dict['progress'] = progress.progress_percent if progress else 0
        students_data.append(student_dict)
    
    return jsonify({
        'status': 'success',
        'students': students_data
    })

@api_bp.route('/admin/courses', methods=['POST'])
@authenticate
@require_role('admin')
def admin_create_course():
    """管理员创建课程"""
    data = request.json
    
    # 验证必填字段
    if not all(k in data for k in ('title', 'description')):
        return jsonify({
            'status': 'error',
            'message': '缺少必要的课程信息'
        }), 400
    
    # 验证教师
    instructor_id = data.get('instructor_id')
    if instructor_id:
        instructor = User.query.filter_by(id=instructor_id, role='teacher').first()
        if not instructor:
            return jsonify({
                'status': 'error',
                'message': '无效的教师ID'
            }), 400
    
    # 处理日期格式
    start_date = None
    end_date = None
    if data.get('start_date'):
        start_date = datetime.fromisoformat(data.get('start_date'))
    if data.get('end_date'):
        end_date = datetime.fromisoformat(data.get('end_date'))
    
    new_course = Course(
        title=data.get('title'),
        description=data.get('description'),
        instructor_id=instructor_id,
        start_date=start_date,
        end_date=end_date,
        status=data.get('status', 'active')
    )
    
    db.session.add(new_course)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '课程创建成功',
        'course': new_course.to_dict()
    }), 201

@api_bp.route('/admin/courses/<int:course_id>', methods=['PUT'])
@authenticate
@require_role('admin')
def admin_update_course(course_id):
    """管理员更新课程"""
    course = Course.query.get_or_404(course_id)
    data = request.json
    
    if 'title' in data:
        course.title = data['title']
    if 'description' in data:
        course.description = data['description']
    if 'instructor_id' in data:
        # 验证教师
        instructor = User.query.filter_by(id=data['instructor_id'], role='teacher').first()
        if instructor:
            course.instructor_id = data['instructor_id']
    if 'start_date' in data and data['start_date']:
        course.start_date = datetime.fromisoformat(data['start_date'])
    if 'end_date' in data and data['end_date']:
        course.end_date = datetime.fromisoformat(data['end_date'])
    if 'status' in data:
        course.status = data['status']
    
    course.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '课程更新成功',
        'course': course.to_dict()
    })

@api_bp.route('/admin/courses/<int:course_id>', methods=['DELETE'])
@authenticate
@require_role('admin')
def admin_delete_course(course_id):
    """管理员删除课程"""
    course = Course.query.get_or_404(course_id)
    
    # 删除课程(可以根据需要处理级联删除)
    db.session.delete(course)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '课程删除成功'
    })

@api_bp.route('/admin/courses/<int:course_id>/students', methods=['POST'])
@authenticate
@require_role('admin')
def admin_add_student_to_course(course_id):
    """管理员为课程添加学生"""
    course = Course.query.get_or_404(course_id)
    data = request.json
    
    if 'student_id' not in data:
        return jsonify({
            'status': 'error',
            'message': '缺少学生ID'
        }), 400
    
    student = User.query.filter_by(id=data['student_id'], role='student').first()
    if not student:
        return jsonify({
            'status': 'error',
            'message': '无效的学生ID'
        }), 400
    
    # 检查学生是否已在课程中
    if course.students.filter_by(id=student.id).first():
        return jsonify({
            'status': 'error',
            'message': '学生已经在此课程中'
        }), 400
    
    # 添加学生到课程
    course.students.append(student)
    
    # 初始化课程进度
    progress = CourseProgress(
        user_id=student.id,
        course_id=course_id,
        progress_percent=0,
        last_activity_date=datetime.utcnow()
    )
    db.session.add(progress)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '学生成功添加到课程'
    })

@api_bp.route('/admin/courses/<int:course_id>/students/<int:student_id>', methods=['DELETE'])
@authenticate
@require_role('admin')
def admin_remove_student_from_course(course_id, student_id):
    """管理员从课程中移除学生"""
    course = Course.query.get_or_404(course_id)
    student = User.query.filter_by(id=student_id, role='student').first()
    
    if not student:
        return jsonify({
            'status': 'error',
            'message': '无效的学生ID'
        }), 400
    
    # 检查学生是否在课程中
    if not course.students.filter_by(id=student.id).first():
        return jsonify({
            'status': 'error',
            'message': '学生不在此课程中'
        }), 400
    
    # 从课程中移除学生
    course.students.remove(student)
    
    # 删除课程进度
    progress = CourseProgress.query.filter_by(
        user_id=student.id, course_id=course_id
    ).first()
    if progress:
        db.session.delete(progress)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '学生已从课程中移除'
    }) 