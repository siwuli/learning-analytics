from flask import jsonify, request, url_for, current_app
from . import api_bp
from ..models import CourseSection, CourseResource, Course, ResourceProgress
from .. import db
import os
from werkzeug.utils import secure_filename
import uuid

# 允许的文件类型
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'zip', 'rar', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({
            'status': 'error',
            'message': '没有找到文件'
        }), 400
        
    file = request.files['file']
    
    # 检查文件名是否为空
    if file.filename == '':
        return jsonify({
            'status': 'error',
            'message': '没有选择文件'
        }), 400
        
    # 检查文件类型
    if not allowed_file(file.filename):
        return jsonify({
            'status': 'error',
            'message': '不支持的文件类型'
        }), 400
        
    # 安全处理文件名
    original_filename = secure_filename(file.filename)
    # 使用UUID生成唯一文件名，保留原始扩展名
    filename = f"{uuid.uuid4().hex}_{original_filename}"
    
    # 确保上传目录存在
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    # 生成文件URL
    file_url = url_for('static', filename=f'uploads/{filename}', _external=True)
    
    return jsonify({
        'status': 'success',
        'message': '文件上传成功',
        'file_path': f'uploads/{filename}',
        'file_url': file_url,
        'original_filename': original_filename
    })

@api_bp.route('/courses/<int:course_id>/sections', methods=['GET'])
def get_course_sections(course_id):
    """获取课程的所有章节"""
    course = Course.query.get_or_404(course_id)
    sections = CourseSection.query.filter_by(course_id=course_id).order_by(CourseSection.order).all()
    
    return jsonify({
        'status': 'success',
        'sections': [section.to_dict() for section in sections]
    })

@api_bp.route('/courses/<int:course_id>/sections/<int:section_id>', methods=['GET'])
def get_course_section(course_id, section_id):
    """获取课程章节详情和资源"""
    course = Course.query.get_or_404(course_id)
    section = CourseSection.query.filter_by(id=section_id, course_id=course_id).first_or_404()
    
    return jsonify({
        'status': 'success',
        'section': section.to_dict_with_resources()
    })

@api_bp.route('/courses/<int:course_id>/sections', methods=['POST'])
def create_course_section(course_id):
    """创建课程章节"""
    course = Course.query.get_or_404(course_id)
    data = request.json
    
    # 获取最大顺序值
    max_order = db.session.query(db.func.max(CourseSection.order))\
        .filter(CourseSection.course_id == course_id).scalar() or 0
    
    section = CourseSection(
        course_id=course_id,
        title=data.get('title'),
        description=data.get('description'),
        order=max_order + 1
    )
    
    db.session.add(section)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '章节创建成功',
        'section': section.to_dict()
    }), 201

@api_bp.route('/courses/<int:course_id>/sections/<int:section_id>', methods=['PUT'])
def update_course_section(course_id, section_id):
    """更新课程章节"""
    section = CourseSection.query.filter_by(id=section_id, course_id=course_id).first_or_404()
    data = request.json
    
    if 'title' in data:
        section.title = data['title']
    if 'description' in data:
        section.description = data['description']
    if 'order' in data:
        section.order = data['order']
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '章节更新成功',
        'section': section.to_dict()
    })

@api_bp.route('/courses/<int:course_id>/sections/<int:section_id>', methods=['DELETE'])
def delete_course_section(course_id, section_id):
    """删除课程章节"""
    section = CourseSection.query.filter_by(id=section_id, course_id=course_id).first_or_404()
    
    # 删除章节下的所有资源
    CourseResource.query.filter_by(section_id=section_id).delete()
    
    db.session.delete(section)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '章节删除成功'
    })

@api_bp.route('/sections/<int:section_id>/resources', methods=['GET'])
def get_section_resources(section_id):
    """获取章节的所有资源"""
    section = CourseSection.query.get_or_404(section_id)
    resources = CourseResource.query.filter_by(section_id=section_id).order_by(CourseResource.order).all()
    
    return jsonify({
        'status': 'success',
        'resources': [resource.to_dict() for resource in resources]
    })

@api_bp.route('/sections/<int:section_id>/resources/<int:resource_id>', methods=['GET'])
def get_section_resource(section_id, resource_id):
    """获取章节资源详情"""
    resource = CourseResource.query.filter_by(id=resource_id, section_id=section_id).first_or_404()
    
    return jsonify({
        'status': 'success',
        'resource': resource.to_dict()
    })

@api_bp.route('/sections/<int:section_id>/resources', methods=['POST'])
def create_section_resource(section_id):
    """创建章节资源"""
    section = CourseSection.query.get_or_404(section_id)
    data = request.json
    
    # 获取最大顺序值
    max_order = db.session.query(db.func.max(CourseResource.order))\
        .filter(CourseResource.section_id == section_id).scalar() or 0
    
    resource = CourseResource(
        section_id=section_id,
        title=data.get('title'),
        description=data.get('description'),
        resource_type=data.get('resource_type'),
        content=data.get('content'),
        file_path=data.get('file_path'),  # 添加文件路径
        data_json=data.get('metadata', {}),
        order=max_order + 1
    )
    
    db.session.add(resource)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '资源创建成功',
        'resource': resource.to_dict()
    }), 201

@api_bp.route('/sections/<int:section_id>/resources/<int:resource_id>', methods=['PUT'])
def update_section_resource(section_id, resource_id):
    """更新章节资源"""
    resource = CourseResource.query.filter_by(id=resource_id, section_id=section_id).first_or_404()
    data = request.json
    
    if 'title' in data:
        resource.title = data['title']
    if 'description' in data:
        resource.description = data['description']
    if 'resource_type' in data:
        resource.resource_type = data['resource_type']
    if 'content' in data:
        resource.content = data['content']
    if 'file_path' in data:
        resource.file_path = data['file_path']  # 更新文件路径
    if 'metadata' in data:
        # 合并现有元数据和新元数据
        current_metadata = resource.data_json or {}
        current_metadata.update(data['metadata'])
        resource.data_json = current_metadata
    if 'order' in data:
        resource.order = data['order']
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '资源更新成功',
        'resource': resource.to_dict()
    })

@api_bp.route('/sections/<int:section_id>/resources/<int:resource_id>', methods=['DELETE'])
def delete_section_resource(section_id, resource_id):
    """删除章节资源"""
    resource = CourseResource.query.filter_by(id=resource_id, section_id=section_id).first_or_404()
    
    # 首先删除与该资源相关的所有进度记录
    ResourceProgress.query.filter_by(resource_id=resource_id).delete()
    
    db.session.delete(resource)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '资源删除成功'
    }) 