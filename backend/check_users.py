from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print("所有用户:")
    for user in users:
        print(f"ID: {user.id}, 用户名: {user.username}, 角色: {user.role}")
    
    # 检查是否有ID为101, 102, 103的用户
    for user_id in [101, 102, 103]:
        user = User.query.get(user_id)
        if user:
            print(f"存在用户ID {user_id}: {user.username}")
        else:
            print(f"不存在用户ID {user_id}") 