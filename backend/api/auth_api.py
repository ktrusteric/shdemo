from flask import Blueprint, request, jsonify
from services.user_service import UserService
from config import Config
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)
user_service = UserService()

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['username', 'password', 'email', 'region', 'trading_products']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400
        
        # 验证地区
        if data['region'] not in Config.REGIONS:
            return jsonify({'error': '无效的地区'}), 400
        
        # 验证交易品种
        for product in data['trading_products']:
            if product not in Config.TRADING_PRODUCTS:
                return jsonify({'error': f'无效的交易品种: {product}'}), 400
        
        # 注册用户
        result = user_service.register_user(
            username=data['username'],
            password=data['password'],
            email=data['email'],
            region=data['region'],
            trading_products=data['trading_products'],
            company_name=data.get('company_name')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"注册接口错误: {e}")
        return jsonify({'error': '服务器错误'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': '用户名和密码不能为空'}), 400
        
        # 登录验证
        result = user_service.login_user(
            username=data['username'],
            password=data['password']
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        logger.error(f"登录接口错误: {e}")
        return jsonify({'error': '服务器错误'}), 500

@auth_bp.route('/regions', methods=['GET'])
def get_regions():
    """获取地区列表"""
    return jsonify({
        'regions': Config.REGIONS
    })

@auth_bp.route('/trading-products', methods=['GET'])
def get_trading_products():
    """获取交易品种列表"""
    return jsonify({
        'products': Config.TRADING_PRODUCTS
    })

@auth_bp.route('/system-users', methods=['GET'])
def get_system_users():
    """获取系统用户列表"""
    return jsonify({
        'users': Config.SYSTEM_USERS
    }) 