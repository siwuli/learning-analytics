from flask import jsonify, request
from . import api_bp
from ..models import CourseReview, User, Course
from .. import db
from sqlalchemy.sql import func

@api_bp.route('/courses/<int:course_id>/reviews', methods=['GET'])
def get_course_reviews(course_id):
    """获取课程的所有评价"""
    course = Course.query.get_or_404(course_id)
    
    # 获取课程评价
    reviews = CourseReview.query.filter_by(course_id=course_id).all()
    
    # 计算平均评分
    avg_rating = db.session.query(func.avg(CourseReview.rating))\
        .filter(CourseReview.course_id == course_id).scalar() or 0
    
    # 统计各个评分的数量
    rating_counts = {}
    for i in range(1, 6):
        count = CourseReview.query.filter_by(course_id=course_id, rating=i).count()
        rating_counts[str(i)] = count
    
    return jsonify({
        'status': 'success',
        'reviews': [review.to_dict() for review in reviews],
        'stats': {
            'average_rating': round(float(avg_rating), 1),
            'review_count': len(reviews),
            'rating_counts': rating_counts
        }
    })

@api_bp.route('/courses/<int:course_id>/reviews/<int:user_id>', methods=['GET'])
def get_user_course_review(course_id, user_id):
    """获取特定用户对课程的评价"""
    course = Course.query.get_or_404(course_id)
    user = User.query.get_or_404(user_id)
    
    review = CourseReview.query.filter_by(course_id=course_id, user_id=user_id).first()
    
    if not review:
        return jsonify({
            'status': 'error',
            'message': '找不到评价记录'
        }), 404
    
    return jsonify({
        'status': 'success',
        'review': review.to_dict()
    })

@api_bp.route('/courses/<int:course_id>/reviews', methods=['POST'])
def create_course_review(course_id):
    """创建课程评价"""
    course = Course.query.get_or_404(course_id)
    data = request.json
    
    user_id = data.get('user_id')
    user = User.query.get_or_404(user_id)
    
    # 检查用户是否已评价过此课程
    existing_review = CourseReview.query.filter_by(course_id=course_id, user_id=user_id).first()
    
    if existing_review:
        return jsonify({
            'status': 'error',
            'message': '用户已经评价过此课程'
        }), 400
    
    # 检查评分是否在有效范围内
    rating = data.get('rating')
    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({
            'status': 'error',
            'message': '评分必须是1-5之间的整数'
        }), 400
    
    # 创建新评价
    review = CourseReview(
        user_id=user_id,
        course_id=course_id,
        rating=rating,
        content=data.get('content', '')
    )
    
    db.session.add(review)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '评价创建成功',
        'review': review.to_dict()
    }), 201

@api_bp.route('/courses/<int:course_id>/reviews/<int:user_id>', methods=['PUT'])
def update_course_review(course_id, user_id):
    """更新课程评价"""
    course = Course.query.get_or_404(course_id)
    user = User.query.get_or_404(user_id)
    data = request.json
    
    review = CourseReview.query.filter_by(course_id=course_id, user_id=user_id).first_or_404()
    
    # 检查评分是否在有效范围内
    if 'rating' in data:
        rating = data['rating']
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({
                'status': 'error',
                'message': '评分必须是1-5之间的整数'
            }), 400
        review.rating = rating
    
    if 'content' in data:
        review.content = data['content']
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '评价更新成功',
        'review': review.to_dict()
    })

@api_bp.route('/courses/<int:course_id>/reviews/<int:user_id>', methods=['DELETE'])
def delete_course_review(course_id, user_id):
    """删除课程评价"""
    course = Course.query.get_or_404(course_id)
    user = User.query.get_or_404(user_id)
    
    review = CourseReview.query.filter_by(course_id=course_id, user_id=user_id).first_or_404()
    
    db.session.delete(review)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '评价删除成功'
    }) 