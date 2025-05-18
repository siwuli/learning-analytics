import os
import sys
from pathlib import Path

# 获取当前文件所在的目录
basedir = os.path.abspath(os.path.dirname(__file__))
# 将 backend 目录添加到 Python 路径
sys.path.insert(0, basedir)

from app import create_app, db, migrate
from app.models import User, Course, Activity

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    """为Flask shell注入上下文"""
    return {
        'db': db,
        'migrate': migrate,
        'User': User,
        'Course': Course,
        'Activity': Activity
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 