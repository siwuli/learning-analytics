from flask import jsonify, request
from . import api_bp
from ..models import CourseProgress, ResourceProgress, User, Course, CourseResource, CourseSection
from .. import db
from ..models.assignment import Assignment, AssignmentSubmission

@api_bp.route('/users/<int:user_id>/courses/<int:course_id>/progress', methods=['GET'])
def get_user_course_progress(user_id, course_id):
    """获取用户在课程中的进度"""
    user = User.query.get_or_404(user_id)
    course = Course.query.get_or_404(course_id)
    
    progress = CourseProgress.query.filter_by(user_id=user_id, course_id=course_id).first()
    
    if not progress:
        # 当找不到进度记录时，不返回404，而是返回默认进度为0
        # 自动计算并创建进度记录
        progress = update_course_progress(user_id, course_id)
    
    return jsonify({
        'status': 'success',
        'progress': progress.to_dict()
    })

@api_bp.route('/users/<int:user_id>/courses/<int:course_id>/progress', methods=['POST', 'PUT'])
def update_user_course_progress(user_id, course_id):
    """更新用户在课程中的进度"""
    user = User.query.get_or_404(user_id)
    course = Course.query.get_or_404(course_id)
    data = request.json
    
    progress = CourseProgress.query.filter_by(user_id=user_id, course_id=course_id).first()
    
    if not progress:
        # 如果不存在，创建新记录
        progress = CourseProgress(
            user_id=user_id,
            course_id=course_id,
            progress_percent=data.get('progress_percent', 0)
        )
        db.session.add(progress)
    else:
        # 如果存在，更新记录
        if 'progress_percent' in data:
            progress.progress_percent = data['progress_percent']
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '进度已更新',
        'progress': progress.to_dict()
    })

@api_bp.route('/users/<int:user_id>/resources/<int:resource_id>/progress', methods=['GET'])
def get_user_resource_progress(user_id, resource_id):
    """获取用户对特定资源的进度"""
    user = User.query.get_or_404(user_id)
    resource = CourseResource.query.get_or_404(resource_id)
    
    progress = ResourceProgress.query.filter_by(user_id=user_id, resource_id=resource_id).first()
    
    if not progress:
        return jsonify({
            'status': 'error',
            'message': '找不到进度记录'
        }), 404
    
    return jsonify({
        'status': 'success',
        'progress': progress.to_dict()
    })

@api_bp.route('/users/<int:user_id>/resources/<int:resource_id>/progress', methods=['POST', 'PUT'])
def update_user_resource_progress(user_id, resource_id):
    """更新用户对特定资源的进度"""
    user = User.query.get_or_404(user_id)
    resource = CourseResource.query.get_or_404(resource_id)
    data = request.json
    
    progress = ResourceProgress.query.filter_by(user_id=user_id, resource_id=resource_id).first()
    
    if not progress:
        # 如果不存在，创建新记录
        progress = ResourceProgress(
            user_id=user_id,
            resource_id=resource_id,
            progress_percent=data.get('progress_percent', 0),
            completed=data.get('completed', False),
            last_position=data.get('last_position'),
            data_json=data.get('metadata', {})
        )
        db.session.add(progress)
    else:
        # 如果存在，更新记录
        if 'progress_percent' in data:
            progress.progress_percent = data['progress_percent']
        if 'completed' in data:
            progress.completed = data['completed']
        if 'last_position' in data:
            progress.last_position = data['last_position']
        if 'metadata' in data:
            # 合并现有元数据和新元数据
            current_metadata = progress.data_json or {}
            current_metadata.update(data['metadata'])
            progress.data_json = current_metadata
    
    db.session.commit()
    
    # 如果资源被标记为完成，更新课程总进度
    if progress.completed:
        update_course_progress(user_id, resource.section.course_id)
    
    return jsonify({
        'status': 'success',
        'message': '进度已更新',
        'progress': progress.to_dict()
    })

def update_course_progress(user_id, course_id):
    """更新课程总进度
    计算规则:
    - 资源完成权重: 70%
    - 作业完成权重: 30%
    - 如果课程没有资源或作业，则相应权重转移至另一部分
    """
    print(f"计算用户{user_id}在课程{course_id}的总进度...")
    
    # 获取课程下所有资源
    course = Course.query.get(course_id)
    sections = CourseSection.query.filter_by(course_id=course_id).all()
    
    # 资源部分计算
    total_resources = 0
    completed_resources = 0
    
    for section in sections:
        resources = CourseResource.query.filter_by(section_id=section.id).all()
        section_resources_count = len(resources)
        total_resources += section_resources_count
        
        print(f"章节 {section.id} ({section.title}) 有 {section_resources_count} 个资源")
        
        for resource in resources:
            progress = ResourceProgress.query.filter_by(
                user_id=user_id, 
                resource_id=resource.id
            ).first()
            
            if progress and progress.completed:
                completed_resources += 1
                print(f"资源 {resource.id} ({resource.title}) 已完成")
            else:
                print(f"资源 {resource.id} ({resource.title}) 未完成")
    
    print(f"资源完成情况: {completed_resources}/{total_resources}")
    
    # 作业部分计算
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    total_assignments = len(assignments)
    completed_assignments = 0
    
    if total_assignments > 0:
        print(f"课程有 {total_assignments} 个作业")
        
        for assignment in assignments:
            # 检查用户是否提交了该作业
            submission = AssignmentSubmission.query.filter_by(
                assignment_id=assignment.id,
                user_id=user_id
            ).first()
            
            if submission:
                completed_assignments += 1
                print(f"作业 {assignment.id} ({assignment.title}) 已提交")
            else:
                print(f"作业 {assignment.id} ({assignment.title}) 未提交")
    
    print(f"作业完成情况: {completed_assignments}/{total_assignments}")
    
    # 计算总体完成百分比 (资源占70%，作业占30%)
    # 如果没有资源或作业，则相应权重转移至另一部分
    progress_percent = 0
    
    if total_resources > 0 and total_assignments > 0:
        # 既有资源又有作业
        resource_percent = (completed_resources / total_resources) * 100 if total_resources > 0 else 0
        assignment_percent = (completed_assignments / total_assignments) * 100 if total_assignments > 0 else 0
        
        # 资源占70%，作业占30%
        progress_percent = (resource_percent * 0.7) + (assignment_percent * 0.3)
        
        print(f"资源进度: {resource_percent}% (权重70%), 作业进度: {assignment_percent}% (权重30%)")
    elif total_resources > 0:
        # 只有资源，没有作业
        progress_percent = (completed_resources / total_resources) * 100
        print(f"只有资源进度: {progress_percent}% (权重100%)")
    elif total_assignments > 0:
        # 只有作业，没有资源
        progress_percent = (completed_assignments / total_assignments) * 100
        print(f"只有作业进度: {progress_percent}% (权重100%)")
    else:
        # 既没有资源也没有作业
        progress_percent = 0
        print("课程没有资源和作业，进度为0%")
    
    # 确保进度值在0-100范围内
    progress_percent = max(0, min(100, progress_percent))
    
    print(f"最终计算的课程总进度: {progress_percent}%")
    
    # 更新课程进度
    course_progress = CourseProgress.query.filter_by(user_id=user_id, course_id=course_id).first()
    
    if not course_progress:
        print(f"为用户{user_id}创建新的课程进度记录")
        course_progress = CourseProgress(
            user_id=user_id,
            course_id=course_id,
            progress_percent=progress_percent
        )
        db.session.add(course_progress)
    else:
        print(f"更新用户{user_id}的现有课程进度记录")
        course_progress.progress_percent = progress_percent
    
    db.session.commit()
    print(f"课程进度已保存到数据库，值为: {course_progress.progress_percent}%")
    
    return course_progress 