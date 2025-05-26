import logging
from models.user import User, UserBehavior
from utils.database import db
from utils.auth import hash_password, verify_password, generate_token

logger = logging.getLogger(__name__)

class UserService:
    """用户服务类（SQLAlchemy/MySQL版）"""
    def __init__(self):
        pass  # 不再需要 collection

    def register_user(self, username, password, email, region, trading_products, company_name=None):
        """用户注册"""
        try:
            # 检查用户名和邮箱是否已存在
            if User.query.filter_by(username=username).first():
                return {'success': False, 'message': '用户名已存在'}
            if User.query.filter_by(email=email).first():
                return {'success': False, 'message': '邮箱已被注册'}

            # 创建用户
            password_hash_val = hash_password(password)
            tags = list(set([region] + trading_products + ([company_name] if company_name else [])))
            user = User(
                username=username,
                password_hash=password_hash_val,
                email=email,
                region=region,
                trading_products=trading_products,
                tags=tags
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"新用户注册成功: {username}")
            return {
                'success': True,
                'message': '注册成功',
                'user_id': user.id
            }
        except Exception as e:
            logger.error(f"用户注册失败: {e}")
            db.session.rollback()
            return {'success': False, 'message': '系统错误，请稍后重试'}

    def login_user(self, username, password):
        """用户登录"""
        try:
            user = User.query.filter_by(username=username).first()
            if not user or not verify_password(password, user.password_hash):
                return {'success': False, 'message': '用户名或密码错误'}
            user.update_last_login()
            token = generate_token(user.id, username)
            logger.info(f"用户登录成功: {username}")
            return {
                'success': True,
                'message': '登录成功',
                'token': token,
                'user': user.to_dict()
            }
        except Exception as e:
            logger.error(f"用户登录失败: {e}")
            return {'success': False, 'message': '系统错误，请稍后重试'}

    def update_user_tags(self, user_id, new_tags):
        """更新用户标签"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'message': '用户不存在'}
            user.update_tags(new_tags)
            logger.info(f"用户标签更新成功: {user_id}, 新标签: {new_tags}")
            return {'success': True, 'message': '标签更新成功'}
        except Exception as e:
            logger.error(f"更新用户标签失败: {e}")
            db.session.rollback()
            return {'success': False, 'message': '系统错误'}

    def record_user_behavior(self, user_id, behavior_type, details):
        """记录用户行为"""
        try:
            behavior = UserBehavior.record_behavior(
                user_id=user_id,
                behavior_type=behavior_type,
                details=details
            )
            self._update_tags_from_behavior(user_id, behavior_type, details)
            logger.info(f"用户行为记录成功: {user_id}, 类型: {behavior_type}")
            return {'success': True, 'message': '行为记录成功'}
        except Exception as e:
            logger.error(f"记录用户行为失败: {e}")
            db.session.rollback()
            return {'success': False, 'message': '系统错误'}

    def _update_tags_from_behavior(self, user_id, behavior_type, details):
        """根据用户行为更新标签"""
        new_tags = []
        # 根据搜索行为生成标签
        if behavior_type == 'search':
            query = details.get('query', '')
            keywords = query.split()
            new_tags.extend(keywords[:3])
            if '最近' in query:
                if '三个月' in query:
                    new_tags.append('最近三个月')
                elif '半年' in query:
                    new_tags.append('最近半年')
                elif '一年' in query:
                    new_tags.append('最近一年')
        elif behavior_type == 'view':
            content_type = details.get('content_type', '')
            duration = details.get('duration', 0)
            if duration > 30:
                new_tags.append(f"关注{content_type}")
        if new_tags:
            self.update_user_tags(user_id, new_tags)

    def upgrade_user_to_paid(self, user_id):
        """升级用户为付费用户"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'message': '用户不存在'}
            user.user_type = 'premium'
            db.session.commit()
            logger.info(f"用户升级为付费用户成功: {user_id}")
            return {'success': True, 'message': '升级成功'}
        except Exception as e:
            logger.error(f"用户升级失败: {e}")
            db.session.rollback()
            return {'success': False, 'message': '系统错误'}

    def get_user_info(self, user_id):
        """获取用户信息"""
        try:
            user = User.query.get(user_id)
            if user:
                return {'success': True, 'user': user.to_dict()}
            else:
                return {'success': False, 'message': '用户不存在'}
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return {'success': False, 'message': '系统错误'} 