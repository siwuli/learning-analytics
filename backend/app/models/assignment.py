from datetime import datetime
from .. import db
from sqlalchemy.dialects.sqlite import JSON

class Assignment(db.Model):
    """作业模型"""
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    points = db.Column(db.Integer, default=10)
    attachments = db.Column(JSON)  # 存储附件列表，包含文件名、路径等
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    course = db.relationship('Course', backref=db.backref('assignments', lazy='dynamic'))
    submissions = db.relationship('AssignmentSubmission', backref='assignment', lazy='dynamic')
    
    def __repr__(self):
        return f'<Assignment {self.title}>'
    
    def to_dict(self, user_id=None):
        """返回作业字典表示，可选传入用户ID以返回针对该用户的作业状态"""
        # 计算提交完成率
        total_students = self.course.students.count()
        submissions_count = self.submissions.count()
        completion_rate = (submissions_count / total_students * 100) if total_students > 0 else 0
        
        # 确定作业状态
        now = datetime.utcnow()
        status = 'pending'
        if not self.deadline:
            status = 'not_started'
        elif now > self.deadline:
            status = 'overdue'
        elif submissions_count == total_students:
            status = 'completed'
            
        # 如果指定了用户ID，检查该用户的提交状态
        if user_id:
            submission = self.submissions.filter_by(user_id=user_id).first()
            if submission:
                # 用户已提交作业，标记为已完成
                status = 'completed'
        
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'points': self.points,
            'attachments': self.attachments or [],  # 确保返回空列表而非None
            'status': status,
            'completion_rate': round(completion_rate, 1),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_dict_for_user(self, user_id):
        """专门为特定用户返回作业信息，包含该用户的提交状态"""
        return self.to_dict(user_id=user_id)


class AssignmentSubmission(db.Model):
    """作业提交模型"""
    __tablename__ = 'assignment_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text)
    files = db.Column(JSON)  # 存储文件列表信息，包含文件名、路径等
    submit_time = db.Column(db.DateTime, default=datetime.utcnow)
    grade = db.Column(db.Integer, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    graded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    graded_at = db.Column(db.DateTime, nullable=True)
    
    # 关系
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('submissions', lazy='dynamic'))
    grader = db.relationship('User', foreign_keys=[graded_by], backref=db.backref('graded_submissions', lazy='dynamic'))
    
    def __repr__(self):
        return f'<AssignmentSubmission {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'user_id': self.user_id,
            'user': self.user.to_dict(),
            'content': self.content,
            'files': self.files,  # 添加文件信息
            'submit_time': self.submit_time.isoformat() if self.submit_time else None,
            'grade': self.grade,
            'feedback': self.feedback,
            'graded_by': self.graded_by,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None,
        } 