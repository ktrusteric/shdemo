import os
import sys
import logging
from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS
from datetime import datetime

# 添加项目路径到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from utils.database import db, init_database, get_database_status

# 导入API路由
from api.auth_api import auth_bp
from api.user_api import user_bp
from api.energy_api import energy_bp
from api.recommendation_api import recommendation_bp

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 启用CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # 初始化数据库
    if init_database(app):
        logger.info("数据库初始化成功")
    else:
        logger.error("数据库初始化失败")
    
    # 创建上传目录
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        logger.info(f"创建上传目录: {upload_folder}")
    
    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(energy_bp, url_prefix='/api/energy')
    app.register_blueprint(recommendation_bp, url_prefix='/api/recommendation')
    
    # 静态文件服务
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    
    # 根路由 - 提供首页
    @app.route('/')
    def index():
        try:
            return send_file(os.path.join(frontend_path, 'index.html'))
        except:
            return jsonify({
                'name': '能源交易一体化系统',
                'version': '1.0.0',
                'status': 'running',
                'time': datetime.now().isoformat()
            })
    
    # 静态文件路由
    @app.route('/<path:filename>')
    def static_files(filename):
        try:
            return send_from_directory(frontend_path, filename)
        except:
            return jsonify({'error': '文件不存在'}), 404
    
    # 健康检查
    @app.route('/health')
    def health_check():
        db_status = get_database_status()
        return jsonify({
            'status': 'healthy' if db_status['connected'] else 'unhealthy',
            'database': 'connected' if db_status['connected'] else 'disconnected',
            'database_info': db_status.get('info', {}),
            'time': datetime.now().isoformat()
        })
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': '资源不存在'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"内部服务器错误: {error}")
        return jsonify({'error': '服务器内部错误'}), 500
    
    return app

if __name__ == '__main__':
    # 获取环境变量
    env = os.environ.get('FLASK_ENV', 'development')
    
    # 创建应用
    app = create_app(env)
    
    # 运行应用
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(env == 'development'))
    
    # 应用关闭时的清理工作
    logger.info("应用关闭") 