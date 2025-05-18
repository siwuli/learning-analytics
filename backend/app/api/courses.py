from flask import jsonify, request
from backend.app.api import api_bp
from backend.app.models import Course, User
from backend.app import db
from datetime import datetime

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

@api_bp.route('/courses/<int:course_id>/students', methods=['GET'])
def get_course_students(course_id):
    """获取课程的所有学生"""
    course = Course.query.get_or_404(course_id)
    
    return jsonify({
        'status': 'success',
        'students': [student.to_dict() for student in course.students]
    }) 