import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from bson import ObjectId
from config import Config

def hash_password(password):
    """密码加密"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password, hashed):
    """验证密码"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def generate_token(user_id, username):
    """生成JWT令牌"""
    payload = {
        'user_id': str(user_id),
        'username': username,
        'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

def decode_token(token):
    """解码JWT令牌"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token已过期'}
    except jwt.InvalidTokenError:
        return {'error': '无效的Token'}

def login_required(f):
    """需要登录的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # 从请求头获取token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': '无效的认证头格式'}), 401
        
        if not token:
            return jsonify({'error': '缺少认证令牌'}), 401
        
        # 解码token
        payload = decode_token(token)
        if 'error' in payload:
            return jsonify(payload), 401
        
        # 将用户信息添加到请求上下文
        request.current_user = {
            'user_id': payload['user_id'],
            'username': payload['username']
        }
        
        return f(*args, **kwargs)
    
    return decorated_function

def paid_user_required(f):
    """需要付费用户权限的装饰器"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        from utils.database import db
        
        # 获取用户信息
        user_id = request.current_user['user_id']
        users_collection = db.get_collection('users')
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        if user.get('user_type') != 'paid':
            return jsonify({'error': '此功能仅对付费用户开放'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function 