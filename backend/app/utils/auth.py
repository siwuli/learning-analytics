from functools import wraps
from flask import request, jsonify
from backend.app.models import User

def authenticate(f):
    """身份验证装饰器（示例）"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # 这里应该实现真正的身份验证逻辑，例如JWT
        # 以下仅作为示例，不应在生产环境中使用
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'status': 'error',
                'message': '未提供认证信息'
            }), 401
        
        # 模拟从令牌中获取用户信息
        # 实际项目中请使用JWT或其他认证方式
        user_id = 1  # 示例用户ID
        
        # 检查用户是否存在
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': '认证失败：用户不存在'
            }), 401
        
        # 将用户信息添加到请求上下文
        request.current_user = user
        
        return f(*args, **kwargs)
    return decorated

def require_role(role):
    """角色要求装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 确保用户已认证
            if not hasattr(request, 'current_user'):
                return jsonify({
                    'status': 'error',
                    'message': '请先进行身份验证'
                }), 401
            
            # 检查角色
            if request.current_user.role != role and request.current_user.role != 'admin':
                return jsonify({
                    'status': 'error',
                    'message': f'需要 {role} 角色权限'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator 