from flask import Blueprint, request, jsonify
from utils.auth import login_required
from utils.database import db
from bson import ObjectId
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

recommendation_bp = Blueprint('recommendation', __name__)

@recommendation_bp.route('/personalized', methods=['GET'])
@login_required
def get_personalized_recommendations():
    """获取个性化推荐内容"""
    try:
        user_id = request.current_user['user_id']
        
        # 获取用户信息和标签
        users_collection = db.get_collection('users')
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        user_tags = user.get('tags', [])
        user_region = user.get('region')
        user_products = user.get('trading_products', [])
        
        recommendations = {
            'news': [],
            'reports': [],
            'price_alerts': []
        }
        
        # 基于标签推荐资讯
        news_collection = db.get_collection('energy_news')
        news_query = {
            'status': 'published',
            '$or': [
                {'tags': {'$in': user_tags}},
                {'content': {'$regex': user_region}},
            ]
        }
        
        recommended_news = list(news_collection.find(news_query)
                               .sort('publish_time', -1)
                               .limit(5))
        
        for news in recommended_news:
            news['_id'] = str(news['_id'])
            news['recommendation_reason'] = '基于您的关注标签推荐'
        
        recommendations['news'] = recommended_news
        
        # 基于标签推荐研报
        reports_collection = db.get_collection('energy_reports')
        report_query = {
            '$or': [
                {'tags': {'$in': user_tags}},
                {'title': {'$regex': '|'.join(user_products)}},
            ]
        }
        
        # 根据用户类型过滤
        if user.get('user_type') == 'free':
            report_query['access_level'] = 'free'
        
        recommended_reports = list(reports_collection.find(report_query)
                                  .sort('publish_date', -1)
                                  .limit(3))
        
        for report in recommended_reports:
            report['_id'] = str(report['_id'])
            report['recommendation_reason'] = '基于您的交易品种推荐'
        
        recommendations['reports'] = recommended_reports
        
        # 推荐价格提醒
        prices_collection = db.get_collection('energy_prices')
        for product in user_products[:2]:  # 最多推荐2个产品的价格
            latest_price = prices_collection.find_one({
                'product_type': product,
                'region': user_region,
                'is_latest': True
            })
            
            if latest_price:
                latest_price['_id'] = str(latest_price['_id'])
                latest_price['recommendation_reason'] = f'您关注的{product}最新价格'
                recommendations['price_alerts'].append(latest_price)
        
        return jsonify(recommendations), 200
        
    except Exception as e:
        logger.error(f"获取个性化推荐错误: {e}")
        return jsonify({'error': '服务器错误'}), 500

@recommendation_bp.route('/guess-you-like', methods=['GET'])
@login_required
def guess_you_like():
    """猜你喜欢功能"""
    try:
        user_id = request.current_user['user_id']
        
        # 获取用户最近的行为数据
        behaviors_collection = db.get_collection('user_behaviors')
        recent_behaviors = list(behaviors_collection.find({
            'user_id': ObjectId(user_id),
            'timestamp': {'$gte': datetime.now() - timedelta(days=7)}
        }).sort('timestamp', -1).limit(20))
        
        # 分析用户行为偏好
        view_preferences = {}
        search_keywords = []
        
        for behavior in recent_behaviors:
            if behavior['behavior_type'] == 'view':
                content_type = behavior['details'].get('content_type')
                if content_type:
                    view_preferences[content_type] = view_preferences.get(content_type, 0) + 1
            elif behavior['behavior_type'] == 'search':
                query = behavior['details'].get('query', '')
                search_keywords.extend(query.split())
        
        # 获取最感兴趣的内容类型
        favorite_content_type = max(view_preferences, key=view_preferences.get) if view_preferences else 'news'
        
        recommendations = []
        
        # 根据偏好推荐内容
        if favorite_content_type == 'news':
            news_collection = db.get_collection('energy_news')
            # 基于搜索关键词推荐
            if search_keywords:
                query = {
                    'status': 'published',
                    '$or': [{'title': {'$regex': keyword}} for keyword in search_keywords[:3]]
                }
            else:
                query = {'status': 'published', 'is_featured': True}
            
            news_list = list(news_collection.find(query).sort('publish_time', -1).limit(5))
            for news in news_list:
                news['_id'] = str(news['_id'])
                news['content_type'] = 'news'
                recommendations.append(news)
        
        elif favorite_content_type == 'report':
            reports_collection = db.get_collection('energy_reports')
            # 获取用户信息
            users_collection = db.get_collection('users')
            user = users_collection.find_one({'_id': ObjectId(user_id)})
            
            query = {'is_featured': True}
            if user.get('user_type') == 'free':
                query['access_level'] = 'free'
            
            reports = list(reports_collection.find(query).sort('publish_date', -1).limit(5))
            for report in reports:
                report['_id'] = str(report['_id'])
                report['content_type'] = 'report'
                recommendations.append(report)
        
        return jsonify({
            'recommendations': recommendations,
            'based_on': '您最近的浏览偏好'
        }), 200
        
    except Exception as e:
        logger.error(f"猜你喜欢功能错误: {e}")
        return jsonify({'error': '服务器错误'}), 500

@recommendation_bp.route('/hot-topics', methods=['GET'])
@login_required
def get_hot_topics():
    """获取热门话题"""
    try:
        # 获取最近7天内浏览量最高的资讯
        news_collection = db.get_collection('energy_news')
        hot_news = list(news_collection.find({
            'status': 'published',
            'publish_time': {'$gte': datetime.now() - timedelta(days=7)}
        }).sort('view_count', -1).limit(10))
        
        for news in hot_news:
            news['_id'] = str(news['_id'])
        
        # 获取最近的重要成交信息（仅付费用户可见详情）
        user_id = request.current_user['user_id']
        users_collection = db.get_collection('users')
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        
        hot_deals = []
        if user.get('user_type') == 'paid':
            deals_collection = db.get_collection('energy_deals')
            hot_deals = list(deals_collection.find({
                'deal_date': {'$gte': datetime.now() - timedelta(days=3)}
            }).sort([('amount', -1), ('deal_date', -1)]).limit(5))
            
            for deal in hot_deals:
                deal['_id'] = str(deal['_id'])
        
        return jsonify({
            'hot_news': hot_news,
            'hot_deals': hot_deals,
            'generated_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"获取热门话题错误: {e}")
        return jsonify({'error': '服务器错误'}), 500 