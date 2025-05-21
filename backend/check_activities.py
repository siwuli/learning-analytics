from app import create_app, db
from app.models import Activity, User, Course

def check_activities():
    print("检查学习活动数据...")
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
        
        # 查询每个用户的活动数
        print("\n用户活动数:")
        users = User.query.all()
        for user in users:
            user_activity_count = Activity.query.filter_by(user_id=user.id).count()
            if user_activity_count > 0:
                print(f"  - 用户 {user.username} (ID: {user.id}): {user_activity_count}条活动记录")
        
        # 查询每个课程的活动数
        print("\n课程活动数:")
        courses = Course.query.all()
        for course in courses:
            course_activity_count = Activity.query.filter_by(course_id=course.id).count()
            if course_activity_count > 0:
                print(f"  - 课程 {course.title} (ID: {course.id}): {course_activity_count}条活动记录")
        
        # 查看几条实际活动记录示例
        print("\n活动记录示例:")
        sample_activities = Activity.query.limit(3).all()
        for i, activity in enumerate(sample_activities):
            print(f"\n示例 {i+1}:")
            print(f"  ID: {activity.id}")
            print(f"  用户ID: {activity.user_id}")
            print(f"  课程ID: {activity.course_id}")
            print(f"  活动类型: {activity.activity_type}")
            print(f"  资源ID: {activity.resource_id}")
            print(f"  持续时间: {activity.duration}秒")
            print(f"  得分: {activity.score}")
            print(f"  是否完成: {activity.completed}")
            print(f"  创建时间: {activity.created_at}")
            
if __name__ == '__main__':
    check_activities() 