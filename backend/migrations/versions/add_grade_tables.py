"""添加成绩相关表

Revision ID: add_grade_tables
Revises: e156851f08eb
Create Date: 2023-08-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_grade_tables'
down_revision = 'e156851f08eb'
branch_labels = None
depends_on = None


def upgrade():
    # 创建成绩设置表
    op.create_table('grade_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('final_exam_weight', sa.Float(), nullable=True),
        sa.Column('regular_grade_weight', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建学生成绩表
    op.create_table('student_grades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('final_exam_score', sa.Float(), nullable=True),
        sa.Column('regular_grade', sa.Float(), nullable=True),
        sa.Column('total_score', sa.Float(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'course_id', name='uq_user_course_grade')
    )


def downgrade():
    # 删除表
    op.drop_table('student_grades')
    op.drop_table('grade_settings') 