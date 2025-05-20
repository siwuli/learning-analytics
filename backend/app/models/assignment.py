from datetime import datetime
from .. import db

class Assignment(db.Model):
    """作业模型"""
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    points = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    course = db.relationship('Course', backref=db.backref('assignments', lazy='dynamic'))
    submissions = db.relationship('AssignmentSubmission', backref='assignment', lazy='dynamic')
    
    def __repr__(self):
        return f'<Assignment {self.title}>'
    
    def to_dict(self):
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
            
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'points': self.points,
            'status': status,
            'completion_rate': round(completion_rate, 1),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AssignmentSubmission(db.Model):
    """作业提交模型"""
    __tablename__ = 'assignment_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text)
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
            'submit_time': self.submit_time.isoformat() if self.submit_time else None,
            'grade': self.grade,
            'feedback': self.feedback,
            'graded_by': self.graded_by,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None,
        } 