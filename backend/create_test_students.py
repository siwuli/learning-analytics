from app import create_app, db
from app.models import Course, User
import random

def create_test_students():
    print("添加测试学生到课程...")
    app = create_app('development')
    with app.app_context():
        # 获取所有课程
        courses = Course.query.all()
        
        if not courses:
            print("没有找到任何课程，请先创建课程")
            return False
            
        # 获取所有学生
        students = User.query.filter_by(role='student').all()
        
        if not students:
            print("没有找到学生，请先创建用户")
            return False
        
        # 为每个课程添加随机学生
        for course in courses:
            print(f"为课程 '{course.title}' 添加学生...")
            
            # 随机选择5-15名学生
            num_students = min(len(students), random.randint(5, 15))
            selected_students = random.sample(students, num_students)
            
            # 添加学生到课程
            for student in selected_students:
                if student not in course.students:
                    course.students.append(student)
                    print(f"  添加学生: {student.username}")
            
            db.session.commit()
            print(f"  为课程 '{course.title}' 添加了 {num_students} 名学生")
        
        print("测试学生添加完成！")
        return True

if __name__ == '__main__':
    create_test_students() 