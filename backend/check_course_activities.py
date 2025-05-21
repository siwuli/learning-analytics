from app import create_app, db
from app.models import Activity, User, Course

def check_course_activities():
    print("检查每个课程的活动数据...")
    app = create_app('development')
    with app.app_context():
        # 查询活动总数
        activity_count = Activity.query.count()
        print(f"活动数据总数: {activity_count}")
        
        if activity_count == 0:
            print("数据库中没有活动数据！")
            return
        
        # 查询活动类型分布
        print("\n活动类型分布:")
        activity_types = {}
        for activity in Activity.query.all():
            activity_type = activity.activity_type
            if activity_type in activity_types:
                activity_types[activity_type] += 1
            else:
                activity_types[activity_type] = 1
        
        for activity_type, count in activity_types.items():
            print(f"  - {activity_type}: {count}条记录")
        
        # 查询每个课程的活动数
        print("\n每个课程的活动数:")
        courses = Course.query.all()
        for course in courses:
            course_activity_count = Activity.query.filter_by(course_id=course.id).count()
            print(f"  - 课程 {course.title} (ID: {course.id}): {course_activity_count}条活动记录")
            
            # 查询该课程的活动类型分布
            if course_activity_count > 0:
                course_activity_types = {}
                for activity in Activity.query.filter_by(course_id=course.id).all():
                    activity_type = activity.activity_type
                    if activity_type in course_activity_types:
                        course_activity_types[activity_type] += 1
                    else:
                        course_activity_types[activity_type] = 1
                
                print("    活动类型分布:")
                for activity_type, count in course_activity_types.items():
                    print(f"      * {activity_type}: {count}条记录")
                
                # 查询该课程有多少学生有活动记录
                user_ids = db.session.query(Activity.user_id) \
                    .filter(Activity.course_id == course.id) \
                    .distinct() \
                    .all()
                active_users = [user_id[0] for user_id in user_ids]
                
                print(f"    活跃学生数: {len(active_users)}")
                
                # 显示每个学生的活动数量
                for user_id in active_users:
                    user = User.query.get(user_id)
                    user_activity_count = Activity.query \
                        .filter_by(course_id=course.id, user_id=user_id) \
                        .count()
                    print(f"      * {user.username} (ID: {user_id}): {user_activity_count}条活动记录")
        
        # 检查API返回数据
        print("\n检查课程分析API数据:")
        # 检查第一个课程的分析数据
        course = Course.query.first()
        if course:
            # 获取课程的总学生数
            student_count = course.students.count()
            print(f"  课程 {course.title} 学生数: {student_count}")
            
            # 获取课程的平均完成率
            course_activities = Activity.query.filter(Activity.course_id == course.id).all()
            if course_activities:
                completion_rate = (sum(1 for act in course_activities if act.completed) / len(course_activities)) * 100
                print(f"  完成率: {completion_rate:.2f}%")
            else:
                print("  无活动数据")

if __name__ == '__main__':
    check_course_activities() 