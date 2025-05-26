#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
导入知识库文章到MongoDB
"""

import os
import sys
import json
from datetime import datetime
import re

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import db
from models.energy_data import EnergyNews, EnergyReport


def extract_regions_from_content(content):
    """从内容中提取地区标签"""
    regions = []
    # 定义常见地区关键词
    region_keywords = {
        '上海': ['上海', '沪'],
        '北京': ['北京', '京'],
        '广州': ['广州', '广东', '粤'],
        '深圳': ['深圳'],
        '浙江': ['浙江', '杭州', '宁波'],
        '江苏': ['江苏', '南京', '苏州'],
        '山东': ['山东', '青岛', '济南'],
        '天津': ['天津', '津'],
        '重庆': ['重庆', '渝'],
        '四川': ['四川', '成都', '川'],
        '湖北': ['湖北', '武汉', '鄂'],
        '湖南': ['湖南', '长沙', '湘'],
        '河南': ['河南', '郑州', '豫'],
        '河北': ['河北', '石家庄', '冀'],
        '福建': ['福建', '福州', '厦门', '闽'],
        '安徽': ['安徽', '合肥', '皖'],
        '江西': ['江西', '南昌', '赣'],
        '陕西': ['陕西', '西安', '陕'],
        '新疆': ['新疆'],
        '西藏': ['西藏'],
        '内蒙古': ['内蒙古', '内蒙'],
        '广西': ['广西', '南宁', '桂'],
        '海南': ['海南', '海口'],
        '贵州': ['贵州', '贵阳', '黔'],
        '云南': ['云南', '昆明', '滇'],
        '甘肃': ['甘肃', '兰州', '甘'],
        '青海': ['青海', '西宁'],
        '宁夏': ['宁夏', '银川'],
        '黑龙江': ['黑龙江', '哈尔滨', '黑'],
        '吉林': ['吉林', '长春', '吉'],
        '辽宁': ['辽宁', '沈阳', '大连', '辽']
    }
    
    for region, keywords in region_keywords.items():
        for keyword in keywords:
            if keyword in content:
                if region not in regions:
                    regions.append(region)
                break
    
    return regions


def extract_product_tags_from_content(content):
    """从内容中提取产品类型标签"""
    products = []
    product_keywords = {
        '管道天然气': ['管道天然气', '管道气', 'PNG'],
        '液化天然气': ['液化天然气', 'LNG', '液化气'],
        '压缩天然气': ['压缩天然气', 'CNG', '压缩气'],
        '原油': ['原油', '石油'],
        '成品油': ['成品油', '汽油', '柴油'],
        '煤炭': ['煤炭', '煤']
    }
    
    for product, keywords in product_keywords.items():
        for keyword in keywords:
            if keyword in content:
                if product not in products:
                    products.append(product)
                break
    
    return products


def extract_policy_tags_from_content(content):
    """从内容中提取政策相关标签"""
    policies = []
    policy_keywords = {
        '价格政策': ['价格', '定价', '价格机制', '价格管理'],
        '市场改革': ['市场化', '改革', '市场建设'],
        '民营经济': ['民营', '民企', '民营企业'],
        '绿色低碳': ['绿色', '低碳', '碳中和', '碳减排', '新能源'],
        '安全保供': ['保供', '供应', '储备', '应急'],
        '交易规则': ['交易', '挂牌', '竞价', '交收'],
        '质量标准': ['质量', '标准', 'GB/', '国标'],
        '监管政策': ['监管', '管理办法', '规范', '监督']
    }
    
    for policy, keywords in policy_keywords.items():
        for keyword in keywords:
            if keyword in content:
                if policy not in policies:
                    policies.append(policy)
                break
    
    return policies


def parse_date_string(date_str):
    """解析各种格式的日期字符串"""
    if not date_str:
        return datetime.now()
    
    # 移除空格和特殊字符
    date_str = date_str.strip().replace(' ', '').replace('-', '')
    
    # 尝试不同的日期格式
    formats = [
        '%Y%m%d',
        '%Y/%m/%d',
        '%Y.%m.%d',
        '%Y年%m月%d日',
        '%m/%d/%y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    
    # 如果都失败了，返回当前日期
    return datetime.now()


def import_knowledge_base_json():
    """导入JSON格式的知识库数据"""
    json_file = os.path.join(os.path.dirname(__file__), '..', 'docs', '知识库标签结构化数据-417eb46d29.json')
    
    if not os.path.exists(json_file):
        print(f"找不到文件: {json_file}")
        return
    
    print("开始导入知识库JSON数据...")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    news_collection = db.get_collection('energy_news')
    reports_collection = db.get_collection('energy_reports')
    
    # 处理规章制度知识库
    if '规章制度知识库' in data:
        print("\n处理规章制度知识库...")
        for item in data['规章制度知识库']:
            # 提取所有标签
            all_tags = item.get('标签', [])
            
            # 从内容中提取额外的标签
            content = item.get('详情内容', '')
            region_tags = extract_regions_from_content(content)
            product_tags = extract_product_tags_from_content(content)
            policy_tags = extract_policy_tags_from_content(content)
            
            # 合并所有标签
            all_tags.extend(region_tags)
            all_tags.extend(product_tags)
            all_tags.extend(policy_tags)
            all_tags = list(set(all_tags))  # 去重
            
            news_doc = {
                'title': item.get('详情标题', item.get('标题', '')),
                'content': content,
                'source': '上海石油天然气交易中心',
                'category': '规章制度',
                'tags': all_tags,
                'publish_time': parse_date_string(item.get('发布时间', '')),
                'view_count': 0,
                'is_featured': False,
                'status': 'published',
                'url': item.get('页面地址', '')
            }
            
            # 检查是否已存在
            if not news_collection.find_one({'title': news_doc['title']}):
                news_collection.insert_one(news_doc)
                print(f"  插入规章制度: {news_doc['title']}")
    
    # 处理上市品种与交易指引知识库
    if '上市品种与交易指引知识库' in data:
        print("\n处理上市品种与交易指引知识库...")
        for item in data['上市品种与交易指引知识库']:
            all_tags = item.get('标签', [])
            content = item.get('详情内容', '')
            
            # 提取标签
            region_tags = extract_regions_from_content(content)
            product_tags = extract_product_tags_from_content(content)
            all_tags.extend(region_tags)
            all_tags.extend(product_tags)
            all_tags = list(set(all_tags))
            
            # 作为研报存储
            report_doc = {
                'title': item.get('标题', ''),
                'author': '上海石油天然气交易中心',
                'organization': '上海石油天然气交易中心',
                'report_type': '交易指引',
                'summary': content[:200] + '...' if len(content) > 200 else content,
                'file_path': item.get('页面地址', ''),
                'tags': all_tags,
                'publish_date': parse_date_string(item.get('发布时间', '')),
                'download_count': 0,
                'view_count': 0,
                'is_featured': False,
                'access_level': 'free'
            }
            
            if not reports_collection.find_one({'title': report_doc['title']}):
                reports_collection.insert_one(report_doc)
                print(f"  插入交易指引: {report_doc['title']}")
    
    # 处理客服助手知识库
    if '客服助手知识库' in data:
        print("\n处理客服助手知识库...")
        for item in data['客服助手知识库']:
            all_tags = item.get('标签', [])
            content = item.get('详情内容', '')
            
            # 提取标签
            region_tags = extract_regions_from_content(content)
            policy_tags = extract_policy_tags_from_content(content)
            all_tags.extend(region_tags)
            all_tags.extend(policy_tags)
            all_tags = list(set(all_tags))
            
            news_doc = {
                'title': item.get('详情标题', item.get('标题', '')),
                'content': content,
                'source': '上海石油天然气交易中心',
                'category': '服务指南',
                'tags': all_tags,
                'publish_time': parse_date_string(item.get('发布时间', '')),
                'view_count': 0,
                'is_featured': False,
                'status': 'published',
                'url': item.get('页面地址', '')
            }
            
            if not news_collection.find_one({'title': news_doc['title']}):
                news_collection.insert_one(news_doc)
                print(f"  插入服务指南: {news_doc['title']}")
    
    # 处理政策数据详情知识库
    if '政策数据详情知识库' in data:
        print("\n处理政策数据详情知识库...")
        for item in data['政策数据详情知识库']:
            all_tags = item.get('标签', [])
            content = item.get('详细内容', '')
            title = item.get('标题', '')
            
            # 提取所有类型的标签
            region_tags = extract_regions_from_content(title + ' ' + content)
            product_tags = extract_product_tags_from_content(title + ' ' + content)
            policy_tags = extract_policy_tags_from_content(title + ' ' + content)
            
            all_tags.extend(region_tags)
            all_tags.extend(product_tags)
            all_tags.extend(policy_tags)
            all_tags = list(set(all_tags))
            
            news_doc = {
                'title': title,
                'content': content,
                'source': '政策发布',
                'category': '政策法规',
                'tags': all_tags,
                'publish_time': parse_date_string(item.get('发布日期', '')),
                'view_count': 0,
                'is_featured': True if '国家能源局' in title or '发改委' in title else False,
                'status': 'published',
                'url': item.get('链接', '')
            }
            
            if not news_collection.find_one({'title': news_doc['title']}):
                news_collection.insert_one(news_doc)
                print(f"  插入政策法规: {news_doc['title']}")


def import_markdown_files():
    """导入Markdown格式的知识库文章"""
    docs_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
    
    # 读取政策数据详情知识库
    policy_file = os.path.join(docs_dir, '政策数据详情知识库1.md')
    if os.path.exists(policy_file):
        print("\n处理政策数据详情Markdown文件...")
        with open(policy_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 这里可以进一步解析Markdown内容
        # 由于JSON文件已经包含了结构化数据，这里就不重复处理了
    
    print("\n知识库数据导入完成！")


def main():
    """主函数"""
    print("开始导入知识库数据...")
    
    # 连接数据库
    if not db.connect():
        print("数据库连接失败")
        return
    
    try:
        # 导入JSON数据
        import_knowledge_base_json()
        
        # 导入Markdown文件（如果需要）
        # import_markdown_files()
        
        # 显示统计信息
        news_collection = db.get_collection('energy_news')
        reports_collection = db.get_collection('energy_reports')
        
        news_count = news_collection.count_documents({})
        reports_count = reports_collection.count_documents({})
        
        print(f"\n导入统计:")
        print(f"  资讯总数: {news_count}")
        print(f"  研报总数: {reports_count}")
        
        # 显示标签统计
        print("\n标签统计:")
        
        # 统计地区标签
        region_pipeline = [
            {"$unwind": "$tags"},
            {"$match": {"tags": {"$in": ["上海", "北京", "广州", "深圳", "浙江", "江苏", "山东", "天津", "重庆", "四川"]}}},
            {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        region_stats = list(news_collection.aggregate(region_pipeline))
        if region_stats:
            print("  地区标签分布:")
            for stat in region_stats:
                print(f"    {stat['_id']}: {stat['count']} 篇")
        
        # 统计产品标签
        product_pipeline = [
            {"$unwind": "$tags"},
            {"$match": {"tags": {"$in": ["管道天然气", "液化天然气", "压缩天然气", "原油", "成品油", "煤炭"]}}},
            {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        product_stats = list(news_collection.aggregate(product_pipeline))
        if product_stats:
            print("\n  产品标签分布:")
            for stat in product_stats:
                print(f"    {stat['_id']}: {stat['count']} 篇")
        
    finally:
        # 关闭数据库连接
        db.close()


if __name__ == '__main__':
    main() 