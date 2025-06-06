# 导入所有模型
from .user import User
from .course import Course
from .activity import Activity
from .resource import CourseSection, CourseResource
from .progress import CourseProgress, ResourceProgress
from .feedback import CourseReview
from .assignment import Assignment, AssignmentSubmission
from .discussion import Discussion, DiscussionReply
from .grade import GradeSetting, StudentGrade 