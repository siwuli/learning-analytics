from flask import Blueprint

api_bp = Blueprint('api', __name__)

# 导入视图
from . import users, courses, activities, analytics 