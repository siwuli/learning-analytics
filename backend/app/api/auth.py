from flask import jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
import os
from . import api_bp
from .. import db
from ..models import User

# 获取密钥，实际应用中应从环境变量或配置文件中获取
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key')

@api_bp.route('/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.json
    
    # 验证必填字段
    if not all(k in data for k in ('account', 'username', 'email', 'password', 'role')):
        return jsonify({
            'status': 'error',
            'message': '缺少必要的注册信息'
        }), 400
    
    # 验证角色
    if data['role'] not in ('student', 'teacher'):
        return jsonify({
            'status': 'error',
            'message': '无效的用户角色'
        }), 400
    
    # 检查账号是否已存在
    if User.query.filter_by(account=data['account']).first():
        return jsonify({
            'status': 'error',
            'message': '账号已被占用'
        }), 400
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'status': 'error',
            'message': '邮箱已被注册'
        }), 400
    
    # 创建新用户
    new_user = User(
        account=data['account'],
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        role=data['role']
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '注册成功',
        'user': new_user.to_dict()
    }), 201

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json
    
    # 验证必填字段
    if not all(k in data for k in ('account', 'password')):
        return jsonify({
            'status': 'error',
            'message': '账号和密码不能为空'
        }), 400
    
    # 查找用户
    user = User.query.filter_by(account=data['account']).first()
    
    # 验证用户存在性和密码
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({
            'status': 'error',
            'message': '账号或密码错误'
        }), 401
    
    # 生成Token
    token_payload = {
        'user_id': user.id,
        'account': user.account,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    
    token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        'status': 'success',
        'message': '登录成功',
        'token': token,
        'user': user.to_dict()
    })

@api_bp.route('/auth/user', methods=['GET'])
def get_current_user():
    """获取当前登录用户信息"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({
            'status': 'error',
            'message': '未提供有效的认证令牌'
        }), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.query.get(payload['user_id'])
        
        if not user:
            raise Exception('用户不存在')
        
        return jsonify({
            'status': 'success',
            'user': user.to_dict()
        })
    except jwt.ExpiredSignatureError:
        return jsonify({
            'status': 'error',
            'message': '认证令牌已过期'
        }), 401
    except (jwt.InvalidTokenError, Exception) as e:
        return jsonify({
            'status': 'error',
            'message': f'无效的认证令牌: {str(e)}'
        }), 401

@api_bp.route('/auth/logout', methods=['POST'])
def logout():
    """用户登出"""
    # 由于使用JWT，服务器端不需要任何操作，客户端只需删除令牌
    return jsonify({
        'status': 'success',
        'message': '成功登出'
    }) 