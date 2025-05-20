from app import create_app, db
from app.models import User, Course
from datetime import datetime, timedelta
import random
import string

def create_test_data():
    print("创建测试数据...")
    app = create_app('development')
    with app.app_context():
        # 创建教师账号
        teachers = [
            {
                'username': '张教授',
                'email': 'zhang@example.com',
                'password_hash': 'pbkdf2:sha256:600000$pWS9hKLl$cffce16dc4db3a5aa24cbc0c9f3fa63f431f3fc8e869fcaaee70139ab9a61d29',  # 密码: password
                'role': 'teacher'
            },
            {
                'username': '李老师',
                'email': 'li@example.com',
                'password_hash': 'pbkdf2:sha256:600000$pWS9hKLl$cffce16dc4db3a5aa24cbc0c9f3fa63f431f3fc8e869fcaaee70139ab9a61d29',  # 密码: password
                'role': 'teacher'
            },
            {
                'username': '王教授',
                'email': 'wang@example.com',
                'password_hash': 'pbkdf2:sha256:600000$pWS9hKLl$cffce16dc4db3a5aa24cbc0c9f3fa63f431f3fc8e869fcaaee70139ab9a61d29',  # 密码: password
                'role': 'teacher'
            }
        ]
        
        created_teachers = []
        for teacher_data in teachers:
            existing_user = User.query.filter_by(email=teacher_data['email']).first()
            if not existing_user:
                teacher = User(**teacher_data)
                db.session.add(teacher)
                db.session.commit()
                created_teachers.append(teacher)
                print(f"创建教师: {teacher.username}")
            else:
                created_teachers.append(existing_user)
                print(f"教师 {existing_user.username} 已存在")
        
        # 创建课程
        courses = [
            {
                'title': '数据结构与算法',
                'description': '本课程介绍常用的数据结构和算法，包括数组、链表、栈、队列、树、图等，以及排序、搜索等算法。',
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=120),
                'status': 'active'
            },
            {
                'title': '机器学习基础',
                'description': '本课程介绍机器学习的基本概念、算法和应用，包括监督学习、无监督学习和强化学习等。',
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=90),
                'status': 'active'
            },
            {
                'title': '数据库系统原理',
                'description': '本课程介绍数据库系统的基本原理、设计方法和应用技术，包括关系数据库、SQL语言、数据库设计等。',
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=100),
                'status': 'active'
            },
            {
                'title': '计算机网络',
                'description': '本课程介绍计算机网络的基本概念、体系结构和协议，包括TCP/IP协议族、网络安全等内容。',
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=110),
                'status': 'active'
            },
            {
                'title': '人工智能导论',
                'description': '本课程介绍人工智能的基本概念、发展历史和应用领域，包括知识表示、搜索算法、机器学习等内容。',
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=85),
                'status': 'active'
            }
        ]
        
        # 分配课程给教师
        for i, course_data in enumerate(courses):
            teacher = created_teachers[i % len(created_teachers)]
            course_data['instructor_id'] = teacher.id
            
            existing_course = Course.query.filter_by(title=course_data['title']).first()
            if not existing_course:
                course = Course(**course_data)
                db.session.add(course)
                db.session.commit()
                print(f"创建课程: {course.title}, 教师: {teacher.username}")
            else:
                print(f"课程 {course_data['title']} 已存在")
                
        # 创建学生账号 (如果没有足够的学生)
        student_count = User.query.filter_by(role='student').count()
        if student_count < 10:
            needed_students = 10 - student_count
            print(f"创建 {needed_students} 个学生账号")
            
            for i in range(needed_students):
                username = f"学生_{random_string(4)}"
                email = f"student_{random_string(6)}@example.com"
                
                existing_user = User.query.filter_by(email=email).first()
                if not existing_user:
                    student = User(
                        username=username,
                        email=email,
                        password_hash='pbkdf2:sha256:600000$pWS9hKLl$cffce16dc4db3a5aa24cbc0c9f3fa63f431f3fc8e869fcaaee70139ab9a61d29',  # 密码: password
                        role='student'
                    )
                    db.session.add(student)
                    db.session.commit()
                    print(f"创建学生: {username}")
        
        print("测试数据创建完成！")


def random_string(length):
    """生成随机字符串"""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


if __name__ == '__main__':
    create_test_data() 