from flask import jsonify, request
from . import api_bp
from ..models import Activity, User, Course
from .. import db
from sqlalchemy import func, and_
from datetime import datetime, timedelta

@api_bp.route('/analytics/user/<int:user_id>', methods=['GET'])
def user_analytics(user_id):
    """获取用户的学习分析数据"""
    user = User.query.get_or_404(user_id)
    
    # 获取用户的总活动时间
    total_duration = db.session.query(func.sum(Activity.duration)) \
        .filter(Activity.user_id == user_id) \
        .scalar() or 0
    
    # 获取用户完成的活动数量
    completed_activities = Activity.query \
        .filter(Activity.user_id == user_id, Activity.completed == True) \
        .count()
    
    # 获取用户的平均得分
    avg_score = db.session.query(func.avg(Activity.score)) \
        .filter(Activity.user_id == user_id) \
        .scalar() or 0
    
    # 获取课程进度
    course_progress = []
    enrolled_courses = user.courses
    
    for course in enrolled_courses:
        course_activities = Activity.query \
            .filter(Activity.course_id == course.id, Activity.user_id == user_id) \
            .all()
        
        total_course_activities = len(course_activities)
        completed_course_activities = sum(1 for act in course_activities if act.completed)
        
        if total_course_activities > 0:
            progress_percent = (completed_course_activities / total_course_activities) * 100
        else:
            progress_percent = 0
        
        course_progress.append({
            'course_id': course.id,
            'course_title': course.title,
            'total_activities': total_course_activities,
            'completed_activities': completed_course_activities,
            'progress_percent': progress_percent
        })
    
    # 获取用户最近的活动
    recent_activities = Activity.query \
        .filter(Activity.user_id == user_id) \
        .order_by(Activity.created_at.desc()) \
        .limit(5) \
        .all()
    
    return jsonify({
        'status': 'success',
        'user_id': user_id,
        'total_duration': total_duration,
        'total_activities': Activity.query.filter(Activity.user_id == user_id).count(),
        'completed_activities': completed_activities,
        'avg_score': avg_score,
        'course_progress': course_progress,
        'recent_activities': [activity.to_dict() for activity in recent_activities]
    })

@api_bp.route('/analytics/course/<int:course_id>', methods=['GET'])
def course_analytics(course_id):
    """获取课程的分析数据"""
    course = Course.query.get_or_404(course_id)
    
    # 获取课程的总学生数
    student_count = course.students.count()
    
    # 获取课程的平均完成率
    course_activities = Activity.query.filter(Activity.course_id == course_id).all()
    
    if course_activities:
        completion_rate = (sum(1 for act in course_activities if act.completed) / len(course_activities)) * 100
    else:
        completion_rate = 0
    
    # 获取课程的平均得分
    avg_score = db.session.query(func.avg(Activity.score)) \
        .filter(Activity.course_id == course_id) \
        .scalar() or 0
    
    # 获取最活跃的学生（基于活动数量）
    active_students = db.session.query(
            User.id, User.username, func.count(Activity.id).label('activity_count')
        ) \
        .join(Activity, Activity.user_id == User.id) \
        .filter(Activity.course_id == course_id) \
        .group_by(User.id) \
        .order_by(func.count(Activity.id).desc()) \
        .limit(5) \
        .all()
    
    active_students_list = [
        {
            'user_id': user_id,
            'username': username,
            'activity_count': count
        }
        for user_id, username, count in active_students
    ]
    
    # 获取不同类型活动的统计
    activity_types = db.session.query(
            Activity.activity_type, func.count(Activity.id).label('count')
        ) \
        .filter(Activity.course_id == course_id) \
        .group_by(Activity.activity_type) \
        .all()
    
    activity_types_stats = {
        activity_type: count
        for activity_type, count in activity_types
    }
    
    return jsonify({
        'status': 'success',
        'course_id': course_id,
        'student_count': student_count,
        'activity_count': len(course_activities),
        'completion_rate': completion_rate,
        'avg_score': avg_score,
        'active_students': active_students_list,
        'activity_types': activity_types_stats
    })

@api_bp.route('/analytics/overview', methods=['GET'])
def analytics_overview():
    """获取系统整体分析概览"""
    # 获取用户数量统计
    user_counts = {
        'total': User.query.count(),
        'students': User.query.filter_by(role='student').count(),
        'teachers': User.query.filter_by(role='teacher').count(),
        'admins': User.query.filter_by(role='admin').count()
    }
    
    # 获取课程统计
    course_counts = {
        'total': Course.query.count(),
        'active': Course.query.filter_by(status='active').count(),
        'archived': Course.query.filter_by(status='archived').count()
    }
    
    # 获取活动统计
    activity_counts = {
        'total': Activity.query.count(),
        'completed': Activity.query.filter_by(completed=True).count()
    }
    
    # 获取平台参与度随时间变化
    # 获取过去30天每天的活动数量
    today = datetime.utcnow().date()
    thirty_days_ago = today - timedelta(days=30)
    
    daily_activities = db.session.query(
            func.date(Activity.created_at).label('date'),
            func.count(Activity.id).label('count')
        ) \
        .filter(func.date(Activity.created_at) >= thirty_days_ago) \
        .group_by(func.date(Activity.created_at)) \
        .order_by(func.date(Activity.created_at)) \
        .all()
    
    activity_trend = [
        {
            'date': date.isoformat(),
            'count': count
        }
        for date, count in daily_activities
    ]
    
    return jsonify({
        'status': 'success',
        'user_counts': user_counts,
        'course_counts': course_counts,
        'activity_counts': activity_counts,
        'activity_trend': activity_trend
    }) 