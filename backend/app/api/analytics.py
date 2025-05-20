from flask import jsonify, request
from . import api_bp
from ..models import Activity, User, Course, CourseProgress, ResourceProgress, Assignment
from .. import db
from sqlalchemy import func, and_, desc, asc
from datetime import datetime, timedelta
import statistics

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
    enrolled_courses = user.enrolled_courses.all()
    
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
    
    # 获取学生进度分布
    progress_data = db.session.query(CourseProgress.progress_percent) \
        .filter(CourseProgress.course_id == course_id) \
        .all()
    
    progress_distribution = {
        "0-20%": 0,
        "21-40%": 0,
        "41-60%": 0,
        "61-80%": 0,
        "81-100%": 0
    }
    
    for (progress,) in progress_data:
        if progress <= 20:
            progress_distribution["0-20%"] += 1
        elif progress <= 40:
            progress_distribution["21-40%"] += 1
        elif progress <= 60:
            progress_distribution["41-60%"] += 1
        elif progress <= 80:
            progress_distribution["61-80%"] += 1
        else:
            progress_distribution["81-100%"] += 1
    
    # 获取作业完成率和平均得分
    assignments = Assignment.query.filter(Assignment.course_id == course_id).all()
    
    assignment_stats = []
    for assignment in assignments:
        submissions_count = assignment.submissions.count()
        student_count = course.students.count()
        
        if student_count > 0:
            completion_rate = (submissions_count / student_count) * 100
        else:
            completion_rate = 0
            
        avg_score = db.session.query(func.avg(Activity.score)) \
            .filter(Activity.resource_id == str(assignment.id)) \
            .scalar() or 0
            
        assignment_stats.append({
            'id': assignment.id,
            'title': assignment.title,
            'completion_rate': completion_rate,
            'avg_score': avg_score
        })
    
    return jsonify({
        'status': 'success',
        'course_id': course_id,
        'student_count': student_count,
        'activity_count': len(course_activities),
        'completion_rate': completion_rate,
        'avg_score': avg_score,
        'active_students': active_students_list,
        'activity_types': activity_types_stats,
        'progress_distribution': progress_distribution,
        'assignment_stats': assignment_stats
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
    
    # 计算每种活动类型的统计信息
    activity_type_counts = db.session.query(
            Activity.activity_type, func.count(Activity.id).label('count')
        ) \
        .group_by(Activity.activity_type) \
        .all()
    
    activity_type_distribution = {
        activity_type: count
        for activity_type, count in activity_type_counts
    }
    
    # 最活跃的课程
    active_courses = db.session.query(
            Course.id, Course.title, func.count(Activity.id).label('activity_count')
        ) \
        .join(Activity, Activity.course_id == Course.id) \
        .group_by(Course.id) \
        .order_by(func.count(Activity.id).desc()) \
        .limit(5) \
        .all()
    
    active_courses_list = [
        {
            'course_id': course_id,
            'course_title': title,
            'activity_count': count
        }
        for course_id, title, count in active_courses
    ]
    
    return jsonify({
        'status': 'success',
        'user_counts': user_counts,
        'course_counts': course_counts,
        'activity_counts': activity_counts,
        'activity_trend': activity_trend,
        'activity_type_distribution': activity_type_distribution,
        'active_courses': active_courses_list
    })

@api_bp.route('/analytics/student-learning/<int:user_id>', methods=['GET'])
def student_learning_analytics(user_id):
    """获取学生个人学习分析详细数据"""
    user = User.query.get_or_404(user_id)
    
    # 学习时间趋势（过去30天）
    today = datetime.utcnow().date()
    thirty_days_ago = today - timedelta(days=30)
    
    daily_duration = db.session.query(
            func.date(Activity.created_at).label('date'),
            func.sum(Activity.duration).label('duration')
        ) \
        .filter(Activity.user_id == user_id) \
        .filter(func.date(Activity.created_at) >= thirty_days_ago) \
        .group_by(func.date(Activity.created_at)) \
        .order_by(func.date(Activity.created_at)) \
        .all()
    
    learning_time_trend = [
        {
            'date': date.isoformat(),
            'duration': duration if duration else 0
        }
        for date, duration in daily_duration
    ]
    
    # 获取学习活动类型分布
    activity_types = db.session.query(
            Activity.activity_type, func.count(Activity.id).label('count')
        ) \
        .filter(Activity.user_id == user_id) \
        .group_by(Activity.activity_type) \
        .all()
    
    activity_type_distribution = {
        activity_type: count
        for activity_type, count in activity_types
    }
    
    # 获取学生得分与平均得分对比
    courses = user.enrolled_courses.all()
    
    score_comparisons = []
    for course in courses:
        # 学生在该课程的平均得分
        student_avg_score = db.session.query(func.avg(Activity.score)) \
            .filter(Activity.user_id == user_id, Activity.course_id == course.id) \
            .scalar() or 0
        
        # 全课程平均得分
        course_avg_score = db.session.query(func.avg(Activity.score)) \
            .filter(Activity.course_id == course.id) \
            .scalar() or 0
        
        score_comparisons.append({
            'course_id': course.id,
            'course_title': course.title,
            'student_avg_score': student_avg_score,
            'course_avg_score': course_avg_score
        })
    
    # 学习强度分析（每天各时段的学习活动分布）
    hourly_activity = db.session.query(
            func.extract('hour', Activity.created_at).label('hour'),
            func.count(Activity.id).label('count')
        ) \
        .filter(Activity.user_id == user_id) \
        .group_by(func.extract('hour', Activity.created_at)) \
        .order_by(func.extract('hour', Activity.created_at)) \
        .all()
    
    hourly_distribution = {
        int(hour): count
        for hour, count in hourly_activity
    }
    
    # 填充缺失的小时
    for hour in range(24):
        if hour not in hourly_distribution:
            hourly_distribution[hour] = 0
    
    # 学习行为分析（学习持续时间分布）
    duration_distribution = {
        "0-15分钟": 0,
        "16-30分钟": 0,
        "31-60分钟": 0,
        "1-2小时": 0,
        "2小时以上": 0
    }
    
    activities = Activity.query.filter(Activity.user_id == user_id).all()
    
    for activity in activities:
        duration_minutes = (activity.duration or 0) / 60
        
        if duration_minutes <= 15:
            duration_distribution["0-15分钟"] += 1
        elif duration_minutes <= 30:
            duration_distribution["16-30分钟"] += 1
        elif duration_minutes <= 60:
            duration_distribution["31-60分钟"] += 1
        elif duration_minutes <= 120:
            duration_distribution["1-2小时"] += 1
        else:
            duration_distribution["2小时以上"] += 1
    
    # 获取未完成作业
    from ..models import Assignment, AssignmentSubmission

    now = datetime.utcnow()
    courses_ids = [course.id for course in courses]
    
    pending_assignments = Assignment.query \
        .filter(Assignment.course_id.in_(courses_ids), Assignment.deadline >= now) \
        .outerjoin(AssignmentSubmission, and_(
            AssignmentSubmission.assignment_id == Assignment.id,
            AssignmentSubmission.user_id == user_id
        )) \
        .filter(AssignmentSubmission.id == None) \
        .order_by(Assignment.deadline.asc()) \
        .limit(5) \
        .all()
    
    pending_assignments_list = [
        {
            'id': assignment.id,
            'title': assignment.title,
            'course_id': assignment.course_id,
            'course_title': Course.query.get(assignment.course_id).title,
            'due_date': assignment.deadline.isoformat() if assignment.deadline else None
        }
        for assignment in pending_assignments
    ]
    
    return jsonify({
        'status': 'success',
        'user_id': user_id,
        'learning_time_trend': learning_time_trend,
        'activity_type_distribution': activity_type_distribution,
        'score_comparisons': score_comparisons,
        'hourly_distribution': hourly_distribution,
        'duration_distribution': duration_distribution,
        'pending_assignments': pending_assignments_list
    })

@api_bp.route('/analytics/class-performance/<int:course_id>', methods=['GET'])
def class_performance_analytics(course_id):
    """获取班级整体表现分析"""
    course = Course.query.get_or_404(course_id)
    
    # 获取所有学生的进度数据
    students = course.students.all()
    progress_data = []
    
    for student in students:
        # 查询学生在该课程的课程进度
        progress = CourseProgress.query \
            .filter(CourseProgress.user_id == student.id, CourseProgress.course_id == course_id) \
            .first()
            
        # 查询学生在该课程的平均得分
        avg_score = db.session.query(func.avg(Activity.score)) \
            .filter(Activity.user_id == student.id, Activity.course_id == course_id) \
            .scalar() or 0
            
        # 查询学生在该课程的活动数量
        activity_count = Activity.query \
            .filter(Activity.user_id == student.id, Activity.course_id == course_id) \
            .count()
            
        # 查询学生在该课程的完成活动数量
        completed_activity_count = Activity.query \
            .filter(Activity.user_id == student.id, Activity.course_id == course_id, Activity.completed == True) \
            .count()
        
        # 计算完成率
        if activity_count > 0:
            completion_rate = (completed_activity_count / activity_count) * 100
        else:
            completion_rate = 0
            
        progress_data.append({
            'user_id': student.id,
            'username': student.username,
            'progress_percent': progress.progress_percent if progress else 0,
            'avg_score': avg_score,
            'activity_count': activity_count,
            'completion_rate': completion_rate
        })
    
    # 统计完成率分布
    if progress_data:
        completion_rates = [p['completion_rate'] for p in progress_data]
        
        completion_stats = {
            'avg': sum(completion_rates) / len(completion_rates) if completion_rates else 0,
            'min': min(completion_rates) if completion_rates else 0,
            'max': max(completion_rates) if completion_rates else 0,
            'median': statistics.median(completion_rates) if completion_rates else 0
        }
        
        # 构建完成率分布直方图
        completion_distribution = {
            "0-20%": 0,
            "21-40%": 0,
            "41-60%": 0,
            "61-80%": 0,
            "81-100%": 0
        }
        
        for rate in completion_rates:
            if rate <= 20:
                completion_distribution["0-20%"] += 1
            elif rate <= 40:
                completion_distribution["21-40%"] += 1
            elif rate <= 60:
                completion_distribution["41-60%"] += 1
            elif rate <= 80:
                completion_distribution["61-80%"] += 1
            else:
                completion_distribution["81-100%"] += 1
    else:
        completion_stats = {
            'avg': 0,
            'min': 0,
            'max': 0,
            'median': 0
        }
        completion_distribution = {
            "0-20%": 0,
            "21-40%": 0,
            "41-60%": 0,
            "61-80%": 0,
            "81-100%": 0
        }
    
    # 统计平均分分布
    if progress_data:
        avg_scores = [p['avg_score'] for p in progress_data]
        
        score_stats = {
            'avg': sum(avg_scores) / len(avg_scores) if avg_scores else 0,
            'min': min(avg_scores) if avg_scores else 0,
            'max': max(avg_scores) if avg_scores else 0,
            'median': statistics.median(avg_scores) if avg_scores else 0
        }
        
        # 构建平均分分布直方图
        score_distribution = {
            "0-20分": 0,
            "21-40分": 0,
            "41-60分": 0,
            "61-80分": 0,
            "81-100分": 0
        }
        
        for score in avg_scores:
            if score <= 20:
                score_distribution["0-20分"] += 1
            elif score <= 40:
                score_distribution["21-40分"] += 1
            elif score <= 60:
                score_distribution["41-60分"] += 1
            elif score <= 80:
                score_distribution["61-80分"] += 1
            else:
                score_distribution["81-100分"] += 1
    else:
        score_stats = {
            'avg': 0,
            'min': 0,
            'max': 0,
            'median': 0
        }
        score_distribution = {
            "0-20分": 0,
            "21-40分": 0,
            "41-60分": 0,
            "61-80分": 0,
            "81-100分": 0
        }
    
    # 学生参与度排名（基于活动数量）
    engagement_ranking = sorted(progress_data, key=lambda x: x['activity_count'], reverse=True)[:10]
    
    # 学生成绩排名（基于平均分）
    performance_ranking = sorted(progress_data, key=lambda x: x['avg_score'], reverse=True)[:10]
    
    return jsonify({
        'status': 'success',
        'course_id': course_id,
        'student_count': len(students),
        'progress_data': progress_data,
        'completion_stats': completion_stats,
        'completion_distribution': completion_distribution,
        'score_stats': score_stats,
        'score_distribution': score_distribution,
        'engagement_ranking': engagement_ranking,
        'performance_ranking': performance_ranking
    }) 