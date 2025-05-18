from flask import jsonify, request
from . import api_bp
from ..models import Activity, User, Course
from .. import db

@api_bp.route('/activities', methods=['GET'])
def get_activities():
    """获取所有活动记录"""
    # 可以添加过滤参数
    user_id = request.args.get('user_id', type=int)
    course_id = request.args.get('course_id', type=int)
    activity_type = request.args.get('type')
    
    query = Activity.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if course_id:
        query = query.filter_by(course_id=course_id)
    if activity_type:
        query = query.filter_by(activity_type=activity_type)
    
    activities = query.all()
    
    return jsonify({
        'status': 'success',
        'activities': [activity.to_dict() for activity in activities]
    })

@api_bp.route('/activities/<int:activity_id>', methods=['GET'])
def get_activity(activity_id):
    """获取单个活动记录"""
    activity = Activity.query.get_or_404(activity_id)
    
    return jsonify({
        'status': 'success',
        'activity': activity.to_dict()
    })

@api_bp.route('/activities', methods=['POST'])
def create_activity():
    """创建学习活动记录"""
    data = request.json
    
    # 验证用户和课程是否存在
    user_id = data.get('user_id')
    course_id = data.get('course_id')
    
    user = User.query.get(user_id)
    course = Course.query.get(course_id)
    
    if not user or not course:
        return jsonify({
            'status': 'error',
            'message': '用户或课程不存在'
        }), 400
    
    # 验证该用户是否已加入该课程
    if user not in course.students and user.id != course.instructor_id:
        return jsonify({
            'status': 'error',
            'message': '用户未加入该课程'
        }), 400
    
    new_activity = Activity(
        user_id=user_id,
        course_id=course_id,
        activity_type=data.get('activity_type'),
        resource_id=data.get('resource_id'),
        duration=data.get('duration'),
        score=data.get('score'),
        completed=data.get('completed', False),
        data_json=data.get('metadata', {})
    )
    
    db.session.add(new_activity)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '活动记录创建成功',
        'activity': new_activity.to_dict()
    }), 201

@api_bp.route('/activities/<int:activity_id>', methods=['PUT'])
def update_activity(activity_id):
    """更新活动记录"""
    activity = Activity.query.get_or_404(activity_id)
    data = request.json
    
    if 'duration' in data:
        activity.duration = data['duration']
    if 'score' in data:
        activity.score = data['score']
    if 'completed' in data:
        activity.completed = data['completed']
    if 'metadata' in data:
        # 合并现有元数据和新元数据
        current_metadata = activity.data_json or {}
        current_metadata.update(data['metadata'])
        activity.data_json = current_metadata
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '活动记录更新成功',
        'activity': activity.to_dict()
    })

@api_bp.route('/activities/<int:activity_id>', methods=['DELETE'])
def delete_activity(activity_id):
    """删除活动记录"""
    activity = Activity.query.get_or_404(activity_id)
    db.session.delete(activity)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '活动记录删除成功'
    })

@api_bp.route('/users/<int:user_id>/activities', methods=['GET'])
def get_user_activities(user_id):
    """获取用户的所有活动记录"""
    user = User.query.get_or_404(user_id)
    activities = Activity.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'status': 'success',
        'activities': [activity.to_dict() for activity in activities]
    })

@api_bp.route('/courses/<int:course_id>/activities', methods=['GET'])
def get_course_activities(course_id):
    """获取课程的所有活动记录"""
    course = Course.query.get_or_404(course_id)
    activities = Activity.query.filter_by(course_id=course_id).all()
    
    return jsonify({
        'status': 'success',
        'activities': [activity.to_dict() for activity in activities]
    }) 