from flask import jsonify, request
from . import api_bp
from ..models import CourseProgress, ResourceProgress, User, Course, CourseResource, CourseSection
from .. import db

@api_bp.route('/users/<int:user_id>/courses/<int:course_id>/progress', methods=['GET'])
def get_user_course_progress(user_id, course_id):
    """获取用户在课程中的进度"""
    user = User.query.get_or_404(user_id)
    course = Course.query.get_or_404(course_id)
    
    progress = CourseProgress.query.filter_by(user_id=user_id, course_id=course_id).first()
    
    if not progress:
        return jsonify({
            'status': 'error',
            'message': '找不到进度记录'
        }), 404
    
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
    """更新课程总进度"""
    # 获取课程下所有资源
    course = Course.query.get(course_id)
    sections = CourseSection.query.filter_by(course_id=course_id).all()
    
    total_resources = 0
    completed_resources = 0
    
    for section in sections:
        resources = CourseResource.query.filter_by(section_id=section.id).all()
        total_resources += len(resources)
        
        for resource in resources:
            progress = ResourceProgress.query.filter_by(
                user_id=user_id, 
                resource_id=resource.id
            ).first()
            
            if progress and progress.completed:
                completed_resources += 1
    
    # 计算完成百分比
    if total_resources > 0:
        progress_percent = (completed_resources / total_resources) * 100
    else:
        progress_percent = 0
    
    # 更新课程进度
    course_progress = CourseProgress.query.filter_by(user_id=user_id, course_id=course_id).first()
    
    if not course_progress:
        course_progress = CourseProgress(
            user_id=user_id,
            course_id=course_id,
            progress_percent=progress_percent
        )
        db.session.add(course_progress)
    else:
        course_progress.progress_percent = progress_percent
    
    db.session.commit()
    
    return course_progress 