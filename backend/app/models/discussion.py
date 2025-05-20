from datetime import datetime
from .. import db

class Discussion(db.Model):
    """讨论话题模型"""
    __tablename__ = 'discussions'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_pinned = db.Column(db.Boolean, default=False)
    
    # 关系
    course = db.relationship('Course', backref=db.backref('discussions', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('discussions', lazy='dynamic'))
    replies = db.relationship('DiscussionReply', backref='discussion', lazy='dynamic', 
                             cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Discussion {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'user_id': self.user_id,
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'role': self.user.role
            },
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_pinned': self.is_pinned,
            'replies_count': self.replies.count()
        }
        
    def to_dict_with_replies(self):
        result = self.to_dict()
        result['replies'] = [reply.to_dict() for reply in self.replies]
        return result


class DiscussionReply(db.Model):
    """讨论回复模型"""
    __tablename__ = 'discussion_replies'
    
    id = db.Column(db.Integer, primary_key=True)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref=db.backref('discussion_replies', lazy='dynamic'))
    
    def __repr__(self):
        return f'<DiscussionReply {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'discussion_id': self.discussion_id,
            'user_id': self.user_id,
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'role': self.user.role
            },
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 