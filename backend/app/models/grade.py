from datetime import datetime
from .. import db

class GradeSetting(db.Model):
    """课程成绩设置模型 - 设置课程的成绩比重"""
    __tablename__ = 'grade_settings'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    final_exam_weight = db.Column(db.Float, default=60.0)  # 期末考试权重，默认60%
    regular_grade_weight = db.Column(db.Float, default=40.0)  # 平时成绩权重，默认40%
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    course = db.relationship('Course', backref=db.backref('grade_setting', uselist=False))

    def __repr__(self):
        return f'<GradeSetting {self.course_id} Final:{self.final_exam_weight}% Regular:{self.regular_grade_weight}%>'

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'final_exam_weight': self.final_exam_weight,
            'regular_grade_weight': self.regular_grade_weight,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class StudentGrade(db.Model):
    """学生成绩模型 - 记录学生在课程中的成绩"""
    __tablename__ = 'student_grades'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    final_exam_score = db.Column(db.Float)  # 期末考试成绩
    regular_grade = db.Column(db.Float)  # 平时成绩
    total_score = db.Column(db.Float)  # 总评成绩
    comment = db.Column(db.Text)  # 教师评语
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 定义联合唯一约束，确保每个学生在每个课程中只有一条成绩记录
    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_id', name='uq_user_course_grade'),
    )

    # 关系
    user = db.relationship('User', backref=db.backref('grades', lazy='dynamic'))
    course = db.relationship('Course', backref=db.backref('student_grades', lazy='dynamic'))

    def __repr__(self):
        return f'<StudentGrade {self.user_id}:{self.course_id} Total:{self.total_score}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'final_exam_score': self.final_exam_score,
            'regular_grade': self.regular_grade,
            'total_score': self.total_score,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def calculate_total_score(self, grade_setting):
        """
        根据课程成绩设置计算总评成绩
        """
        if self.final_exam_score is None or self.regular_grade is None:
            return None
            
        final_weight = grade_setting.final_exam_weight / 100
        regular_weight = grade_setting.regular_grade_weight / 100
        
        return self.final_exam_score * final_weight + self.regular_grade * regular_weight 