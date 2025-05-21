from app import create_app, db
from app.models import User, Course, Activity, CourseSection, CourseResource
from datetime import datetime, timedelta
import random

def create_test_activities():
    print("创建测试学习活动数据...")
    app = create_app('development')
    with app.app_context():
        # 获取所有学生和课程
        students = User.query.filter_by(role='student').all()
        courses = Course.query.all()
        
        if not students:
            print("没有找到学生用户，请先创建学生用户")
            return False
            
        if not courses:
            print("没有找到课程，请先创建课程")
            return False
        
        # 获取资源
        resources = CourseResource.query.all()
        if not resources:
            print("没有找到课程资源，请先创建课程资源")
            return False
        
        # 删除现有活动数据(用于测试)
        Activity.query.delete()
        db.session.commit()
        print("已清除旧的活动数据")
        
        # 活动类型定义
        activity_types = ['video_watch', 'document_read', 'quiz', 'assignment', 'discussion']
        
        # 为每个学生创建活动数据
        total_activities = 0
        now = datetime.utcnow()
        
        # 为每个课程创建一些资源
        course_resources = {}
        for course in courses:
            # 检查该课程是否有对应的章节
            sections = CourseSection.query.filter_by(course_id=course.id).all()
            
            # 如果没有章节，创建一个默认章节
            if not sections:
                print(f"为课程 {course.title} 创建默认章节和资源")
                default_section = CourseSection(
                    course_id=course.id,
                    title=f"{course.title} - 默认章节",
                    description="自动创建的默认章节",
                    order=1
                )
                db.session.add(default_section)
                db.session.flush()  # 获取ID
                
                # 为默认章节创建几个资源
                for i, res_type in enumerate(['document', 'video', 'quiz', 'assignment']):
                    resource = CourseResource(
                        section_id=default_section.id,
                        title=f"{res_type.capitalize()} 资源 {i+1}",
                        description=f"{course.title} 的 {res_type} 资源",
                        resource_type=res_type,
                        content=f"测试内容 {i+1}",
                        order=i+1
                    )
                    db.session.add(resource)
                
                db.session.commit()
                
                # 重新获取章节
                sections = [default_section]
            
            # 获取该课程所有章节下的资源
            course_res = []
            for section in sections:
                section_resources = CourseResource.query.filter_by(section_id=section.id).all()
                course_res.extend(section_resources)
            
            if course_res:
                course_resources[course.id] = course_res
            else:
                print(f"警告: 课程 {course.title} (ID: {course.id}) 没有找到资源")
        
        for student in students:
            # 确定该学生已注册的课程
            enrolled_courses = student.enrolled_courses.all()
            if not enrolled_courses:
                # 如果学生没有注册课程，随机注册1-3个课程
                sample_size = min(len(courses), random.randint(1, 3))
                enrolled_courses = random.sample(courses, sample_size)
                for course in enrolled_courses:
                    course.students.append(student)
                db.session.commit()
                print(f"为学生 {student.username} 随机注册了 {len(enrolled_courses)} 个课程")
            
            # 为每个已注册的课程创建活动
            for course in enrolled_courses:
                # 跳过没有资源的课程
                if course.id not in course_resources or not course_resources[course.id]:
                    print(f"跳过没有资源的课程: {course.title} (ID: {course.id})")
                    continue
                
                course_resources_list = course_resources[course.id]
                
                # 为每个学生在每个课程中创建3-10个活动
                activity_count = random.randint(3, 10)
                
                for _ in range(activity_count):
                    # 随机选择活动类型
                    activity_type = random.choice(activity_types)
                    
                    # 随机选择资源
                    resource = random.choice(course_resources_list)
                    
                    # 创建随机时间(过去30天内)
                    random_days = random.randint(0, 30)
                    random_hours = random.randint(0, 23)
                    random_minutes = random.randint(0, 59)
                    activity_time = now - timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
                    
                    # 根据活动类型设置活动属性
                    duration = None
                    score = None
                    completed = random.choice([True, False])
                    
                    if activity_type == 'video_watch':
                        duration = random.randint(60, 3600)  # 1分钟到1小时
                    elif activity_type == 'document_read':
                        duration = random.randint(300, 1800)  # 5分钟到30分钟
                    elif activity_type == 'quiz':
                        duration = random.randint(300, 1200)  # 5分钟到20分钟
                        if completed:
                            score = random.randint(60, 100)
                    elif activity_type == 'assignment':
                        duration = random.randint(1800, 7200)  # 30分钟到2小时
                        if completed:
                            score = random.randint(70, 100)
                    elif activity_type == 'discussion':
                        duration = random.randint(300, 1200)  # 5分钟到20分钟
                    
                    # 创建活动记录
                    activity = Activity(
                        user_id=student.id,
                        course_id=course.id,
                        activity_type=activity_type,
                        resource_id=str(resource.id),
                        duration=duration,
                        score=score,
                        completed=completed,
                        created_at=activity_time,
                        updated_at=activity_time
                    )
                    
                    db.session.add(activity)
                    total_activities += 1
                    
                    # 每添加50条记录提交一次，减少内存使用
                    if total_activities % 50 == 0:
                        db.session.commit()
                        print(f"已创建 {total_activities} 条活动记录...")
        
        # 最终提交
        db.session.commit()
        print(f"测试活动数据创建完成，共创建了 {total_activities} 条活动记录")
        return True

if __name__ == '__main__':
    create_test_activities() 