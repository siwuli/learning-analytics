from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

# 管理员用户数据
admin_user = {
    'account': 'admin',
    'username': '系统管理员',
    'email': 'admin@example.com',
    'password': 'admin123',
    'role': 'admin'
}

with app.app_context():
    # 检查管理员用户是否已存在
    existing_admin = User.query.filter_by(account=admin_user['account']).first()
    if existing_admin:
        print(f"管理员用户 {admin_user['account']} 已存在，跳过创建")
    else:
        # 创建管理员用户
        new_admin = User(
            account=admin_user['account'],
            username=admin_user['username'],
            email=admin_user['email'],
            password_hash=generate_password_hash(admin_user['password']),
            role=admin_user['role']
        )
        
        db.session.add(new_admin)
        db.session.commit()
        print(f"管理员用户 {admin_user['account']} 创建成功")
        print(f"用户名: {admin_user['username']}")
        print(f"邮箱: {admin_user['email']}")
        print(f"密码: {admin_user['password']}")
    
    # 显示所有管理员用户
    admin_users = User.query.filter_by(role='admin').all()
    print("\n系统中的管理员用户:")
    for user in admin_users:
        print(f"ID: {user.id}, 账号: {user.account}, 用户名: {user.username}, 邮箱: {user.email}") 