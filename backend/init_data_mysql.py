#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MySQL版本数据初始化脚本
"""

import os
import sys
from datetime import datetime, timedelta
import random

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.user import User, UserBehavior, UserTag
from models.energy_data import EnergyNews, EnergyPrice, EnergyDeal, EnergyReport, EnergyIndex
from utils.database import db

# --- 以下为 shdemo 数据库初始化建表 SQL 示例 ---
# 可直接在 MySQL 客户端执行：
'''
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    region VARCHAR(50),
    trading_products JSON,
    user_type VARCHAR(20) DEFAULT 'free',
    tags JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login DATETIME,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE user_behaviors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    behavior_type VARCHAR(50) NOT NULL,
    target_type VARCHAR(50),
    target_id VARCHAR(100),
    details JSON,
    session_id VARCHAR(100),
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX(user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE user_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    tag_name VARCHAR(100) NOT NULL,
    tag_value VARCHAR(255),
    tag_source VARCHAR(50),
    confidence FLOAT DEFAULT 1.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX(user_id),
    INDEX(tag_name),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE energy_news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT,
    summary TEXT,
    source VARCHAR(200),
    author VARCHAR(100),
    category VARCHAR(100),
    tags JSON,
    url VARCHAR(500),
    view_count INT DEFAULT 0,
    share_count INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'published',
    is_featured BOOLEAN DEFAULT FALSE,
    publish_time DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX(title),
    INDEX(category),
    INDEX(publish_time)
);

CREATE TABLE energy_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    product_type VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    price FLOAT NOT NULL,
    price_unit VARCHAR(50) DEFAULT '元/立方米',
    opening_price FLOAT,
    closing_price FLOAT,
    highest_price FLOAT,
    lowest_price FLOAT,
    change_amount FLOAT,
    change_percent FLOAT,
    market VARCHAR(100),
    trading_volume FLOAT,
    is_latest BOOLEAN DEFAULT TRUE,
    price_date DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX(product_name),
    INDEX(product_type),
    INDEX(region),
    INDEX(is_latest),
    INDEX(price_date)
);

CREATE TABLE energy_deals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    deal_id VARCHAR(100) NOT NULL UNIQUE,
    product_name VARCHAR(200) NOT NULL,
    product_type VARCHAR(100) NOT NULL,
    buyer VARCHAR(200) NOT NULL,
    seller VARCHAR(200) NOT NULL,
    deal_price FLOAT NOT NULL,
    deal_quantity FLOAT NOT NULL,
    deal_amount FLOAT NOT NULL,
    price_unit VARCHAR(50),
    quantity_unit VARCHAR(50),
    region VARCHAR(100),
    delivery_location VARCHAR(200),
    deal_type VARCHAR(50),
    contract_period VARCHAR(100),
    deal_date DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX(deal_id),
    INDEX(product_type),
    INDEX(buyer),
    INDEX(seller),
    INDEX(region),
    INDEX(deal_date)
);

CREATE TABLE energy_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    author VARCHAR(200),
    organization VARCHAR(200),
    report_type VARCHAR(100),
    summary TEXT,
    keywords JSON,
    tags JSON,
    file_path VARCHAR(500),
    file_size INT,
    page_count INT,
    access_level VARCHAR(20) DEFAULT 'free',
    download_count INT DEFAULT 0,
    view_count INT DEFAULT 0,
    rating FLOAT,
    is_featured BOOLEAN DEFAULT FALSE,
    publish_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX(title),
    INDEX(report_type),
    INDEX(access_level),
    INDEX(publish_date)
);

CREATE TABLE energy_indexes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    index_name VARCHAR(200) NOT NULL,
    index_code VARCHAR(50),
    index_value FLOAT NOT NULL,
    base_value FLOAT,
    change_amount FLOAT,
    change_percent FLOAT,
    category VARCHAR(100),
    region VARCHAR(100),
    description TEXT,
    calculation_method TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    index_date DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX(index_name),
    INDEX(index_code),
    INDEX(category),
    INDEX(index_date)
);
'''

def init_sample_data():
    """初始化示例数据"""
    print("开始初始化示例数据...")
    
    # 创建Flask应用上下文
    app = create_app('development')
    
    with app.app_context():
        # 删除现有数据（可选）
        # db.drop_all()
        # 创建所有表
        db.create_all()
        
        # 1. 初始化资讯数据
        print("1. 初始化资讯数据...")
        init_news_data()
        
        # 2. 初始化价格数据
        print("2. 初始化价格数据...")
        init_price_data()
        
        # 3. 初始化成交数据
        print("3. 初始化成交数据...")
        init_deal_data()
        
        # 4. 初始化研报数据
        print("4. 初始化研报数据...")
        init_report_data()
        
        # 5. 初始化指数数据
        print("5. 初始化指数数据...")
        init_index_data()
        
        # 6. 初始化测试用户数据
        print("6. 初始化测试用户数据...")
        init_user_data()
        
        print("\n示例数据初始化完成！")

def init_news_data():
    """初始化资讯数据"""
    news_data = [
        {
            'title': '国家能源局发布天然气发展规划',
            'content': '国家能源局近日发布《天然气发展"十四五"规划》，明确提出到2025年天然气消费量将达到4300-4600亿立方米...',
            'summary': '国家能源局发布天然气发展规划，明确未来发展目标',
            'source': '国家能源局',
            'author': '能源司',
            'category': '政策法规',
            'tags': ['天然气', '十四五规划', '政策'],
            'publish_time': datetime.now() - timedelta(days=1),
            'view_count': 1250,
            'is_featured': True
        },
        {
            'title': 'LNG价格持续上涨，市场供需趋紧',
            'content': '受国际能源价格波动影响，国内LNG价格持续上涨，主要接收站报价普遍上调...',
            'summary': 'LNG价格受国际因素影响持续上涨',
            'source': '中国能源报',
            'author': '市场部',
            'category': '市场动态',
            'tags': ['LNG', '价格', '供需'],
            'publish_time': datetime.now() - timedelta(hours=12),
            'view_count': 892,
            'is_featured': False
        },
        {
            'title': '上海石油天然气交易中心月度交易报告',
            'content': '上海石油天然气交易中心发布11月份交易报告，本月交易量创历史新高...',
            'summary': '上海石油天然气交易中心11月份交易量创新高',
            'source': '上海石油天然气交易中心',
            'author': '交易部',
            'category': '市场动态',
            'tags': ['交易报告', '上海', '月度数据'],
            'publish_time': datetime.now() - timedelta(hours=6),
            'view_count': 567,
            'is_featured': True
        },
        {
            'title': '天然气管网建设加速，互联互通格局形成',
            'content': '随着国家管网公司成立，全国天然气管网建设进入加速期，互联互通格局正在形成...',
            'summary': '天然气管网建设加速，互联互通取得重要进展',
            'source': '中国石油报',
            'author': '基础设施部',
            'category': '基础设施',
            'tags': ['管网', '基础设施', '互联互通'],
            'publish_time': datetime.now() - timedelta(hours=3),
            'view_count': 423,
            'is_featured': False
        },
        {
            'title': '绿色低碳转型推动天然气需求增长',
            'content': '在碳达峰碳中和目标引领下，天然气作为清洁能源的作用日益凸显，需求持续增长...',
            'summary': '绿色低碳转型为天然气发展带来新机遇',
            'source': '能源观察',
            'author': '研究院',
            'category': '行业分析',
            'tags': ['绿色低碳', '转型', '需求增长'],
            'publish_time': datetime.now() - timedelta(minutes=30),
            'view_count': 156,
            'is_featured': False
        }
    ]
    
    for data in news_data:
        if not EnergyNews.query.filter_by(title=data['title']).first():
            news = EnergyNews(**data)
            db.session.add(news)
    
    db.session.commit()
    print(f"  已插入 {len(news_data)} 条资讯数据")

def init_price_data():
    """初始化价格数据"""
    products = [
        ('管道天然气', 'PNG'),
        ('液化天然气', 'LNG'),
        ('压缩天然气', 'CNG')
    ]
    
    regions = ['北京', '上海', '广州', '深圳', '天津', '重庆', '江苏', '浙江', '山东', '河北', '湖北', '四川']
    
    price_count = 0
    base_date = datetime.now() - timedelta(days=30)
    
    for product_name, product_type in products:
        for region in regions:
            # 生成最近30天的价格数据
            for i in range(30):
                current_date = base_date + timedelta(days=i)
                
                # 基础价格（根据产品类型设定）
                if product_type == 'PNG':
                    base_price = random.uniform(2.5, 3.5)
                elif product_type == 'LNG':
                    base_price = random.uniform(4.0, 6.0)
                else:  # CNG
                    base_price = random.uniform(3.0, 4.5)
                
                # 添加随机波动
                price = round(base_price * (1 + random.uniform(-0.1, 0.1)), 2)
                
                # 计算变化
                change_percent = round(random.uniform(-5, 5), 2)
                change_amount = round(price * change_percent / 100, 2)
                
                price_data = {
                    'product_name': product_name,
                    'product_type': product_type,
                    'region': region,
                    'price': price,
                    'price_unit': '元/立方米',
                    'change_amount': change_amount,
                    'change_percent': change_percent,
                    'market': f'{region}能源交易市场',
                    'trading_volume': round(random.uniform(100, 1000), 2),
                    'is_latest': (i == 29),  # 最后一天为最新价格
                    'price_date': current_date
                }
                
                price = EnergyPrice(**price_data)
                db.session.add(price)
                price_count += 1
    
    db.session.commit()
    print(f"  已插入 {price_count} 条价格数据")

def init_deal_data():
    """初始化成交数据"""
    deal_data = [
        {
            'deal_id': 'DEAL202411001',
            'product_name': '管道天然气',
            'product_type': 'PNG',
            'buyer': '华润燃气（上海）有限公司',
            'seller': '中海石油天然气供应有限责任公司',
            'deal_price': 3.25,
            'deal_quantity': 500.0,
            'deal_amount': 1625000.0,
            'price_unit': '元/立方米',
            'quantity_unit': '万立方米',
            'region': '上海',
            'delivery_location': '上海LNG接收站',
            'deal_type': '现货',
            'contract_period': '1个月',
            'deal_date': datetime.now() - timedelta(days=2)
        },
        {
            'deal_id': 'DEAL202411002',
            'product_name': '液化天然气',
            'product_type': 'LNG',
            'buyer': '广东大鹏LNG有限公司',
            'seller': '中国石化销售股份有限公司',
            'deal_price': 5.80,
            'deal_quantity': 200.0,
            'deal_amount': 1160000.0,
            'price_unit': '元/立方米',
            'quantity_unit': '万立方米',
            'region': '广东',
            'delivery_location': '深圳大鹏湾',
            'deal_type': '现货',
            'contract_period': '即期',
            'deal_date': datetime.now() - timedelta(days=1)
        },
        {
            'deal_id': 'DEAL202411003',
            'product_name': '压缩天然气',
            'product_type': 'CNG',
            'buyer': '北京燃气集团有限责任公司',
            'seller': '中国石油天然气销售东北公司',
            'deal_price': 4.10,
            'deal_quantity': 100.0,
            'deal_amount': 410000.0,
            'price_unit': '元/立方米',
            'quantity_unit': '万立方米',
            'region': '北京',
            'delivery_location': '北京门站',
            'deal_type': '期货',
            'contract_period': '3个月',
            'deal_date': datetime.now() - timedelta(hours=6)
        }
    ]
    
    for data in deal_data:
        if not EnergyDeal.query.filter_by(deal_id=data['deal_id']).first():
            deal = EnergyDeal(**data)
            db.session.add(deal)
    
    db.session.commit()
    print(f"  已插入 {len(deal_data)} 条成交数据")

def init_report_data():
    """初始化研报数据"""
    report_data = [
        {
            'title': '2024年中国天然气市场分析报告',
            'author': '中国石油规划总院',
            'organization': '中国石油规划总院',
            'report_type': '行业分析',
            'summary': '深入分析2024年中国天然气市场供需情况、价格走势及未来发展趋势...',
            'keywords': ['天然气', '市场分析', '供需', '价格'],
            'tags': ['市场分析', '天然气', '2024'],
            'file_path': '/reports/2024_china_gas_market.pdf',
            'file_size': 2048576,
            'page_count': 65,
            'access_level': 'free',
            'download_count': 1200,
            'view_count': 3500,
            'rating': 4.7,
            'is_featured': True,
            'publish_date': datetime.now() - timedelta(days=7)
        },
        {
            'title': 'LNG接收站建设投资分析',
            'author': '能源咨询研究院',
            'organization': '中国能源建设集团',
            'report_type': '投资分析',
            'summary': '对当前LNG接收站建设的投资环境、成本分析和收益预测进行深度解析...',
            'keywords': ['LNG', '接收站', '投资', '建设'],
            'tags': ['LNG', '投资分析', '基础设施'],
            'file_path': '/reports/lng_terminal_investment.pdf',
            'file_size': 1536000,
            'page_count': 45,
            'access_level': 'premium',
            'download_count': 680,
            'view_count': 1850,
            'rating': 4.4,
            'is_featured': False,
            'publish_date': datetime.now() - timedelta(days=14)
        },
        {
            'title': '天然气价格机制改革研究',
            'author': '发展研究中心',
            'organization': '国务院发展研究中心',
            'report_type': '政策解读',
            'summary': '分析天然气价格机制改革的背景、现状和未来发展方向...',
            'keywords': ['价格机制', '改革', '政策', '天然气'],
            'tags': ['价格机制', '改革', '政策解读'],
            'file_path': '/reports/gas_pricing_reform.pdf',
            'file_size': 1024000,
            'page_count': 32,
            'access_level': 'free',
            'download_count': 2100,
            'view_count': 4200,
            'rating': 4.8,
            'is_featured': True,
            'publish_date': datetime.now() - timedelta(days=3)
        }
    ]
    
    for data in report_data:
        if not EnergyReport.query.filter_by(title=data['title']).first():
            report = EnergyReport(**data)
            db.session.add(report)
    
    db.session.commit()
    print(f"  已插入 {len(report_data)} 条研报数据")

def init_index_data():
    """初始化指数数据"""
    index_names = [
        ('中国天然气价格指数', 'CNGPI'),
        ('上海石油天然气现货指数', 'SHPGSI'),
        ('华南LNG价格指数', 'HNLPI'),
        ('华东管道气价格指数', 'HDPGI'),
        ('华北天然气供需指数', 'HBGDSI')
    ]
    
    categories = ['价格指数', '供需指数', '市场指数']
    regions = ['全国', '华东', '华南', '华北', '西南']
    
    index_count = 0
    base_date = datetime.now() - timedelta(days=14)
    
    for i, (index_name, index_code) in enumerate(index_names):
        for day in range(14):
            current_date = base_date + timedelta(days=day)
            
            # 基础指数值
            base_value = 100.0 + random.uniform(-20, 20)
            index_value = round(base_value * (1 + random.uniform(-0.05, 0.05)), 2)
            
            # 计算变化
            change_percent = round(random.uniform(-3, 3), 2)
            change_amount = round(index_value * change_percent / 100, 2)
            
            index_data = {
                'index_name': index_name,
                'index_code': index_code,
                'index_value': index_value,
                'base_value': 100.0,
                'change_amount': change_amount,
                'change_percent': change_percent,
                'category': categories[i % len(categories)],
                'region': regions[i % len(regions)],
                'description': f'{index_name}反映相关市场的价格变化趋势',
                'calculation_method': '加权平均法',
                'is_active': True,
                'index_date': current_date
            }
            
            index = EnergyIndex(**index_data)
            db.session.add(index)
            index_count += 1
    
    db.session.commit()
    print(f"  已插入 {index_count} 条指数数据")

def init_user_data():
    """初始化测试用户数据"""
    import bcrypt
    
    # 创建测试用户
    test_users = [
        {
            'username': 'testuser1',
            'email': 'test1@example.com',
            'password': 'password123',
            'region': '上海',
            'trading_products': ['管道天然气', '液化天然气'],
            'user_type': 'free'
        },
        {
            'username': 'premiumuser',
            'email': 'premium@example.com',
            'password': 'premium123',
            'region': '北京',
            'trading_products': ['液化天然气', '压缩天然气'],
            'user_type': 'premium'
        }
    ]
    
    for user_data in test_users:
        if not User.query.filter_by(username=user_data['username']).first():
            # 加密密码
            password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=password_hash,
                region=user_data['region'],
                trading_products=user_data['trading_products'],
                user_type=user_data['user_type'],
                tags=[user_data['region']] + user_data['trading_products']
            )
            
            db.session.add(user)
    
    db.session.commit()
    print(f"  已插入 {len(test_users)} 个测试用户")

if __name__ == '__main__':
    init_sample_data() 