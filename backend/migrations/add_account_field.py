"""
添加用户账号字段的迁移脚本

此脚本会在users表中添加account字段，并将现有用户的username复制到account字段中初始化
"""

from app import db, create_app
from app.models import User
from sqlalchemy import Column, String
from sqlalchemy.exc import OperationalError

def migrate():
    """执行迁移操作"""
    app = create_app()
    with app.app_context():
        # 1. 检查是否已存在account字段
        try:
            # 尝试查询一个用户的account字段，如果不存在会抛出异常
            User.query.with_entities(User.account).first()
            print("account字段已存在，无需迁移")
            return
        except (OperationalError, AttributeError):
            print("account字段不存在，开始迁移...")
        
        # 2. 添加account字段
        # 使用db.engine直接执行SQL语句
        db.engine.execute('ALTER TABLE users ADD COLUMN account VARCHAR(64) UNIQUE')
        print("已添加account字段")
        
        # 3. 将username的值复制到account字段
        users = User.query.all()
        for user in users:
            # 直接执行SQL更新，因为模型中的account字段还不能直接访问
            db.engine.execute(f"UPDATE users SET account = '{user.username}' WHERE id = {user.id}")
        
        print(f"已初始化{len(users)}个用户的account字段")
        print("迁移完成！")

if __name__ == "__main__":
    migrate() 