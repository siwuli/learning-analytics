"""
修复数据库中现有的头像URL格式
"""
from app import create_app, db
from app.models.user import User
import os
import re

def fix_avatar_urls():
    """修复用户头像URL"""
    app = create_app('development')
    with app.app_context():
        users = User.query.all()
        
        print(f"系统中共有 {len(users)} 个用户")
        fixed_count = 0
        
        for user in users:
            if not user.avatar:
                continue
                
            original_url = user.avatar
            print(f"\n处理用户: {user.username} (ID: {user.id})")
            print(f"  原始头像URL: {original_url}")
            
            # 如果URL包含有效文件名
            filename_match = re.search(r'([^/\\]+\.(jpg|jpeg|png|gif))$', original_url, re.IGNORECASE)
            if filename_match:
                filename = filename_match.group(1)
                # 创建新的标准格式URL
                new_url = f"/api/static/uploads/avatars/{filename}"
                
                # 检查文件是否存在于目标目录
                avatar_dir = os.path.join(app.static_folder, 'uploads', 'avatars')
                if not os.path.exists(os.path.join(avatar_dir, filename)):
                    print(f"  警告: 文件 {filename} 在头像目录中不存在")
                    # 如果需要，可以在这里添加文件复制逻辑
                
                # 更新用户头像URL
                user.avatar = new_url
                fixed_count += 1
                print(f"  新头像URL: {new_url}")
            else:
                print(f"  无法从URL中提取有效的文件名")
        
        # 提交更改
        if fixed_count > 0:
            db.session.commit()
            print(f"\n已修复 {fixed_count} 个用户的头像URL")
        else:
            print("\n没有需要修复的头像URL")

if __name__ == '__main__':
    fix_avatar_urls() 