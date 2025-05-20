from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

# 测试用户数据
test_users = [
    {'id': 101, 'username': 'student1', 'email': 'student1@example.com', 'password': '123456', 'role': 'student'},
    {'id': 102, 'username': 'student2', 'email': 'student2@example.com', 'password': '123456', 'role': 'student'},
    {'id': 103, 'username': 'student3', 'email': 'student3@example.com', 'password': '123456', 'role': 'student'}
]

with app.app_context():
    # 检查并创建测试用户
    for user_data in test_users:
        # 检查用户是否已存在
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if existing_user:
            print(f"用户 {user_data['username']} 已存在，跳过")
            continue
        
        # 创建新用户
        new_user = User(
            username=user_data['username'],
            email=user_data['email'],
            password_hash=generate_password_hash(user_data['password']),
            role=user_data['role']
        )
        
        db.session.add(new_user)
        print(f"添加用户 {user_data['username']}")
    
    # 提交所有更改
    db.session.commit()
    print("用户创建完成")
    
    # 验证用户创建
    users = User.query.all()
    print("\n所有用户:")
    for user in users:
        print(f"ID: {user.id}, 用户名: {user.username}, 角色: {user.role}") 