from app import create_app, db
from app.models import Course, User

def check_courses():
    print("检查课程和学生关联数据...")
    app = create_app('development')
    with app.app_context():
        # 查询所有课程
        courses = Course.query.all()
        print(f"课程总数: {len(courses)}")
        
        if not courses:
            print("数据库中没有课程数据！")
            return
        
        # 显示每个课程的基本信息和学生数量
        print("\n课程信息:")
        for course in courses:
            student_count = course.students.count()
            print(f"  - 课程ID: {course.id}, 名称: {course.title}, 状态: {course.status}, 学生数: {student_count}")
            
            # 如果有学生，显示学生信息
            if student_count > 0:
                students = course.students.all()
                print("    注册学生:")
                for student in students:
                    print(f"      * {student.username} (ID: {student.id})")
        
        # 检查有多少学生没有注册任何课程
        students = User.query.filter_by(role='student').all()
        unregistered_students = []
        for student in students:
            courses = student.enrolled_courses.all()
            if not courses:
                unregistered_students.append(student)
        
        print(f"\n未注册任何课程的学生: {len(unregistered_students)} / {len(students)}")
        for student in unregistered_students:
            print(f"  - {student.username} (ID: {student.id})")

if __name__ == '__main__':
    check_courses() 