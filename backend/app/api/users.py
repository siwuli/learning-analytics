from flask import jsonify, request
from . import api_bp
from ..models import User
from .. import db

@api_bp.route('/users', methods=['GET'])
def get_users():
    """获取所有用户"""
    users = User.query.all()
    return jsonify({
        'status': 'success',
        'users': [user.to_dict() for user in users]
    })

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取单个用户"""
    user = User.query.get_or_404(user_id)
    return jsonify({
        'status': 'success',
        'user': user.to_dict()
    })

@api_bp.route('/users', methods=['POST'])
def create_user():
    """创建用户"""
    # 这里应该有更详细的数据验证和密码哈希处理
    data = request.json
    new_user = User(
        username=data.get('username'),
        email=data.get('email'),
        password_hash='暂时明文密码',  # 实际应用中需要哈希处理
        role=data.get('role', 'student')
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        'status': 'success',
        'message': '用户创建成功',
        'user': new_user.to_dict()
    }), 201

@api_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户"""
    user = User.query.get_or_404(user_id)
    data = request.json
    
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'role' in data:
        user.role = data['role']
    
    db.session.commit()
    return jsonify({
        'status': 'success',
        'message': '用户更新成功',
        'user': user.to_dict()
    })

@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({
        'status': 'success',
        'message': '用户删除成功'
    }) 