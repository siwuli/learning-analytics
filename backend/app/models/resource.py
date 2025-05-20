from datetime import datetime
from .. import db

class CourseSection(db.Model):
    """课程章节模型"""
    __tablename__ = 'course_sections'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)  # 章节顺序
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    course = db.relationship('Course', backref=db.backref('sections', lazy='dynamic', order_by='CourseSection.order'))
    resources = db.relationship('CourseResource', backref='section', lazy='dynamic', order_by='CourseResource.order')

    def __repr__(self):
        return f'<CourseSection {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'order': self.order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_dict_with_resources(self):
        result = self.to_dict()
        result['resources'] = [resource.to_dict() for resource in self.resources]
        return result


class CourseResource(db.Model):
    """课程资源模型"""
    __tablename__ = 'course_resources'

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('course_sections.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    resource_type = db.Column(db.String(50), nullable=False)  # document, video, quiz, assignment
    content = db.Column(db.Text)  # 内容或资源URL
    data_json = db.Column(db.JSON)  # 其他元数据
    order = db.Column(db.Integer, default=0)  # 资源顺序
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<CourseResource {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'section_id': self.section_id,
            'title': self.title,
            'description': self.description,
            'resource_type': self.resource_type,
            'content': self.content,
            'metadata': self.data_json,
            'order': self.order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 