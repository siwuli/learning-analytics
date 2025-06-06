from flask import jsonify, request
from . import api_bp
from ..models import Course, User, Assignment, AssignmentSubmission
from .. import db
from datetime import datetime

@api_bp.route('/courses/<int:course_id>/assignments', methods=['GET'])
def get_course_assignments(course_id):
    """获取课程的所有作业"""
    course = Course.query.get_or_404(course_id)
    
    # 获取查询参数中的user_id
    user_id = request.args.get('user_id', type=int)
    
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    
    # 根据是否传入user_id来决定使用哪种序列化方法
    if user_id:
        # 使用针对特定用户的序列化
        assignment_dicts = [assignment.to_dict_for_user(user_id) for assignment in assignments]
    else:
        # 使用通用序列化
        assignment_dicts = [assignment.to_dict() for assignment in assignments]
    
    return jsonify({
        'status': 'success',
        'assignments': assignment_dicts
    })

@api_bp.route('/courses/<int:course_id>/assignments/<int:assignment_id>', methods=['GET'])
def get_course_assignment(course_id, assignment_id):
    """获取课程的特定作业"""
    assignment = Assignment.query.filter_by(id=assignment_id, course_id=course_id).first_or_404()
    
    # 获取查询参数中的user_id
    user_id = request.args.get('user_id', type=int)
    
    # 根据是否传入user_id来决定使用哪种序列化方法
    if user_id:
        # 使用针对特定用户的序列化
        assignment_dict = assignment.to_dict_for_user(user_id)
    else:
        # 使用通用序列化
        assignment_dict = assignment.to_dict()
    
    return jsonify({
        'status': 'success',
        'assignment': assignment_dict
    })

@api_bp.route('/courses/<int:course_id>/assignments', methods=['POST'])
def create_course_assignment(course_id):
    """创建课程作业"""
    course = Course.query.get_or_404(course_id)
    data = request.json
    
    # 处理日期时间格式
    deadline = None
    if data.get('deadline'):
        try:
            deadline = datetime.fromisoformat(data.get('deadline'))
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': '无效的截止日期格式'
            }), 400
    
    # 处理附件列表
    attachments = data.get('attachments', [])
    
    new_assignment = Assignment(
        course_id=course_id,
        title=data.get('title'),
        description=data.get('description'),
        deadline=deadline,
        points=data.get('points', 10),
        attachments=attachments  # 保存附件列表
    )
    
    db.session.add(new_assignment)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '作业创建成功',
        'assignment': new_assignment.to_dict()
    }), 201

@api_bp.route('/courses/<int:course_id>/assignments/<int:assignment_id>', methods=['PUT'])
def update_course_assignment(course_id, assignment_id):
    """更新课程作业"""
    assignment = Assignment.query.filter_by(id=assignment_id, course_id=course_id).first_or_404()
    data = request.json
    
    if 'title' in data:
        assignment.title = data['title']
    if 'description' in data:
        assignment.description = data['description']
    if 'deadline' in data and data['deadline']:
        try:
            assignment.deadline = datetime.fromisoformat(data['deadline'])
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': '无效的截止日期格式'
            }), 400
    if 'points' in data:
        assignment.points = data['points']
    if 'attachments' in data:
        assignment.attachments = data['attachments']
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '作业更新成功',
        'assignment': assignment.to_dict()
    })

@api_bp.route('/courses/<int:course_id>/assignments/<int:assignment_id>', methods=['DELETE'])
def delete_course_assignment(course_id, assignment_id):
    """删除课程作业"""
    assignment = Assignment.query.filter_by(id=assignment_id, course_id=course_id).first_or_404()
    
    # 同时删除所有相关的提交
    AssignmentSubmission.query.filter_by(assignment_id=assignment_id).delete()
    
    db.session.delete(assignment)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '作业删除成功'
    })

@api_bp.route('/courses/<int:course_id>/assignments/<int:assignment_id>/submissions', methods=['GET'])
def get_assignment_submissions(course_id, assignment_id):
    """获取作业的所有提交"""
    assignment = Assignment.query.filter_by(id=assignment_id, course_id=course_id).first_or_404()
    
    # 获取所有提交
    submissions = AssignmentSubmission.query.filter_by(assignment_id=assignment_id).all()
    
    # 获取课程学生总数
    total_students = assignment.course.students.count()
    
    return jsonify({
        'status': 'success',
        'submissions': [submission.to_dict() for submission in submissions],
        'total_students': total_students
    })

@api_bp.route('/courses/<int:course_id>/assignments/<int:assignment_id>/submissions/<int:user_id>', methods=['GET'])
def get_user_assignment_submission(course_id, assignment_id, user_id):
    """获取特定用户的作业提交"""
    assignment = Assignment.query.filter_by(id=assignment_id, course_id=course_id).first_or_404()
    
    # 检查用户是否存在
    user = User.query.get_or_404(user_id)
    
    # 获取用户提交
    submission = AssignmentSubmission.query.filter_by(
        assignment_id=assignment_id,
        user_id=user_id
    ).first()
    
    if submission:
        return jsonify({
            'status': 'success',
            'submission': submission.to_dict()
        })
    else:
        return jsonify({
            'status': 'success',
            'submission': None
        })

@api_bp.route('/courses/<int:course_id>/assignments/<int:assignment_id>/submissions', methods=['POST'])
def submit_assignment(course_id, assignment_id):
    """提交作业"""
    assignment = Assignment.query.filter_by(id=assignment_id, course_id=course_id).first_or_404()
    data = request.json
    
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({
            'status': 'error',
            'message': '用户ID不能为空'
        }), 400
    
    # 检查用户是否存在
    user = User.query.get_or_404(user_id)
    
    # 处理文件列表
    files = data.get('files', [])
    # 如果有文件列表，确保包含必要的信息
    processed_files = []
    if files:
        for file in files:
            if isinstance(file, dict) and 'name' in file:
                # 已经处理过的文件对象
                processed_files.append(file)
            elif hasattr(file, 'name'):
                # 文件对象需要转换为dict
                processed_files.append({
                    'name': file.get('name', 'unknown'),
                    'size': file.get('size', 0),
                    'type': file.get('type', ''),
                    'url': f'/api/static/uploads/{file.get("name", "unknown")}'
                })
    
    # 查看是否已经提交过
    existing_submission = AssignmentSubmission.query.filter_by(
        assignment_id=assignment_id,
        user_id=user_id
    ).first()
    
    if existing_submission:
        # 更新现有提交
        if 'content' in data:
            existing_submission.content = data['content']
        
        # 更新文件列表
        if processed_files:
            existing_submission.files = processed_files
            
        existing_submission.submit_time = datetime.utcnow()
        
        db.session.commit()
        
        # 更新课程进度
        from .progress import update_course_progress
        update_course_progress(user_id, course_id)
        
        return jsonify({
            'status': 'success',
            'message': '作业更新成功',
            'submission': existing_submission.to_dict()
        })
    else:
        # 创建新提交
        new_submission = AssignmentSubmission(
            assignment_id=assignment_id,
            user_id=user_id,
            content=data.get('content'),
            files=processed_files if processed_files else None,
            submit_time=datetime.utcnow()
        )
        
        db.session.add(new_submission)
        db.session.commit()
        
        # 更新课程进度
        from .progress import update_course_progress
        update_course_progress(user_id, course_id)
        
        return jsonify({
            'status': 'success',
            'message': '作业提交成功',
            'submission': new_submission.to_dict()
        })

@api_bp.route('/courses/<int:course_id>/assignments/<int:assignment_id>/submissions/<int:submission_id>/grade', methods=['POST'])
def grade_assignment(course_id, assignment_id, submission_id):
    """评分作业提交"""
    assignment = Assignment.query.filter_by(id=assignment_id, course_id=course_id).first_or_404()
    submission = AssignmentSubmission.query.get_or_404(submission_id)
    
    # 验证提交是否属于该作业
    if submission.assignment_id != assignment_id:
        return jsonify({
            'status': 'error',
            'message': '提交不属于该作业'
        }), 400
    
    data = request.json
    
    # 更新评分信息
    submission.grade = data.get('grade')
    submission.feedback = data.get('feedback')
    submission.graded_by = data.get('graded_by')
    submission.graded_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '评分成功',
        'submission': submission.to_dict()
    }) 