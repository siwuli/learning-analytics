from app import create_app, db
from app.models import Course, User, Assignment, AssignmentSubmission
from datetime import datetime, timedelta
import random

def create_test_assignments():
    print("创建测试作业数据...")
    app = create_app('development')
    with app.app_context():
        # 获取所有课程
        courses = Course.query.all()
        
        if not courses:
            print("没有找到任何课程，请先创建课程")
            return False
            
        # 获取所有教师和学生
        teachers = User.query.filter_by(role='teacher').all()
        students = User.query.filter_by(role='student').all()
        
        if not teachers or not students:
            print("没有找到教师或学生，请先创建用户")
            return False
            
        # 为每个课程创建作业
        for course in courses:
            print(f"为课程 '{course.title}' 创建作业...")
            
            # 创建3个不同类型的作业
            assignments = [
                Assignment(
                    course_id=course.id,
                    title="第一周作业：课程介绍与基础知识",
                    description="请阅读课程第一章并回答以下问题：\n1. 什么是学习分析？\n2. 学习分析的主要应用场景有哪些？\n3. 描述一个你感兴趣的学习分析应用案例。",
                    deadline=datetime.utcnow() + timedelta(days=7),
                    points=10
                ),
                Assignment(
                    course_id=course.id,
                    title="第二周作业：数据收集与清洗",
                    description="本次作业要求：\n1. 从提供的学习系统中导出学生行为数据\n2. 使用Python进行数据清洗\n3. 生成基础的描述性统计报告\n4. 将分析过程和结果整理成报告提交",
                    deadline=datetime.utcnow() + timedelta(days=14),
                    points=15
                ),
                Assignment(
                    course_id=course.id,
                    title="期末项目：学习行为分析",
                    description="期末项目要求学生完成一个完整的学习分析案例。\n\n要求包括：\n- 确定分析问题\n- 收集相关数据\n- 进行数据处理与分析\n- 形成可视化报告\n- 提出改进建议\n\n提交内容：分析报告和演示文稿",
                    deadline=datetime.utcnow() + timedelta(days=30),
                    points=30
                )
            ]
            
            db.session.add_all(assignments)
            db.session.commit()
            
            # 为学生随机创建一些提交
            for assignment in assignments:
                print(f"  创建作业 '{assignment.title}' 的提交...")
                
                # 随机选择部分学生已完成作业
                submitting_students = random.sample(students, k=random.randint(1, len(students)))
                
                for student in submitting_students:
                    submission = AssignmentSubmission(
                        assignment_id=assignment.id,
                        user_id=student.id,
                        content=f"这是{student.username}提交的作业内容。我已经完成了所有要求的任务，包括阅读材料和回答问题。",
                        submit_time=datetime.utcnow() - timedelta(days=random.randint(0, 5))
                    )
                    db.session.add(submission)
                    
                    # 随机为部分提交评分
                    if random.choice([True, False]):
                        submission.grade = random.randint(int(assignment.points * 0.6), assignment.points)
                        submission.feedback = "作业完成得不错，继续努力！" if submission.grade > assignment.points * 0.8 else "作业中有一些概念理解不够准确，请复习相关内容。"
                        submission.graded_by = random.choice(teachers).id
                        submission.graded_at = datetime.utcnow()
            
            db.session.commit()
        
        print("测试作业数据创建完成！")
        return True

if __name__ == '__main__':
    create_test_assignments() 