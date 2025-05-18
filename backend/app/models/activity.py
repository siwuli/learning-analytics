from datetime import datetime
from backend.app import db

class Activity(db.Model):
    """学习活动模型"""
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # video_watch, quiz, assignment
    resource_id = db.Column(db.String(100))  # 资源ID（例如视频ID、测验ID）
    duration = db.Column(db.Integer)  # 持续时间（秒）
    score = db.Column(db.Float)  # 得分（如适用）
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = db.Column(db.JSON)  # 其他元数据（如进度、正确答案数等）

    def __repr__(self):
        return f'<Activity {self.id}: {self.activity_type}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'activity_type': self.activity_type,
            'resource_id': self.resource_id,
            'duration': self.duration,
            'score': self.score,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'metadata': self.metadata
        } 