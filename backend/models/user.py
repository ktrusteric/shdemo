#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户相关的数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from utils.database import db

# 用户模型
class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 基本信息
    region = db.Column(db.String(50), index=True)
    trading_products = db.Column(db.JSON)  # 希望交易的品种
    user_type = db.Column(db.String(20), default='free')  # free, premium
    
    # 标签信息
    tags = db.Column(db.JSON)  # 用户标签列表
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)
    
    # 关联关系
    behaviors = relationship('UserBehavior', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'region': self.region,
            'trading_products': self.trading_products or [],
            'user_type': self.user_type,
            'tags': self.tags or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }
    
    @classmethod
    def create_user(cls, username, email, password_hash, region=None, trading_products=None):
        """创建用户"""
        user = cls(
            username=username,
            email=email,
            password_hash=password_hash,
            region=region,
            trading_products=trading_products or []
        )
        db.session.add(user)
        db.session.commit()
        return user
    
    def update_tags(self, new_tags):
        """更新用户标签"""
        if not isinstance(new_tags, list):
            new_tags = [new_tags]
        
        current_tags = self.tags or []
        for tag in new_tags:
            if tag not in current_tags:
                current_tags.append(tag)
        
        self.tags = current_tags
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.utcnow()
        db.session.commit()


class UserBehavior(db.Model):
    """用户行为模型"""
    __tablename__ = 'user_behaviors'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # 行为信息
    behavior_type = db.Column(db.String(50), nullable=False, index=True)  # view, search, click, etc.
    target_type = db.Column(db.String(50))  # news, price, report, etc.
    target_id = db.Column(db.String(100))  # 目标资源ID
    
    # 行为详情
    details = db.Column(db.JSON)  # 详细信息
    session_id = db.Column(db.String(100))  # 会话ID
    ip_address = db.Column(db.String(45))  # IP地址
    user_agent = db.Column(db.Text)  # 用户代理
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<UserBehavior {self.behavior_type} by User {self.user_id}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'behavior_type': self.behavior_type,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'details': self.details or {},
            'session_id': self.session_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def record_behavior(cls, user_id, behavior_type, target_type=None, target_id=None, 
                       details=None, session_id=None, ip_address=None, user_agent=None):
        """记录用户行为"""
        behavior = cls(
            user_id=user_id,
            behavior_type=behavior_type,
            target_type=target_type,
            target_id=target_id,
            details=details or {},
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(behavior)
        db.session.commit()
        return behavior


class UserTag(db.Model):
    """用户标签模型"""
    __tablename__ = 'user_tags'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    tag_name = db.Column(db.String(100), nullable=False, index=True)
    tag_value = db.Column(db.String(255))
    tag_source = db.Column(db.String(50))  # system, user, behavior
    confidence = db.Column(db.Float, default=1.0)  # 标签置信度
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserTag {self.tag_name}={self.tag_value} for User {self.user_id}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tag_name': self.tag_name,
            'tag_value': self.tag_value,
            'tag_source': self.tag_source,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def add_tag(cls, user_id, tag_name, tag_value, tag_source='system', confidence=1.0):
        """添加用户标签"""
        # 检查是否已存在
        existing = cls.query.filter_by(
            user_id=user_id, 
            tag_name=tag_name, 
            tag_value=tag_value
        ).first()
        
        if existing:
            existing.confidence = max(existing.confidence, confidence)
            existing.updated_at = datetime.utcnow()
            db.session.commit()
            return existing
        
        # 创建新标签
        tag = cls(
            user_id=user_id,
            tag_name=tag_name,
            tag_value=tag_value,
            tag_source=tag_source,
            confidence=confidence
        )
        db.session.add(tag)
        db.session.commit()
        return tag 