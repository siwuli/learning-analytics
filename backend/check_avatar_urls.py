"""
检查用户的头像URL配置
"""
from app import create_app, db
from app.models.user import User

def check_avatars():
    """检查所有用户的头像URL"""
    app = create_app('development')
    with app.app_context():
        users = User.query.all()
        
        print(f"系统中共有 {len(users)} 个用户")
        
        for user in users:
            print(f"\n用户: {user.username} (ID: {user.id})")
            print(f"  角色: {user.role}")
            print(f"  头像URL: {user.avatar or '无'}")
            
        print("\n要测试头像访问，请尝试以下URL:")
        for user in users:
            if user.avatar:
                # 去掉开头的斜杠以构建完整URL
                avatar_path = user.avatar[1:] if user.avatar.startswith('/') else user.avatar
                print(f"  http://localhost:5000/{avatar_path}")

if __name__ == '__main__':
    check_avatars() 