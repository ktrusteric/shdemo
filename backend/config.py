import os
from datetime import timedelta

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'energy-trading-system-secret-key-2024'
    
    # 数据库配置 - 使用MySQL（远程访问）
    MYSQL_HOST = '14.103.245.50'  # 远程数据库地址
    MYSQL_PORT = 3306              # 默认端口
    MYSQL_USER = 'root'            # 替换为实际的用户名
    MYSQL_PASSWORD = 'welcome1'    # 替换为实际的密码
    MYSQL_DB = 'shdemo'            # 连接新建的数据库
    
    # SQLAlchemy配置
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_timeout': 30,
        'max_overflow': 20
    }
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-2024'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # CORS配置
    CORS_ORIGINS = ['*']
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx'}
    
    # AI助手配置
    AI_BOT_CONFIG = {
        'customer_service': {
            'id': '9714d9bc-31ca-40b5-a720-4329f5fc4af7',
            'token': 'e0dc8833077b48669a04ad4a70a7ebe2',
            'url': 'https://ai.wiseocean.cn/bot/#/9714d9bc-31ca-40b5-a720-4329f5fc4af7/e0dc8833077b48669a04ad4a70a7ebe2?botSource=1'
        },
        'news': {
            'id': '158ab70e-2996-4cce-9822-6f8195a7cfa5',
            'token': '9bc6008decb94efeaee65dd076aab5e8',
            'url': 'https://ai.wiseocean.cn/bot/#/158ab70e-2996-4cce-9822-6f8195a7cfa5/9bc6008decb94efeaee65dd076aab5e8?botSource=1'
        },
        'trading': {
            'id': '1e72acc1-43a8-4cda-8d54-f409c9c5d5ed',
            'token': '18703d14357040c88f32ae5e4122c2d6',
            'url': 'https://ai.wiseocean.cn/bot/#/1e72acc1-43a8-4cda-8d54-f409c9c5d5ed/18703d14357040c88f32ae5e4122c2d6?botSource=1'
        }
    }
    
    # 系统用户标签
    SYSTEM_USERS = [
        "中国石化天然气分公司华南天然气销售中心",
        "华港燃气集团有限公司"
    ]
    
    # 交易品种
    TRADING_PRODUCTS = [
        "管道天然气",
        "液化天然气(LNG)",
        "压缩天然气(CNG)",
        "天然气期货",
        "天然气现货"
    ]
    
    # 地区列表
    REGIONS = [
        "北京", "上海", "广州", "深圳", "天津", "重庆",
        "江苏", "浙江", "广东", "山东", "河北", "河南",
        "湖北", "湖南", "四川", "福建", "安徽", "江西"
    ]

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    
class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 