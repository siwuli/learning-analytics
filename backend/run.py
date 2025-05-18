import os
from backend.app import create_app, db
from backend.app.models import User, Course, Activity

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    """为Flask shell注入上下文"""
    return {
        'db': db,
        'User': User,
        'Course': Course,
        'Activity': Activity
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 