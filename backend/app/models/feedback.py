from datetime import datetime
from .. import db

class CourseReview(db.Model):
    """课程评价模型"""
    __tablename__ = 'course_reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5星评分
    content = db.Column(db.Text)  # 评价内容
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 定义联合唯一约束，确保每个用户只能对每个课程评价一次
    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_id', name='uq_user_course_review'),
    )

    # 关系
    user = db.relationship('User', backref=db.backref('course_reviews', lazy='dynamic'))
    course = db.relationship('Course', backref=db.backref('reviews', lazy='dynamic'))

    def __repr__(self):
        return f'<CourseReview {self.user_id}:{self.course_id} {self.rating}星>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'course_id': self.course_id,
            'rating': self.rating,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 