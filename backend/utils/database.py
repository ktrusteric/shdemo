#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MySQL数据库连接和管理工具
"""

import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pymysql

# 配置日志
logger = logging.getLogger(__name__)

# SQLAlchemy实例
db = SQLAlchemy()

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine = None
        self.connected = False
    
    def init_app(self, app):
        """初始化Flask应用的数据库"""
        try:
            # 初始化SQLAlchemy
            db.init_app(app)
            
            # 创建数据库引擎
            self.engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
            
            # 创建数据库（如果不存在）
            self.create_database_if_not_exists(app.config)
            
            # 在应用上下文中创建表
            with app.app_context():
                db.create_all()
            
            self.connected = True
            logger.info("成功连接到MySQL数据库")
            return True
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            self.connected = False
            return False
    
    def create_database_if_not_exists(self, config):
        """创建数据库（如果不存在）"""
        try:
            # 连接MySQL服务器（不指定数据库）
            connection_url = f"mysql+pymysql://{config['MYSQL_USER']}@{config['MYSQL_HOST']}:{config['MYSQL_PORT']}/?charset=utf8mb4"
            temp_engine = create_engine(connection_url)
            
            with temp_engine.connect() as conn:
                # 检查数据库是否存在
                result = conn.execute(text(f"SHOW DATABASES LIKE '{config['MYSQL_DB']}'"))
                if not result.fetchone():
                    # 创建数据库
                    conn.execute(text(f"CREATE DATABASE {config['MYSQL_DB']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                    logger.info(f"创建数据库: {config['MYSQL_DB']}")
                else:
                    logger.info(f"数据库已存在: {config['MYSQL_DB']}")
            
            temp_engine.dispose()
            
        except Exception as e:
            logger.error(f"创建数据库失败: {e}")
            raise
    
    def test_connection(self):
        """测试数据库连接"""
        if not self.engine:
            return False
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False
    
    def get_database_info(self):
        """获取数据库信息"""
        if not self.engine:
            return {}
        
        try:
            with self.engine.connect() as conn:
                # 获取数据库版本
                version_result = conn.execute(text("SELECT VERSION()"))
                version = version_result.fetchone()[0] if version_result else "Unknown"
                
                # 获取数据库大小
                size_result = conn.execute(text("""
                    SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size_mb
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE()
                """))
                size_mb = size_result.fetchone()[0] or 0
                
                # 获取表数量
                tables_result = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = DATABASE()
                """))
                table_count = tables_result.fetchone()[0] or 0
                
                return {
                    'version': version,
                    'size_mb': float(size_mb),
                    'table_count': int(table_count),
                    'status': 'connected'
                }
        except Exception as e:
            logger.error(f"获取数据库信息失败: {e}")
            return {'status': 'error', 'error': str(e)}

# 全局数据库管理器实例
database_manager = DatabaseManager()

def get_db():
    """获取数据库实例"""
    return db

def init_database(app):
    """初始化数据库"""
    return database_manager.init_app(app)

def get_database_status():
    """获取数据库状态"""
    return {
        'connected': database_manager.connected,
        'info': database_manager.get_database_info()
    } 