from flask import Blueprint, request, jsonify
from services.user_service import UserService
from utils.auth import login_required
import logging

logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__)
user_service = UserService()

@user_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """获取用户个人信息"""
    try:
        user_id = request.current_user['user_id']
        result = user_service.get_user_info(user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"获取用户信息错误: {e}")
        return jsonify({'error': '服务器错误'}), 500

@user_bp.route('/upgrade', methods=['POST'])
@login_required
def upgrade_to_paid():
    """升级为付费用户"""
    try:
        user_id = request.current_user['user_id']
        result = user_service.upgrade_user_to_paid(user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"用户升级错误: {e}")
        return jsonify({'error': '服务器错误'}), 500

@user_bp.route('/behavior', methods=['POST'])
@login_required
def record_behavior():
    """记录用户行为"""
    try:
        user_id = request.current_user['user_id']
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('behavior_type') or not data.get('details'):
            return jsonify({'error': '缺少必填字段'}), 400
        
        # 记录行为
        result = user_service.record_user_behavior(
            user_id=user_id,
            behavior_type=data['behavior_type'],
            details=data['details']
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"记录用户行为错误: {e}")
        return jsonify({'error': '服务器错误'}), 500

@user_bp.route('/tags', methods=['GET'])
@login_required
def get_user_tags():
    """获取用户标签"""
    try:
        user_id = request.current_user['user_id']
        result = user_service.get_user_info(user_id)
        
        if result['success']:
            return jsonify({
                'tags': result['user'].get('tags', [])
            }), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"获取用户标签错误: {e}")
        return jsonify({'error': '服务器错误'}), 500

@user_bp.route('/tags', methods=['POST'])
@login_required
def add_user_tags():
    """添加用户标签"""
    try:
        user_id = request.current_user['user_id']
        data = request.get_json()
        
        if not data.get('tags'):
            return jsonify({'error': '缺少标签数据'}), 400
        
        # 更新标签
        result = user_service.update_user_tags(
            user_id=user_id,
            new_tags=data['tags']
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"添加用户标签错误: {e}")
        return jsonify({'error': '服务器错误'}), 500 