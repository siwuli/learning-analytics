from flask import jsonify, request
from . import api_bp
from ..models import Course, User, Discussion, DiscussionReply
from .. import db
from datetime import datetime

@api_bp.route('/courses/<int:course_id>/discussions', methods=['GET'])
def get_course_discussions(course_id):
    """获取课程的所有讨论话题"""
    course = Course.query.get_or_404(course_id)
    
    # 获取讨论列表，置顶的排在前面，然后按创建时间倒序排列
    discussions = Discussion.query.filter_by(course_id=course_id) \
        .order_by(Discussion.is_pinned.desc(), Discussion.created_at.desc()).all()
    
    return jsonify({
        'status': 'success',
        'discussions': [discussion.to_dict() for discussion in discussions]
    })

@api_bp.route('/courses/<int:course_id>/discussions/<int:discussion_id>', methods=['GET'])
def get_course_discussion(course_id, discussion_id):
    """获取课程的特定讨论话题及其回复"""
    discussion = Discussion.query.filter_by(id=discussion_id, course_id=course_id).first_or_404()
    
    return jsonify({
        'status': 'success',
        'discussion': discussion.to_dict_with_replies()
    })

@api_bp.route('/courses/<int:course_id>/discussions', methods=['POST'])
def create_course_discussion(course_id):
    """创建课程讨论话题"""
    course = Course.query.get_or_404(course_id)
    data = request.json
    
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({
            'status': 'error',
            'message': '用户ID不能为空'
        }), 400
    
    # 检查用户是否存在
    user = User.query.get_or_404(user_id)
    
    new_discussion = Discussion(
        course_id=course_id,
        user_id=user_id,
        title=data.get('title'),
        content=data.get('content'),
        is_pinned=data.get('is_pinned', False)
    )
    
    db.session.add(new_discussion)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '讨论创建成功',
        'discussion': new_discussion.to_dict()
    }), 201

@api_bp.route('/courses/<int:course_id>/discussions/<int:discussion_id>', methods=['PUT'])
def update_course_discussion(course_id, discussion_id):
    """更新课程讨论话题"""
    discussion = Discussion.query.filter_by(id=discussion_id, course_id=course_id).first_or_404()
    data = request.json
    
    # 只有话题创建者或教师可以更新话题
    if 'user_id' in data and int(data['user_id']) != discussion.user_id:
        user = User.query.get_or_404(data['user_id'])
        if user.role != 'teacher':
            return jsonify({
                'status': 'error',
                'message': '没有权限更新此讨论话题'
            }), 403
    
    if 'title' in data:
        discussion.title = data['title']
    if 'content' in data:
        discussion.content = data['content']
    if 'is_pinned' in data:
        discussion.is_pinned = data['is_pinned']
    
    discussion.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '讨论更新成功',
        'discussion': discussion.to_dict()
    })

@api_bp.route('/courses/<int:course_id>/discussions/<int:discussion_id>', methods=['DELETE'])
def delete_course_discussion(course_id, discussion_id):
    """删除课程讨论话题"""
    discussion = Discussion.query.filter_by(id=discussion_id, course_id=course_id).first_or_404()
    
    # 删除讨论及其所有回复
    db.session.delete(discussion)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '讨论删除成功'
    })

@api_bp.route('/courses/<int:course_id>/discussions/<int:discussion_id>/replies', methods=['POST'])
def create_discussion_reply(course_id, discussion_id):
    """创建讨论回复"""
    discussion = Discussion.query.filter_by(id=discussion_id, course_id=course_id).first_or_404()
    data = request.json
    
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({
            'status': 'error',
            'message': '用户ID不能为空'
        }), 400
    
    # 检查用户是否存在
    user = User.query.get_or_404(user_id)
    
    new_reply = DiscussionReply(
        discussion_id=discussion_id,
        user_id=user_id,
        content=data.get('content')
    )
    
    db.session.add(new_reply)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '回复成功',
        'reply': new_reply.to_dict()
    }), 201

@api_bp.route('/discussions/replies/<int:reply_id>', methods=['PUT'])
def update_discussion_reply(reply_id):
    """更新讨论回复"""
    reply = DiscussionReply.query.get_or_404(reply_id)
    data = request.json
    
    # 只有回复创建者或教师可以更新回复
    if 'user_id' in data and int(data['user_id']) != reply.user_id:
        user = User.query.get_or_404(data['user_id'])
        if user.role != 'teacher':
            return jsonify({
                'status': 'error',
                'message': '没有权限更新此回复'
            }), 403
    
    if 'content' in data:
        reply.content = data['content']
    
    reply.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '回复更新成功',
        'reply': reply.to_dict()
    })

@api_bp.route('/discussions/replies/<int:reply_id>', methods=['DELETE'])
def delete_discussion_reply(reply_id):
    """删除讨论回复"""
    reply = DiscussionReply.query.get_or_404(reply_id)
    
    # 可以添加权限检查
    
    db.session.delete(reply)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '回复删除成功'
    }) 