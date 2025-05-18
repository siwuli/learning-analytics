from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    """应用工厂函数"""
    from config import config

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    
    # 启用CORS
    CORS(app)

    # 注册蓝图
    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/health')
    def health_check():
        return {'status': 'ok'}

    return app

# 确保导出这些变量
__all__ = ['db', 'migrate', 'create_app'] 