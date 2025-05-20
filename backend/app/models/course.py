from datetime import datetime
from .. import db

# 课程学生关联表（多对多关系）
course_students = db.Table('course_students',
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('enrolled_at', db.DateTime, default=datetime.utcnow)
)

class Course(db.Model):
    """课程模型"""
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, archived

    # 关系
    instructor = db.relationship('User', backref='teaching_courses', foreign_keys=[instructor_id])
    activities = db.relationship('Activity', backref='course', lazy='dynamic')
    
    # 多对多关系：课程的学生
    students = db.relationship('User',
        secondary=course_students,
        backref=db.backref('enrolled_courses', lazy='dynamic'),
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<Course {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'instructor_id': self.instructor_id,
            'instructorName': self.instructor.username if self.instructor else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'student_count': self.students.count()
        }
        
    def to_dict_with_students(self):
        result = self.to_dict()
        result['students'] = [student.to_dict() for student in self.students]
        return result 