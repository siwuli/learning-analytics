"""
添加用户账号字段的迁移脚本
"""

from app import db, create_app
from app.models import User
import sqlalchemy

app = create_app()
with app.app_context():
    try:
        # 检查字段是否存在
        inspector = sqlalchemy.inspect(db.engine)
        columns = [column['name'] for column in inspector.get_columns('users')]
        
        if 'account' in columns:
            print("account字段已存在，无需迁移")
        else:
            print("account字段不存在，开始迁移...")
            
            # 添加account字段，SQLite不支持直接添加UNIQUE约束，先添加普通列
            with db.engine.connect() as conn:
                conn.execute(sqlalchemy.text('ALTER TABLE users ADD COLUMN account VARCHAR(64)'))
                print("已添加account字段")
                
                # 将username的值复制到account字段
                users = User.query.all()
                for user in users:
                    conn.execute(sqlalchemy.text(f"UPDATE users SET account = '{user.username}' WHERE id = {user.id}"))
                
                print(f"已初始化{len(users)}个用户的account字段")
                conn.commit()
                print("迁移完成！")
    except Exception as e:
        print(f"发生错误: {e}") 