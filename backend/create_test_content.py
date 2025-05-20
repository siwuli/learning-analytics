from app import create_app, db
from app.models import Course, CourseSection, CourseResource

app = create_app()

with app.app_context():
    # 检查课程是否存在
    course = Course.query.first()
    if not course:
        print("没有找到课程，请先创建课程")
    else:
        print(f"为课程 '{course.title}' 添加章节和资源")
        
        # 删除现有章节和资源（用于测试）
        CourseResource.query.filter(
            CourseResource.section_id.in_(
                CourseSection.query.filter_by(course_id=course.id).with_entities(CourseSection.id)
            )
        ).delete(synchronize_session=False)
        CourseSection.query.filter_by(course_id=course.id).delete()
        
        # 创建章节
        sections = [
            {
                'title': '第一章：课程介绍',
                'description': '本章介绍课程的基本内容和学习目标',
                'order': 1,
                'resources': [
                    {
                        'title': '课程大纲',
                        'description': '详细介绍课程的内容与安排',
                        'resource_type': 'document',
                        'content': '# 课程大纲\n\n## 学习目标\n- 理解基本概念\n- 掌握核心技能\n- 应用到实际场景',
                        'order': 1
                    },
                    {
                        'title': '课程导览视频',
                        'description': '5分钟视频介绍课程内容',
                        'resource_type': 'video',
                        'content': 'https://example.com/intro-video.mp4',
                        'order': 2
                    }
                ]
            },
            {
                'title': '第二章：基础知识',
                'description': '学习本课程所需的基础理论',
                'order': 2,
                'resources': [
                    {
                        'title': '基础理论文档',
                        'description': '基础理论详解',
                        'resource_type': 'document',
                        'content': '# 基础理论\n\n## 核心概念\n- 概念A\n- 概念B\n- 概念C\n\n## 应用场景\n...',
                        'order': 1
                    },
                    {
                        'title': '基础知识测试',
                        'description': '检验基础知识掌握情况',
                        'resource_type': 'quiz',
                        'content': '{"questions":[{"question":"问题1","options":["选项A","选项B","选项C"],"answer":0}]}',
                        'order': 2
                    }
                ]
            },
            {
                'title': '第三章：实践应用',
                'description': '将理论知识应用到实际场景',
                'order': 3,
                'resources': [
                    {
                        'title': '实践案例',
                        'description': '案例分析',
                        'resource_type': 'document',
                        'content': '# 实践案例\n\n## 案例1\n...\n\n## 案例2\n...',
                        'order': 1
                    },
                    {
                        'title': '作业1',
                        'description': '完成实践作业',
                        'resource_type': 'assignment',
                        'content': '{"title":"实践作业","description":"根据所学知识，完成...","due_date":"2025-06-01"}',
                        'order': 2
                    }
                ]
            }
        ]
        
        # 添加章节和资源
        for section_data in sections:
            section = CourseSection(
                course_id=course.id,
                title=section_data['title'],
                description=section_data['description'],
                order=section_data['order']
            )
            db.session.add(section)
            db.session.flush()  # 获取ID
            
            # 添加资源
            for resource_data in section_data['resources']:
                resource = CourseResource(
                    section_id=section.id,
                    title=resource_data['title'],
                    description=resource_data['description'],
                    resource_type=resource_data['resource_type'],
                    content=resource_data['content'],
                    order=resource_data['order']
                )
                db.session.add(resource)
        
        db.session.commit()
        print("添加章节和资源完成") 