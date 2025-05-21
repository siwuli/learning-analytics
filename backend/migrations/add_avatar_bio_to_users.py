"""
添加avatar和bio字段到用户表的迁移脚本
"""
from app import create_app, db
from flask import current_app
from app.models import User
from alembic import op
import sqlalchemy as sa

def upgrade():
    """添加avatar和bio字段到用户表"""
    # 创建上下文
    app = create_app()
    with app.app_context():
        # 添加字段
        op.add_column('users', sa.Column('avatar', sa.String(200), nullable=True))
        op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
        
        # 提交更改
        db.session.commit()
        print("已添加avatar和bio字段到用户表")

def downgrade():
    """移除avatar和bio字段"""
    # 创建上下文
    app = create_app()
    with app.app_context():
        # 移除字段
        op.drop_column('users', 'avatar')
        op.drop_column('users', 'bio')
        
        # 提交更改
        db.session.commit()
        print("已移除avatar和bio字段")

if __name__ == '__main__':
    # 执行升级
    upgrade()
    print("迁移完成") 