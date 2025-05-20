from app import create_app, db
from app.models import Course, User, Discussion, DiscussionReply
from datetime import datetime, timedelta
import random

def create_test_discussions():
    print("创建测试讨论数据...")
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
            
        # 讨论话题示例标题
        discussion_titles = [
            "请自我介绍并分享学习目标",
            "第一章内容讨论：基本概念",
            "有关作业的疑问",
            "课程资料下载问题",
            "项目小组组队",
            "期末考试范围讨论",
            "推荐一些学习资源",
            "关于实践项目的提示"
        ]
        
        # 讨论内容示例
        discussion_contents = [
            "大家好，我是本课程的老师。这个讨论区可以用来交流课程相关的问题。希望大家积极参与讨论，相互学习。",
            "请各位同学在此进行自我介绍，分享你的学习背景和对这门课程的期望。",
            "我对第一章中的概念有些疑惑，特别是关于数据分析的部分，有谁能解释一下吗？",
            "请问期中作业的截止日期是否可以延长？我需要更多时间完成。",
            "我无法下载课程资料，系统提示错误。有谁遇到类似问题吗？",
            "有兴趣一起组队完成课程项目的同学请在这里留言。",
            "分享一些我发现的有用资源，希望对大家有帮助。"
        ]
        
        # 回复内容示例
        reply_contents = [
            "谢谢分享，这些信息很有帮助。",
            "我同意你的观点，我也遇到了类似的问题。",
            "我可以帮你解释这个概念。其实很简单，...",
            "我也有这个疑问，希望老师能解答。",
            "已解决，谢谢提醒！",
            "我很感兴趣，我们可以组队。",
            "我有不同的看法，我认为...",
            "这是我找到的一些补充资料：...",
            "非常有趣的讨论，学到了很多。"
        ]
            
        # 为每个课程创建讨论
        for course in courses:
            print(f"为课程 '{course.title}' 创建讨论话题...")
            
            # 获取该课程的学生
            course_students = list(course.students)
            if not course_students:
                print(f"  课程 '{course.title}' 没有学生，跳过创建讨论")
                continue
            
            # 为每个课程创建3-5个讨论话题
            num_discussions = random.randint(3, 5)
            for _ in range(num_discussions):
                # 随机选择创建者（教师或学生）
                is_teacher_topic = random.choice([True, False])
                creator = course.instructor if is_teacher_topic else random.choice(course_students)
                
                # 创建讨论话题
                discussion = Discussion(
                    course_id=course.id,
                    user_id=creator.id,
                    title=random.choice(discussion_titles),
                    content=random.choice(discussion_contents),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                    is_pinned=is_teacher_topic and random.choice([True, False])  # 教师的话题有可能被置顶
                )
                
                db.session.add(discussion)
                db.session.commit()  # 提交以获取讨论ID
                
                print(f"  创建讨论话题: '{discussion.title}'")
                
                # 为讨论创建回复
                num_replies = random.randint(1, 8)
                for _ in range(num_replies):
                    # 随机选择回复者
                    is_teacher_reply = random.choice([True, False])
                    replier = course.instructor if is_teacher_reply else random.choice(course_students)
                    
                    # 创建回复
                    reply = DiscussionReply(
                        discussion_id=discussion.id,
                        user_id=replier.id,
                        content=random.choice(reply_contents),
                        created_at=discussion.created_at + timedelta(hours=random.randint(1, 72))
                    )
                    
                    db.session.add(reply)
            
            db.session.commit()
            print(f"  为课程 '{course.title}' 创建了 {num_discussions} 个讨论话题")
        
        print("测试讨论数据创建完成！")
        return True

if __name__ == '__main__':
    create_test_discussions() 