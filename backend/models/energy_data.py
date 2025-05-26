#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
能源数据相关模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Float, Enum
from utils.database import db

# 能源资讯模型
class EnergyNews(db.Model):
    """能源资讯模型"""
    __tablename__ = 'energy_news'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(500), nullable=False, index=True)
    content = db.Column(db.Text)
    summary = db.Column(db.Text)
    source = db.Column(db.String(200))
    author = db.Column(db.String(100))
    category = db.Column(db.String(100), index=True)
    tags = db.Column(db.JSON)
    url = db.Column(db.String(500))
    
    # 统计信息
    view_count = db.Column(db.Integer, default=0)
    share_count = db.Column(db.Integer, default=0)
    
    # 状态
    status = db.Column(db.String(20), default='published')  # draft, published, archived
    is_featured = db.Column(db.Boolean, default=False)
    
    # 时间戳
    publish_time = db.Column(db.DateTime, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<EnergyNews {self.title[:50]}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'source': self.source,
            'author': self.author,
            'category': self.category,
            'tags': self.tags or [],
            'url': self.url,
            'view_count': self.view_count,
            'share_count': self.share_count,
            'status': self.status,
            'is_featured': self.is_featured,
            'publish_time': self.publish_time.isoformat() if self.publish_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def increment_view_count(self):
        """增加查看次数"""
        self.view_count += 1
        db.session.commit()


# 能源价格模型
class EnergyPrice(db.Model):
    """能源价格模型"""
    __tablename__ = 'energy_prices'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(200), nullable=False, index=True)
    product_type = db.Column(db.String(100), nullable=False, index=True)
    region = db.Column(db.String(100), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    price_unit = db.Column(db.String(50), default='元/立方米')
    
    # 价格信息
    opening_price = db.Column(db.Float)
    closing_price = db.Column(db.Float)
    highest_price = db.Column(db.Float)
    lowest_price = db.Column(db.Float)
    change_amount = db.Column(db.Float)
    change_percent = db.Column(db.Float)
    
    # 市场信息
    market = db.Column(db.String(100))
    trading_volume = db.Column(db.Float)
    
    # 状态
    is_latest = db.Column(db.Boolean, default=True, index=True)
    
    # 时间戳
    price_date = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EnergyPrice {self.product_name} {self.region} {self.price}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'product_name': self.product_name,
            'product_type': self.product_type,
            'region': self.region,
            'price': self.price,
            'price_unit': self.price_unit,
            'opening_price': self.opening_price,
            'closing_price': self.closing_price,
            'highest_price': self.highest_price,
            'lowest_price': self.lowest_price,
            'change_amount': self.change_amount,
            'change_percent': self.change_percent,
            'market': self.market,
            'trading_volume': self.trading_volume,
            'is_latest': self.is_latest,
            'price_date': self.price_date.isoformat() if self.price_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# 能源成交模型
class EnergyDeal(db.Model):
    """能源成交模型"""
    __tablename__ = 'energy_deals'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deal_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    product_name = db.Column(db.String(200), nullable=False)
    product_type = db.Column(db.String(100), nullable=False, index=True)
    
    # 交易双方
    buyer = db.Column(db.String(200), nullable=False, index=True)
    seller = db.Column(db.String(200), nullable=False, index=True)
    
    # 交易信息
    deal_price = db.Column(db.Float, nullable=False)
    deal_quantity = db.Column(db.Float, nullable=False)
    deal_amount = db.Column(db.Float, nullable=False)  # 成交金额
    price_unit = db.Column(db.String(50))
    quantity_unit = db.Column(db.String(50))
    
    # 地理位置
    region = db.Column(db.String(100), index=True)
    delivery_location = db.Column(db.String(200))
    
    # 交易详情
    deal_type = db.Column(db.String(50))  # 交易类型：现货、期货
    contract_period = db.Column(db.String(100))  # 合约期限
    
    # 时间戳
    deal_date = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EnergyDeal {self.deal_id}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'deal_id': self.deal_id,
            'product_name': self.product_name,
            'product_type': self.product_type,
            'buyer': self.buyer,
            'seller': self.seller,
            'deal_price': self.deal_price,
            'deal_quantity': self.deal_quantity,
            'deal_amount': self.deal_amount,
            'price_unit': self.price_unit,
            'quantity_unit': self.quantity_unit,
            'region': self.region,
            'delivery_location': self.delivery_location,
            'deal_type': self.deal_type,
            'contract_period': self.contract_period,
            'deal_date': self.deal_date.isoformat() if self.deal_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# 能源研报模型
class EnergyReport(db.Model):
    """能源研报模型"""
    __tablename__ = 'energy_reports'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(500), nullable=False, index=True)
    author = db.Column(db.String(200))
    organization = db.Column(db.String(200))
    report_type = db.Column(db.String(100), index=True)
    
    # 内容信息
    summary = db.Column(db.Text)
    keywords = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    
    # 文件信息
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    page_count = db.Column(db.Integer)
    
    # 访问控制
    access_level = db.Column(db.String(20), default='free', index=True)  # free, premium, vip
    
    # 统计信息
    download_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float)
    
    # 状态
    is_featured = db.Column(db.Boolean, default=False)
    
    # 时间戳
    publish_date = db.Column(db.DateTime, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<EnergyReport {self.title[:50]}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'organization': self.organization,
            'report_type': self.report_type,
            'summary': self.summary,
            'keywords': self.keywords or [],
            'tags': self.tags or [],
            'file_path': self.file_path,
            'file_size': self.file_size,
            'page_count': self.page_count,
            'access_level': self.access_level,
            'download_count': self.download_count,
            'view_count': self.view_count,
            'rating': self.rating,
            'is_featured': self.is_featured,
            'publish_date': self.publish_date.isoformat() if self.publish_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def increment_view_count(self):
        """增加查看次数"""
        self.view_count += 1
        db.session.commit()
    
    def increment_download_count(self):
        """增加下载次数"""
        self.download_count += 1
        db.session.commit()


# 能源指数模型
class EnergyIndex(db.Model):
    """能源指数模型"""
    __tablename__ = 'energy_indexes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    index_name = db.Column(db.String(200), nullable=False, index=True)
    index_code = db.Column(db.String(50), index=True)
    index_value = db.Column(db.Float, nullable=False)
    
    # 指数信息
    base_value = db.Column(db.Float)
    change_amount = db.Column(db.Float)
    change_percent = db.Column(db.Float)
    
    # 分类信息
    category = db.Column(db.String(100), index=True)
    region = db.Column(db.String(100))
    
    # 描述信息
    description = db.Column(db.Text)
    calculation_method = db.Column(db.Text)
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)
    
    # 时间戳
    index_date = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EnergyIndex {self.index_name} {self.index_value}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'index_name': self.index_name,
            'index_code': self.index_code,
            'index_value': self.index_value,
            'base_value': self.base_value,
            'change_amount': self.change_amount,
            'change_percent': self.change_percent,
            'category': self.category,
            'region': self.region,
            'description': self.description,
            'calculation_method': self.calculation_method,
            'is_active': self.is_active,
            'index_date': self.index_date.isoformat() if self.index_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 