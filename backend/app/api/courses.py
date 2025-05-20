from flask import jsonify, request
from . import api_bp
from ..models import Course, User, CourseProgress
from .. import db
from datetime import datetime
from sqlalchemy import or_

@api_bp.route('/courses', methods=['GET'])
def get_courses():
    """获取所有课程"""
    courses = Course.query.all()
    return jsonify({
        'status': 'success',
        'courses': [course.to_dict() for course in courses]
    })

@api_bp.route('/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """获取单个课程"""
    course = Course.query.get_or_404(course_id)
    return jsonify({
        'status': 'success',
        'course': course.to_dict()
    })

@api_bp.route('/courses', methods=['POST'])
def create_course():
    """创建课程"""
    data = request.json
    
    # 验证课程教师是否存在
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

@api_bp.route('/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    """更新课程"""
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
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '课程更新成功',
        'course': course.to_dict()
    })

@api_bp.route('/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """删除课程"""
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '课程删除成功'
    })

@api_bp.route('/courses/<int:course_id>/enroll/<int:user_id>', methods=['POST'])
def enroll_student(course_id, user_id):
    """将学生加入课程"""
    course = Course.query.get_or_404(course_id)
    user = User.query.get_or_404(user_id)
    
    if user in course.students:
        return jsonify({
            'status': 'error',
            'message': '学生已经加入该课程'
        }), 400
    
    course.students.append(user)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '学生成功加入课程'
    })

@api_bp.route('/courses/<int:course_id>/batch-enroll', methods=['POST'])
def batch_enroll_students(course_id):
    """批量添加学生到课程"""
    course = Course.query.get_or_404(course_id)
    data = request.json
    
    student_ids = data.get('student_ids', [])
    if not student_ids:
        return jsonify({
            'status': 'error',
            'message': '未提供学生ID列表'
        }), 400
    
    # 统计结果
    success_count = 0
    already_enrolled_count = 0
    failed_ids = []
    
    for student_id in student_ids:
        try:
            student = User.query.filter_by(id=student_id, role='student').first()
            if not student:
                failed_ids.append(student_id)
                continue
                
            if student in course.students:
                already_enrolled_count += 1
                continue
                
            course.students.append(student)
            success_count += 1
        except Exception as e:
            failed_ids.append(student_id)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'批量添加完成: {success_count}个学生添加成功, {already_enrolled_count}个学生已在课程中, {len(failed_ids)}个添加失败',
        'success_count': success_count,
        'already_enrolled_count': already_enrolled_count,
        'failed_ids': failed_ids
    })

@api_bp.route('/courses/<int:course_id>/students', methods=['GET'])
def get_course_students(course_id):
    """获取课程的所有学生"""
    course = Course.query.get_or_404(course_id)
    
    return jsonify({
        'status': 'success',
        'students': [student.to_dict() for student in course.students]
    })

@api_bp.route('/courses/<int:course_id>/students/search', methods=['GET'])
def search_not_enrolled_students(course_id):
    """查找未选课的学生，用于添加学生功能"""
    course = Course.query.get_or_404(course_id)
    
    # 获取查询参数
    query = request.args.get('q', '')
    
    # 构建查询
    enrolled_student_ids = [student.id for student in course.students]
    
    students_query = User.query.filter_by(role='student')
    
    # 如果有已选课学生，排除他们
    if enrolled_student_ids:
        students_query = students_query.filter(~User.id.in_(enrolled_student_ids))
    
    # 如果有搜索关键词，按用户名或邮箱搜索
    if query:
        students_query = students_query.filter(
            or_(
                User.username.like(f'%{query}%'),
                User.email.like(f'%{query}%')
            )
        )
    
    # 获取结果，限制最多返回20条
    students = students_query.limit(20).all()
    
    return jsonify({
        'status': 'success',
        'students': [student.to_dict() for student in students]
    })

@api_bp.route('/courses/<int:course_id>/enroll/<int:user_id>', methods=['DELETE'])
def drop_student(course_id, user_id):
    """学生退选课程"""
    course = Course.query.get_or_404(course_id)
    user = User.query.get_or_404(user_id)
    
    if user not in course.students:
        return jsonify({
            'status': 'error',
            'message': '学生未选修该课程'
        }), 400
    
    course.students.remove(user)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '学生成功退选课程'
    })

@api_bp.route('/users/<int:user_id>/courses', methods=['GET'])
def get_user_courses(user_id):
    """获取用户选修的所有课程"""
    user = User.query.get_or_404(user_id)
    
    # 根据用户角色返回不同类型的课程
    if user.role == 'teacher':
        courses = Course.query.filter_by(instructor_id=user_id).all()
        course_list = [course.to_dict() for course in courses]
    else:
        courses = user.enrolled_courses
        course_list = []
        for course in courses:
            course_dict = course.to_dict()
            # 查询该用户在该课程的进度
            progress = CourseProgress.query.filter_by(user_id=user_id, course_id=course.id).first()
            if progress:
                course_dict['progress'] = progress.progress_percent
            else:
                course_dict['progress'] = 0
            course_list.append(course_dict)
    
    return jsonify({
        'status': 'success',
        'courses': course_list
    }) 