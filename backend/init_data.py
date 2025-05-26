#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化示例数据脚本
"""

import os
import sys
from datetime import datetime, timedelta
import random

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import db
from models.energy_data import EnergyNews, EnergyPrice, EnergyDeal, EnergyReport, EnergyIndex
from config import Config

def init_sample_data():
    """初始化示例数据"""
    print("开始初始化示例数据...")
    
    # 连接数据库
    if not db.connect():
        print("数据库连接失败")
        return
    
    # 1. 初始化资讯数据
    print("1. 初始化资讯数据...")
    news_collection = db.get_collection('energy_news')
    
    sample_news = [
        {
            'title': '国家发改委：推动天然气市场化改革，建立多元化供应体系',
            'content': '国家发改委近日发布通知，要求各地加快推进天然气市场化改革，建立多元化供应体系。通知指出，要进一步放开天然气气源和销售价格，完善管道运输价格机制，推动天然气交易中心建设，形成公开透明的价格形成机制。',
            'source': '国家发改委',
            'category': '政策法规',
            'tags': ['天然气改革', '市场化', '价格机制']
        },
        {
            'title': '中海油与卡塔尔能源公司签署长期LNG购销协议',
            'content': '中国海洋石油集团有限公司（中海油）与卡塔尔能源公司今日签署了一份为期27年的液化天然气（LNG）长期购销协议。根据协议，卡塔尔能源公司每年将向中海油供应400万吨LNG。',
            'source': '中海油官网',
            'category': '企业新闻',
            'tags': ['中海油', 'LNG', '国际合作', '卡塔尔']
        },
        {
            'title': '2024年上半年中国天然气消费量同比增长8.5%',
            'content': '根据国家统计局最新数据，2024年上半年，中国天然气表观消费量达到1950亿立方米，同比增长8.5%。其中，城市燃气消费增长最快，工业用气保持稳定增长。',
            'source': '国家统计局',
            'category': '市场动态',
            'tags': ['天然气消费', '市场数据', '2024年']
        },
        {
            'title': '新技术：氢能与天然气混合输送技术取得突破',
            'content': '中国石油天然气管道科学研究院成功完成氢能与天然气混合输送技术试验。该技术可以利用现有天然气管网输送氢气，为未来氢能大规模应用奠定基础。',
            'source': '中石油管道研究院',
            'category': '技术创新',
            'tags': ['氢能', '天然气', '管道输送', '技术创新']
        },
        {
            'title': '江苏LNG接收站三期工程正式投产',
            'content': '江苏LNG接收站三期扩建工程今日正式投产运行。项目新增3座20万立方米储罐，年接收能力从650万吨提升至1000万吨，将有效提升长三角地区天然气供应保障能力。',
            'source': '中石油新闻中心',
            'category': '企业新闻',
            'tags': ['江苏', 'LNG接收站', '基础设施']
        }
    ]
    
    for news_data in sample_news:
        news_doc = EnergyNews.create_news_doc(**news_data)
        news_collection.insert_one(news_doc)
    
    print(f"  已插入 {len(sample_news)} 条资讯数据")
    
    # 2. 初始化价格数据
    print("2. 初始化价格数据...")
    prices_collection = db.get_collection('energy_prices')
    
    # 生成最近7天的价格数据
    products = ['管道天然气', '液化天然气(LNG)', '压缩天然气(CNG)']
    regions = ['上海', '北京', '广州', '深圳']
    
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        for product in products:
            for region in regions:
                base_price = {'管道天然气': 3.5, '液化天然气(LNG)': 4.2, '压缩天然气(CNG)': 3.8}
                price = base_price.get(product, 3.5) + random.uniform(-0.3, 0.3)
                
                price_doc = EnergyPrice.create_price_doc(
                    product_type=product,
                    price_type='spot',
                    price=round(price, 2),
                    unit='元/立方米',
                    region=region,
                    source='上海石油天然气交易中心'
                )
                price_doc['price_date'] = date
                price_doc['is_latest'] = (i == 0)  # 最新一天的数据标记为最新
                
                prices_collection.insert_one(price_doc)
    
    print(f"  已插入 {7 * len(products) * len(regions)} 条价格数据")
    
    # 3. 初始化成交数据
    print("3. 初始化成交数据...")
    deals_collection = db.get_collection('energy_deals')
    
    sample_deals = [
        {
            'buyer': '华港燃气集团有限公司',
            'seller': '中国石化天然气分公司华南天然气销售中心',
            'product_type': '管道天然气',
            'quantity': 5000,
            'price': 3.45,
            'amount': 17250000,
            'deal_date': datetime.now() - timedelta(days=1)
        },
        {
            'buyer': '上海燃气集团',
            'seller': '中海油气电集团',
            'product_type': '液化天然气(LNG)',
            'quantity': 3000,
            'price': 4.15,
            'amount': 12450000,
            'deal_date': datetime.now() - timedelta(days=2)
        },
        {
            'buyer': '深圳燃气集团',
            'seller': '中石油昆仑能源',
            'product_type': '管道天然气',
            'quantity': 8000,
            'price': 3.38,
            'amount': 27040000,
            'deal_date': datetime.now() - timedelta(days=3)
        }
    ]
    
    for deal_data in sample_deals:
        deal_doc = EnergyDeal.create_deal_doc(**deal_data)
        deals_collection.insert_one(deal_doc)
    
    print(f"  已插入 {len(sample_deals)} 条成交数据")
    
    # 4. 初始化研报数据
    print("4. 初始化研报数据...")
    reports_collection = db.get_collection('energy_reports')
    
    sample_reports = [
        {
            'title': '2024年中国天然气市场发展趋势分析',
            'author': '张明',
            'organization': '中国石油经济技术研究院',
            'report_type': '行业分析',
            'summary': '本报告深入分析了2024年中国天然气市场的供需状况、价格走势、政策环境等关键因素，并对未来发展趋势进行了预测。',
            'file_path': '/reports/2024_gas_market_analysis.pdf',
            'tags': ['市场分析', '2024年', '发展趋势'],
            'access_level': 'free'
        },
        {
            'title': 'LNG进口策略优化研究报告',
            'author': '李华',
            'organization': '上海国际能源交易中心',
            'report_type': '市场预测',
            'summary': '基于国际LNG市场价格波动和供应格局变化，本报告提出了优化中国LNG进口策略的建议。',
            'file_path': '/reports/lng_import_strategy.pdf',
            'tags': ['LNG', '进口策略', '国际市场'],
            'access_level': 'paid'
        },
        {
            'title': '碳中和背景下天然气行业转型路径研究',
            'author': '王强',
            'organization': '清华大学能源环境经济研究所',
            'report_type': '技术研究',
            'summary': '探讨在碳中和目标下，天然气行业如何通过技术创新和产业升级实现绿色转型。',
            'file_path': '/reports/carbon_neutral_transformation.pdf',
            'tags': ['碳中和', '转型升级', '技术创新'],
            'access_level': 'free'
        }
    ]
    
    for report_data in sample_reports:
        report_doc = EnergyReport.create_report_doc(**report_data)
        reports_collection.insert_one(report_doc)
    
    print(f"  已插入 {len(sample_reports)} 条研报数据")
    
    # 5. 初始化指数数据
    print("5. 初始化指数数据...")
    indexes_collection = db.get_collection('energy_indexes')
    
    # 生成最近7天的指数数据
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        base_value = 100
        
        # 天然气价格指数
        price_index_value = base_value + random.uniform(-5, 5)
        price_index_doc = EnergyIndex.create_index_doc(
            index_name='中国天然气价格指数',
            index_value=round(price_index_value, 2),
            change_value=round(random.uniform(-2, 2), 2),
            change_rate=round(random.uniform(-2, 2), 2),
            index_date=date
        )
        indexes_collection.insert_one(price_index_doc)
        
        # 天然气供需指数
        supply_demand_value = base_value + random.uniform(-3, 3)
        supply_demand_doc = EnergyIndex.create_index_doc(
            index_name='天然气供需平衡指数',
            index_value=round(supply_demand_value, 2),
            change_value=round(random.uniform(-1.5, 1.5), 2),
            change_rate=round(random.uniform(-1.5, 1.5), 2),
            index_date=date
        )
        indexes_collection.insert_one(supply_demand_doc)
    
    print(f"  已插入 {7 * 2} 条指数数据")
    
    print("\n示例数据初始化完成！")
    
    # 关闭数据库连接
    db.close()

if __name__ == '__main__':
    init_sample_data() 