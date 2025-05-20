from datetime import datetime
from .. import db

class CourseProgress(db.Model):
    """课程进度模型 - 跟踪学生在课程中的整体进度"""
    __tablename__ = 'course_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    progress_percent = db.Column(db.Float, default=0.0)  # 0-100
    last_activity_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 定义联合唯一约束，确保每个用户在每个课程中只有一条进度记录
    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_id', name='uq_user_course_progress'),
    )

    # 关系
    user = db.relationship('User', backref=db.backref('course_progress', lazy='dynamic'))
    course = db.relationship('Course', backref=db.backref('student_progress', lazy='dynamic'))

    def __repr__(self):
        return f'<CourseProgress {self.user_id}:{self.course_id} {self.progress_percent}%>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'progress_percent': self.progress_percent,
            'last_activity_at': self.last_activity_at.isoformat() if self.last_activity_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ResourceProgress(db.Model):
    """资源进度模型 - 跟踪学生对特定资源的学习进度"""
    __tablename__ = 'resource_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('course_resources.id'), nullable=False)
    progress_percent = db.Column(db.Float, default=0.0)  # 0-100
    completed = db.Column(db.Boolean, default=False)
    last_position = db.Column(db.String(100))  # 视频时间点或文档位置
    data_json = db.Column(db.JSON)  # 其他进度相关数据
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 定义联合唯一约束，确保每个用户对每个资源只有一条进度记录
    __table_args__ = (
        db.UniqueConstraint('user_id', 'resource_id', name='uq_user_resource_progress'),
    )

    # 关系
    user = db.relationship('User', backref=db.backref('resource_progress', lazy='dynamic'))
    resource = db.relationship('CourseResource', backref=db.backref('user_progress', lazy='dynamic'))

    def __repr__(self):
        return f'<ResourceProgress {self.user_id}:{self.resource_id} {self.progress_percent}%>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'progress_percent': self.progress_percent,
            'completed': self.completed,
            'last_position': self.last_position,
            'metadata': self.data_json,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 