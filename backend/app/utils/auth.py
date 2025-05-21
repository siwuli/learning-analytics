from functools import wraps
from flask import request, jsonify
from ..models import User
import jwt
import os

# 获取密钥，保持与auth.py中相同
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key')

def authenticate(f):
    """身份验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        print(f"认证开始: {request.path}")
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            print(f"认证失败: 未提供有效令牌 - {request.path}")
            return jsonify({
                'status': 'error',
                'message': '未提供有效的认证令牌'
            }), 401
        
        token = auth_header.split(' ')[1]
        print(f"获取令牌: {token[:10]}... - {request.path}")
        
        try:
            # 使用JWT解码令牌
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            role = payload.get('role', 'unknown')
            print(f"令牌解码成功: 用户ID={user_id}, 角色={role} - {request.path}")
            
            # 检查用户是否存在
            user = User.query.get(user_id)
            if not user:
                print(f"认证失败: 用户不存在(ID={user_id}) - {request.path}")
                return jsonify({
                    'status': 'error',
                    'message': '认证失败：用户不存在'
                }), 401
            
            print(f"认证成功: 用户={user.username}, 角色={user.role} - {request.path}")
            # 将用户信息添加到请求上下文
            request.current_user = user
            
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            print(f"认证失败: 令牌已过期 - {request.path}")
            return jsonify({
                'status': 'error',
                'message': '认证令牌已过期'
            }), 401
        except (jwt.InvalidTokenError, Exception) as e:
            print(f"认证失败: 令牌无效 - {str(e)} - {request.path}")
            return jsonify({
                'status': 'error',
                'message': f'无效的认证令牌: {str(e)}'
            }), 401
    return decorated

def require_role(role):
    """角色要求装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 确保用户已认证
            if not hasattr(request, 'current_user'):
                print(f"权限检查失败: 用户未认证 - {request.path}")
                return jsonify({
                    'status': 'error',
                    'message': '请先进行身份验证'
                }), 401
            
            # 检查角色
            print(f"检查权限: 用户={request.current_user.username}, 角色={request.current_user.role}, 需要角色={role} - {request.path}")
            if request.current_user.role != role and request.current_user.role != 'admin':
                print(f"权限检查失败: 用户={request.current_user.username}, 角色={request.current_user.role}, 需要角色={role} - {request.path}")
                return jsonify({
                    'status': 'error',
                    'message': f'需要 {role} 角色权限'
                }), 403
            
            print(f"权限检查通过: 用户={request.current_user.username}, 角色={request.current_user.role} - {request.path}")
            return f(*args, **kwargs)
        return decorated_function
    return decorator 