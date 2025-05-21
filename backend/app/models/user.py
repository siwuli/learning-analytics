from datetime import datetime
from .. import db

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='student')  # student, teacher, admin
    avatar = db.Column(db.String(200))  # 头像URL
    bio = db.Column(db.Text)  # 个人简介
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    activities = db.relationship('Activity', backref='user', lazy='dynamic')
    # 课程关系在Course模型中通过backref定义

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        avatar_url = self.avatar
        # 如果头像URL存在但不是以http开头，则添加服务器地址前缀
        if avatar_url and not (avatar_url.startswith('http://') or avatar_url.startswith('https://')):
            # 确保路径格式正确
            if not avatar_url.startswith('/'):
                avatar_url = '/' + avatar_url
            # 确保路径以/api开头
            if not avatar_url.startswith('/api'):
                avatar_url = '/api' + avatar_url
                
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'avatar': avatar_url,
            'bio': self.bio,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 课程注册表 (多对多关系)
course_enrollments = db.Table('course_enrollments',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True),
    db.Column('enrolled_at', db.DateTime, default=datetime.utcnow)
) 