from flask import Blueprint, request, jsonify
from utils.auth import login_required, paid_user_required
from utils.database import db
from bson import ObjectId
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

energy_bp = Blueprint('energy', __name__)

@energy_bp.route('/news', methods=['GET'])
@login_required
def get_news():
    """获取能源资讯列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        category = request.args.get('category')
        
        # 构建查询条件
        query = {'status': 'published'}
        if category:
            query['category'] = category
        
        # 查询数据
        news_collection = db.get_collection('energy_news')
        total = news_collection.count_documents(query)
        news_list = list(news_collection.find(query)
                        .sort('publish_time', -1)
                        .skip((page - 1) * limit)
                        .limit(limit))
        
        # 转换ObjectId为字符串
        for news in news_list:
            news['_id'] = str(news['_id'])
            
        return jsonify({
            'data': news_list,
            'total': total,
            'page': page,
            'limit': limit
        }), 200
        
    except Exception as e:
        logger.error(f"获取资讯列表错误: {e}")
        return jsonify({'error': '服务器错误'}), 500

@energy_bp.route('/news/<news_id>', methods=['GET'])
@login_required
def get_news_detail(news_id):
    """获取资讯详情"""
    try:
        news_collection = db.get_collection('energy_news')
        news = news_collection.find_one({'_id': ObjectId(news_id)})
        
        if news:
            # 增加浏览次数
            news_collection.update_one(
                {'_id': ObjectId(news_id)},
                {'$inc': {'view_count': 1}}
            )
            
            news['_id'] = str(news['_id'])
            return jsonify(news), 200
        else:
            return jsonify({'error': '资讯不存在'}), 404
            
    except Exception as e:
        logger.error(f"获取资讯详情错误: {e}")
        return jsonify({'error': '服务器错误'}), 500

@energy_bp.route('/prices', methods=['GET'])
@login_required
def get_prices():
    """获取能源价格数据"""
    try:
        # 获取查询参数
        product_type = request.args.get('product_type')
        region = request.args.get('region')
        days = int(request.args.get('days', 7))  # 默认查询7天内的数据
        
        # 构建查询条件
        query = {}
        if product_type:
            query['product_type'] = product_type
        if region:
            query['region'] = region
        
        # 只查询最近几天的数据
        start_date = datetime.now() - timedelta(days=days)
        query['price_date'] = {'$gte': start_date}
        
        # 查询数据
        prices_collection = db.get_collection('energy_prices')
        prices = list(prices_collection.find(query).sort('price_date', -1))
        
        # 转换ObjectId为字符串
        for price in prices:
            price['_id'] = str(price['_id'])
            
        return jsonify({
            'data': prices,
            'count': len(prices)
        }), 200
        
    except Exception as e:
        logger.error(f"获取价格数据错误: {e}")
        return jsonify({'error': '服务器错误'}), 500

@energy_bp.route('/prices/latest', methods=['GET'])
@login_required
def get_latest_prices():
    """获取最新价格数据"""
    try:
        prices_collection = db.get_collection('energy_prices')
        
        # 查询每个产品类型和地区的最新价格
        pipeline = [
            {'$match': {'is_latest': True}},
            {'$sort': {'price_date': -1}},
            {'$group': {
                '_id': {
                    'product_type': '$product_type',
                    'region': '$region'
                },
                'latest_price': {'$first': '$$ROOT'}
            }}
        ]
        
        results = list(prices_collection.aggregate(pipeline))
        
        # 整理数据格式
        latest_prices = []
        for result in results:
            price_data = result['latest_price']
            price_data['_id'] = str(price_data['_id'])
            latest_prices.append(price_data)
            
        return jsonify({
            'data': latest_prices,
            'count': len(latest_prices)
        }), 200
        
    except Exception as e:
        logger.error(f"获取最新价格错误: {e}")
        return jsonify({'error': '服务器错误'}), 500

@energy_bp.route('/deals', methods=['GET'])
@paid_user_required
def get_deals():
    """获取成交数据（仅付费用户）"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        product_type = request.args.get('product_type')
        days = int(request.args.get('days', 30))
        
        # 构建查询条件
        query = {}
        if product_type:
            query['product_type'] = product_type
        
        # 只查询最近几天的数据
        start_date = datetime.now() - timedelta(days=days)
        query['deal_date'] = {'$gte': start_date}
        
        # 查询数据
        deals_collection = db.get_collection('energy_deals')
        total = deals_collection.count_documents(query)
        deals = list(deals_collection.find(query)
                    .sort('deal_date', -1)
                    .skip((page - 1) * limit)
                    .limit(limit))
        
        # 转换ObjectId为字符串
        for deal in deals:
            deal['_id'] = str(deal['_id'])
            
        return jsonify({
            'data': deals,
            'total': total,
            'page': page,
            'limit': limit
        }), 200
        
    except Exception as e:
        logger.error(f"获取成交数据错误: {e}")
        return jsonify({'error': '服务器错误'}), 500

@energy_bp.route('/reports', methods=['GET'])
@login_required
def get_reports():
    """获取研究报告列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        report_type = request.args.get('report_type')
        
        # 获取用户类型
        user_id = request.current_user['user_id']
        users_collection = db.get_collection('users')
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        user_type = user.get('user_type', 'free')
        
        # 构建查询条件
        query = {}
        if report_type:
            query['report_type'] = report_type
        
        # 免费用户只能看到免费报告
        if user_type == 'free':
            query['access_level'] = 'free'
        
        # 查询数据
        reports_collection = db.get_collection('energy_reports')
        total = reports_collection.count_documents(query)
        reports = list(reports_collection.find(query)
                      .sort('publish_date', -1)
                      .skip((page - 1) * limit)
                      .limit(limit))
        
        # 转换ObjectId为字符串
        for report in reports:
            report['_id'] = str(report['_id'])
            
        return jsonify({
            'data': reports,
            'total': total,
            'page': page,
            'limit': limit
        }), 200
        
    except Exception as e:
        logger.error(f"获取研报列表错误: {e}")
        return jsonify({'error': '服务器错误'}), 500

@energy_bp.route('/indexes', methods=['GET'])
@login_required
def get_indexes():
    """获取能源指数数据"""
    try:
        # 获取查询参数
        index_name = request.args.get('index_name')
        days = int(request.args.get('days', 7))
        
        # 构建查询条件
        query = {}
        if index_name:
            query['index_name'] = index_name
        
        # 只查询最近几天的数据
        start_date = datetime.now() - timedelta(days=days)
        query['index_date'] = {'$gte': start_date}
        
        # 查询数据
        indexes_collection = db.get_collection('energy_indexes')
        indexes = list(indexes_collection.find(query).sort('index_date', -1))
        
        # 转换ObjectId为字符串
        for index in indexes:
            index['_id'] = str(index['_id'])
            
        return jsonify({
            'data': indexes,
            'count': len(indexes)
        }), 200
        
    except Exception as e:
        logger.error(f"获取指数数据错误: {e}")
        return jsonify({'error': '服务器错误'}), 500 