from flask import jsonify, request, current_app
from . import api_bp
from ..models import User
from .. import db
import os
from werkzeug.utils import secure_filename
import uuid

# 允许的图片格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        role=data.get('role', 'student'),
        bio=data.get('bio', '')
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
    """更新用户信息"""
    user = User.query.get_or_404(user_id)
    data = request.json
    
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'role' in data:
        user.role = data['role']
    if 'bio' in data:
        user.bio = data['bio']
    
    db.session.commit()
    return jsonify({
        'status': 'success',
        'message': '用户更新成功',
        'user': user.to_dict()
    })

@api_bp.route('/users/<int:user_id>/avatar', methods=['POST'])
def upload_avatar(user_id):
    """上传用户头像"""
    user = User.query.get_or_404(user_id)
    
    # 检查是否有文件上传
    if 'avatar' not in request.files:
        return jsonify({
            'status': 'error',
            'message': '没有上传文件'
        }), 400
    
    file = request.files['avatar']
    
    # 如果用户未选择文件，浏览器也会提交一个没有文件名的空文件
    if file.filename == '':
        return jsonify({
            'status': 'error',
            'message': '未选择文件'
        }), 400
    
    if file and allowed_file(file.filename):
        # 创建唯一文件名
        filename = secure_filename(file.filename)
        filename = f"{uuid.uuid4()}_{filename}"
        
        # 确保上传目录存在
        upload_folder = os.path.join(current_app.static_folder, 'uploads', 'avatars')
        os.makedirs(upload_folder, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # 更新用户头像路径
        avatar_url = f"/static/uploads/avatars/{filename}"
        user.avatar = avatar_url
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '头像上传成功',
            'avatar_url': avatar_url,
            'user': user.to_dict()
        })
    
    return jsonify({
        'status': 'error',
        'message': '不支持的文件类型'
    }), 400

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