from flask import jsonify, request
from . import api_bp
from ..models import GradeSetting, StudentGrade, Course, User
from .. import db

@api_bp.route('/courses/<int:course_id>/grade-settings', methods=['GET'])
def get_grade_settings(course_id):
    """获取课程成绩设置"""
    course = Course.query.get_or_404(course_id)
    
    # 获取课程的成绩设置
    settings = GradeSetting.query.filter_by(course_id=course_id).first()
    
    # 如果没有设置，返回默认设置
    if not settings:
        return jsonify({
            'status': 'success',
            'settings': {
                'course_id': course_id,
                'final_exam_weight': 60.0,
                'regular_grade_weight': 40.0
            }
        })
    
    return jsonify({
        'status': 'success',
        'settings': settings.to_dict()
    })

@api_bp.route('/courses/<int:course_id>/grade-settings', methods=['POST', 'PUT'])
def update_grade_settings(course_id):
    """更新课程成绩设置"""
    course = Course.query.get_or_404(course_id)
    data = request.json
    
    # 检查权限 - 只有课程教师可以更新成绩设置
    # 在实际系统中应添加权限验证
    
    settings = GradeSetting.query.filter_by(course_id=course_id).first()
    
    if not settings:
        # 创建新设置
        settings = GradeSetting(
            course_id=course_id,
            final_exam_weight=data.get('final_exam_weight', 60.0),
            regular_grade_weight=data.get('regular_grade_weight', 40.0)
        )
        db.session.add(settings)
    else:
        # 更新现有设置
        if 'final_exam_weight' in data:
            settings.final_exam_weight = data['final_exam_weight']
        if 'regular_grade_weight' in data:
            settings.regular_grade_weight = data['regular_grade_weight']
    
    # 确保权重总和为100%
    total_weight = settings.final_exam_weight + settings.regular_grade_weight
    if abs(total_weight - 100.0) > 0.01:  # 允许0.01的误差
        return jsonify({
            'status': 'error',
            'message': '成绩权重总和必须为100%'
        }), 400
    
    db.session.commit()
    
    # 更新所有学生的总评成绩
    update_all_total_scores(course_id)
    
    return jsonify({
        'status': 'success',
        'message': '成绩设置已更新',
        'settings': settings.to_dict()
    })

@api_bp.route('/courses/<int:course_id>/students/<int:student_id>/grades', methods=['GET'])
def get_student_grade(course_id, student_id):
    """获取学生在指定课程中的成绩"""
    course = Course.query.get_or_404(course_id)
    student = User.query.get_or_404(student_id)
    
    grade = StudentGrade.query.filter_by(course_id=course_id, user_id=student_id).first()
    
    if not grade:
        return jsonify({
            'status': 'success',
            'grade': {
                'course_id': course_id,
                'user_id': student_id,
                'final_exam_score': None,
                'regular_grade': None,
                'total_score': None,
                'comment': None
            }
        })
    
    return jsonify({
        'status': 'success',
        'grade': grade.to_dict()
    })

@api_bp.route('/courses/<int:course_id>/students/<int:student_id>/grades', methods=['POST', 'PUT'])
def update_student_grade(course_id, student_id):
    """更新学生成绩"""
    course = Course.query.get_or_404(course_id)
    student = User.query.get_or_404(student_id)
    data = request.json
    
    # 检查权限 - 只有课程教师可以更新成绩
    # 在实际系统中应添加权限验证
    
    grade = StudentGrade.query.filter_by(course_id=course_id, user_id=student_id).first()
    
    # 获取课程成绩设置
    settings = GradeSetting.query.filter_by(course_id=course_id).first()
    if not settings:
        # 如果未设置，创建默认设置
        settings = GradeSetting(course_id=course_id)
        db.session.add(settings)
        db.session.commit()
    
    if not grade:
        # 创建新成绩记录
        grade = StudentGrade(
            course_id=course_id,
            user_id=student_id,
            final_exam_score=data.get('final_exam_score'),
            regular_grade=data.get('regular_grade'),
            comment=data.get('comment')
        )
        db.session.add(grade)
    else:
        # 更新现有成绩记录
        if 'final_exam_score' in data:
            grade.final_exam_score = data['final_exam_score']
        if 'regular_grade' in data:
            grade.regular_grade = data['regular_grade']
        if 'comment' in data:
            grade.comment = data['comment']
    
    # 计算总评成绩
    if grade.final_exam_score is not None and grade.regular_grade is not None:
        grade.total_score = grade.calculate_total_score(settings)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '学生成绩已更新',
        'grade': grade.to_dict()
    })

@api_bp.route('/courses/<int:course_id>/grades', methods=['GET'])
def get_course_grades(course_id):
    """获取课程所有学生的成绩"""
    course = Course.query.get_or_404(course_id)
    
    # 查询所有已选课学生
    students = course.students.all()
    student_ids = [student.id for student in students]
    
    # 查询所有学生的成绩
    grades = StudentGrade.query.filter_by(course_id=course_id).all()
    
    # 创建学生ID到成绩的映射
    grades_map = {grade.user_id: grade for grade in grades}
    
    # 获取成绩设置
    settings = GradeSetting.query.filter_by(course_id=course_id).first()
    if not settings:
        settings = GradeSetting(course_id=course_id)
        db.session.add(settings)
        db.session.commit()
    
    # 准备结果数据
    results = []
    for student in students:
        # 如果学生有成绩记录，使用它
        if student.id in grades_map:
            grade = grades_map[student.id]
            grade_data = grade.to_dict()
        else:
            # 如果没有成绩记录，创建空记录
            grade_data = {
                'course_id': course_id,
                'user_id': student.id,
                'final_exam_score': None,
                'regular_grade': None,
                'total_score': None,
                'comment': None
            }
        
        # 添加学生信息
        grade_data['student'] = {
            'id': student.id,
            'username': student.username,
            'email': student.email
        }
        
        results.append(grade_data)
    
    return jsonify({
        'status': 'success',
        'grades': results,
        'settings': settings.to_dict()
    })

@api_bp.route('/courses/<int:course_id>/grades/batch', methods=['POST'])
def batch_update_grades(course_id):
    """批量更新学生成绩"""
    course = Course.query.get_or_404(course_id)
    data = request.json
    
    grades_data = data.get('grades', [])
    if not grades_data:
        return jsonify({
            'status': 'error',
            'message': '未提供成绩数据'
        }), 400
    
    # 获取课程成绩设置
    settings = GradeSetting.query.filter_by(course_id=course_id).first()
    if not settings:
        settings = GradeSetting(course_id=course_id)
        db.session.add(settings)
    
    # 统计结果
    success_count = 0
    failed_ids = []
    
    for grade_data in grades_data:
        try:
            student_id = grade_data.get('user_id')
            if not student_id:
                continue
                
            # 检查学生是否存在
            student = User.query.get(student_id)
            if not student:
                failed_ids.append(student_id)
                continue
            
            grade = StudentGrade.query.filter_by(course_id=course_id, user_id=student_id).first()
            
            if not grade:
                # 创建新成绩记录
                grade = StudentGrade(
                    course_id=course_id,
                    user_id=student_id,
                    final_exam_score=grade_data.get('final_exam_score'),
                    regular_grade=grade_data.get('regular_grade'),
                    comment=grade_data.get('comment')
                )
                db.session.add(grade)
            else:
                # 更新现有成绩记录
                if 'final_exam_score' in grade_data:
                    grade.final_exam_score = grade_data['final_exam_score']
                if 'regular_grade' in grade_data:
                    grade.regular_grade = grade_data['regular_grade']
                if 'comment' in grade_data:
                    grade.comment = grade_data['comment']
            
            # 计算总评成绩
            if grade.final_exam_score is not None and grade.regular_grade is not None:
                grade.total_score = grade.calculate_total_score(settings)
            
            success_count += 1
            
        except Exception as e:
            if student_id:
                failed_ids.append(student_id)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'批量更新完成: {success_count}个学生成绩更新成功, {len(failed_ids)}个更新失败',
        'success_count': success_count,
        'failed_ids': failed_ids
    })

@api_bp.route('/users/<int:user_id>/grades', methods=['GET'])
def get_user_grades(user_id):
    """获取用户在所有课程中的成绩"""
    user = User.query.get_or_404(user_id)
    
    # 查询用户的所有成绩
    grades = StudentGrade.query.filter_by(user_id=user_id).all()
    
    # 获取用户选修的所有课程
    courses = user.enrolled_courses.all()
    course_ids = [course.id for course in courses]
    
    # 创建课程ID到成绩的映射
    grades_map = {grade.course_id: grade for grade in grades}
    
    # 准备结果数据
    results = []
    for course in courses:
        # 如果课程有成绩记录，使用它
        if course.id in grades_map:
            grade = grades_map[course.id]
            grade_data = grade.to_dict()
        else:
            # 如果没有成绩记录，创建空记录
            grade_data = {
                'course_id': course.id,
                'user_id': user_id,
                'final_exam_score': None,
                'regular_grade': None,
                'total_score': None,
                'comment': None
            }
        
        # 添加课程信息
        grade_data['course'] = {
            'id': course.id,
            'title': course.title,
            'instructor_id': course.instructor_id,
            'instructor_name': course.instructor.username if course.instructor else None
        }
        
        # 获取课程成绩设置
        settings = GradeSetting.query.filter_by(course_id=course.id).first()
        if settings:
            grade_data['settings'] = settings.to_dict()
        else:
            grade_data['settings'] = {
                'final_exam_weight': 60.0,
                'regular_grade_weight': 40.0
            }
        
        results.append(grade_data)
    
    return jsonify({
        'status': 'success',
        'grades': results
    })

def update_all_total_scores(course_id):
    """更新课程中所有学生的总评成绩"""
    # 获取课程成绩设置
    settings = GradeSetting.query.filter_by(course_id=course_id).first()
    if not settings:
        return
    
    # 获取所有学生的成绩记录
    grades = StudentGrade.query.filter_by(course_id=course_id).all()
    
    for grade in grades:
        if grade.final_exam_score is not None and grade.regular_grade is not None:
            grade.total_score = grade.calculate_total_score(settings)
    
    db.session.commit() 