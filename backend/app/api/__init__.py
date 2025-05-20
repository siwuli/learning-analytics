from flask import Blueprint

api_bp = Blueprint('api', __name__)
 
# 导入视图
from . import auth, users, courses, activities, analytics, resources, progress, reviews, assignments, discussions